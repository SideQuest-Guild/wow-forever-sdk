"""Record live Battle.net responses into ``tests/fixtures`` for the offline test suite.

Run with app credentials in the environment:

    BATTLENET_CLIENT_ID=... BATTLENET_CLIENT_SECRET=... uv run scripts/record_fixtures.py

Every index document is recorded, then the first entry it links to is recorded as the detail fixture, so ids follow
whatever Blizzard currently publishes. Routes that are not live yet are reported and skipped, never written.
Fixtures keep only the headers the SDK reads; tokens are never written.
"""

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

REGION = "us"
LOCALE = "en_US"
FIXTURES = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
KEPT_HEADERS = ("battlenet-namespace", "cache-control", "content-type", "last-modified")

# (namespace kind, index path, key in the index holding the entry list)
INDEXED: list[tuple[str, str, str]] = [
    ("static", "achievement-category/index", "categories"),
    ("static", "achievement/index", "achievements"),
    ("static", "creature-family/index", "creature_families"),
    ("static", "creature-type/index", "creature_types"),
    ("static", "item-class/index", "item_classes"),
    ("static", "item-set/index", "item_sets"),
    ("static", "mount/index", "mounts"),
    ("static", "pet/index", "pets"),
    ("static", "playable-class/index", "classes"),
    ("static", "playable-race/index", "races"),
    ("static", "playable-specialization/index", "character_specializations"),
    ("static", "power-type/index", "power_types"),
    ("static", "profession/index", "professions"),
    ("static", "quest/area/index", "areas"),
    ("static", "quest/category/index", "categories"),
    ("static", "quest/type/index", "types"),
    ("static", "reputation-faction/index", "factions"),
    ("static", "reputation-tiers/index", "reputation_tiers"),
    ("static", "talent-tree/index", "spec_talent_trees"),
    ("static", "talent/index", "talents"),
    ("static", "title/index", "titles"),
    ("static", "toy/index", "toys"),
    ("dynamic", "region/index", "regions"),
    ("dynamic", "realm/index", "realms"),
]

# Documents with no index of their own: (namespace kind, path, query params)
SINGLE: list[tuple[str, str, dict[str, str]]] = [
    ("static", "item/19019", {}),
    ("static", "media/item/19019", {}),
    ("static", "media/playable-class/1", {}),
    ("static", "quest/1", {}),
    ("static", "search/item", {"name.en_US": "Thunderfury", "_pageSize": "5"}),
    ("static", "search/mount", {"name.en_US": "Horse", "_pageSize": "5"}),
    ("dynamic", "search/realm", {"_pageSize": "5"}),
]


def fixture_path(kind: str, path: str) -> Path:
    """Map ``static`` + ``playable-class/1`` to ``tests/fixtures/static/playable-class/1.json``."""
    return FIXTURES / kind / f"{path}.json"


def record(client: httpx.Client, kind: str, path: str, params: dict[str, str] | None = None) -> dict[str, Any] | None:
    """Fetch one document and write it as a fixture; return its body, or ``None`` if it is not live."""
    query = {"namespace": f"{kind}-forever-{REGION}", "locale": LOCALE, **(params or {})}
    response = client.get(f"/data/wow/{path}", params=query)
    time.sleep(0.05)
    if response.status_code != httpx.codes.OK:
        print(f"skip {response.status_code} {kind} {path}")
        return None
    body = response.json()
    target = fixture_path(kind, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fixture = {
        "request": {"path": f"/data/wow/{path}", "params": query},
        "status": response.status_code,
        "headers": {name: response.headers[name] for name in KEPT_HEADERS if name in response.headers},
        "body": body,
    }
    target.write_text(json.dumps(fixture, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ok   {kind} {path}")
    return body


def main() -> int:
    """Record every route, then the first detail document of each index."""
    client_id = os.environ.get("BATTLENET_CLIENT_ID")
    client_secret = os.environ.get("BATTLENET_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("set BATTLENET_CLIENT_ID and BATTLENET_CLIENT_SECRET", file=sys.stderr)
        return 2
    token_response = httpx.post(
        "https://oauth.battle.net/token",
        auth=(client_id, client_secret),
        data={"grant_type": "client_credentials"},
    )
    token_response.raise_for_status()
    token = token_response.json()["access_token"]

    with httpx.Client(
        base_url=f"https://{REGION}.api.blizzard.com",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    ) as client:
        for kind, index_path, list_key in INDEXED:
            index = record(client, kind, index_path)
            if entries := (index or {}).get(list_key):
                first = entries[0]
                href = first.get("href") or first["key"]["href"]
                record(client, kind, httpx.URL(href).path.removeprefix("/data/wow/"))
        for kind, path, params in SINGLE:
            record(client, kind, path, params)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
