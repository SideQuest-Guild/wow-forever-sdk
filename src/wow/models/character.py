"""Models for the Character Profile API.

Forever characters have no realm. A character's address is its ``name-surname`` slug, such as
``/profile/wow/character/psyence-spiritbound``, and an app token can read any character. Battle.net has no search for
characters: you look one up by its exact name and surname.
"""

from msgspec import field

from wow.models._common import Document, IdName, IdRef, Link, Model, Ref, TypedName
from wow.models.guild import GuildRef
from wow.models.item import ItemPreview, ItemPreviewSet

__all__ = [
    "AchievementCategoryProgress",
    "AchievementEvent",
    "AppearanceCustomization",
    "AppearanceCustomizationChoice",
    "AppearanceCustomizationOption",
    "AppearanceItem",
    "CharacterAchievement",
    "CharacterAchievementStatistics",
    "CharacterAchievements",
    "CharacterAppearance",
    "CharacterCollections",
    "CharacterCompletedQuests",
    "CharacterEquipment",
    "CharacterHunterPet",
    "CharacterHunterPets",
    "CharacterMedia",
    "CharacterMediaAsset",
    "CharacterMounts",
    "CharacterPets",
    "CharacterProfession",
    "CharacterProfessions",
    "CharacterProfile",
    "CharacterPvpSummary",
    "CharacterQuests",
    "CharacterRef",
    "CharacterReputation",
    "CharacterReputations",
    "CharacterSpecializations",
    "CharacterStatistics",
    "CharacterStatus",
    "CharacterToys",
    "CharacterTransmogs",
    "CollectedMount",
    "CollectedPet",
    "CollectedPetStats",
    "CollectedToy",
    "CombatRating",
    "CombatRatingValue",
    "CriteriaProgress",
    "EnchantmentSlot",
    "EquippedItem",
    "GuildCrest",
    "GuildCrestBackground",
    "GuildCrestColor",
    "GuildCrestColorRgba",
    "GuildCrestPart",
    "ItemEnchantment",
    "ItemTransmog",
    "LearnedSpecialization",
    "LearnedTalent",
    "LearnedTalentTooltip",
    "ProfessionTierProgress",
    "PvpMapStatistics",
    "PvpMatchStatistics",
    "ReputationStanding",
    "SpecializationGroup",
    "StatValue",
    "Statistic",
    "StatisticCategory",
    "TransmogSlot",
]


class CharacterRef(Model):
    """The character a profile document belongs to."""

    key: Link
    id: int
    name: str
    surname: str
    slug: str


class CharacterProfile(Document):
    """A character's summary, with links to every other part of its profile.

    Attributes:
        name_search: The full name as Battle.net indexes it, such as ``Psyence Spiritbound``.
        last_login_timestamp: When the character last logged out, in Unix milliseconds. Battle.net updates a profile
            when its character logs out.
        is_remix: Whether this is a Remix character.
        guild: The character's guild, or ``None`` if it has none.
        hunter_pets: A link to a hunter's pets. Only hunters have it.
    """

    id: int
    name: str
    surname: str
    name_search: str
    gender: TypedName
    faction: TypedName
    race: Ref
    character_class: Ref
    ruleset: Ref
    level: int
    experience: int
    achievement_points: int
    average_item_level: int
    equipped_item_level: int
    last_login_timestamp: int
    is_remix: bool
    achievements: Link
    achievements_statistics: Link
    appearance: Link
    collections: Link
    encounters: Link
    equipment: Link
    media: Link
    mythic_keystone_profile: Link
    professions: Link
    pvp_summary: Link
    quests: Link
    reputations: Link
    specializations: Link
    statistics: Link
    titles: Link
    guild: GuildRef | None = None
    hunter_pets: Link | None = None


class CharacterStatus(Document):
    """Whether a character still exists. ``id`` changes if the character was deleted and its name reused."""

    id: int
    is_valid: bool


class CharacterMediaAsset(Model):
    """One rendered image of a character, such as ``avatar`` or ``main-raw``."""

    key: str
    value: str


class CharacterMedia(Document):
    """A character's rendered images. Battle.net renders them some time after the character first logs out."""

    character: CharacterRef
    assets: tuple[CharacterMediaAsset, ...] = ()


class PvpMatchStatistics(Model):
    """How many battlegrounds a character played, won and lost on one map."""

    played: int
    won: int
    lost: int


class PvpMapStatistics(Model):
    """A character's record on one battleground map."""

    world_map: IdName
    match_statistics: PvpMatchStatistics


