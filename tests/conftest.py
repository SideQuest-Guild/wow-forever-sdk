"""Shared fixtures: a mocked Battle.net serving ``tests/fixtures``, and clients for every I/O flavor.

Every test that takes ``client`` or ``make_client`` runs three times: against the sync :class:`~wow.Client`, and
against :class:`~wow.AsyncClient` under asyncio and under trio. Async clients are driven from the synchronous test
body through an anyio blocking portal, so one test proves the same behavior for all three.
"""

import inspect
import json
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import ExitStack
from pathlib import Path
from typing import Any, cast

import httpx
import pytest
import respx
from anyio.from_thread import BlockingPortal, start_blocking_portal

from wow import AsyncClient, Client
from wow._async._resource import AsyncResource

FIXTURES = Path(__file__).parent / "fixtures"
API = "https://us.api.blizzard.com"
TOKEN_URL = "https://oauth.battle.net/token"
APP_TOKEN = "app-token"

type ClientFactory = Callable[..., Client]


def load_fixture(name: str) -> dict[str, Any]:
    """Load ``tests/fixtures/{name}.json``, such as ``static/playable-class/1``."""
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def serve_fixture(request: httpx.Request) -> httpx.Response:
    """Answer an API request from the fixture recorded for its namespace kind and path, like Battle.net would."""
    namespace = request.url.params.get("namespace", "")
    kind, _, rest = namespace.partition("-")
    if kind not in {"static", "dynamic", "profile"} or not rest.endswith("forever-us"):
        return httpx.Response(403, json={"code": 403, "type": "BLZWEBAPI00000403", "detail": "Forbidden"})
    path = request.url.path.removeprefix("/data/wow/").removeprefix("/profile/")
    if path.endswith("/"):
        path = f"{path}index"
    file = FIXTURES / kind / f"{path}.json"
    if not file.exists():
        return httpx.Response(
            404,
            json={"code": 404, "type": "BLZWEBAPI00000404", "detail": "Not Found"},
            headers={"battlenet-namespace": namespace},
        )
    fixture = json.loads(file.read_text(encoding="utf-8"))
    return httpx.Response(fixture["status"], json=fixture["body"], headers=fixture["headers"])


def mock_route(router: respx.MockRouter, path: str) -> respx.Route:
    """Add a route for one API path that takes precedence over the fixture-serving fallback."""
    fallback = router.routes.pop("api")
    route = router.get(host="us.api.blizzard.com", path=path)
    router.routes.add(fallback, name="api")
    return route


class Blocking:
    """Expose an async client or resource with a sync surface, running each call in an anyio portal."""

    def __init__(self, target: object, portal: BlockingPortal) -> None:
        self._target = target
        self._portal = portal

    def __repr__(self) -> str:
        return repr(self._target)

    def __getattr__(self, name: str) -> Any:
        value = getattr(self._target, "aclose" if name == "close" else name)
        if isinstance(value, AsyncResource):
            return Blocking(value, self._portal)
        if not callable(value):
            return value

        def call(*args: Any, **kwargs: Any) -> Any:
            result = value(*args, **kwargs)
            if inspect.iscoroutine(result):
                result = self._portal.call(_awaited, result)
            if isinstance(result, AsyncIterator):
                return self._iterate(result)
            if isinstance(result, AsyncClient):
                return Blocking(result, self._portal)
            return result

        return call

    def _iterate(self, iterator: AsyncIterator[Any]) -> Iterator[Any]:
        while True:
            try:
                yield self._portal.call(anext, iterator)
            except StopAsyncIteration:
                return


async def _awaited(awaitable: Any) -> Any:
    return await awaitable


@pytest.fixture
def battlenet() -> Iterator[respx.MockRouter]:
    """Mock the token endpoint and the US API host; override single paths with :func:`mock_route`."""
    with respx.mock(assert_all_called=False) as router:
        router.post(TOKEN_URL, name="token").respond(
            json={"access_token": APP_TOKEN, "token_type": "bearer", "expires_in": 86399, "sub": "app"}
        )
        router.get(url__startswith=API, name="api").mock(side_effect=serve_fixture)
        yield router


@pytest.fixture(params=["sync", "asyncio", "trio"])
def make_client(request: pytest.FixtureRequest, battlenet: respx.MockRouter) -> Iterator[ClientFactory]:
    """Build clients of the parametrized flavor; all are closed when the test ends."""
    with ExitStack() as stack:
        if request.param == "sync":

            def make(*args: Any, **kwargs: Any) -> Client:
                return stack.enter_context(Client(*args, **kwargs))

        else:
            portal = stack.enter_context(start_blocking_portal(backend=request.param))

            def make(*args: Any, **kwargs: Any) -> Client:
                client = AsyncClient(*args, **kwargs)
                stack.callback(portal.call, client.aclose)
                return cast("Client", Blocking(client, portal))

        yield make


@pytest.fixture
def client(make_client: ClientFactory) -> Client:
    """A client wired to the mocked Battle.net, without retries getting in the way."""
    return make_client("id", "secret", max_retries=0)


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    """Record retry sleeps of every client flavor instead of waiting."""
    recorded: list[float] = []

    async def record(seconds: float) -> None:
        recorded.append(seconds)

    monkeypatch.setattr("wow._sync._client.sleep", recorded.append)
    monkeypatch.setattr("wow._async._client.async_sleep", record)
    return recorded
