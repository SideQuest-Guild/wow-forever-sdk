"""Models for the Creature Family and Creature Type APIs."""

from wow.models._common import Document, IdRef, Ref

__all__ = ["CreatureFamily", "CreatureFamilyIndex", "CreatureType", "CreatureTypeIndex"]


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