class CharacterPvpSummary(Document):
    """A character's lifetime honorable kills and PvP rank, and their record on each battleground they have played."""

    character: CharacterRef
    honorable_kills: int
    pvp_rank: int
    pvp_map_statistics: tuple[PvpMapStatistics, ...] = ()


class EnchantmentSlot(Model):
    """Where an enchantment sits on an item.

    A permanent enchant carries ``type`` ``PERMANENT``. A temporary one, such as a weapon imbue, carries only an id.
    """

    id: int
    type: str | None = None


class ItemEnchantment(Model):
    """An enchantment on an equipped item, and the item that applied it.

    A spell's imbue, such as a shaman's Rockbiter, has no ``source_item``.
    """

    enchantment_id: int
    display_string: str
    enchantment_slot: EnchantmentSlot
    source_item: Ref | None = None


class ItemTransmog(Model):
    """The appearance an equipped item is transmogrified to.

    Shoulders can show a different appearance on each side; ``second_item`` is the other side's.
    """

    item: Ref
    display_string: str
    item_modified_appearance_id: int
    second_item: Ref | None = None
    second_item_modified_appearance_id: int | None = None


class EquippedItem(ItemPreview, kw_only=True):
    """An item a character wears: the item's tooltip plus its slot, enchantments and transmog."""

    slot: TypedName
    quantity: int | None = None
    enchantments: tuple[ItemEnchantment, ...] = ()
    transmog: ItemTransmog | None = None


class CharacterEquipment(Document):
    """Every item a character wears, and each item set it wears pieces of with the bonuses those pieces give."""

    character: CharacterRef
    equipped_items: tuple[EquippedItem, ...] = ()
    equipped_item_sets: tuple[ItemPreviewSet, ...] = ()


class StatValue(Model):
    """A primary stat, armor or a resistance: its value before and after gear and buffs."""

    base: int
    effective: int


class CombatRating(Model):
    """A secondary stat's rating, such as speed or avoidance.

    ``value`` is the percentage the rating gives. Sheets Battle.net wrote before its 2026-11-05 update leave it out
    for speed and avoidance.
    """

    rating_bonus: float
    rating_normalized: int
    value: float | None = None


class CombatRatingValue(CombatRating):
    """A secondary stat's rating and the percentage it gives, such as crit or dodge."""

    value: float


class CharacterStatistics(Document, kw_only=True):
    """A character's stats sheet, as the character pane shows it.

    Battle.net writes the sheet when the character logs out. Sheets written before its 2026-11-05 update lack the
    hit, expertise, defense, ranged and movement stats, so those are ``None`` until the character plays again.
    """

    character: CharacterRef
    health: int
    power: int
    power_type: Ref
    strength: StatValue
    agility: StatValue
    intellect: StatValue
    stamina: StatValue
    spirit: StatValue
    armor: StatValue
    bonus_armor: int
    attack_power: int
    ranged_attack_power: int | None = None
    spell_power: int
    spell_penetration: int
    spell_healing: int | None = None
    mana_regen: float
    mana_regen_combat: float
    main_hand_damage_min: float
    main_hand_damage_max: float
    main_hand_speed: float
    main_hand_dps: float
    off_hand_damage_min: float
    off_hand_damage_max: float
    off_hand_speed: float
    off_hand_dps: float
    ranged_damage_min: float | None = None
    ranged_damage_max: float | None = None
    melee_hit: CombatRatingValue | None = None
    ranged_hit: CombatRatingValue | None = None
    spell_hit: CombatRatingValue | None = None
    off_hand_hit: CombatRatingValue | None = None
    expertise: float | None = None
    off_hand_expertise: float | None = None
    armor_penetration: float | None = None
    defense: StatValue | None = None
    melee_crit: CombatRatingValue
    melee_haste: CombatRatingValue
    ranged_crit: CombatRatingValue
    ranged_haste: CombatRatingValue
    spell_crit: CombatRatingValue
    spell_haste: CombatRatingValue
    mastery: CombatRatingValue
    lifesteal: CombatRatingValue
    dodge: CombatRatingValue
    parry: CombatRatingValue
    block: CombatRatingValue
    speed: CombatRating
    avoidance: CombatRating
    movement_speed: float | None = None
    versatility: float
    versatility_damage_done_bonus: float
    versatility_healing_done_bonus: float
    versatility_damage_taken_bonus: float
    fire_resistance: StatValue
    frost_resistance: StatValue
    nature_resistance: StatValue
    shadow_resistance: StatValue
    arcane_resistance: StatValue


