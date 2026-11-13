"""Models for the Spell API."""

from wow.models._common import Document, IdRef, LocalizedString, Model

__all__ = ["Spell", "SpellSearchData"]


class Spell(Document):
    """A spell, such as a talent or an ability."""

    id: int
    name: str
    media: IdRef | None = None
    description: str | None = None


class _SpellSearchIdOnly(Model):
    """A media reference stripped down to its id, as search results carry it."""

    id: int


class SpellSearchData(Model):
    """One spell as indexed for search: every locale's name at once, no ``_links``."""

    id: int
    name: LocalizedString
    media: _SpellSearchIdOnly | None = None
