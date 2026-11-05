"""Models for the Title API."""

from wow.models._common import Document, GenderedName, Model, Ref, TypedName

__all__ = ["Title", "TitleIndex", "TitleSource"]


class TitleIndex(Document):
    """Every title."""

    titles: tuple[Ref, ...]


class TitleSource(Model):
    """How a title is earned, such as by the quests that award it."""

    type: TypedName
    quests: tuple[Ref, ...] = ()


class Title(Document):
    """A title, such as Commander, with its male and female forms around ``{name}``."""

    id: int
    name: str
    gender_name: GenderedName
    source: TitleSource | None = None
