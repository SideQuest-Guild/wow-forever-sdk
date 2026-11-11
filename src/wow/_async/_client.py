"""The client: configuration, authentication, retries and resource namespaces."""

import os
import re
from dataclasses import dataclass, field, replace
from functools import cached_property
from typing import TYPE_CHECKING, Self
from urllib.parse import urlencode

import httpx
from msgspec import Struct

from wow._async.resources.account import AsyncAccount
from wow._async.resources.achievement import AsyncAchievementCategories, AsyncAchievements
from wow._async.resources.auction import AsyncAuctions
from wow._async.resources.character import AsyncCharacters
from wow._async.resources.creature import AsyncCreatureFamilies, AsyncCreatureTypes
from wow._async.resources.guild import AsyncGuilds
from wow._async.resources.item import AsyncItemClasses, AsyncItems, AsyncItemSets
from wow._async.resources.mount import AsyncMounts
from wow._async.resources.pet import AsyncPets
from wow._async.resources.playable_class import AsyncPlayableClasses
from wow._async.resources.playable_race import AsyncPlayableRaces
from wow._async.resources.playable_specialization import AsyncPlayableSpecializations
from wow._async.resources.power_type import AsyncPowerTypes
from wow._async.resources.profession import AsyncProfessions
from wow._async.resources.quest import AsyncQuestAreas, AsyncQuestCategories, AsyncQuests, AsyncQuestTypes
from wow._async.resources.realm import AsyncRealms
from wow._async.resources.recipe import AsyncRecipes
from wow._async.resources.region import AsyncRegions
from wow._async.resources.reputation import AsyncReputationFactions, AsyncReputationTiers
from wow._async.resources.ruleset import AsyncRulesets
from wow._async.resources.talent import AsyncTalents, AsyncTalentTrees
from wow._async.resources.title import AsyncTitles
from wow._async.resources.toy import AsyncToys
from wow._base import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    OAUTH_URL,
    TOKEN_EXPIRY_MARGIN,
    USER_AGENT,
    OAuthToken,
    api_url,
    backoff,
    connection_error,
    parse_model,
    parse_token,
    raise_for_status,
    request_params,
    retry_delay,
    should_retry,
)
from wow._concurrency import AsyncLock, async_sleep
from wow._exceptions import WowError
from wow._response import APIResponse
from wow._types import DEFAULT_LOCALES, LOCALES, Locale, NamespaceKind, Region, is_locale

if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    from types import TracebackType

__all__ = ["AsyncClient"]


@dataclass(frozen=True, slots=True)
class _Config:
    """Per-client settings; :meth:`AsyncClient.with_options` copies and changes these."""

    region: Region
    locale: Locale
    locale_is_default: bool
    access_token: str | None = field(repr=False)
    timeout: httpx.Timeout
    max_retries: int
    base_url: str | None
    oauth_url: str
    static_version: str | None

    @property
    def api_url(self) -> str:
        return self.base_url or api_url(self.region)


@dataclass(slots=True)
class _Session:
    """State shared by a client and every copy made with :meth:`AsyncClient.with_options`."""

    http: httpx.AsyncClient
    client_id: str | None
    client_secret: str | None = field(repr=False)
    app_token: OAuthToken | None = None
    token_lock: AsyncLock = field(default_factory=AsyncLock)


