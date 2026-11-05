"""Models for the Quest API."""

from wow.models._common import Document, Model, Ref

__all__ = [
    "Quest",
    "QuestArea",
    "QuestAreaIndex",
    "QuestCategory",
    "QuestCategoryIndex",
    "QuestMoneyReward",
    "QuestMoneyUnits",
    "QuestRequirements",
    "QuestReward",
    "QuestRewardItem",
    "QuestRewardItems",
    "QuestRewards",
    "QuestType",
    "QuestTypeIndex",
]


class QuestRequirements(Model):
    """A quest's prerequisites. Battle.net sends an empty object for quests with none."""


class QuestRewardItem(Model):
    """One item reward."""

    item: Ref


class QuestRewardItems(Model):
    """The item rewards for completing a quest."""

    items: tuple[QuestRewardItem, ...] = ()


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
    """A reputation reward: the faction and the amount of reputation gained or lost."""

    reward: Ref
    value: int


class QuestRewards(Model):
    """The rewards for completing a quest."""

    experience: int | None = None
    items: QuestRewardItems | None = None
    money: QuestMoneyReward | None = None
    reputations: tuple[QuestReward, ...] = ()


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
    area: Ref
    description: str
    requirements: QuestRequirements
    rewards: QuestRewards