class LearnedTalentTooltip(Model):
    """The tooltip of a talent rank a character has learned."""

    spell: IdName
    description: str
    cast_time: str
    power_cost: str | None = None
    cooldown: str | None = None
    range_: str | None = field(name="range", default=None)


class LearnedTalent(Model):
    """A talent a character has put points into, and the rank it reached."""

    talent: IdName
    talent_rank: int
    spell_tooltip: LearnedTalentTooltip


class LearnedSpecialization(Model):
    """The talents a character has learned in one specialization's tree."""

    specialization: Ref
    specialization_name: str
    spent_points: int
    talents: tuple[LearnedTalent, ...] = ()


class SpecializationGroup(Model):
    """One talent loadout. ``is_active`` marks the one the character uses now."""

    is_active: bool
    specializations: tuple[LearnedSpecialization, ...] = ()


class CharacterSpecializations(Document):
    """A character's talent loadouts."""

    character: CharacterRef
    specialization_groups: tuple[SpecializationGroup, ...] = ()


class ProfessionTierProgress(Model):
    """A character's skill in one profession tier, and the recipes it knows there."""

    tier: IdName
    skill_points: int
    max_skill_points: int
    known_recipes: tuple[Ref, ...] = ()


class CharacterProfession(Model):
    """A profession a character has learned."""

    profession: Ref
    tiers: tuple[ProfessionTierProgress, ...] = ()


class CharacterProfessions(Document):
    """A character's primary professions, such as Mining, and secondary ones, such as Cooking."""

    character: CharacterRef
    primaries: tuple[CharacterProfession, ...] = ()
    secondaries: tuple[CharacterProfession, ...] = ()


class ReputationStanding(Model):
    """A character's standing with one faction.

    Attributes:
        raw: Reputation earned in total.
        value: Progress within the current tier, out of ``max``.
        tier: The tier's position, counting up from Hated.
        name: The tier's name, such as ``Honored``.
    """

    raw: int
    value: int
    max: int
    tier: int
    name: str


class CharacterReputation(Model):
    """A character's standing with one faction."""

    faction: Ref
    standing: ReputationStanding


class CharacterReputations(Document):
    """Every faction a character has met."""

    character: CharacterRef
    reputations: tuple[CharacterReputation, ...] = ()


class CriteriaProgress(Model):
    """A character's progress on an achievement's criteria, or on one part of them."""

    id: int
    is_completed: bool
    amount: int | None = None
    child_criteria: tuple[CriteriaProgress, ...] = ()


class CharacterAchievement(Model):
    """An achievement a character has made progress on. ``completed_timestamp`` is set once it is earned."""

    id: int
    achievement: Ref
    criteria: CriteriaProgress
    completed_timestamp: int | None = None


class AchievementCategoryProgress(Model):
    """How many achievements, and points, a character has earned in one category."""

    category: Ref
    quantity: int
    points: int


class AchievementEvent(Model):
    """An achievement a character earned recently, and when, in Unix milliseconds."""

    achievement: Ref
    timestamp: int


class CharacterAchievements(Document):
    """A character's achievements, points and recent achievement events."""

    character: CharacterRef
    total_quantity: int
    total_points: int
    statistics: Link
    achievements: tuple[CharacterAchievement, ...] = ()
    category_progress: tuple[AchievementCategoryProgress, ...] = ()
    recent_events: tuple[AchievementEvent, ...] = ()


class Statistic(Model):
    """One counter on the statistics pane, such as Total kills."""

    id: int
    name: str
    quantity: float
    last_updated_timestamp: int
    description: str | None = None


class StatisticCategory(Model):
    """A group of statistics, such as Kills, with its sub-groups."""

    id: int
    name: str
    statistics: tuple[Statistic, ...] = ()
    sub_categories: tuple[StatisticCategory, ...] = ()


class CharacterAchievementStatistics(Document):
    """A character's statistics pane: kills, deaths, consumables and more."""

    character: CharacterRef
    categories: tuple[StatisticCategory, ...] = ()


class CharacterCollections(Document):
    """Links to every collection a character has."""

    character: CharacterRef
    mounts: Link
    pets: Link
    toys: Link
    heirlooms: Link
    transmogs: Link


class CollectedMount(Model):
    """A mount a character has collected."""

    mount: Ref
    is_useable: bool
    is_favorite: bool = False


