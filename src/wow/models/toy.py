"""Models for the Toy API."""

from wow.models._common import Document, IdRef, Ref, TypedName

__all__ = ["Toy", "ToyIndex"]


class ToyIndex(Document):
    """Every toy."""

    toys: tuple[Ref, ...]


class Toy(Document):
    """A toy item that unlocks a toy-box entry."""

    id: int
    item: Ref
    media: IdRef
    source: TypedName
    should_exclude_if_uncollected: bool
    source_description: str | None = None
