"""Models for the Playable Class API."""

from wow.models._common import Document, GenderedName, IdRef, Link, Ref

__all__ = ["PlayableClass", "PlayableClassIndex"]


class PlayableClassIndex(Document):
    """Every playable class. Forever has the nine original classes."""

    classes: tuple[Ref, ...]


class PlayableClass(Document):
    """A playable class with its specializations, races and power types."""

    id: int
    name: str
    gender_name: GenderedName
    power_type: Ref
    specializations: tuple[Ref, ...]
    media: IdRef
    playable_races: tuple[Ref, ...]
    additional_power_types: tuple[Ref, ...] = ()
    pvp_talent_slots: Link | None = None
