"""Models for the Playable Specialization API."""

from wow.models._common import Document, IdRef, NamedLink, Ref

__all__ = ["PlayableSpecialization", "PlayableSpecializationIndex"]


class PlayableSpecializationIndex(Document):
    """Every playable specialization, across every class."""

    character_specializations: tuple[Ref, ...]


class PlayableSpecialization(Document):
    """A class specialization, such as Elemental Combat for Shaman."""

    id: int
    name: str
    playable_class: Ref
    power_type: Ref
    media: IdRef
    spec_talent_tree: NamedLink