class CharacterMounts(Document):
    """A character's mounts."""

    mounts: tuple[CollectedMount, ...] = ()


class CollectedPetStats(Model):
    """A collected battle pet's breed and stats."""

    breed_id: int
    health: int
    power: int
    speed: int


class CollectedPet(Model):
    """A battle pet a character has collected. ``id`` names this pet, ``species`` its kind."""

    id: int
    species: Ref
    level: int
    quality: TypedName
    stats: CollectedPetStats
    creature_display: IdRef
    is_favorite: bool = False


class CharacterPets(Document):
    """A character's battle pets, and how many battle slots it has unlocked."""

    unlocked_battle_pet_slots: int
    pets: tuple[CollectedPet, ...] = ()


class CollectedToy(Model):
    """A toy a character has collected."""

    toy: Ref
    is_favorite: bool = False


class CharacterToys(Document):
    """A character's toys."""

    toys: tuple[CollectedToy, ...] = ()


class TransmogSlot(Model):
    """The appearances a character has collected for one equipment slot."""

    slot: TypedName
    appearances: tuple[IdRef, ...] = ()


class CharacterTransmogs(Document):
    """A character's collected appearances, by slot."""

    slots: tuple[TransmogSlot, ...] = ()


class CharacterQuests(Document):
    """The quests a character has in its quest log, and a link to the ones it has completed."""

    character: CharacterRef
    completed: Link
    in_progress: tuple[Ref, ...] = ()


class CharacterCompletedQuests(Document):
    """Every quest a character has completed."""

    character: CharacterRef
    quests: tuple[Ref, ...] = ()


class GuildCrestColorRgba(Model):
    """The RGBA color a crest color renders as. Only some crest colors carry one."""

    r: int
    g: int
    b: int
    a: float


class GuildCrestColor(Model):
    """A crest color: its catalog id, and its RGBA value when Battle.net sends one."""

    id: int
    rgba: GuildCrestColorRgba | None = None


class GuildCrestPart(Model):
    """A guild crest's border or its emblem: the catalog id, its color and its rendered media."""

    id: int
    color: GuildCrestColor
    media: IdRef


class GuildCrestBackground(Model):
    """A guild crest's background color."""

    color: GuildCrestColor


class GuildCrest(Model):
    """A character's guild's crest, as its tabard renders it."""

    background: GuildCrestBackground
    border: GuildCrestPart
    emblem: GuildCrestPart


class AppearanceCustomizationOption(Model):
    """A customization category, such as Hair Style."""

    id: int
    name: str


class AppearanceCustomizationChoice(Model):
    """A customization choice a character made. Some choices, such as a hairstyle, carry a name."""

    id: int
    display_order: int
    name: str | None = None


class AppearanceCustomization(Model):
    """One customization slot and the choice a character made in it."""

    option: AppearanceCustomizationOption
    choice: AppearanceCustomizationChoice


class AppearanceItem(Model):
    """One item contributing to a character's rendered appearance.

    ``item_appearance_modifier_id`` and ``subclass`` only appear for some slots, such as cloaks. A split-slot item,
    such as shoulders transmogrified to two different appearances, also carries a ``secondary_*`` set for the other
    side.
    """

    id: int
    slot: TypedName
    enchant: int
    internal_slot_id: int
    item_appearance_modifier_id: int | None = None
    subclass: int | None = None
    secondary_id: int | None = None
    secondary_item_appearance_modifier_id: int | None = None
    secondary_subclass: int | None = None


class CharacterAppearance(Document):
    """A character's rendered appearance: its gear, customizations and guild crest.

    ``guild_crest`` is absent for a guildless character.
    """

    character: CharacterRef
    playable_race: Ref
    playable_class: Ref
    gender: TypedName
    faction: TypedName
    items: tuple[AppearanceItem, ...] = ()
    customizations: tuple[AppearanceCustomization, ...] = ()
    guild_crest: GuildCrest | None = None


class CharacterHunterPet(Model):
    """One tamed pet in a hunter's stable.

    ``is_active`` marks the pet in the hunter's active pet slot; ``is_summoned`` marks the one currently summoned.
    """

    name: str
    level: int
    slot: int
    creature: Ref
    creature_display: IdRef
    is_active: bool = False
    is_summoned: bool = False


class CharacterHunterPets(Document):
    """A hunter's tamed pets.

    Only hunters have this document; one with no pets currently tamed answers with no ``hunter_pets`` at all.
    """

    character: CharacterRef
    hunter_pets: tuple[CharacterHunterPet, ...] = ()
