"""Routes of the Achievement API."""

from wow._async._resource import AsyncResource
from wow.models.achievement import (
    Achievement,
    AchievementCategory,
    AchievementCategoryIndex,
    AchievementIndex,
)

__all__ = ["AsyncAchievementCategories", "AsyncAchievements"]


class AsyncAchievements(AsyncResource):
    """``client.achievements``: achievements such as Explorer and Master of Alterac Valley."""

    __slots__ = ()

    async def index(self) -> AchievementIndex:
        """List every achievement."""
        return await self._get("static", "/data/wow/achievement/index", AchievementIndex)

    async def get(self, achievement_id: int) -> Achievement:
        """Get one achievement by id."""
        return await self._get("static", f"/data/wow/achievement/{achievement_id}", Achievement)


class AsyncAchievementCategories(AsyncResource):
    """``client.achievement_categories``: the groups achievements are organized into."""

    __slots__ = ()

    async def index(self) -> AchievementCategoryIndex:
        """List every achievement category."""
        return await self._get("static", "/data/wow/achievement-category/index", AchievementCategoryIndex)

    async def get(self, category_id: int) -> AchievementCategory:
        """Get one achievement category by id."""
        return await self._get("static", f"/data/wow/achievement-category/{category_id}", AchievementCategory)
