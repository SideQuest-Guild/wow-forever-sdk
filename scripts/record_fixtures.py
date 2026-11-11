"""Record live Battle.net responses into ``tests/fixtures`` for the offline test suite.

Run with app credentials in the environment:

    BATTLENET_CLIENT_ID=... BATTLENET_CLIENT_SECRET=... uv run scripts/record_fixtures.py

Every index document is recorded, then the first entry it links to is recorded as the detail fixture, so ids follow
whatever Blizzard currently publishes. ``VARIANTS`` adds documents whose shape the first entry does not show: fields
that only some documents carry, or leave out. Characters and guilds have no index; ``CHARACTERS`` and ``GUILDS`` name
the ones to record. Routes that are not live yet are reported and skipped, never written. Fixtures keep only the
headers the SDK reads; tokens are never written.
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
    ("dynamic", "ruleset/index", "rulesets"),
]

# Documents with no index of their own: (namespace kind, path, query params)
SINGLE: list[tuple[str, str, dict[str, str]]] = [
    ("static", "item/19019", {}),
    ("static", "media/achievement/62041", {}),
    ("static", "media/item/19019", {}),
    ("static", "media/playable-class/1", {}),
    ("static", "media/playable-specialization/26", {}),
    ("static", "media/profession/164", {}),
    ("static", "media/recipe/1631", {}),
    ("static", "profession/164/skill-tier/2938", {}),
    ("static", "quest/1", {}),
    ("static", "recipe/1631", {}),
    ("static", "search/item", {"name.en_US": "Thunderfury", "_pageSize": "5"}),
    ("static", "search/mount", {"_pageSize": "1000", "orderby": "id"}),
    ("dynamic", "search/realm", {"_pageSize": "5"}),
]

# Documents chosen because, together, they carry every field Battle.net sends for their type, and leave out every
# field it sometimes leaves out. ``make audit-models`` checks every live document; pick new ones here when it finds
# a shape no fixture has.
VARIANTS: list[tuple[str, str]] = [
    ("static", "achievement/728"),
    ("static", "achievement/62049"),
    ("static", "achievement/64001"),
    ("static", "achievement/64015"),
    ("static", "achievement/64018"),
    ("static", "achievement-category/15425"),
    ("static", "achievement-category/15587"),
    ("static", "creature-family/310"),
    ("static", "item/3464"),
    ("static", "item/4305"),
    ("static", "item/4937"),
    ("static", "item/4964"),
    ("static", "item/18160"),
    ("static", "item/18660"),
    ("static", "item/18798"),
    ("static", "item/19682"),
    ("static", "item/20052"),
    ("static", "item/21199"),
    ("static", "item/21404"),
    ("static", "item/22133"),
    ("static", "item/22243"),
    ("static", "item/23065"),
    ("static", "item/226856"),
    ("static", "item/228311"),
    ("static", "item/236395"),
    ("static", "item/238642"),
    ("static", "item/238928"),
    ("static", "item/254682"),
    ("static", "item/264233"),
    ("static", "item/269901"),
    ("static", "item/272562"),
    ("static", "item/274800"),
    ("static", "item/275347"),
    ("static", "item-class/18"),
    ("static", "mount/9"),
    ("static", "mount/62"),
    ("static", "mount/84"),
    ("static", "pet/162"),
    ("static", "pet/5008"),
    ("static", "quest/1036"),
    ("static", "quest/1049"),
    ("static", "quest/1054"),
    ("static", "quest/1103"),
    ("static", "quest/1185"),
    ("static", "quest/1281"),
    ("static", "quest/1371"),
    ("static", "quest/1470"),
    ("static", "quest/1533"),
    ("static", "quest/2203"),
    ("static", "quest/3638"),
    ("static", "quest/8433"),
    ("static", "quest/81864"),
    ("static", "quest/89258"),
    ("static", "recipe/1353"),
    ("static", "recipe/2427"),
    ("static", "recipe/4289"),
    ("static", "recipe/4766"),
    ("static", "recipe/52639"),
    ("static", "reputation-faction/169"),
    ("static", "reputation-faction/2819"),
    ("static", "talent/133102"),
    ("static", "talent/134433"),
    ("static", "talent-tree/1114/playable-specialization/613"),
    ("static", "title/2"),
    ("static", "toy/1759"),
]

# Characters and guilds, by slug, and the documents to record for each. Together the characters show every shape a
# profile document takes today: one has collections and rendered images, one is a hunter with recent achievements,
# one has a temporary weapon imbue and a stats sheet from before Blizzard's 2026-11-05 update, one has a shaman imbue
# with no source item and favorite mounts, one has battleground statistics, one wears transmogrified gear with split
# shoulders, one wears most of an item set, one has favorite pets, one is a hunter with a collected pet, and one is a
# hunter whose hunter-pets document answers 200 with no ``hunter_pets`` key.
CHARACTERS = [
    "terrorskull-gloomstep",
    "evoke-saint",
    "daribow-thaumaturge",
    "vaelun-skyrend",
    "drakaus-warrior",
    "monnick-mortis",
    "sliding-door",
    "aille-mistgaze",
    "hiccup-nightfury",
    "septo-caine",
]
CHARACTER_DOCUMENTS = [
    "",
    "/achievements",
    "/achievements/statistics",
    "/appearance",
    "/character-media",
    "/collections",
    "/collections/mounts",
    "/collections/pets",
    "/collections/toys",
    "/collections/transmogs",
    "/equipment",
    "/hunter-pets",
    "/professions",
    "/pvp-summary",
    "/quests",
    "/quests/completed",
    "/reputations",
    "/specializations",
    "/statistics",
    "/status",
]
GUILDS = ["sidequest"]
GUILD_DOCUMENTS = ["", "/roster"]

# Ruleset 2 (Normal, SideQuest's ruleset) lists the same fifteen auction houses every ruleset does. House 125 is a
# small Blackwater house with auctions and commodities; house 112 is empty, with no auctions or commodities, so it
# shows the shape of a house whose ``auctions`` field is missing.
AUCTION_RULESET = 2
AUCTION_HOUSES = [125, 112]


def fixture_path(kind: str, path: str) -> Path:
    """Map ``static`` + ``playable-class/1`` to ``tests/fixtures/static/playable-class/1.json``.

    A path ending in ``/``, such as an auction house index, is stored as that directory's ``index``.
    """
    name = f"{path}index" if path.endswith("/") else path
    return FIXTURES / kind / f"{name}.json"


def api_path(path: str) -> str:
    """Turn a fixture path into its route: ``wow/character/...`` and ``user/wow`` live under ``/profile/``."""
    return f"/profile/{path}" if path.startswith(("wow/", "user/")) else f"/data/wow/{path}"


def record(client: httpx.Client, kind: str, path: str, params: dict[str, str] | None = None) -> dict[str, Any] | None:
    """Fetch one document and write it as a fixture; return its body, or ``None`` if it is not live."""
    query = {"namespace": f"{kind}-forever-{REGION}", "locale": LOCALE, **(params or {})}
    response = client.get(api_path(path), params=query)
    time.sleep(0.05)
    if response.status_code != httpx.codes.OK:
        print(f"skip {response.status_code} {kind} {path}")
        return None
    body = response.json()
    target = fixture_path(kind, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fixture = {
        "request": {"path": api_path(path), "params": query},
        "status": response.status_code,
        "headers": {name: response.headers[name] for name in KEPT_HEADERS if name in response.headers},
        "body": body,
    }
    target.write_text(json.dumps(fixture, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(f"ok   {kind} {path}")
    return body


def record_auction_houses(client: httpx.Client) -> None:
    """Record ruleset 2's auction house index and its small and empty houses, with their commodities."""
    record(client, "dynamic", f"ruleset/{AUCTION_RULESET}/auctions/")
    for house_id in AUCTION_HOUSES:
        record(client, "dynamic", f"ruleset/{AUCTION_RULESET}/auctions/{house_id}")
        record(client, "dynamic", f"ruleset/{AUCTION_RULESET}/auctions/{house_id}/commodities")


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
        for kind, path in VARIANTS:
            record(client, kind, path)
        for slug in CHARACTERS:
            for document in CHARACTER_DOCUMENTS:
                record(client, "profile", f"wow/character/{slug}{document}")
        for slug in GUILDS:
            for document in GUILD_DOCUMENTS:
                record(client, "profile", f"guild/{slug}{document}")
        record_auction_houses(client)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
