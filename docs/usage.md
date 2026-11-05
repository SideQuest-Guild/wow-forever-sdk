# Usage

## Clients

{class}`wow.Client` and {class}`wow.AsyncClient` have the same methods; the async ones are awaited. Create one client
for the life of your program and close it when done, ideally as a context manager:

```python
from wow import AsyncClient, Client

with Client() as client:
    druid = client.playable_classes.get(11)

async with AsyncClient() as client:
    druid = await client.playable_classes.get(11)
```

The async client runs under asyncio and trio.

## Credentials

Game data needs an app client from https://develop.battle.net/access/clients. Pass its id and secret, or set
`BATTLENET_CLIENT_ID` and `BATTLENET_CLIENT_SECRET`. The client trades them for an access token on the first request,
caches it, and fetches a new one five minutes before it expires or when Battle.net rejects it.

### User login for profile routes

The account profile belongs to a player, so it needs that player's token with the `wow.profile` scope:

```python
url = client.authorization_url("https://app.example/callback", state=session_state)
# Redirect the player to `url`. Battle.net sends them back with ?code=...&state=...
token = client.exchange_code(code, "https://app.example/callback")

profile = client.with_options(access_token=token.access_token).account.profile()
for character in profile.wow_accounts[0].characters:
    print(character.name, character.surname, character.realm_id)
```

Check that `state` matches before exchanging the code. Forever characters have a `surname` and no `realm` field;
{attr}`~wow.models.AccountCharacter.realm_id` reads the realm from the protected-character link.

## Regions and locales

`region` picks the host (`us`, `eu`, `kr`, `tw`) and the namespace suffix. `locale` picks the language of names and
descriptions and defaults to the region's main locale (`en_US`, `en_GB`, `ko_KR`, `zh_TW`).

{meth}`~wow.Client.with_options` returns a copy that shares the connection pool and the cached app token:

```python
eu = client.with_options(region="eu")
german = eu.with_options(locale="de_DE")
```

China is not supported: it uses separate hosts and developer accounts, and Forever has not been verified there.

## Search

Items, mounts and realms support Battle.net search. `name` matches in the client's locale; `filters` take any indexed
field:

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

Search data comes back in every locale whatever the client's locale, so localized fields are dictionaries.
Battle.net returns at most 1,000 results per query.

## Errors

Every exception derives from {class}`wow.WowError`. HTTP failures raise a subclass of {class}`wow.APIStatusError`
carrying the response, its decoded `body` and the `namespace` header:

| Status | Exception | Usual cause |
| --- | --- | --- |
| 400 | `BadRequestError` | Invalid search syntax or OAuth code |
| 401 | `AuthenticationError` | Bad client credentials, or an expired user token |
| 403 | `PermissionDeniedError` | Unknown namespace, or a token without the needed scope |
| 404 | `NotFoundError` | No document at that path |
| 429 | `RateLimitError` | Quota exceeded after retries |
| 5xx | `InternalServerError` | Battle.net failed after retries |

`NotFoundError.namespace` is set when Battle.net recognised the namespace, which separates "this does not exist" from
"this namespace is unknown". Much of Forever answers 404 while Blizzard is still publishing it.

`APIConnectionError` and `APITimeoutError` mean no response arrived. `APIResponseValidationError` means a response did
not match its model.

## Retries and timeouts

Connection errors, timeouts, 408, 429 and 5xx responses are retried `max_retries` times (default 2). The wait doubles
from half a second up to eight seconds with jitter, or follows `Retry-After` up to 60 seconds; a longer
`Retry-After` raises immediately. The default timeout is 15 seconds, 5 to connect.

```python
client = Client(max_retries=5, timeout=30)
patient = client.with_options(max_retries=10)
```

## Raw access

{meth}`~wow.Client.get` reads any document, including links from other documents, and returns an
{class}`~wow.APIResponse`. Links must point at the client's own API host and scheme; anything else raises
`ValueError` rather than sending your token elsewhere.

```python
response = client.get("/data/wow/journal-instance/index", namespace="static")
response.namespace  # "static-1.60.1_70399-forever-us": the concrete namespace Battle.net used
response.last_modified  # datetime from the Last-Modified header
response.json()  # untyped body

warrior = client.playable_classes.get(1)
media = client.get(warrior.media.key.href).parse(Media)
```

## Bring your own HTTP client

Pass `http_client=` to route requests through proxies, custom transports or an HTTP cache. The client never closes
an `http_client` it was given.
