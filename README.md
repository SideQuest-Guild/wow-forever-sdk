# wow

A typed Python client for the **World of Warcraft: Forever** Battle.net API, sync and async.

- `Client` and `AsyncClient` have the same methods. The async client runs under asyncio and trio.
- Each response becomes a typed, immutable [msgspec](https://msgspec.dev) model. A new field from Blizzard never stops
  a response from decoding.
- The client gets, caches and refreshes app tokens for you. Profile routes use a player's token from the OAuth login.
- The client retries connection errors, timeouts, 408, 429 and 5xx responses, and obeys `Retry-After`.
- Search takes filters, ranges and sort orders, and `search_all` reads every page for you.

Blizzard does not document a Forever API. Players found the namespaces `static-forever-{region}`,
`dynamic-forever-{region}` and `profile-forever-{region}` by trial. This package covers the routes that answer today.

## Install

```console
uv add wow
```

The package needs Python 3.14 or later.

## Quick start

Create an API client at https://develop.battle.net/access/clients. Then:

```python
from wow import Client

with Client(client_id="...", client_secret="...") as client:  # or BATTLENET_CLIENT_ID/SECRET env vars
    warrior = client.playable_classes.get(1)
    print(warrior.name, [spec.name for spec in warrior.specializations])

    for hit in client.items.search_all(name="Thunderfury"):
        print(hit.data.id, hit.data.name["en_US"])
```

The async client has the same calls with `await`:

```python
from wow import AsyncClient

async with AsyncClient(region="eu") as client:
    races = await client.playable_races.index()
```

## What it covers

| Namespace | Resources |
| --- | --- |
| static | `achievements`, `achievement_categories`, `creature_families`, `creature_types`, `items`, `item_classes`, `item_sets`, `mounts`, `pets`, `playable_classes`, `playable_races`, `playable_specializations`, `power_types`, `professions`, `quests`, `quest_areas`, `quest_categories`, `quest_types`, `recipes`, `reputation_factions`, `reputation_tiers`, `talents`, `talent_trees`, `titles`, `toys` |
| dynamic | `regions`, `realms`, `rulesets` |
| profile | `characters` and `guilds`, which an app token can read; `account`, which needs a player's token |

For any other route, call `client.get(path, namespace=...)`. It returns the raw response.

## Documentation

The guide is at https://docs.sidequest-guild.com/developers/wow-forever-sdk/ and the full API reference at
https://docs.sidequest-guild.com/reference/wow-forever-sdk/.

## Development

```console
make install   # uv sync --locked
make ci        # lint, format, types, generated code, tests at 100% coverage, docs, build
make help      # every target
```

`make generate` writes `src/wow/_sync` from `src/wow/_async`. Edit the async code only.

## License

MIT
