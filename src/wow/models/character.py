"""Models for the Character Profile API.

Forever characters have no realm. A character's address is its ``name-surname`` slug, such as
``/profile/wow/character/psyence-spiritbound``, and an app token can read any character. Battle.net has no search for
characters: you look one up by its exact name and surname.
"""

from msgspec import field

from wow.models._common import Document, IdName, IdRef, Link, Model, Ref, TypedName
from wow.models.guild import GuildRef
from wow.models.item import ItemPreview

__all__ = [
    "AchievementCategoryProgress",
    "AchievementEvent",
    "CharacterAchievement",
    "CharacterAchievementStatistics",
    "CharacterAchievements",
    "CharacterCollections",
    "CharacterCompletedQuests",
    "CharacterEquipment",
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
    "ItemEnchantment",
    "LearnedSpecialization",
    "LearnedTalent",
    "LearnedTalentTooltip",
    "ProfessionTierProgress",
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


class CharacterPvpSummary(Document):
    """A character's lifetime honorable kills and PvP rank."""

    character: CharacterRef
    honorable_kills: int
    pvp_rank: int


class EnchantmentSlot(Model):
    """Where an enchantment sits on an item.

    A permanent enchant carries ``type`` ``PERMANENT``. A temporary one, such as a weapon imbue, carries only an id.
    """

    id: int
    type: str | None = None


class ItemEnchantment(Model):
    """An enchantment on an equipped item, and the item that applied it."""

    enchantment_id: int
    display_string: str
    enchantment_slot: EnchantmentSlot
    source_item: Ref


class EquippedItem(ItemPreview, kw_only=True):
    """An item a character wears: the item's tooltip plus its slot and enchantments."""

    slot: TypedName
    quantity: int | None = None
    enchantments: tuple[ItemEnchantment, ...] = ()


class CharacterEquipment(Document):
    """Every item a character wears."""

    character: CharacterRef
    equipped_items: tuple[EquippedItem, ...] = ()


class StatValue(Model):
    """A primary stat, armor or a resistance: its value before and after gear and buffs."""

    base: int
    effective: int


class CombatRating(Model):
    """A secondary stat's rating, such as speed or avoidance."""

    rating_bonus: float
    rating_normalized: int


class CombatRatingValue(CombatRating):
    """A secondary stat's rating and the percentage it gives, such as crit or dodge."""

    value: float


class CharacterStatistics(Document):
    """A character's stats sheet, as the character pane shows it."""

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
    spell_power: int
    spell_penetration: int
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


class CharacterPets(Document):
    """A character's battle pets, and how many battle slots it has unlocked."""

    unlocked_battle_pet_slots: int
    pets: tuple[CollectedPet, ...] = ()


class CollectedToy(Model):
    """A toy a character has collected."""

    toy: Ref


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
