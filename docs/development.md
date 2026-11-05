# Development

## Set up

```console
make install   # uv sync --locked into .venv
make hooks     # prek git hooks
make help      # every target, by section
```

## Layout

| Path | Contents |
| --- | --- |
| `src/wow/_async/` | The client and the resources, written as async code. Edit this code. |
| `src/wow/_sync/` | The sync client. `make generate` writes it from `_async`. Do not edit it. |
| `src/wow/_base.py` | Code that both clients use and that does no I/O: the retry rules, token parse and request parameters. |
| `src/wow/models/` | One module for each Battle.net API. |
| `tests/fixtures/` | Recorded responses. The mock Battle.net in `tests/conftest.py` sends them. |
| `scripts/` | `unasync.py` for `make generate`, `record_fixtures.py` for `make fixtures`, `audit_models.py` for `make audit-models`. |

## Checks

`make ci` runs the same checks as CI:

- `make check`: ruff lint and format, pyproject-fmt, codespell, zizmor, the check of the generated code, and pyrefly in
  strict mode.
- `make test`: pytest with branch coverage. It fails below 100%.
- `make docs`: Sphinx. A warning stops the build.
- `make build`: the sdist and the wheel.

Each test that uses the `client` or `make_client` fixture runs 3 times. It runs against the sync client, and against
the async client under asyncio and under trio. A test must check behavior that a user can see. To close a gap in
coverage, write such a test, or delete the code.

## Type checks

Pyrefly runs with the `strict` preset against `pyrefly-baseline.json`. Pyrefly accepts the errors in that file and
fails on a new error. `make type-baseline` writes the file again, so read its diff as you read code.

## Fixtures

`make fixtures` records `tests/fixtures` again from the live API. Set `BATTLENET_CLIENT_ID` and
`BATTLENET_CLIENT_SECRET` first. The script records each index and the first document in it. It also records the
documents in `VARIANTS`, which together have each shape that Battle.net sends.

Blizzard does not serve realm and account documents for Forever yet. Their fixtures come from community tests, and a
`source` key in each one tells you so.

## Keep the models complete

A model skips a field that it does not declare, so a new field from Blizzard can go missing without an error. Two
checks find it:

- `tests/test_models.py` decodes each fixture and encodes it again. If a field goes missing, the test fails and gives
  its path.
- `make audit-models` does the same check on each document that it can get from the live API. It starts at each index
  and search, and follows each link to a known route. Set `REGION=eu` to check a different region.

Run `make audit-models` after a game patch. If it finds a problem, do these steps:

1. Add a document that shows the new shape to `VARIANTS` in `scripts/record_fixtures.py`.
2. Run `make fixtures`.
3. Change the model until `make test` passes.

## Release

1. Change `version` in `pyproject.toml`. Move the Unreleased entries of the changelog under the new version.
2. Merge to `main`. CI builds and checks the dist, and keeps it as an artifact with the name of the commit.
3. On that commit, publish a GitHub release with the tag `v<version>`. `publish.yml` downloads that artifact, checks its
   checksums and publishes it to PyPI through Trusted Publishing.
