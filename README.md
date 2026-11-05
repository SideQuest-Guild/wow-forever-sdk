# wow

Typed sync and async Python client for the **World of Warcraft: Forever** Battle.net API.

- Sync `Client` and async `AsyncClient` (asyncio and trio) with the same surface.
- Typed, immutable Pydantic models built from recorded live responses; unknown fields are kept, never fatal.
- App tokens are fetched, cached and refreshed for you; user tokens via the OAuth login flow for profile routes.
- Retries with backoff for connection errors, timeouts, 408, 429 and 5xx, honoring `Retry-After`.
- Battle.net search with filters, ranges, sorting and auto-pagination.

Blizzard has not documented a Forever API. The namespaces (`static-forever-{region}`, `dynamic-forever-{region}`,
`profile-forever-{region}`) were found by community probing; this package covers the routes that answer today.

## Install

```console
uv add wow
```

Requires Python 3.14+.

## Quick start

Create an API client at https://develop.battle.net/access/clients, then:

```python
from wow import Client

with Client(client_id="...", client_secret="...") as client:  # or BATTLENET_CLIENT_ID/SECRET env vars
    warrior = client.playable_classes.get(1)
    print(warrior.name, [spec.name for spec in warrior.specializations])

    for hit in client.items.search_all(name="Thunderfury"):
        print(hit.data.id, hit.data.name["en_US"])
```

The async client is identical, with `await`:

```python
from wow import AsyncClient

async with AsyncClient(region="eu") as client:
    races = await client.playable_races.index()
```

## What is covered

| Namespace | Resources |
| --- | --- |
| static | `achievements`, `achievement_categories`, `creature_families`, `creature_types`, `items`, `item_classes`, `item_sets`, `mounts`, `pets`, `playable_classes`, `playable_races`, `playable_specializations`, `power_types`, `professions`, `quests`, `quest_areas`, `quest_categories`, `quest_types`, `reputation_factions`, `reputation_tiers`, `talents`, `talent_trees`, `titles`, `toys` |
| dynamic | `regions`, `realms` |
| profile | `account` (needs a user token) |

Anything else is one call away with `client.get(path, namespace=...)`, which returns the raw response.

## Documentation

https://jacobcoffee.github.io/wow-forever-sdk covers authentication, regions and locales, search, errors, and the full API
reference.

## Development

```console
make install   # uv sync --locked
make ci        # lint, format, types, generated code, tests at 100% coverage, docs, build
make help      # every target
```

`src/wow/_sync` is generated from `src/wow/_async` by `make generate`; edit the async code only.

## License

MIT
