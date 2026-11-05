"""Models for the Achievement API."""

from wow.models._common import Document, IdRef, Model, Ref, TypedName

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
    """The condition that completes an achievement, or one part of it.

    A criteria with ``child_criteria`` completes when its ``operator`` (such as ``AND``) holds over its children.
    """

    id: int
    description: str | None
    amount: int
    operator: TypedName | None = None
    child_criteria: tuple[AchievementCriteria, ...] = ()
    achievement: Ref | None = None
    faction: TypedName | None = None
    show_progress_bar: bool = False


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
    achievements: tuple[Ref, ...] = ()
    parent_category: Ref | None = None
    aggregates_by_faction: dict[str, AchievementFactionAggregate] | None = None
