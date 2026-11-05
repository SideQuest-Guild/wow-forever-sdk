"""Check every model against every live Battle.net document it can reach.

Run from the repository root with app credentials in the environment:

    BATTLENET_CLIENT_ID=... BATTLENET_CLIENT_SECRET=... uv run python -m scripts.audit_models [region]

Starting from each index and search in ``tests/test_models.py``'s ``ROUTES``, and from each character and guild the
fixtures hold, it follows every link to a route that table knows, decodes each document with its model, and reports
documents that fail to decode and fields a model drops. Characters link to their guild and guilds to their members, so
``LIMITS`` caps how many of each it reads. It exits non-zero if it finds a problem. Record a document with each new
shape as a fixture (``VARIANTS`` or ``CHARACTERS`` in ``scripts/record_fixtures.py``), then fix the model.
"""

import re
import sys
from collections import Counter, defaultdict
from typing import cast

import anyio
import anyio.abc
import httpx
import msgspec

from tests.test_models import RECORDED, ROUTES, api_path, dropped, route
from wow import APIStatusError, AsyncClient, NamespaceKind
from wow.search import MAX_PAGE_SIZE

# Requests in flight at once. Battle.net allows 100 requests a second per client.
CONCURRENCY = 8

# The most documents read of each route that links outward without end: every character links to its guild, and
# every guild to its members.
LIMITS = {"profile/wow/character/{id}": 60, "profile/guild/{id}": 10}


def document_name(href: str) -> str | None:
    """Turn a link into a fixture-style name such as ``static/item/19019``, or ``None`` if it is not a document."""
    url = httpx.URL(href)
    namespace = url.params.get("namespace", "")
    if not namespace:
        return None
    for prefix in ("/data/wow/", "/profile/"):
        if url.path.startswith(prefix):
            return f"{namespace.partition('-')[0]}/{url.path.removeprefix(prefix)}"
    return None


def links(body: object) -> list[str]:
    """Every ``href`` in a document except its own ``_links``."""
    if isinstance(body, dict):
        nested = [href for key, value in body.items() if key != "_links" for href in links(value)]
        return [*nested, body["href"]] if isinstance(body.get("href"), str) else nested
    if isinstance(body, list):
        return [href for value in body for href in links(value)]
    return []


class Audit:
    """One crawl of the live API, and what it found."""

    def __init__(self, client: AsyncClient, tasks: anyio.abc.TaskGroup) -> None:
        self.client = client
        self.tasks = tasks
        self.limiter = anyio.CapacityLimiter(CONCURRENCY)
        self.seen: set[str] = set()
        self.started: Counter[str] = Counter()
        self.decoded: Counter[str] = Counter()
        self.failures: defaultdict[str, Counter[str]] = defaultdict(Counter)
        self.drops: defaultdict[str, Counter[str]] = defaultdict(Counter)
        self.missing: Counter[tuple[str, int]] = Counter()

    def start(self) -> None:
        """Visit every index and every recorded character and guild, and read every search."""
        for name in ROUTES:
            if name.endswith("/index"):
                self.follow(name)
            elif "/search/" in name:
                self.tasks.start_soon(self.search, name)
        for name in RECORDED:
            if route(name) in LIMITS:
                self.follow(name)

    def follow(self, name: str) -> None:
        """Visit a document unless it was seen, or its route has reached its limit."""
        key = route(name)
        if name in self.seen or key not in ROUTES or self.started[key] >= LIMITS.get(key, sys.maxsize):
            return
        self.seen.add(name)
        self.started[key] += 1
        self.tasks.start_soon(self.visit, name)

    def check(self, name: str, body: bytes) -> object:
        """Decode one document with its model, record any problem, and return the raw JSON."""
        key = route(name)
        self.decoded[key] += 1
        raw = msgspec.json.decode(body)
        try:
            model = msgspec.json.decode(body, type=ROUTES[key])
        except msgspec.ValidationError as error:
            self.failures[key][re.sub(r"\[\d+\]", "[]", str(error))] += 1
            return raw
        for path in dropped(raw, msgspec.to_builtins(model)):
            self.drops[key][re.sub(r"\[\d+\]", "[]", path)] += 1
        return raw

    async def visit(self, name: str) -> None:
        """Fetch and check one document, then visit every new document it links to."""
        namespace, path = api_path(name)
        async with self.limiter:
            try:
                response = await self.client.get(path, namespace=cast("NamespaceKind", namespace))
            except APIStatusError as error:
                self.missing[route(name), error.status_code] += 1
                return
        for href in links(self.check(name, response.http_response.content)):
            if linked := document_name(href):
                self.follow(linked)

    async def search(self, name: str) -> None:
        """Read and check every page of one search."""
        namespace, path = api_path(name)
        page, pages = 1, 1
        while page <= pages:
            async with self.limiter:
                params = {"_page": page, "_pageSize": MAX_PAGE_SIZE}
                response = await self.client.get(path, namespace=cast("NamespaceKind", namespace), params=params)
            raw = self.check(name, response.http_response.content)
            pages = raw.get("pageCount", 0) if isinstance(raw, dict) else 0
            page += 1

    def report(self, region: str) -> int:
        """Print what the crawl found; return the number of routes with problems or documents left unchecked."""
        print(f"{region}: {self.decoded.total()} documents")
        for key in sorted(self.decoded):
            problem = bool(self.failures[key] or self.drops[key])
            print(f"  {'FAIL' if problem else 'ok  '} {key}: {self.decoded[key]} decoded")
            for message, count in self.failures[key].most_common():
                print(f"         {count} fail to decode: {message}")
            for path, count in sorted(self.drops[key].items()):
                print(f"         {count} drop {path}")
        # A 404 is a route Blizzard has not published. Anything else, such as a 429 after every retry, means those
        # documents went unchecked, so the audit is incomplete.
        unchecked = 0
        for (key, status), count in sorted(self.missing.items()):
            print(f"  {'not live' if status == httpx.codes.NOT_FOUND else 'NOT CHECKED'}: {key} {status} ({count})")
            unchecked += status != httpx.codes.NOT_FOUND
        return unchecked + sum(1 for key in self.decoded if self.failures[key] or self.drops[key])


async def main(region: str) -> int:
    """Crawl one region and report; return the number of routes with problems."""
    async with AsyncClient(region=region) as client, anyio.create_task_group() as tasks:
        audit = Audit(client, tasks)
        audit.start()
    return audit.report(region)


if __name__ == "__main__":
    raise SystemExit(1 if anyio.run(main, sys.argv[1] if len(sys.argv) > 1 else "us") else 0)