class AsyncClient:
    """Async client for the World of Warcraft: Forever API.

    Game data needs app credentials from https://develop.battle.net; the client trades them for an access token and
    refreshes it before it expires. Profile routes need a user's token instead, from :meth:`exchange_code`.

    Use one client for the life of your program and close it when done; it is a context manager::

        async with AsyncClient(region="eu") as client:
            druid = await client.playable_classes.get(11)

    Args:
        client_id: App client id. Defaults to the ``BATTLENET_CLIENT_ID`` environment variable.
        client_secret: App client secret. Defaults to ``BATTLENET_CLIENT_SECRET``.
        access_token: A token to send instead of fetching one with the app credentials, such as a user token with
            the ``wow.profile`` scope.
        region: The API region to read.
        locale: The language for names and descriptions. Defaults to the region's main locale.
        timeout: Seconds, or an ``httpx.Timeout``, applied to every request.
        max_retries: Retries for connection errors, timeouts, 408, 429 and 5xx responses. ``0`` disables retrying.
        http_client: An ``httpx.AsyncClient`` to send requests through, for proxies, transports or caching. The
            caller keeps ownership and must close it.
        base_url: Override the API host, for example to point at a mock server.
        oauth_url: Override the OAuth host.
        static_version: Pin static-data requests (playable classes, items, talents and the rest of game data that
            only changes with patches) to one build, such as ``"1.60.1_70399"``, instead of Battle.net's current
            static namespace. Dynamic and profile requests are unaffected.

    Raises:
        WowError: Neither app credentials nor an access token were given.
        ValueError: ``locale``, ``max_retries`` or ``access_token`` is invalid.
    """

    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        *,
        access_token: str | None = None,
        region: Region | str = Region.US,
        locale: Locale | None = None,
        timeout: float | httpx.Timeout = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        http_client: httpx.AsyncClient | None = None,
        base_url: str | None = None,
        oauth_url: str = OAUTH_URL,
        static_version: str | None = None,
    ) -> None:
        client_id = client_id or os.environ.get("BATTLENET_CLIENT_ID")
        client_secret = client_secret or os.environ.get("BATTLENET_CLIENT_SECRET")
        if access_token is None and not (client_id and client_secret):
            msg = (
                "no credentials: pass client_id and client_secret, set BATTLENET_CLIENT_ID and "
                "BATTLENET_CLIENT_SECRET, or pass access_token"
            )
            raise WowError(msg)
        resolved_region = Region(region)
        self._config = _Config(
            region=resolved_region,
            locale=_check_locale(locale or DEFAULT_LOCALES[resolved_region]),
            locale_is_default=locale is None,
            access_token=None if access_token is None else _check_access_token(access_token),
            timeout=timeout if isinstance(timeout, httpx.Timeout) else httpx.Timeout(timeout),
            max_retries=_check_retries(max_retries),
            base_url=base_url.rstrip("/") if base_url else None,
            oauth_url=oauth_url.rstrip("/"),
            static_version=static_version,
        )
        self._session = _Session(
            http=http_client or httpx.AsyncClient(headers={"User-Agent": USER_AGENT}),
            client_id=client_id,
            client_secret=client_secret,
        )
        self._owns_http = http_client is None

    @classmethod
    def _from_parts(cls, config: _Config, session: _Session) -> Self:
        client = cls.__new__(cls)
        client._config = config  # noqa: SLF001 - initialising a copy of this class
        client._session = session  # noqa: SLF001 - initialising a copy of this class
        client._owns_http = False  # noqa: SLF001 - copies never close the shared pool
        return client

    def __repr__(self) -> str:
        return f"<{type(self).__name__} region={self.region.value} locale={self.locale}>"

    @property
    def region(self) -> Region:
        """The region this client reads."""
        return self._config.region

    @property
    def locale(self) -> Locale:
        """The locale names and descriptions come back in."""
        return self._config.locale

    @property
    def static_version(self) -> str | None:
        """The build static-data requests are pinned to, or ``None`` for Battle.net's current static namespace."""
        return self._config.static_version

    # Resources, alphabetical. Each is created on first use and bound to this client's settings.

    @cached_property
    def account(self) -> AsyncAccount:
        """The authenticated user's WoW Forever accounts and characters."""
        return AsyncAccount(self)

    @cached_property
    def achievement_categories(self) -> AsyncAchievementCategories:
        """The groups achievements are organized into."""
        return AsyncAchievementCategories(self)

    @cached_property
    def achievements(self) -> AsyncAchievements:
        """Achievements such as Explorer and Master of Alterac Valley."""
        return AsyncAchievements(self)

    @cached_property
    def auctions(self) -> AsyncAuctions:
        """The auction houses Forever's rulesets use in place of realm auction houses."""
        return AsyncAuctions(self)

    @cached_property
    def characters(self) -> AsyncCharacters:
        """Any character's public profile: gear, stats, talents, professions and more."""
        return AsyncCharacters(self)

    @cached_property
    def creature_families(self) -> AsyncCreatureFamilies:
        """Pet families such as Bat and Wolf."""
        return AsyncCreatureFamilies(self)

    @cached_property
    def creature_types(self) -> AsyncCreatureTypes:
        """Creature types such as Beast and Dragonkin."""
        return AsyncCreatureTypes(self)

    @cached_property
    def guilds(self) -> AsyncGuilds:
        """Guilds and their rosters."""
        return AsyncGuilds(self)

    @cached_property
    def item_classes(self) -> AsyncItemClasses:
        """Item classes such as Weapon and Consumable."""
        return AsyncItemClasses(self)

    @cached_property
    def item_sets(self) -> AsyncItemSets:
        """Equipment sets."""
        return AsyncItemSets(self)

    @cached_property
    def items(self) -> AsyncItems:
        """Items."""
        return AsyncItems(self)

    @cached_property
    def mounts(self) -> AsyncMounts:
        """Mounts."""
        return AsyncMounts(self)

    @cached_property
    def pets(self) -> AsyncPets:
        """Battle pet species."""
        return AsyncPets(self)

    @cached_property
    def playable_classes(self) -> AsyncPlayableClasses:
        """Playable classes such as Warrior and Mage."""
        return AsyncPlayableClasses(self)

    @cached_property
    def playable_races(self) -> AsyncPlayableRaces:
        """Playable races such as Human and Orc."""
        return AsyncPlayableRaces(self)

    @cached_property
    def playable_specializations(self) -> AsyncPlayableSpecializations:
        """Class specializations such as Fury or Restoration."""
        return AsyncPlayableSpecializations(self)

    @cached_property
    def power_types(self) -> AsyncPowerTypes:
        """Power types such as Mana and Rage."""
        return AsyncPowerTypes(self)

    @cached_property
    def professions(self) -> AsyncProfessions:
        """Professions such as Tailoring and Cooking."""
        return AsyncProfessions(self)

    @cached_property
    def quest_areas(self) -> AsyncQuestAreas:
        """The zones quests take place in."""
        return AsyncQuestAreas(self)

    @cached_property
    def quest_categories(self) -> AsyncQuestCategories:
        """Quest groupings such as Epic or Seasonal."""
        return AsyncQuestCategories(self)

    @cached_property
    def quest_types(self) -> AsyncQuestTypes:
        """Quest kinds such as Elite, PvP or Raid."""
        return AsyncQuestTypes(self)

    @cached_property
    def quests(self) -> AsyncQuests:
        """Individual quests."""
        return AsyncQuests(self)

    @cached_property
    def realms(self) -> AsyncRealms:
        """WoW Forever realms."""
        return AsyncRealms(self)

    @cached_property
    def recipes(self) -> AsyncRecipes:
        """Profession recipes."""
        return AsyncRecipes(self)

    @cached_property
    def regions(self) -> AsyncRegions:
        """Battle.net API regions."""
        return AsyncRegions(self)

    @cached_property
    def reputation_factions(self) -> AsyncReputationFactions:
        """Reputation factions such as cities, tribes and armies."""
        return AsyncReputationFactions(self)

    @cached_property
    def reputation_tiers(self) -> AsyncReputationTiers:
        """The standing levels a faction's reputation can reach."""
        return AsyncReputationTiers(self)

    @cached_property
    def rulesets(self) -> AsyncRulesets:
        """Rulesets such as Normal and PvP, which Forever has in place of realms."""
        return AsyncRulesets(self)

    @cached_property
    def talent_trees(self) -> AsyncTalentTrees:
        """Class and specialization talent trees."""
        return AsyncTalentTrees(self)

    @cached_property
    def talents(self) -> AsyncTalents:
        """Individual talents across every class and specialization."""
        return AsyncTalents(self)

    @cached_property
    def titles(self) -> AsyncTitles:
        """Character titles such as Commander."""
        return AsyncTitles(self)

    @cached_property
    def toys(self) -> AsyncToys:
        """Toy-box toys."""
        return AsyncToys(self)

    def with_options(
        self,
        *,
        region: Region | str | None = None,
        locale: Locale | None = None,
        access_token: str | None = None,
        timeout: float | httpx.Timeout | None = None,
        max_retries: int | None = None,
        static_version: str | None = None,
    ) -> Self:
        """Return a client with some settings changed.

        The copy shares the connection pool and the cached app token, so it is cheap; make one per region, locale
        or user token as needed. Only the original client closes the pool.

        Args:
            region: Read another region. The locale follows the region unless one was set explicitly.
            locale: Use another locale.
            access_token: Authenticate as a user, for profile routes.
            timeout: Change the request timeout.
            max_retries: Change the retry budget.
            static_version: Pin static-data requests to another build.

        Raises:
            ValueError: ``locale``, ``max_retries`` or ``access_token`` is invalid.
        """
        config = self._config
        new_region = Region(region) if region is not None else config.region
        if locale is not None:
            new_locale, locale_is_default = _check_locale(locale), False
        elif config.locale_is_default:
            new_locale, locale_is_default = DEFAULT_LOCALES[new_region], True
        else:
            new_locale, locale_is_default = config.locale, False
        changed = replace(
            config,
            region=new_region,
            locale=new_locale,
            locale_is_default=locale_is_default,
            access_token=config.access_token if access_token is None else _check_access_token(access_token),
            timeout=config.timeout
            if timeout is None
            else timeout
            if isinstance(timeout, httpx.Timeout)
            else httpx.Timeout(timeout),
            max_retries=config.max_retries if max_retries is None else _check_retries(max_retries),
            static_version=static_version if static_version is not None else config.static_version,
        )
        return self._from_parts(changed, self._session)

    async def aclose(self) -> None:
        """Close the connection pool, unless it was passed in as ``http_client`` or this client is a copy."""
        if self._owns_http:
            await self._session.http.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.aclose()

    async def get(
        self,
        path: str,
        *,
        namespace: NamespaceKind | None = None,
        params: Mapping[str, str | int] | None = None,
    ) -> APIResponse:
        """GET any document, for routes without a typed method or links followed by hand.

        Args:
            path: A path such as ``/data/wow/playable-class/1``, or a full ``href`` from a document's links. Hrefs
                already carry their namespace.
            namespace: The document family to read. Leave it out for hrefs.
            params: Extra query parameters.

        Raises:
            ValueError: ``path`` is a URL on another host; the client never sends its token elsewhere.
            APIStatusError: Battle.net answered with an error status.
            APIConnectionError: No response arrived.
        """
        api = httpx.URL(self._config.api_url)
        if path.startswith(("https://", "http://")):
            url = httpx.URL(path)
            if (url.scheme, url.host, url.port) != (api.scheme, api.host, api.port):
                msg = f"refusing to send credentials to {url.scheme}://{url.host}: links must point at {api}"
                raise ValueError(msg)
        else:
            url = httpx.URL(f"{self._config.api_url}/{path.lstrip('/')}")
        merged = {
            **dict(url.params),
            **request_params(namespace, self._config.region, self._config.locale, params, self._config.static_version),
        }
        return APIResponse(await self._api_request(str(url.copy_with(query=None)), merged))

    async def _get_model[ModelT: Struct](
        self,
        namespace: NamespaceKind,
        path: str,
        model: type[ModelT],
        params: Mapping[str, str | int] | None = None,
    ) -> ModelT:
        url = f"{self._config.api_url}{path}"
        response = await self._api_request(
            url,
            request_params(namespace, self._config.region, self._config.locale, params, self._config.static_version),
        )
        return parse_model(response, model)

    def authorization_url(
        self,
        redirect_uri: str,
        *,
        state: str,
        scopes: str | Iterable[str] = ("wow.profile",),
    ) -> str:
        """Build the Battle.net login URL for the authorization code flow.

        Send the user here; Battle.net redirects back to ``redirect_uri`` with ``code`` and ``state`` query
        parameters. Check ``state`` matches, then pass ``code`` to :meth:`exchange_code`.

        Args:
            redirect_uri: A redirect URL registered for the app.
            state: An unguessable value tied to the user's session, to stop cross-site request forgery.
            scopes: Scopes to request, as one string or several. ``wow.profile`` unlocks the account profile; add
                ``openid`` for an ID token.
        """
        query = urlencode(
            {
                "response_type": "code",
                "client_id": self._require_client_id(),
                "redirect_uri": redirect_uri,
                "scope": scopes if isinstance(scopes, str) else " ".join(scopes),
                "state": state,
            }
        )
        return f"{self._config.oauth_url}/authorize?{query}"

    async def exchange_code(self, code: str, redirect_uri: str) -> OAuthToken:
        """Trade an authorization code for the user's access token.

        Use the token with ``client.with_options(access_token=token.access_token)``.

        Args:
            code: The ``code`` query parameter Battle.net redirected back with.
            redirect_uri: The same ``redirect_uri`` given to :meth:`authorization_url`.

        Raises:
            AuthenticationError: The app credentials were rejected.
            BadRequestError: The code is invalid, expired or already used, or ``redirect_uri`` does not match.
        """
        # Never retried: a code is single-use, so a retry after a lost response would only fail with invalid_grant.
        response = await self._token_request(
            {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri}, max_retries=0
        )
        return parse_token(response)

    def _require_client_id(self) -> str:
        if not self._session.client_id:
            msg = "this needs app credentials, but the client was created with only an access token"
            raise WowError(msg)
        return self._session.client_id

    async def _token_request(self, data: Mapping[str, str], *, max_retries: int | None = None) -> httpx.Response:
        client_id = self._require_client_id()
        auth = httpx.BasicAuth(client_id, self._session.client_secret or "")
        url = f"{self._config.oauth_url}/token"
        return await self._send("POST", url, data=data, auth=auth, max_retries=max_retries)

    async def _app_token(self) -> OAuthToken:
        session = self._session
        token = session.app_token
        if token is not None and not token.expires_within(TOKEN_EXPIRY_MARGIN):
            return token
        async with session.token_lock:
            token = session.app_token
            if token is None or token.expires_within(TOKEN_EXPIRY_MARGIN):
                token = parse_token(await self._token_request({"grant_type": "client_credentials"}))
                session.app_token = token
            return token

    async def _api_request(self, url: str, params: Mapping[str, str | int]) -> httpx.Response:
        """GET an API URL with a bearer token, replacing a rejected app token once."""
        token_refreshed = False
        while True:
            app_token = None if self._config.access_token is not None else await self._app_token()
            bearer = app_token.access_token if app_token is not None else self._config.access_token
            response = await self._send("GET", url, params=params, headers={"Authorization": f"Bearer {bearer}"})
            if response.status_code == httpx.codes.UNAUTHORIZED and app_token is not None and not token_refreshed:
                # The app token was revoked or expired early. Drop it unless a concurrent request already replaced
                # it, then fetch (or reuse) a fresh one, once.
                async with self._session.token_lock:
                    if self._session.app_token is app_token:
                        self._session.app_token = None
                token_refreshed = True
                continue
            raise_for_status(response)
            return response

    async def _send(
        self,
        method: str,
        url: str,
        *,
        params: Mapping[str, str | int] | None = None,
        data: Mapping[str, str] | None = None,
        headers: Mapping[str, str] | None = None,
        auth: httpx.Auth | None = None,
        max_retries: int | None = None,
    ) -> httpx.Response:
        """Send a request, retrying connection failures, timeouts, 408, 429 and 5xx; never raises for status."""
        config = self._config
        budget = config.max_retries if max_retries is None else max_retries
        retries_done = 0
        while True:
            try:
                response = await self._session.http.request(
                    method, url, params=params, data=data, headers=headers, auth=auth, timeout=config.timeout
                )
            except httpx.TransportError as error:
                if retries_done >= budget:
                    raise connection_error(method, error) from error
                delay = backoff(retries_done)
            else:
                if not should_retry(response) or retries_done >= budget:
                    return response
                if (delay := retry_delay(retries_done, response)) is None:
                    return response
            await async_sleep(delay)
            retries_done += 1


# A bearer token is visible ASCII with no whitespace (RFC 6750). No other character can be part of one, and most
# make the ``Authorization`` header illegal.
_SENDABLE_TOKEN = re.compile(r"[!-~]+")


def _check_access_token(access_token: str) -> str:
    if not _SENDABLE_TOKEN.fullmatch(access_token):
        # Never quote the token here: this message is logged. Left unchecked, the HTTP layer would fail on every
        # attempt and name the whole header, token included, in its error.
        msg = (
            "access_token is empty, or has whitespace, control or non-ASCII characters; "
            "pass the token exactly as Battle.net issued it, without a trailing newline"
        )
        raise ValueError(msg)
    return access_token


def _check_locale(locale: str) -> Locale:
    if not is_locale(locale):
        msg = f"unknown locale {locale!r}; expected one of {', '.join(sorted(LOCALES))}"
        raise ValueError(msg)
    return locale


def _check_retries(max_retries: int) -> int:
    if max_retries < 0:
        msg = f"max_retries must be 0 or more, got {max_retries}"
        raise ValueError(msg)
    return max_retries
