"""Models for the Mount API."""

from wow.models._common import Document, IdRef, LocalizedString, Model, Ref

__all__ = ["Mount", "MountIndex", "MountSearchData"]


class MountIndex(Document):
    """Every mount."""

    mounts: tuple[Ref, ...]


class Mount(Document):
    """A mount."""

    id: int
    name: str
    description: str | None
    creature_displays: tuple[IdRef, ...] = ()


class _MountSearchIdOnly(Model):
    """A creature display reference stripped down to its id, as search results carry it."""

    id: int


class _MountSearchFaction(Model):
    """A mount's faction restriction, localized."""

    type: str
    name: LocalizedString


class MountSearchData(Model):
    """One mount as indexed for search: every locale's name at once, no ``_links``."""

    id: int
    name: LocalizedString
    creature_displays: tuple[_MountSearchIdOnly, ...] = ()
    faction: _MountSearchFaction
