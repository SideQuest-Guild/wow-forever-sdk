"""Models for the Profession API."""

from wow.models._common import Document, IdRef, Ref, TypedName

__all__ = ["Profession", "ProfessionIndex"]


class ProfessionIndex(Document):
    """Every profession, primary and secondary."""

    professions: tuple[Ref, ...]


class Profession(Document):
    """A profession, such as Tailoring, with its skill tiers."""

    id: int
    name: str
    description: str
    type: TypedName
    media: IdRef
    skill_tiers: tuple[Ref, ...] = ()
