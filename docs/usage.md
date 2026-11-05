# Usage

## Clients

{class}`wow.Client` and {class}`wow.AsyncClient` have the same methods. With the async client, you `await` each call.
Make one client when your program starts, and close it when your program stops. A `with` block closes it for you:

```python
from wow import AsyncClient, Client

with Client() as client:
    druid = client.playable_classes.get(11)

async with AsyncClient() as client:
    druid = await client.playable_classes.get(11)
```

The async client runs under asyncio and trio.

## Credentials

Game data needs an app client from https://develop.battle.net/access/clients. Give its id and secret to the client, or
set `BATTLENET_CLIENT_ID` and `BATTLENET_CLIENT_SECRET`. On the first request, the client gets an access token and
keeps it. It gets a new token 5 minutes before the old one expires, or when Battle.net refuses the old one.

### User login for profile routes

The account profile belongs to a player. To read it, you need that player's token with the `wow.profile` scope:

```python
url = client.authorization_url("https://app.example/callback", state=session_state)
# Send the player to `url`. Battle.net sends them back with ?code=...&state=...
token = client.exchange_code(code, "https://app.example/callback")

profile = client.with_options(access_token=token.access_token).account.profile()
for character in profile.wow_accounts[0].characters:
    print(character.name, character.surname, character.realm_id)
```

Before you exchange the code, make sure that `state` is the value you sent. A Forever character has a `surname` and
no `realm` field. {attr}`~wow.models.AccountCharacter.realm_id` reads the realm from the link to the character.

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

```python
response = client.get("/data/wow/journal-instance/index", namespace="static")
response.namespace  # "static-1.60.1_70399-forever-us": the namespace that Battle.net used
response.last_modified  # datetime from the Last-Modified header
response.json()  # the body, with no model

warrior = client.playable_classes.get(1)
media = client.get(warrior.media.key.href).parse(Media)
```

## Use your own HTTP client

To send requests through a proxy, a custom transport or an HTTP cache, give an `httpx` client as `http_client=`. The
client does not close an `http_client` that you give it.
