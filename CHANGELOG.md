# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [semantic versioning](https://semver.org/).

## [Unreleased]

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
