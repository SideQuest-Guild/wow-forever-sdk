# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [semantic versioning](https://semver.org/).

## [Unreleased]

## [0.4.0] - 2026-11-07

### Added

- `client.auctions` reads the Auction House API: `houses(ruleset_id)` lists a ruleset's auction houses (every
  ruleset lists the same fifteen), `get(ruleset_id, house_id)` reads one house's posted auctions, and
  `commodities(ruleset_id, house_id)` reads its stackable commodities. An empty house, such as house 112, has no
  `auctions`.
- `AuctionHouseIndex`, `AuctionHouse`, `AuctionEntry`, `AuctionItem`, `AuctionItemModifier`, `CommodityHouse` and
  `CommodityEntry` model the new routes.

### Changed

- `Ruleset.auctions` now links to a live document; its docstring no longer says Battle.net does not serve it.

## [0.3.0] - 2026-11-06

### Added

- `CharacterStatistics` reads the stats Battle.net added on 2026-11-05: `melee_hit`, `ranged_hit`, `spell_hit`,
  `off_hand_hit`, `expertise`, `off_hand_expertise`, `armor_penetration`, `defense`, `ranged_attack_power`,
  `ranged_damage_min`, `ranged_damage_max`, `spell_healing` and `movement_speed`, and `value` on `speed` and
  `avoidance`. Each is `None` on a sheet written before that update.
- `EquippedItem.transmog` (`ItemTransmog`): the appearance an item is transmogrified to, and the other shoulder's
  when the two differ.
- `CharacterEquipment.equipped_item_sets`, with `is_equipped` on each set piece and `is_active` on each bonus.
- `CharacterPvpSummary.pvp_map_statistics` (`PvpMapStatistics`): played, won and lost per battleground map.
- `is_favorite` on `CollectedMount`, `CollectedPet` and `CollectedToy`.

### Changed

- `ItemEnchantment.source_item` can be `None`: a spell's imbue, such as a shaman's Rockbiter, has no source item.
  Before, equipment with one failed to decode.
- `CharacterStatistics` is keyword-only.
- Test fixtures re-recorded from the live API on 2026-11-06, with five more characters for the new shapes.

## [0.2.0] - 2026-11-05

### Added

- `playable_specializations.media(spec_id)` and `achievements.media(achievement_id)`: the specialization and
  achievement icons.

## [0.1.0] - 2026-11-05

### Added

- `Client` and `AsyncClient` for the World of Warcraft: Forever Battle.net API, sharing one surface across sync,
  asyncio and trio.
- App-token caching and refresh, the OAuth authorization code flow (`authorization_url`, `exchange_code`) and
  user tokens via `with_options(access_token=...)`.
- Retries with exponential backoff and `Retry-After` support for connection errors, timeouts, 408, 429 and 5xx.
- Typed msgspec models and routes for the achievement, creature, item, mount, pet, playable class, race and
  specialization, power type, profession, quest, region, realm, reputation, talent, title, toy and account profile
  APIs. Undeclared fields are skipped rather than fatal.
- Search with filters (`Range`, `Not`, any-of), sorting, paging and `search_all` auto-pagination.
- `client.get` for raw access to any document or link, with `battlenet-namespace` and `Last-Modified` headers. It
  only follows links on the client's own API host and scheme, so tokens never leave Battle.net.
- Authorization codes are exchanged exactly once; `exchange_code` never retries.
- `client.characters` reads any character's public profile with an app token, by its `name-surname` slug: summary,
  status, images, equipment, stats, talents, professions, reputations, PvP summary, achievements, statistics, quests
  and collections (mounts, pets, toys, appearances).
- `client.guilds` reads a guild and its roster by slug; `client.rulesets` reads the rulesets Forever has in place of
  realms.
- `client.recipes`, plus `client.professions.skill_tier` and `client.professions.media`, read profession recipes,
  their reagents and icons.
