"""Models for the Pet API."""

from wow.models._common import Document, IdRef, Model, Ref

__all__ = ["BattlePetType", "Pet", "PetIndex"]


class BattlePetType(Model):
    """A battle pet's family, such as Critter or Dragonkin."""

    id: int
    name: str
    type: str


class PetIndex(Document):
    """Every battle pet species."""

    pets: tuple[Ref, ...]


class Pet(Document):
    """A battle pet species and the creature it is tamed from."""

    id: int
    name: str
    icon: str
    battle_pet_type: BattlePetType
    creature: Ref
    media: IdRef
    is_alliance_only: bool
    is_battlepet: bool
    is_capturable: bool
    is_horde_only: bool
    is_random_creature_display: bool
    is_tradable: bool
    description: str | None = None
