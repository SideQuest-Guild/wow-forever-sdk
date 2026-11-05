"""I/O-free pieces shared by the sync and async clients: defaults, retry policy, tokens and response parsing."""

import email.utils
import random
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from importlib.metadata import version
from typing import TYPE_CHECKING, Final

import httpx
from pydantic import BaseModel, ConfigDict, ValidationError

from wow._exceptions import APIConnectionError, APIResponseValidationError, APITimeoutError, error_for_response

if TYPE_CHECKING:
    from collections.abc import Mapping

    from wow._types import Locale, NamespaceKind, Region

__all__ = [
    "DEFAULT_MAX_RETRIES",
    "DEFAULT_TIMEOUT",
    "OAUTH_URL",
    "OAuthToken",
    "api_url",
    "backoff",
    "connection_error",
    "namespace_for",
    "parse_model",
    "parse_token",
    "raise_for_status",
    "request_params",
    "retry_delay",
    "should_retry",
]

DEFAULT_TIMEOUT: Final = httpx.Timeout(15.0, connect=5.0)
"""Fifteen seconds per read, write and pool wait; five to connect."""

DEFAULT_MAX_RETRIES: Final = 2
"""Retries after the first attempt for connection errors, timeouts, 408, 429 and 5xx responses."""

OAUTH_URL: Final = "https://oauth.battle.net"
"""The OAuth host shared by the US, EU, KR and TW regions."""

USER_AGENT: Final = f"wow-python/{version('wow')} httpx/{httpx.__version__}"

INITIAL_RETRY_DELAY: Final = 0.5
MAX_RETRY_DELAY: Final = 8.0
MAX_RETRY_AFTER: Final = 60.0
"""A ``Retry-After`` longer than this is not waited out; the error is raised instead."""

TOKEN_EXPIRY_MARGIN: Final = timedelta(minutes=5)
"""App tokens are refreshed this long before Battle.net says they expire."""

_RETRYABLE_STATUSES: Final = frozenset({408, 429, 500, 502, 503, 504})


def api_url(region: Region) -> str:
    """Return the API host for a region, such as ``https://us.api.blizzard.com``."""
    return f"https://{region.value}.api.blizzard.com"


def namespace_for(kind: NamespaceKind, region: Region) -> str:
    """Return the WoW Forever namespace for a document family, such as ``static-forever-us``."""
    return f"{kind}-forever-{region.value}"


def should_retry(response: httpx.Response) -> bool:
    """Whether a failed response is worth another attempt."""
    return response.status_code in _RETRYABLE_STATUSES


def backoff(retries_done: int) -> float:
    """Exponential backoff: half a second doubling up to eight, minus up to 25% jitter so clients spread out."""
    delay = min(INITIAL_RETRY_DELAY * 2**retries_done, MAX_RETRY_DELAY)
    return delay * (1 - 0.25 * random.random())  # noqa: S311 - jitter, not cryptography


def retry_delay(retries_done: int, response: httpx.Response) -> float | None:
    """Seconds to wait before retrying ``response``, or ``None`` when the server asked for too long a wait.

    ``Retry-After`` wins when it is valid, as whole seconds or an HTTP date (RFC 9110); otherwise :func:`backoff`
    decides.
    """
    header = response.headers.get("retry-after")
    if header is None:
        return backoff(retries_done)
    if header.isascii() and header.isdigit():
        seconds = float(header)
    else:
        try:
            seconds = (email.utils.parsedate_to_datetime(header) - datetime.now(UTC)).total_seconds()
        except TypeError, ValueError:
            return backoff(retries_done)
    if seconds > MAX_RETRY_AFTER:
        return None
    return max(seconds, 0.0)


def raise_for_status(response: httpx.Response) -> None:
    """Raise the matching :class:`~wow.APIStatusError` subclass for a 4xx or 5xx response."""
    if response.is_error:
        raise error_for_response(response)


def connection_error(method: str, error: httpx.TransportError) -> APIConnectionError:
    """Wrap an ``httpx`` transport failure in :class:`~wow.APITimeoutError` or :class:`~wow.APIConnectionError`."""
    if isinstance(error, httpx.TimeoutException):
        return APITimeoutError(f"timed out: {method} {error.request.url}", request=error.request)
    return APIConnectionError(f"connection failed: {method} {error.request.url}: {error}", request=error.request)


def parse_model[ModelT: BaseModel](response: httpx.Response, model: type[ModelT]) -> ModelT:
    """Validate a successful response body into ``model``."""
    try:
        return model.model_validate_json(response.content)
    except ValidationError as error:
        message = f"response from {response.request.url} does not match {model.__name__}"
        raise APIResponseValidationError(message, response=response, error=error) from error


@dataclass(frozen=True, slots=True)
class OAuthToken:
    """An access token issued by ``oauth.battle.net``.

    Attributes:
        access_token: The bearer token to send to the API.
        expires_at: When Battle.net stops accepting it.
        scopes: The scopes it was granted; ``wow.profile`` is needed for profile routes.
        token_type: Always ``bearer`` today.
        sub: The Battle.net account id, for user tokens.
        id_token: The OpenID Connect ID token, when ``openid`` was requested.
    """

    access_token: str = field(repr=False)
    expires_at: datetime
    scopes: frozenset[str] = frozenset()
    token_type: str = "bearer"  # noqa: S105 - a token type, not a secret
    sub: str | None = None
    id_token: str | None = field(default=None, repr=False)

    def expires_within(self, margin: timedelta) -> bool:
        """Whether the token expires within ``margin`` from now."""
        return datetime.now(UTC) + margin >= self.expires_at


class _TokenPayload(BaseModel):
    """The JSON body of a successful ``/token`` response."""

    # Validation errors would otherwise quote the token in tracebacks and logs.
    model_config = ConfigDict(hide_input_in_errors=True)

    access_token: str
    expires_in: int
    token_type: str = "bearer"  # noqa: S105 - a token type, not a secret
    scope: str = ""
    sub: str | None = None
    id_token: str | None = None


def parse_token(response: httpx.Response) -> OAuthToken:
    """Read a token endpoint response.

    Raises:
        APIStatusError: The token endpoint answered with an error, such as :class:`~wow.AuthenticationError`.
        APIResponseValidationError: The body is not a token.
    """
    raise_for_status(response)
    payload = parse_model(response, _TokenPayload)
    return OAuthToken(
        access_token=payload.access_token,
        expires_at=datetime.now(UTC) + timedelta(seconds=payload.expires_in),
        scopes=frozenset(payload.scope.split()),
        token_type=payload.token_type,
        sub=payload.sub,
        id_token=payload.id_token,
    )


def request_params(
    kind: NamespaceKind | None,
    region: Region,
    locale: Locale,
    params: Mapping[str, str | int] | None,
) -> dict[str, str | int]:
    """Merge the namespace and locale into a request's query parameters; explicit params win."""
    merged: dict[str, str | int] = {"locale": locale}
    if kind is not None:
        merged["namespace"] = namespace_for(kind, region)
    if params:
        merged.update(params)
    return merged
