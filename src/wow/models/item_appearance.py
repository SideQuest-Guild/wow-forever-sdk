"""Models for the Item Appearance API."""

from wow.models._common import Document, IdRef, Link, LocalizedString, Model, Ref, TypedName

__all__ = [
    "ItemAppearance",
    "ItemAppearanceSearchData",
    "ItemAppearanceSet",
    "ItemAppearanceSetIndex",
    "ItemAppearanceSlot",
    "ItemAppearanceSlotIndex",
    "ItemAppearanceSlotRef",
]


class ItemAppearance(Document):
    """An item appearance: the rendered look one or more items share."""

    id: int
    slot: TypedName
    item_class: Ref
    item_subclass: Ref
    item_display_info_id: int
    items: tuple[Ref, ...]
    media: IdRef


class ItemAppearanceSetIndex(Document):
    """Every item appearance set, such as a transmog set."""

    appearance_sets: tuple[Ref, ...]


class ItemAppearanceSet(Document):
    """An item appearance set: the appearances that make it up."""

    id: int
    set_name: str
    appearances: tuple[IdRef, ...]


class ItemAppearanceSlotRef(Model):
    """A link to one equipment slot's item appearances; the slot type is the last segment of ``key``'s href."""

    key: Link


class ItemAppearanceSlotIndex(Document):
    """Every equipment slot that has item appearances."""

    slots: tuple[ItemAppearanceSlotRef, ...]


class ItemAppearanceSlot(Document):
    """One equipment slot's item appearances."""

    appearances: tuple[IdRef, ...]


class _ItemAppearanceSearchLocalizedType(Model):
    """A ``type`` constant with its localized label, as search results carry a slot."""

    type: str
    name: LocalizedString


class ItemAppearanceSearchData(Model):
    """One item appearance as indexed for search: every locale's name at once, no ``_links``."""

    id: int
    item_display_info_id: int
    slot: _ItemAppearanceSearchLocalizedType
