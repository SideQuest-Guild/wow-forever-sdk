"""Models for the Title API."""

from wow.models._common import Document, GenderedName, Ref

__all__ = ["Title", "TitleIndex"]


class TitleIndex(Document):
    """Every title."""

    titles: tuple[Ref, ...]


class Title(Document):
    """A title, such as Commander, with its male and female forms around ``{name}``."""

    id: int
    name: str
    gender_name: GenderedName
