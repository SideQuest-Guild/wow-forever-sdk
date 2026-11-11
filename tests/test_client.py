import base64
import threading
import time
import traceback
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime
from functools import partial
from typing import TYPE_CHECKING

import anyio
import httpx
import pytest

from tests.conftest import APP_TOKEN, ClientFactory, load_fixture, mock_route
from wow import (
    APIConnectionError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AsyncClient,
    AuthenticationError,
    BadRequestError,
    Client,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    Region,
    WowError,
)
from wow.models import Media, PlayableClass

if TYPE_CHECKING:
    import respx

CLASS_PATH = "/data/wow/playable-class/1"
EMPTY_DOCUMENT = {"_links": {"self": {"href": "https://us.api.blizzard.com/data/wow/x"}}}


def class_route(battlenet: respx.MockRouter) -> respx.Route:
    return mock_route(battlenet, CLASS_PATH)


def api_authorization(battlenet: respx.MockRouter) -> str:
    return battlenet["api"].calls.last.request.headers["authorization"]


class TestConfiguration:
    def test_missing_credentials_raise(self, make_client: ClientFactory, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("BATTLENET_CLIENT_ID", raising=False)
        monkeypatch.delenv("BATTLENET_CLIENT_SECRET", raising=False)

        with pytest.raises(WowError, match="no credentials"):
            make_client()

    def test_credentials_come_from_the_environment(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("BATTLENET_CLIENT_ID", "env-id")
        monkeypatch.setenv("BATTLENET_CLIENT_SECRET", "env-secret")

        make_client().playable_classes.get(1)

        authorization = battlenet["token"].calls.last.request.headers["authorization"]
        assert authorization == "Basic " + base64.b64encode(b"env-id:env-secret").decode()

    @pytest.mark.parametrize(
        ("setting", "message"),
        [({"locale": "en_XX"}, "unknown locale 'en_XX'"), ({"max_retries": -1}, "max_retries must be 0 or more")],
    )
    def test_invalid_settings_are_rejected(
        self, make_client: ClientFactory, setting: dict[str, object], message: str
    ) -> None:
        with pytest.raises(ValueError, match=message):
            make_client("id", "secret", **setting)

    def test_region_selects_host_namespace_and_default_locale(
        self, make_client: ClientFactory, battlenet: respx.MockRouter
    ) -> None:
        route = battlenet.get("https://eu.api.blizzard.com/data/wow/playable-class/1").respond(json=EMPTY_DOCUMENT)

        make_client("id", "secret", region="eu").get(CLASS_PATH, namespace="static")

        params = route.calls.last.request.url.params
        assert (params["namespace"], params["locale"]) == ("static-forever-eu", "en_GB")

    def test_static_version_pins_static_requests_only(
        self, make_client: ClientFactory, battlenet: respx.MockRouter
    ) -> None:
        client = make_client("id", "secret", static_version="1.60.1_70399")

        client.get(CLASS_PATH, namespace="static")
        static_params = battlenet["api"].calls.last.request.url.params
        assert static_params["namespace"] == "static-1.60.1_70399-forever-us"

        client.get("/data/wow/realm/index", namespace="dynamic")
        dynamic_params = battlenet["api"].calls.last.request.url.params
        assert dynamic_params["namespace"] == "dynamic-forever-us"

        assert client.static_version == "1.60.1_70399"

    def test_custom_hosts_replace_battlenet(self, make_client: ClientFactory, battlenet: respx.MockRouter) -> None:
        token = battlenet.post("http://oauth.test/token").respond(json={"access_token": "t", "expires_in": 86399})
        api = battlenet.get("http://api.test/mock/data/wow/playable-class/1").respond(
            json=load_fixture("static/playable-class/1")["body"]
        )

        client = make_client("id", "secret", base_url="http://api.test/mock/", oauth_url="http://oauth.test")
        client.get(CLASS_PATH, namespace="static")
        client.playable_classes.get(1)

        assert token.call_count == 1
        assert api.call_count == 2

    def test_timeout_applies_to_every_request(self, make_client: ClientFactory, battlenet: respx.MockRouter) -> None:
        client = make_client("id", "secret", timeout=3)

        client.playable_classes.get(1)
        client.with_options(timeout=httpx.Timeout(9, connect=1)).playable_classes.get(1)

        first, second = (call.request.extensions["timeout"] for call in battlenet["api"].calls)
        assert first == {"connect": 3, "read": 3, "write": 3, "pool": 3}
        assert second == {"connect": 1, "read": 9, "write": 9, "pool": 9}

    @pytest.mark.usefixtures("battlenet")
    def test_passed_in_http_client_is_left_open(self) -> None:
        http = httpx.Client()
        with Client("id", "secret", http_client=http) as client:
            client.playable_classes.get(1)

        async def use_async_client() -> httpx.AsyncClient:
            async_http = httpx.AsyncClient()
            async with AsyncClient("id", "secret", http_client=async_http) as async_client:
                await async_client.playable_classes.get(1)
            return async_http

        async_http = anyio.run(use_async_client)

        assert not http.is_closed
        assert not async_http.is_closed
        http.close()
        anyio.run(async_http.aclose)


class TestAppToken:
    def test_token_is_fetched_once_and_reused(self, client: Client, battlenet: respx.MockRouter) -> None:
        client.playable_classes.get(1)
        client.playable_classes.index()

        assert battlenet["token"].call_count == 1
        assert battlenet["token"].calls.last.request.content == b"grant_type=client_credentials"
        assert api_authorization(battlenet) == f"Bearer {APP_TOKEN}"

    def test_token_close_to_expiry_is_refreshed(self, client: Client, battlenet: respx.MockRouter) -> None:
        battlenet["token"].respond(json={"access_token": "short", "token_type": "bearer", "expires_in": 60})

        client.playable_classes.get(1)
        client.playable_classes.get(1)

        assert battlenet["token"].call_count == 2

    def test_token_still_valid_is_kept_when_its_early_refresh_fails(
        self, client: Client, battlenet: respx.MockRouter
    ) -> None:
        battlenet["token"].side_effect = [
            httpx.Response(200, json={"access_token": "two-minutes-left", "expires_in": 120}),
            httpx.Response(503),
        ]
        client.playable_classes.get(1)

        assert client.playable_classes.get(1).id == 1

        assert battlenet["token"].call_count == 2
        assert api_authorization(battlenet) == "Bearer two-minutes-left"

    def test_expired_token_is_not_sent_when_its_refresh_fails(
        self, client: Client, battlenet: respx.MockRouter
    ) -> None:
        battlenet["token"].side_effect = [
            httpx.Response(200, json={"access_token": "expired", "expires_in": 0}),
            httpx.Response(503),
        ]
        client.playable_classes.get(1)

        with pytest.raises(InternalServerError):
            client.playable_classes.get(1)

        assert battlenet["api"].call_count == 1

    def test_rejected_token_is_replaced_once(self, client: Client, battlenet: respx.MockRouter) -> None:
        battlenet["token"].side_effect = [
            httpx.Response(200, json={"access_token": "revoked", "expires_in": 86399}),
            httpx.Response(200, json={"access_token": "fresh", "expires_in": 86399}),
        ]

        def accept_fresh_token(request: httpx.Request) -> httpx.Response:
            status = 200 if request.headers["authorization"] == "Bearer fresh" else 401
            return httpx.Response(status, json=EMPTY_DOCUMENT)

        route = class_route(battlenet).mock(side_effect=accept_fresh_token)

        client.get(CLASS_PATH, namespace="static")

        assert [call.request.headers["authorization"] for call in route.calls] == ["Bearer revoked", "Bearer fresh"]

    def test_second_rejection_raises(self, client: Client, battlenet: respx.MockRouter) -> None:
        class_route(battlenet).respond(401, json={"code": 401, "detail": "Unauthorized"})

        with pytest.raises(AuthenticationError, match="401 Unauthorized"):
            client.playable_classes.get(1)

        assert battlenet["token"].call_count == 2

    def test_bad_client_credentials_raise_authentication_error(
        self, client: Client, battlenet: respx.MockRouter
    ) -> None:
        battlenet["token"].respond(401, json={"error": "invalid_client", "error_description": "Bad client credentials"})

        with pytest.raises(AuthenticationError, match="Bad client credentials"):
            client.playable_classes.get(1)

    @pytest.mark.parametrize(
        "body", [b'{"token_type": "bearer"}', b"<html>maintenance</html>"], ids=["no-token", "not-json"]
    )
    def test_token_response_that_is_not_a_token(self, client: Client, battlenet: respx.MockRouter, body: bytes) -> None:
        battlenet["token"].respond(200, content=body)

        with pytest.raises(APIResponseValidationError, match="does not match _TokenPayload"):
            client.playable_classes.get(1)

    def test_rejected_token_body_is_not_quoted_in_errors(self, client: Client, battlenet: respx.MockRouter) -> None:
        battlenet["token"].respond(200, json={"access_token": "secret-token"})

        with pytest.raises(APIResponseValidationError) as caught:
            client.playable_classes.get(1)

        assert "secret-token" not in "".join(traceback.format_exception(caught.value))

    @pytest.mark.parametrize("flavor", ["threads", "tasks"])
    def test_concurrent_requests_share_one_token_fetch(self, battlenet: respx.MockRouter, flavor: str) -> None:
        def slow_token(_: httpx.Request) -> httpx.Response:
            time.sleep(0.05)  # keep the first fetch in flight while the others arrive
            return httpx.Response(200, json={"access_token": APP_TOKEN, "expires_in": 86399})

        battlenet["token"].side_effect = slow_token

        if flavor == "threads":
            with Client("id", "secret") as client:
                threads = [threading.Thread(target=client.playable_classes.get, args=(1,)) for _ in range(5)]
                for thread in threads:
                    thread.start()
                for thread in threads:
                    thread.join()
        else:

            async def fan_out() -> None:
                async with AsyncClient("id", "secret") as client, anyio.create_task_group() as group:
                    for _ in range(5):
                        group.start_soon(client.playable_classes.get, 1)

            anyio.run(fan_out)

        assert battlenet["token"].call_count == 1
        assert battlenet["api"].call_count == 5


class TestConcurrentRefresh:
    """Five requests all get a 401 for the same revoked token at once; only one replacement may be fetched."""

    WORKERS = 5

    @pytest.fixture
    def route(self, battlenet: respx.MockRouter) -> respx.Route:
        issued = iter(["revoked", "fresh"])

        def issue_token(_: httpx.Request) -> httpx.Response:
            return httpx.Response(200, json={"access_token": next(issued), "expires_in": 86399})

        battlenet["token"].side_effect = issue_token
        return class_route(battlenet)

    @staticmethod
    def answer(request: httpx.Request) -> httpx.Response:
        status = 200 if request.headers["authorization"] == "Bearer fresh" else 401
        return httpx.Response(status, json=EMPTY_DOCUMENT)

    def assert_one_refresh(self, battlenet: respx.MockRouter, route: respx.Route) -> None:
        assert battlenet["token"].call_count == 2
        fresh = [call for call in route.calls if call.request.headers["authorization"] == "Bearer fresh"]
        assert len(fresh) == self.WORKERS

    def test_threads(self, battlenet: respx.MockRouter, route: respx.Route) -> None:
        all_rejected = threading.Barrier(self.WORKERS)

        def reject_together(request: httpx.Request) -> httpx.Response:
            if request.headers["authorization"] == "Bearer revoked":
                all_rejected.wait(timeout=5)
            return self.answer(request)

        route.side_effect = reject_together
        with Client("id", "secret") as client:
            threads = [
                threading.Thread(target=client.get, args=(CLASS_PATH,), kwargs={"namespace": "static"})
                for _ in range(self.WORKERS)
            ]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join()

        self.assert_one_refresh(battlenet, route)

    def test_tasks(self, battlenet: respx.MockRouter, route: respx.Route) -> None:
        async def fan_out() -> None:
            arrived = 0
            everyone_arrived = anyio.Event()

            async def reject_together(request: httpx.Request) -> httpx.Response:
                nonlocal arrived
                if request.headers["authorization"] == "Bearer revoked":
                    arrived += 1
                    if arrived == self.WORKERS:
                        everyone_arrived.set()
                    await everyone_arrived.wait()
                return self.answer(request)

            route.side_effect = reject_together
            async with AsyncClient("id", "secret") as client, anyio.create_task_group() as group:
                for _ in range(self.WORKERS):
                    group.start_soon(partial(client.get, CLASS_PATH, namespace="static"))

        anyio.run(fan_out)

        self.assert_one_refresh(battlenet, route)


class TestUserToken:
    def test_access_token_is_sent_without_fetching_an_app_token(
        self, make_client: ClientFactory, battlenet: respx.MockRouter
    ) -> None:
        make_client(access_token="user-token").playable_classes.get(1)

        assert not battlenet["token"].called
        assert api_authorization(battlenet) == "Bearer user-token"

    def test_rejected_user_token_raises_without_retrying(
        self, make_client: ClientFactory, battlenet: respx.MockRouter
    ) -> None:
        route = class_route(battlenet).respond(401, json={"detail": "Unauthorized"})

        with pytest.raises(AuthenticationError):
            make_client(access_token="expired").playable_classes.get(1)

        assert route.call_count == 1
        assert not battlenet["token"].called

    def test_user_token_copy_authenticates_as_the_user(self, client: Client, battlenet: respx.MockRouter) -> None:
        client.with_options(access_token="user-token").playable_classes.get(1)

        assert api_authorization(battlenet) == "Bearer user-token"

    @pytest.mark.parametrize(
        "token",
        ["user-token\n", "user-token ", "user-token\r\nX-Injected: 1", "user-token\x00", "user-tökën", ""],
        ids=["newline", "trailing-space", "header-injection", "nul", "non-ascii", "empty"],
    )
    def test_token_that_cannot_be_sent_is_rejected_without_quoting_it(
        self, make_client: ClientFactory, client: Client, battlenet: respx.MockRouter, token: str
    ) -> None:
        with pytest.raises(ValueError, match="access_token") as on_create:
            make_client(access_token=token)
        with pytest.raises(ValueError, match="access_token") as on_copy:
            client.with_options(access_token=token)

        assert "user-t" not in f"{on_create.value}{on_copy.value}"
        assert not battlenet["api"].called


class TestRetries:
    def test_server_errors_are_retried_with_backoff(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, sleeps: list[float]
    ) -> None:
        class_route(battlenet).side_effect = [
            httpx.Response(503),
            httpx.Response(502),
            httpx.Response(200, json=EMPTY_DOCUMENT),
        ]

        response = make_client("id", "secret", max_retries=2).get(CLASS_PATH, namespace="static")

        assert response.status_code == 200
        assert len(sleeps) == 2
        assert 0.375 <= sleeps[0] <= 0.5
        assert 0.75 <= sleeps[1] <= 1.0

    @pytest.mark.parametrize("status", [501, 507, 599])
    def test_every_5xx_status_is_retried(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, sleeps: list[float], status: int
    ) -> None:
        route = class_route(battlenet)
        route.side_effect = [httpx.Response(status), httpx.Response(200, json=EMPTY_DOCUMENT)]

        assert make_client("id", "secret").get(CLASS_PATH, namespace="static").status_code == 200
        assert route.call_count == 2
        assert len(sleeps) == 1

    def test_retry_after_seconds_are_honored(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, sleeps: list[float]
    ) -> None:
        class_route(battlenet).side_effect = [
            httpx.Response(429, headers={"retry-after": "3"}),
            httpx.Response(200, json=EMPTY_DOCUMENT),
        ]

        make_client("id", "secret").get(CLASS_PATH, namespace="static")

        assert sleeps == [3.0]

    @pytest.mark.parametrize(("offset", "low", "high"), [(31, 29.0, 31.0), (-30, 0.0, 0.0)], ids=["future", "past"])
    def test_retry_after_dates_are_honored(
        self,
        make_client: ClientFactory,
        battlenet: respx.MockRouter,
        sleeps: list[float],
        offset: int,
        low: float,
        high: float,
    ) -> None:
        when = datetime.now(UTC).replace(microsecond=0) + timedelta(seconds=offset)
        class_route(battlenet).side_effect = [
            httpx.Response(503, headers={"retry-after": format_datetime(when, usegmt=True)}),
            httpx.Response(200, json=EMPTY_DOCUMENT),
        ]

        make_client("id", "secret").get(CLASS_PATH, namespace="static")

        assert len(sleeps) == 1
        assert low <= sleeps[0] <= high

    @pytest.mark.parametrize("retry_after", ["soon", "nan", "1.5", "²"])
    def test_unreadable_retry_after_falls_back_to_backoff(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, sleeps: list[float], retry_after: str
    ) -> None:
        class_route(battlenet).side_effect = [
            httpx.Response(503, headers=[(b"retry-after", retry_after.encode("latin-1"))]),
            httpx.Response(200, json=EMPTY_DOCUMENT),
        ]

        make_client("id", "secret").get(CLASS_PATH, namespace="static")

        assert 0.375 <= sleeps[0] <= 0.5

    def test_zero_retry_after_retries_immediately(
        self, make_client: ClientFactory, battlenet: respx.MockRouter
    ) -> None:
        route = class_route(battlenet)
        route.side_effect = [
            httpx.Response(503, headers={"retry-after": "0"}),
            httpx.Response(200, json=EMPTY_DOCUMENT),
        ]

        assert make_client("id", "secret").get(CLASS_PATH, namespace="static").status_code == 200
        assert route.call_count == 2

    def test_retry_after_beyond_the_cap_is_not_waited_out(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, sleeps: list[float]
    ) -> None:
        class_route(battlenet).respond(429, headers={"retry-after": "3600"})

        with pytest.raises(RateLimitError):
            make_client("id", "secret").get(CLASS_PATH, namespace="static")

        assert sleeps == []

    def test_retries_give_up_after_max_retries(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, sleeps: list[float]
    ) -> None:
        route = class_route(battlenet).respond(500)

        with pytest.raises(InternalServerError):
            make_client("id", "secret", max_retries=1).get(CLASS_PATH, namespace="static")

        assert route.call_count == 2
        assert len(sleeps) == 1

    def test_client_errors_are_not_retried(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, sleeps: list[float]
    ) -> None:
        route = class_route(battlenet).respond(400, json={"detail": "bad filter"})

        with pytest.raises(BadRequestError, match="bad filter"):
            make_client("id", "secret").get(CLASS_PATH, namespace="static")

        assert route.call_count == 1
        assert sleeps == []

    def test_copy_can_change_the_retry_budget(
        self, client: Client, battlenet: respx.MockRouter, sleeps: list[float]
    ) -> None:
        route = class_route(battlenet).respond(503)

        with pytest.raises(InternalServerError):
            client.with_options(max_retries=3).get(CLASS_PATH, namespace="static")

        assert route.call_count == 4
        assert len(sleeps) == 3

    @pytest.mark.parametrize(
        ("failure", "error", "message"),
        [
            (httpx.ConnectError("refused"), APIConnectionError, "connection failed: GET .* refused"),
            (httpx.ReadTimeout("slow"), APITimeoutError, "timed out: GET"),
            (httpx.DecodingError("incorrect header check"), APIConnectionError, "connection failed: GET .* header"),
        ],
    )
    def test_failures_without_a_response_are_retried_then_raised(
        self,
        make_client: ClientFactory,
        battlenet: respx.MockRouter,
        sleeps: list[float],
        failure: httpx.RequestError,
        error: type[APIConnectionError],
        message: str,
    ) -> None:
        route = class_route(battlenet).mock(side_effect=failure)

        with pytest.raises(error, match=message) as caught:
            make_client("id", "secret", max_retries=2).get(CLASS_PATH, namespace="static")

        assert caught.value.request.url.path == CLASS_PATH
        assert route.call_count == 3
        assert len(sleeps) == 2

    @pytest.mark.parametrize(
        "failure",
        [
            httpx.UnsupportedProtocol("Request URL is missing an 'http://' or 'https://' protocol."),
            httpx.TooManyRedirects("Exceeded maximum allowed redirects."),
        ],
        ids=["no-scheme", "redirect-loop"],
    )
    def test_failures_that_would_repeat_are_raised_without_retrying(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, sleeps: list[float], failure: httpx.RequestError
    ) -> None:
        route = class_route(battlenet).mock(side_effect=failure)

        with pytest.raises(APIConnectionError, match="connection failed: GET") as caught:
            make_client("id", "secret", max_retries=2).get(CLASS_PATH, namespace="static")

        assert caught.value.request.url.path == CLASS_PATH
        assert route.call_count == 1
        assert sleeps == []


class TestErrors:
    def test_missing_document_in_a_live_namespace(self, client: Client) -> None:
        with pytest.raises(NotFoundError) as caught:
            client.get("/data/wow/token/index", namespace="dynamic")

        assert caught.value.status_code == 404
        assert caught.value.namespace == "dynamic-forever-us"
        assert caught.value.body == {"code": 404, "type": "BLZWEBAPI00000404", "detail": "Not Found"}

    def test_unknown_namespace_is_permission_denied_without_namespace(self, client: Client) -> None:
        with pytest.raises(PermissionDeniedError) as caught:
            client.get(CLASS_PATH, params={"namespace": "static-bogus-us"})

        assert caught.value.namespace is None

    def test_non_json_error_body_is_kept_as_text(self, client: Client, battlenet: respx.MockRouter) -> None:
        class_route(battlenet).respond(418, text="teapot")

        with pytest.raises(APIStatusError) as caught:
            client.get(CLASS_PATH, namespace="static")

        assert type(caught.value) is APIStatusError
        assert caught.value.body == "teapot"
        assert str(caught.value) == f"418 I'm a teapot for {caught.value.request.url}"

    def test_body_that_does_not_match_the_model(self, client: Client, battlenet: respx.MockRouter) -> None:
        class_route(battlenet).respond(json={**EMPTY_DOCUMENT, "id": "not-a-number"})

        with pytest.raises(APIResponseValidationError, match="does not match PlayableClass") as caught:
            client.playable_classes.get(1)

        assert caught.value.response.status_code == 200
        assert caught.value.__cause__ is not None


class TestRawAccess:
    def test_requests_carry_namespace_and_locale(self, client: Client, battlenet: respx.MockRouter) -> None:
        client.playable_classes.get(1)

        params = battlenet["api"].calls.last.request.url.params
        assert (params["namespace"], params["locale"]) == ("static-forever-us", "en_US")

    def test_explicit_params_override_defaults(self, client: Client, battlenet: respx.MockRouter) -> None:
        client.get(CLASS_PATH, namespace="static", params={"locale": "de_DE"})

        assert battlenet["api"].calls.last.request.url.params["locale"] == "de_DE"

    def test_following_an_href_keeps_its_namespace(self, client: Client, battlenet: respx.MockRouter) -> None:
        warrior = client.playable_classes.get(1)

        media = client.get(warrior.media.key.href).parse(Media)

        params = battlenet["api"].calls.last.request.url.params
        assert (params["namespace"], params["locale"]) == ("static-1.60.1_70399-forever-us", "en_US")
        assert media.assets[0].key == "icon"

    @pytest.mark.parametrize(
        "href",
        [
            "https://attacker.example/data/wow/playable-class/1",
            "http://us.api.blizzard.com/data/wow/playable-class/1",
            "https://eu.api.blizzard.com/data/wow/playable-class/1",
        ],
        ids=["foreign-host", "plain-http", "other-region"],
    )
    def test_links_off_the_api_host_are_refused(self, client: Client, battlenet: respx.MockRouter, href: str) -> None:
        with pytest.raises(ValueError, match="refusing to send credentials"):
            client.get(href)

        assert not battlenet["token"].called

    def test_relative_paths_need_no_leading_slash(self, client: Client, battlenet: respx.MockRouter) -> None:
        client.get(CLASS_PATH.lstrip("/"), namespace="static")

        assert battlenet["api"].calls.last.request.url.path == CLASS_PATH

    def test_raw_response_exposes_the_document_and_battlenet_headers(self, client: Client) -> None:
        response = client.get(CLASS_PATH, namespace="static")

        assert httpx.URL(response.url).copy_with(query=None) == f"https://us.api.blizzard.com{CLASS_PATH}"
        assert response.namespace == "static-1.60.1_70399-forever-us"
        assert response.last_modified == datetime(2026, 11, 10, 15, 22, 34, tzinfo=UTC)
        assert response.headers["cache-control"] == "public, max-age=86400"
        assert response.json()["name"] == "Warrior"
        assert response.parse(PlayableClass).id == 1

    def test_last_modified_is_none_without_the_header(self, client: Client, battlenet: respx.MockRouter) -> None:
        class_route(battlenet).respond(json=EMPTY_DOCUMENT)

        assert client.get(CLASS_PATH, namespace="static").last_modified is None


class TestWithOptions:
    def test_region_change_moves_the_default_locale(self, client: Client) -> None:
        korean = client.with_options(region=Region.KR)

        assert (korean.region, korean.locale) == (Region.KR, "ko_KR")
        assert (client.region, client.locale) == (Region.US, "en_US")

    def test_explicit_locale_survives_region_change(self, make_client: ClientFactory) -> None:
        client = make_client("id", "secret", locale="fr_FR")

        assert client.with_options(region="eu").locale == "fr_FR"
        assert client.with_options(locale="de_DE").with_options(region="kr").locale == "de_DE"

    def test_static_version_survives_an_unrelated_option_change(
        self, make_client: ClientFactory, battlenet: respx.MockRouter
    ) -> None:
        client = make_client("id", "secret", static_version="1.60.1_70399")

        client.with_options(locale="de_DE").get(CLASS_PATH, namespace="static")

        params = battlenet["api"].calls.last.request.url.params
        assert params["namespace"] == "static-1.60.1_70399-forever-us"

    def test_with_options_can_pin_a_different_static_version(self, client: Client, battlenet: respx.MockRouter) -> None:
        pinned = client.with_options(static_version="1.60.1_70399")

        pinned.get(CLASS_PATH, namespace="static")

        assert battlenet["api"].calls.last.request.url.params["namespace"] == "static-1.60.1_70399-forever-us"
        assert client.static_version is None

    def test_copies_share_the_app_token(self, client: Client, battlenet: respx.MockRouter) -> None:
        german = client.with_options(locale="de_DE")

        german.playable_classes.get(1)
        client.playable_classes.get(1)

        assert battlenet["token"].call_count == 1
        assert [call.request.url.params["locale"] for call in battlenet["api"].calls] == ["de_DE", "en_US"]

    def test_closing_a_copy_leaves_the_pool_open(self, client: Client) -> None:
        client.with_options(locale="de_DE").close()

        assert client.playable_classes.get(1).id == 1

    def test_repr_shows_settings(self, client: Client) -> None:
        assert repr(client.with_options(region="eu")).endswith("Client region=eu locale=en_GB>")


class TestUserLogin:
    @pytest.mark.parametrize(
        ("scopes", "expected"), [("wow.profile", "wow.profile"), (["openid", "wow.profile"], "openid wow.profile")]
    )
    def test_authorization_url(self, client: Client, scopes: str | list[str], expected: str) -> None:
        url = httpx.URL(client.authorization_url("https://app.example/callback", state="xyz", scopes=scopes))

        assert url.copy_with(query=None) == "https://oauth.battle.net/authorize"
        assert dict(url.params) == {
            "response_type": "code",
            "client_id": "id",
            "redirect_uri": "https://app.example/callback",
            "scope": expected,
            "state": "xyz",
        }

    def test_exchange_code_returns_the_user_token(self, client: Client, battlenet: respx.MockRouter) -> None:
        battlenet["token"].respond(
            json={
                "access_token": "user-token",
                "token_type": "bearer",
                "expires_in": 86399,
                "scope": "openid wow.profile",
                "sub": "12345",
                "id_token": "jwt",
            }
        )

        token = client.exchange_code("the-code", "https://app.example/callback")

        assert token.access_token == "user-token"
        assert token.scopes == {"openid", "wow.profile"}
        assert (token.sub, token.id_token) == ("12345", "jwt")
        assert not token.expires_within(timedelta(hours=23))
        assert "user-token" not in repr(token)
        form = dict(httpx.QueryParams(battlenet["token"].calls.last.request.content.decode()))
        assert form == {
            "grant_type": "authorization_code",
            "code": "the-code",
            "redirect_uri": "https://app.example/callback",
        }

    def test_rejected_code_raises_bad_request(self, client: Client, battlenet: respx.MockRouter) -> None:
        battlenet["token"].respond(400, json={"error": "invalid_grant", "error_description": "Invalid code"})

        with pytest.raises(BadRequestError, match="Invalid code"):
            client.exchange_code("stale", "https://app.example/callback")

    def test_code_exchange_is_never_retried(
        self, make_client: ClientFactory, battlenet: respx.MockRouter, sleeps: list[float]
    ) -> None:
        battlenet["token"].respond(503)

        with pytest.raises(InternalServerError):
            make_client("id", "secret", max_retries=3).exchange_code("once", "https://app.example/callback")

        assert battlenet["token"].call_count == 1
        assert sleeps == []

    def test_login_needs_app_credentials(self, make_client: ClientFactory) -> None:
        with pytest.raises(WowError, match="needs app credentials"):
            make_client(access_token="user-token").authorization_url("https://app.example/callback", state="xyz")
