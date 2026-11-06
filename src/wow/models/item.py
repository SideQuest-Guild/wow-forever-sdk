"""Models for the Item, Item Class and Item Set APIs."""

from msgspec import field

from wow.models._common import Document, IdRef, LocalizedString, Model, Ref, TypedName

__all__ = [
    "Item",
    "ItemAbilityRequirement",
    "ItemArmor",
    "ItemClass",
    "ItemClassIndex",
    "ItemDisplayValue",
    "ItemDps",
    "ItemFactionRequirement",
    "ItemHolidayRequirement",
    "ItemPlayableRequirement",
    "ItemPreview",
    "ItemPreviewSet",
    "ItemPreviewSetItem",
    "ItemPreviewSpell",
    "ItemReagent",
    "ItemRecipe",
    "ItemReputationRequirement",
    "ItemRequirements",
    "ItemSearchData",
    "ItemSellPrice",
    "ItemSellPriceStrings",
    "ItemSet",
    "ItemSetEffect",
    "ItemSetIndex",
    "ItemSetRequirements",
    "ItemSkillRequirement",
    "ItemStartsQuest",
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
    """An item class with its subclasses. A class with no subclasses, such as WoW Token, lists none."""

    id: int
    name: str
    item_subclasses: tuple[Ref, ...] = ()


class ItemSetIndex(Document):
    """Every item set."""

    item_sets: tuple[Ref, ...]


class ItemSetEffect(Model):
    """One bonus an item set grants at a piece-count threshold.

    ``is_active`` is set only in a character's equipment, when the character wears enough pieces for the bonus.
    """

    display_string: str
    required_count: int
    is_active: bool = False


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


class ItemPlayableRequirement(Model):
    """The classes, or the races, that can use an item."""

    display_string: str
    links: tuple[Ref, ...]


class ItemReputationRequirement(Model):
    """The reputation standing an item needs. ``min_reputation_level`` counts tiers up from Hated, which is 0."""

    faction: Ref
    min_reputation_level: int
    display_string: str


class ItemAbilityRequirement(Model):
    """A spell a character must know before using an item, such as a riding skill."""

    spell: Ref
    display_string: str


class ItemFactionRequirement(Model):
    """The one faction, Horde or Alliance, that can use an item."""

    value: TypedName
    display_string: str


class ItemHolidayRequirement(Model):
    """The world event an item needs, such as Love is in the Air."""

    display_string: str


class ItemRequirements(Model):
    """What a character needs before equipping an item."""

    level: ItemDisplayValue | None = None
    playable_classes: ItemPlayableRequirement | None = None
    playable_races: ItemPlayableRequirement | None = None
    reputation: ItemReputationRequirement | None = None
    skill: ItemSkillRequirement | None = None
    ability: ItemAbilityRequirement | None = None
    faction: ItemFactionRequirement | None = None
    holiday: ItemHolidayRequirement | None = None


class ItemPreviewSpell(Model):
    """A spell an item grants or procs, with the tooltip text describing it."""

    spell: Ref
    description: str
    display_color: ItemStatColor | None = None


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
    """One stat line on an item's tooltip, such as ``+5 Agility``. A few lines, such as resistances, have only text."""

    display: ItemStatDisplay
    type: TypedName | None = None
    value: int | None = None
    is_equip_bonus: bool = False
    is_hidden: bool = False


class ItemArmor(Model):
    """An armor or a block value line on an item's tooltip."""

    value: int
    display: ItemStatDisplay


class ItemSellPriceStrings(Model):
    """A sell price split into the coins the tooltip shows."""

    header: str
    gold: str
    silver: str
    copper: str


class ItemSellPrice(Model):
    """What a vendor pays for an item, in copper, with its tooltip text."""

    value: int
    display_strings: ItemSellPriceStrings


class ItemSkillRequirement(Model):
    """A profession skill level, such as Tailoring 300."""

    profession: Ref
    level: int
    display_string: str


class ItemSetRequirements(Model):
    """What a character needs before an item set's bonuses apply."""

    skill: ItemSkillRequirement


class ItemPreviewSetItem(Model):
    """One piece of an item set, as an item's tooltip lists it.

    ``is_equipped`` is set only in a character's equipment, for the pieces the character wears.
    """

    item: Ref
    is_equipped: bool = False


class ItemPreviewSet(Model):
    """The item set an item belongs to, as its tooltip shows it.

    In a character's equipment, ``display_string`` counts the pieces worn, such as ``Rotmender's Raiment (4/5)``.
    """

    item_set: Ref
    items: tuple[ItemPreviewSetItem, ...]
    display_string: str
    effects: tuple[ItemSetEffect, ...] = ()
    requirements: ItemSetRequirements | None = None


class ItemWeaponDamage(Model):
    """A weapon's damage range."""

    min_value: int
    max_value: int
    display_string: str
    damage_class: TypedName


class ItemWeapon(Model):
    """Weapon-specific tooltip data: speed, damage range and resulting DPS. Some weapons show only their damage."""

    damage: ItemWeaponDamage
    attack_speed: ItemDisplayValue | None = None
    dps: ItemDps | None = None


class ItemStartsQuest(Model):
    """The quest that an item starts when a character uses it."""

    quest: Ref
    display_string: str


class ItemReagent(Model):
    """One reagent that a recipe uses, and how many."""

    reagent: Ref
    quantity: int


class ItemRecipe(Model):
    """What a recipe item makes, and the reagents it uses."""

    item: ItemPreview
    reagents: tuple[ItemReagent, ...]
    reagents_display_string: str


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
    limit_category: str | None = None
    name_description: ItemStatDisplay | None = None
    description: str | None = None
    armor: ItemArmor | None = None
    shield_block: ItemArmor | None = None
    weapon: ItemWeapon | None = None
    stats: tuple[ItemStat, ...] = ()
    spells: tuple[ItemPreviewSpell, ...] = ()
    requirements: ItemRequirements | None = None
    durability: ItemDisplayValue | None = None
    charges: ItemDisplayValue | None = None
    container_slots: ItemDisplayValue | None = None
    expiration_time_left: ItemDisplayValue | None = None
    level: ItemDisplayValue | None = None
    sell_price: ItemSellPrice | None = None
    set_: ItemPreviewSet | None = field(name="set", default=None)
    recipe: ItemRecipe | None = None
    item_starts_quest: ItemStartsQuest | None = None
    crafting_reagent: str | None = None
    toy: str | None = None
    bonus_list: tuple[int, ...] = ()
    context: int | None = None
    is_subclass_hidden: bool = False


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
    preview_item: ItemPreview
    description: str | None = None
    appearances: tuple[IdRef, ...] = ()


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
