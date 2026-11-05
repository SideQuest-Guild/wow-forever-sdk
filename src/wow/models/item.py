"""Models for the Item, Item Class and Item Set APIs."""

from wow.models._common import Document, IdRef, LocalizedString, Model, Ref, TypedName

__all__ = [
    "Item",
    "ItemClass",
    "ItemClassIndex",
    "ItemDisplayValue",
    "ItemDps",
    "ItemPreview",
    "ItemPreviewSpell",
    "ItemRequirements",
    "ItemSearchData",
    "ItemSet",
    "ItemSetEffect",
    "ItemSetIndex",
    "ItemStat",
    "ItemStatColor",
    "ItemStatDisplay",
    "ItemWeapon",
    "ItemWeaponDamage",
]


class ItemClassIndex(Document):
    """Every item class, such as Weapon or Consumable."""

    item_classes: tuple[Ref, ...]


class ItemClass(Document):
    """An item class with its subclasses."""

    id: int
    name: str
    item_subclasses: tuple[Ref, ...]


class ItemSetIndex(Document):
    """Every item set."""

    item_sets: tuple[Ref, ...]


class ItemSetEffect(Model):
    """One bonus an item set grants at a piece-count threshold."""

    display_string: str
    required_count: int


class ItemSet(Document):
    """An equipment set and the bonuses wearing pieces of it grants."""

    id: int
    name: str
    items: tuple[Ref, ...]
    effects: tuple[ItemSetEffect, ...] = ()


class ItemDisplayValue(Model):
    """An integer value with its rendered tooltip label, such as durability, item level or weapon speed."""

    display_string: str
    value: int


class ItemDps(Model):
    """A weapon's damage-per-second rating with its rendered tooltip label."""

    display_string: str
    value: float


class ItemRequirements(Model):
    """What a character needs before equipping an item."""

    level: ItemDisplayValue | None = None


class ItemPreviewSpell(Model):
    """A spell an item grants or procs, with the tooltip text describing it."""

    spell: Ref
    description: str


class ItemStatColor(Model):
    """The RGBA color the tooltip renders a stat line in."""

    r: int
    g: int
    b: int
    a: float


class ItemStatDisplay(Model):
    """A stat's rendered label and tooltip color."""

    display_string: str
    color: ItemStatColor


class ItemStat(Model):
    """One stat line on an item's tooltip, such as ``+5 Agility``."""

    type: TypedName
    value: int
    display: ItemStatDisplay


class ItemWeaponDamage(Model):
    """A weapon's damage range."""

    min_value: int
    max_value: int
    display_string: str
    damage_class: TypedName


class ItemWeapon(Model):
    """Weapon-specific tooltip data: speed, damage range and resulting DPS."""

    damage: ItemWeaponDamage
    attack_speed: ItemDisplayValue
    dps: ItemDps


class ItemPreview(Model):
    """The rendered tooltip for an item: everything the game client shows on hover."""

    item: IdRef
    quality: TypedName
    name: str
    media: IdRef
    item_class: Ref
    item_subclass: Ref
    inventory_type: TypedName
    binding: TypedName | None = None
    unique_equipped: str | None = None
    weapon: ItemWeapon | None = None
    stats: tuple[ItemStat, ...] = ()
    spells: tuple[ItemPreviewSpell, ...] = ()
    requirements: ItemRequirements | None = None
    durability: ItemDisplayValue | None = None
    level: ItemDisplayValue | None = None


class Item(Document):
    """An item, Thunderfury included."""

    id: int
    name: str
    quality: TypedName
    level: int
    required_level: int
    media: IdRef
    item_class: Ref
    item_subclass: Ref
    inventory_type: TypedName
    is_equippable: bool
    is_stackable: bool
    max_count: int
    purchase_price: int
    purchase_quantity: int
    sell_price: int
    appearances: tuple[IdRef, ...] = ()
    preview_item: ItemPreview


class _ItemSearchIdOnly(Model):
    """An id-only reference, as search results carry it."""

    id: int


class _ItemSearchLocalizedRef(Model):
    """An id and localized name, as search results carry nested class and subclass refs."""

    id: int
    name: LocalizedString


class _ItemSearchLocalizedType(Model):
    """A ``type`` constant with its localized label, as search results carry it."""

    type: str
    name: LocalizedString


class ItemSearchData(Model):
    """One item as indexed for search: every locale's name at once, no ``_links``."""

    id: int
    name: LocalizedString
    quality: _ItemSearchLocalizedType
    level: int
    required_level: int
    media: _ItemSearchIdOnly
    item_class: _ItemSearchLocalizedRef
    item_subclass: _ItemSearchLocalizedRef
    inventory_type: _ItemSearchLocalizedType
    is_equippable: bool
    is_stackable: bool
    max_count: int
    purchase_price: int
    purchase_quantity: int
    sell_price: int
    appearances: tuple[_ItemSearchIdOnly, ...] = ()
