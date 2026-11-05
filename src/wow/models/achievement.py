"""Models for the Achievement API."""

from wow.models._common import Document, IdRef, Model, Ref

__all__ = [
    "Achievement",
    "AchievementCategory",
    "AchievementCategoryIndex",
    "AchievementCriteria",
    "AchievementFactionAggregate",
    "AchievementIndex",
]


class AchievementIndex(Document):
    """Every achievement."""

    achievements: tuple[Ref, ...]


class AchievementCategoryIndex(Document):
    """Every achievement category, plus the subset that are root categories."""

    categories: tuple[Ref, ...]
    root_categories: tuple[Ref, ...]


class AchievementCriteria(Model):
    """The condition that completes an achievement."""

    id: int
    description: str
    amount: int


class Achievement(Document):
    """A single achievement."""

    id: int
    name: str
    description: str
    points: int
    is_account_wide: bool
    category: Ref
    criteria: AchievementCriteria
    media: IdRef
    display_order: int
    reward_description: str | None = None


class AchievementFactionAggregate(Model):
    """Points and achievement count earned by one faction within a category."""

    quantity: int
    points: int


class AchievementCategory(Document):
    """A group of related achievements, such as a class or a zone."""

    id: int
    name: str
    is_guild_category: bool
    display_order: int
    subcategories: tuple[Ref, ...] = ()
    aggregates_by_faction: dict[str, AchievementFactionAggregate] | None = None
