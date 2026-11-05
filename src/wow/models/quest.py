"""Models for the Quest API."""

from wow.models._common import Document, Model, Ref, TypedName

__all__ = [
    "Quest",
    "QuestArea",
    "QuestAreaIndex",
    "QuestCategory",
    "QuestCategoryIndex",
    "QuestCondition",
    "QuestMoneyReward",
    "QuestMoneyUnits",
    "QuestReputationRequirement",
    "QuestRequirements",
    "QuestReward",
    "QuestRewardItem",
    "QuestRewardItems",
    "QuestRewards",
    "QuestType",
    "QuestTypeIndex",
]


class QuestCondition(Model):
    """A rule about other quests: one ``target`` quest, or an ``operator`` (such as ``AND``) over more conditions."""

    operator: TypedName | None = None
    conditions: tuple[QuestCondition, ...] = ()
    target: Ref | None = None
    must_be_incomplete: bool = False


class QuestReputationRequirement(Model):
    """A reputation range a character must be in, in reputation points."""

    faction: Ref
    min_reputation: int | None = None
    max_reputation: int | None = None


class QuestRequirements(Model):
    """A quest's prerequisites. Battle.net sends an empty object for quests with none."""

    faction: TypedName | None = None
    classes: tuple[Ref, ...] = ()
    races: tuple[Ref, ...] = ()
    reputations: tuple[QuestReputationRequirement, ...] = ()
    quests: QuestCondition | None = None
    min_character_level: int | None = None
    max_character_level: int | None = None


class QuestRewardItem(Model):
    """One item reward."""

    item: Ref


class QuestRewardItems(Model):
    """The item rewards for completing a quest: items given, and items to pick one from."""

    items: tuple[QuestRewardItem, ...] = ()
    choice_of: tuple[QuestRewardItem, ...] = ()


class QuestMoneyUnits(Model):
    """A copper amount broken into gold, silver and copper."""

    gold: int
    silver: int
    copper: int


class QuestMoneyReward(Model):
    """The money reward for completing a quest."""

    value: int
    units: QuestMoneyUnits


class QuestReward(Model):
    """A reputation or currency reward: the faction or currency, and the amount gained or lost."""

    reward: Ref
    value: int


class QuestRewards(Model):
    """The rewards for completing a quest."""

    experience: int | None = None
    items: QuestRewardItems | None = None
    money: QuestMoneyReward | None = None
    reputations: tuple[QuestReward, ...] = ()
    currency: tuple[QuestReward, ...] = ()
    spell: Ref | None = None
    trade_skill_spell: Ref | None = None


class QuestAreaIndex(Document):
    """Every quest area."""

    areas: tuple[Ref, ...]


class QuestArea(Document):
    """A quest area, with every quest that takes place there."""

    id: int
    area: str
    quests: tuple[Ref, ...]


class QuestCategoryIndex(Document):
    """Every quest category."""

    categories: tuple[Ref, ...]


class QuestCategory(Document):
    """A quest category, such as Epic or Seasonal, with every quest in it."""

    id: int
    category: str
    quests: tuple[Ref, ...]


class QuestTypeIndex(Document):
    """Every quest type."""

    types: tuple[Ref, ...]


class QuestType(Document):
    """A quest type, such as Elite, PvP or Raid, with every quest of that type."""

    id: int
    type: str
    quests: tuple[Ref, ...]


class Quest(Document):
    """A quest."""

    id: int
    title: str
    requirements: QuestRequirements
    rewards: QuestRewards
    description: str | None = None
    area: Ref | None = None
    category: Ref | None = None
    type: Ref | None = None
    is_repeatable: bool = False
    is_daily: bool = False
    is_weekly: bool = False
