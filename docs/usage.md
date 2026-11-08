# Usage

## Install

The package needs Python 3.14 or later.

::::: {tab-set}
:sync-group: installer

:::: {tab-item} {iconify}`simple-icons:uv` uv
:sync: uv

```console
uv add wow
```
::::

:::: {tab-item} {iconify}`simple-icons:pypi` pip
:sync: pip

```console
pip install wow
```
::::

:::: {tab-item} {iconify}`simple-icons:pdm` pdm
:sync: pdm

```console
pdm add wow
```
::::

:::: {tab-item} {iconify}`simple-icons:poetry` poetry
:sync: poetry

```console
poetry add wow
```
::::

:::: {tab-item} {iconify}`simple-icons:python` pipenv
:sync: pipenv

```console
pipenv install wow
```
::::
:::::

## Clients

{class}`wow.Client` and {class}`wow.AsyncClient` have the same methods. With the async client, you `await` each call.
Make one client when your program starts, and close it when your program stops. A `with` block closes it for you.
The async client runs under asyncio and trio.

::::: {tab-set}
:sync-group: io

:::: {tab-item} Sync
:sync: sync

```python
from wow import Client

with Client() as client:
    druid = client.playable_classes.get(11)
```
::::

:::: {tab-item} Async
:sync: async

```python
from wow import AsyncClient

async with AsyncClient() as client:
    druid = await client.playable_classes.get(11)
```
::::
:::::

## Credentials

Game data needs an app client from https://develop.battle.net/access/clients. Give its id and secret to the client, or
set `BATTLENET_CLIENT_ID` and `BATTLENET_CLIENT_SECRET`. On the first request, the client gets an access token and
keeps it. It gets a new token 5 minutes before the old one expires, or when Battle.net refuses the old one.

### User login for profile routes

The account profile belongs to a player. To read it, you need that player's token with the `wow.profile` scope:

::::: {tab-set}
:sync-group: io

:::: {tab-item} Sync
:sync: sync

```python
url = client.authorization_url("https://app.example/callback", state=session_state)
# Send the player to `url`. Battle.net sends them back with ?code=...&state=...
token = client.exchange_code(code, "https://app.example/callback")

profile = client.with_options(access_token=token.access_token).account.profile()
for character in profile.wow_accounts[0].characters:
    print(character.name, character.surname, character.realm_id)
```
::::

:::: {tab-item} Async
:sync: async

```python
url = client.authorization_url("https://app.example/callback", state=session_state)
# Send the player to `url`. Battle.net sends them back with ?code=...&state=...
token = await client.exchange_code(code, "https://app.example/callback")

profile = await client.with_options(access_token=token.access_token).account.profile()
for character in profile.wow_accounts[0].characters:
    print(character.name, character.surname, character.realm_id)
```
::::
:::::

Before you exchange the code, make sure that `state` is the value you sent. A Forever character has a `surname` and
no `realm` field. {attr}`~wow.models.AccountCharacter.realm_id` reads the realm from the link to the character.

## Characters and guilds

Forever has no realms in the API. A character's address is its name and surname with a hyphen between them, and a
guild's address is its name. Your app token can read any character and any guild:

::::: {tab-set}
:sync-group: io

:::: {tab-item} Sync
:sync: sync

```python
evoke = client.characters.get("evoke-saint")
print(evoke.level, evoke.character_class.name, evoke.guild.name if evoke.guild else None)

gear = client.characters.equipment("evoke-saint")
roster = client.guilds.roster("sidequest")
for member in roster.members:
    print(member.rank, member.character.name, member.character.surname, member.character.slug)
```
::::

:::: {tab-item} Async
:sync: async

```python
evoke = await client.characters.get("evoke-saint")
print(evoke.level, evoke.character_class.name, evoke.guild.name if evoke.guild else None)

gear = await client.characters.equipment("evoke-saint")
roster = await client.guilds.roster("sidequest")
for member in roster.members:
    print(member.rank, member.character.name, member.character.surname, member.character.slug)
```
::::
:::::

The case of the slug does not matter. Battle.net has no search for characters or guilds, so you must know the exact
name. A character shows only after it logs out once, and Battle.net updates it each time it logs out. A character
that does not exist gives {class}`~wow.NotFoundError`. So does a part of a profile that Battle.net has not made yet,
such as the images of a new character.

Characters and guilds link to a ruleset, such as Normal or PvP. `client.rulesets` reads them.

## Auction houses

Forever has fifteen auction houses per ruleset: five groups of an Alliance, a Horde and a Blackwater house. Every
ruleset lists the same fifteen. `client.auctions.houses` lists them, `client.auctions.get` reads one house's posted
auctions, and `client.auctions.commodities` reads its stackable commodities. An empty house, such as house 112, has
no `auctions`:

::::: {tab-set}
:sync-group: io

:::: {tab-item} Sync
:sync: sync

```python
from collections import defaultdict

lowest = defaultdict(lambda: None)
house = client.auctions.get(2, 125)
for auction in house.auctions:
    if auction.buyout is not None and (lowest[auction.item.id] is None or auction.buyout < lowest[auction.item.id]):
        lowest[auction.item.id] = auction.buyout
```
::::

:::: {tab-item} Async
:sync: async

