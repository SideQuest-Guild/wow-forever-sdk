# wow-forever-sdk

`wow`, a typed sync and async Python client for the World of Warcraft: Forever Battle.net web API. `README.md`
explains it to users. `docs/development.md` covers setup, layout, checks, fixtures and releases; read it first.

- `make ci` runs what CI runs and must pass before you commit.
- `src/wow/_sync/` is generated from `src/wow/_async/` by `make generate`; never edit it by hand.
- `AGENTS.md` is in the global gitignore; add it with `git add -f AGENTS.md`.

## Forever game data (checked 2026-11-05)
- Forever went live 2026-11-04 at 3:00 p.m. PST on build 1.60.1.70790 (Battle.net product `wowf`). Static data still
  carries the beta build's namespace: every `_links.self.href` has `namespace=static-1.60.1_70399-forever-us`, and a
  re-record on 2026-11-06 changed only a title index order, one toy and one pet. Re-record with `make fixtures`;
  `tests/test_models.py` then names any field Blizzard added.
- Profile documents are written when the character logs out, so their shape follows Blizzard's updates one character
  at a time. Blizzard's 2026-11-05 update added hit, expertise, defense, ranged and movement stats to `statistics`;
  sheets written before it lack them, so those fields stay optional. Daribow Thaumaturge's fixture is the old shape.
- The web API calls the game `forever` (`static-forever-us`). Inside the client, Blizzard's UI source and the data
  tools still call it `camelot`: `WOW_PROJECT_CAMELOT` is 18, the interface number is 16001, and `forever` has been
  an alias only since build 70291. Search for both names.
- To check IDs and names, compare them with the game's own tables for the same build:
  `https://wago.tools/db2/<Table>/csv?build=1.60.1.70790`. Fetch with curl; Python urllib's default user agent gets
  a 403. All ten playable races in the fixtures match `ChrRaces` by ID and name.
- Those tables and Blizzard's `Enum`s are shared with Midnight. `ChrRaces` has 58 rows, Pandaren, Dracthyr and
  Earthen among them, and `Enum.PowerType` lists Chi and Essence. A row or enum value existing doesn't mean Forever
  has it; what the web API's index routes return is what Forever has.
- Enum sources for the live build: `Gethe/wow-ui-source` branch `forever` (`Blizzard_APIDocumentationGenerated/`)
  and `Ketho/BlizzardInterfaceResources` branch `forever` (`Resources/LuaEnum.lua`).
- Since launch, an app token reads any character at `/profile/wow/character/{name}-{surname}` and any guild at
  `/data/wow/guild/{slug}` (both `profile-forever-{region}`). Neither path has a realm. There is no character or guild
  search (`/data/wow/search/character` and `/search/guild` are 404), so lookups need the exact name.
- `realm/index` and `realm/{slug}` are 404 since launch (checked 2026-11-05). Characters and guilds link to
  `/data/wow/ruleset/{id}` (`dynamic`) instead: 1 PvP, 2 Normal, 3 Roleplay, 15 Roleplay PvP.
- Character `character-media` is 404 until Battle.net renders the character, and `hunter-pets`, `encounters`,
  `titles`, `mythic-keystone-profile` and guild `activity`/`achievements` hold nothing beyond their links yet, so the
  SDK has no models for them.
- Addon-development guides for Forever (secret values, the combat-log ban, TOC files, the in-game Lua API) describe
  code running inside the client. None of it applies to the web API.
