# Models

Each typed method returns a model: an immutable [msgspec](https://msgspec.dev) `Struct` that holds one Battle.net
document. The models are in {mod}`wow.models`. Each model comes from documents that Battle.net sent, not from a
specification, because Blizzard does not publish one for Forever.

## Read a model

A field has the name that Battle.net uses. Five names change, so that each one is a valid Python name:

| Battle.net | Model |
| --- | --- |
| `_links` | `links` |
| `self` | `self_` |
| `range` | `range_` |
| `set` | `set_` |
| `pageSize`, `maxPageSize`, `pageCount`, `resultCountCapped` | `page_size`, `max_page_size`, `page_count`, `result_count_capped` |

::::: {tab-set}
:sync-group: io

:::: {tab-item} Sync
:sync: sync

```python
druid = client.playable_classes.get(11)
druid.name  # "Druid"
druid.links.self_.href
[spec.name for spec in druid.specializations]
```
::::

:::: {tab-item} Async
:sync: async

```python
druid = await client.playable_classes.get(11)
druid.name  # "Druid"
druid.links.self_.href
[spec.name for spec in druid.specializations]
```
::::
:::::

You cannot change a model. If you set a field, Python raises `AttributeError`. To make a changed copy, use
`msgspec.structs.replace`:

```python
import msgspec

renamed = msgspec.structs.replace(druid, name="Shapeshifter")
```

## Fields that can be missing

Battle.net leaves out some fields on some documents. Each of these fields has a default:

| Kind of field | Default |
| --- | --- |
| A value or a nested object | `None` |
| A list | `()` |
| A flag, such as `should_exclude_if_uncollected` | `False` |

For example, a talent for a whole class has no specialization, so its `playable_specialization` is `None`. Some
talents are only an id, so all their other fields have the default.

## Fields that a model does not declare

When Battle.net adds a field, the model skips it, and the response still decodes. To read the new field before a
release adds it, get the raw document:

::::: {tab-set}
:sync-group: io

:::: {tab-item} Sync
:sync: sync

```python
raw = client.get("/data/wow/mount/9", namespace="static").json()
raw["new_field"]
```
::::

:::: {tab-item} Async
:sync: async

```python
raw = (await client.get("/data/wow/mount/9", namespace="static")).json()
raw["new_field"]
```
::::
:::::

## Turn a model into JSON

msgspec converts a model back to the names and the shape that Battle.net uses:

```python
msgspec.to_builtins(druid)  # dict
msgspec.json.encode(druid)  # JSON bytes
```

## Decode errors

If a response does not agree with its model, the client raises {class}`~wow.APIResponseValidationError`. The error
has the `response`. Its `__cause__` is the `msgspec.ValidationError`, which gives the path of the bad field:

```text
Object missing required field `faction` - at `$.results[3].data`
```

The error never shows the value of a field, so a token in a response cannot get into your logs.

## How the models stay correct

The test suite decodes each recorded document, then encodes it again. If a field is missing from the result, the test
fails and gives the path of the field. `make audit-models` does the same check on each document that it can get from
the live API. The [development guide](https://github.com/SideQuest-Guild/wow-forever-sdk/blob/main/docs/development.md#keep-the-models-complete)
says when to run it.