```python
from collections import defaultdict

lowest = defaultdict(lambda: None)
house = await client.auctions.get(2, 125)
for auction in house.auctions:
    if auction.buyout is not None and (lowest[auction.item.id] is None or auction.buyout < lowest[auction.item.id]):
        lowest[auction.item.id] = auction.buyout
```
::::
:::::

## Regions and locales

`region` selects the host and the namespace: `us`, `eu`, `kr` or `tw`. `locale` selects the language of names and
descriptions. Each region has a default locale: `en_US`, `en_GB`, `ko_KR` and `zh_TW`.

{meth}`~wow.Client.with_options` gives a copy of the client. The copy uses the same connections and the same app token:

```python
eu = client.with_options(region="eu")
german = eu.with_options(locale="de_DE")
```

The package does not support China. China has different hosts and different developer accounts, and nobody has
checked Forever there.

## Search

You can search items, mounts and realms. `name` finds a name in the locale of the client. `filters` takes any field
that Battle.net indexes:

::::: {tab-set}
:sync-group: io

:::: {tab-item} Sync
:sync: sync

```python
from wow import Not, Range

page = client.items.search(
    name="Sword",
    filters={
        "required_level": Range(50, 60),
        "quality.type": ["EPIC", "LEGENDARY"],
        "inventory_type.type": Not("TWOHWEAPON"),
    },
    order_by=["level:desc", "id"],
    page_size=50,
)

for hit in client.items.search_all(name="Sword"):
    print(hit.data.id, hit.data.name["en_US"], hit.key.href)
```
::::

:::: {tab-item} Async
:sync: async

```python
from wow import Not, Range

page = await client.items.search(
    name="Sword",
    filters={
        "required_level": Range(50, 60),
        "quality.type": ["EPIC", "LEGENDARY"],
        "inventory_type.type": Not("TWOHWEAPON"),
    },
    order_by=["level:desc", "id"],
    page_size=50,
)

async for hit in client.items.search_all(name="Sword"):
    print(hit.data.id, hit.data.name["en_US"], hit.key.href)
```
::::
:::::

Search data has all locales, whatever the locale of the client. Thus each name in search data is a dictionary.
Battle.net gives a maximum of 1,000 results for one search.

## Models

Each typed method returns an immutable model. {doc}`models` tells how to read a model, which fields can be missing,
and how to read a field that a model does not declare.

## Errors

Each exception comes from {class}`wow.WowError`. For an HTTP error, the client raises a subclass of
{class}`wow.APIStatusError`. The error has the response, its decoded `body` and the `namespace` header:

| Status | Exception | Usual cause |
| --- | --- | --- |
| 400 | `BadRequestError` | Bad search syntax, or a bad OAuth code |
| 401 | `AuthenticationError` | Bad client credentials, or an expired user token |
| 403 | `PermissionDeniedError` | An unknown namespace, or a token without the necessary scope |
| 404 | `NotFoundError` | No document at that path |
| 429 | `RateLimitError` | Too many requests, after all retries |
| 5xx | `InternalServerError` | Battle.net failed, after all retries |

Battle.net sets `NotFoundError.namespace` only for a namespace that it knows. Thus you can tell a document that does not
exist from a namespace that Battle.net does not know. Many Forever routes give 404 while Blizzard adds the data.

`APIConnectionError` and `APITimeoutError` tell you that no response came. `APIResponseValidationError` tells you that
a response did not agree with its model.

## Retries and timeouts

The client retries connection errors, timeouts, and 408, 429 and 5xx responses. It retries `max_retries` times, and
the default is 2. The wait starts at half a second and doubles to a maximum of 8 seconds, with a small random change.
If Battle.net sends `Retry-After`, the client waits that long, to a maximum of 60 seconds. If `Retry-After` is longer,
the client raises the error at once. The default timeout is 15 seconds, and 5 seconds to connect.

```python
client = Client(max_retries=5, timeout=30)
patient = client.with_options(max_retries=10)
```

## Raw access

{meth}`~wow.Client.get` reads any document, and it can follow a link from another document. It returns an
{class}`~wow.APIResponse`. A link must use the host and the scheme of the client's API. For any other link, `get`
raises `ValueError`, so your token never goes to a different host.

::::: {tab-set}
:sync-group: io

:::: {tab-item} Sync
:sync: sync

```python
response = client.get("/data/wow/journal-instance/index", namespace="static")
response.namespace  # "static-1.60.1_70399-forever-us": the namespace that Battle.net used
response.last_modified  # datetime from the Last-Modified header
response.json()  # the body, with no model

warrior = client.playable_classes.get(1)
media = client.get(warrior.media.key.href).parse(Media)
```
::::

:::: {tab-item} Async
:sync: async

```python
response = await client.get("/data/wow/journal-instance/index", namespace="static")
response.namespace  # "static-1.60.1_70399-forever-us": the namespace that Battle.net used
response.last_modified  # datetime from the Last-Modified header
response.json()  # the body, with no model

warrior = await client.playable_classes.get(1)
media = (await client.get(warrior.media.key.href)).parse(Media)
```
::::
:::::

## Use your own HTTP client

To send requests through a proxy, a custom transport or an HTTP cache, give an `httpx` client as `http_client=`. The
client does not close an `http_client` that you give it.
