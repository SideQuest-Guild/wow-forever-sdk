"""Models for the Mount API."""

from wow.models._common import Document, IdRef, LocalizedString, Model, Ref, TypedName

__all__ = ["Mount", "MountIndex", "MountRequirements", "MountSearchData"]


class MountIndex(Document):
    """Every mount."""

    mounts: tuple[Ref, ...]


class MountRequirements(Model):
    """Who can use a mount: a faction, and for some mounts only certain classes or races."""

    faction: TypedName | None = None
    classes: tuple[Ref, ...] = ()
    races: tuple[Ref, ...] = ()


class Mount(Document):
    """A mount."""

    id: int
    name: str
    description: str | None
    creature_displays: tuple[IdRef, ...] = ()
    faction: TypedName | None = None
    requirements: MountRequirements | None = None
    source: TypedName | None = None
    should_exclude_if_uncollected: bool = False


class _MountSearchIdOnly(Model):
    """A creature display reference stripped down to its id, as search results carry it."""

    id: int


class _MountSearchLocalizedType(Model):
    """A ``type`` constant with its localized label, such as a faction or a source, as search results carry it."""

    type: str
    name: LocalizedString


class MountSearchData(Model):
    """One mount as indexed for search: every locale's name at once, no ``_links``."""

    id: int
    name: LocalizedString
    creature_displays: tuple[_MountSearchIdOnly, ...] = ()
    faction: _MountSearchLocalizedType | None = None
    source: _MountSearchLocalizedType | None = None
