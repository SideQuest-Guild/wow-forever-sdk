"""Models for the Power Type API."""

from wow.models._common import Document, Ref

__all__ = ["PowerType", "PowerTypeIndex"]


class PowerTypeIndex(Document):
    """Every power type, such as Mana or Rage."""

    power_types: tuple[Ref, ...]


class PowerType(Document):
    """A power type."""

    id: int
    name: str
