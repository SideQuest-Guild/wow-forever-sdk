"""Models for the Realm API.

Blizzard has not announced or documented a Forever realm API. Realm has not been recorded live for this package: the
realm index has answered 404 on every region since launch. This shape comes from community probing
(https://mhuijskens.com/WoWForever/Api/), not from a recorded live response.
"""

from wow.models._common import Document, IdName, Link, LocalizedString, Model, Ref, TypedName

__all__ = ["Realm", "RealmIndex", "RealmRef", "RealmSearchData"]


class RealmRef(Ref):
    """A realm index entry: id, name, link and slug.

    Shape from community probing; Blizzard has not documented it.
    """

    slug: str


class RealmIndex(Document):
    """Every realm.

    Shape from community probing; Blizzard has not documented it.
    """

    realms: tuple[RealmRef, ...]


class Realm(Document):
    """One realm: its ruleset, locale, timezone and connected realm.

    Shape from community probing; Blizzard has not documented it.
    """

    id: int
    region: IdName
    connected_realm: Link
    name: str
    category: str
    locale: str
    timezone: str
    type: TypedName
    is_tournament: bool
    slug: str


class RealmSearchData(Model):
    """Search-indexed realm data.

    Shape from community probing; Blizzard has not documented it.
    """

    id: int
    name: LocalizedString
    category: LocalizedString
    locale: str
    timezone: str
    type: TypedName
    is_tournament: bool
    slug: str
