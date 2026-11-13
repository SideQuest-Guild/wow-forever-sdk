"""Models for the Creature, Creature Family and Creature Type APIs."""

from wow.models._common import Document, IdRef, LocalizedString, Model, Ref

__all__ = [
    "Creature",
    "CreatureFamily",
    "CreatureFamilyIndex",
    "CreatureSearchData",
    "CreatureType",
    "CreatureTypeIndex",
]


class CreatureFamilyIndex(Document):
    """Every creature family, such as Bat or Wolf."""

    creature_families: tuple[Ref, ...]


class CreatureFamily(Document):
    """A creature family: the pet family icon shared by related beasts. A few families have no icon."""

    id: int
    name: str
    media: IdRef | None = None


class CreatureTypeIndex(Document):
    """Every creature type, such as Beast or Dragonkin."""

    creature_types: tuple[Ref, ...]


class CreatureType(Document):
    """A creature type."""

    id: int
    name: str


class _CreatureSearchIdOnly(Model):
    """A creature display reference stripped down to its id, as search results carry it."""

    id: int


class _CreatureSearchLocalizedRef(Model):
    """An id and localized name, as search results carry nested type and family refs."""

    id: int
    name: LocalizedString


class Creature(Document):
    """A creature, Forest Spider included."""

    id: int
    name: str
    type: Ref
    is_tameable: bool
    family: Ref | None = None
    creature_displays: tuple[IdRef, ...] = ()


class CreatureSearchData(Model):
    """One creature as indexed for search: every locale's name at once, no ``_links``."""

    id: int
    name: LocalizedString
    type: _CreatureSearchLocalizedRef
    is_tameable: bool
    family: _CreatureSearchLocalizedRef | None = None
    creature_displays: tuple[_CreatureSearchIdOnly, ...] = ()
