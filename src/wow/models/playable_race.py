"""Models for the Playable Race API."""

from wow.models._common import Document, GenderedName, Ref, TypedName

__all__ = ["PlayableRace", "PlayableRaceIndex"]


class PlayableRaceIndex(Document):
    """Every playable race. Forever adds the High Order Skyborne and Windshaper Skyborne (ids 95 and 96)."""

    races: tuple[Ref, ...]


class PlayableRace(Document):
    """A playable race with its selectable classes and racial spells."""

    id: int
    name: str
    gender_name: GenderedName
    faction: TypedName
    playable_classes: tuple[Ref, ...]
    racial_spells: tuple[Ref, ...]
    is_allied_race: bool
    is_selectable: bool
