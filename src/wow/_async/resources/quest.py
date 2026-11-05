"""Routes of the Quest API."""

from wow._async._resource import AsyncResource
from wow.models.quest import (
    Quest,
    QuestArea,
    QuestAreaIndex,
    QuestCategory,
    QuestCategoryIndex,
    QuestType,
    QuestTypeIndex,
)

__all__ = ["AsyncQuestAreas", "AsyncQuestCategories", "AsyncQuestTypes", "AsyncQuests"]


class AsyncQuests(AsyncResource):
    """``client.quests``: individual quests."""

    __slots__ = ()

    async def get(self, quest_id: int) -> Quest:
        """Get one quest by id."""
        return await self._get("static", f"/data/wow/quest/{quest_id}", Quest)


class AsyncQuestAreas(AsyncResource):
    """``client.quest_areas``: the zones quests take place in."""

    __slots__ = ()

    async def index(self) -> QuestAreaIndex:
        """List every quest area."""
        return await self._get("static", "/data/wow/quest/area/index", QuestAreaIndex)

    async def get(self, area_id: int) -> QuestArea:
        """Get one quest area and its quests by id."""
        return await self._get("static", f"/data/wow/quest/area/{area_id}", QuestArea)


class AsyncQuestCategories(AsyncResource):
    """``client.quest_categories``: quest groupings such as Epic or Seasonal."""

    __slots__ = ()

    async def index(self) -> QuestCategoryIndex:
        """List every quest category."""
        return await self._get("static", "/data/wow/quest/category/index", QuestCategoryIndex)

    async def get(self, category_id: int) -> QuestCategory:
        """Get one quest category and its quests by id."""
        return await self._get("static", f"/data/wow/quest/category/{category_id}", QuestCategory)


class AsyncQuestTypes(AsyncResource):
    """``client.quest_types``: quest kinds such as Elite, PvP or Raid."""

    __slots__ = ()

    async def index(self) -> QuestTypeIndex:
        """List every quest type."""
        return await self._get("static", "/data/wow/quest/type/index", QuestTypeIndex)

    async def get(self, type_id: int) -> QuestType:
        """Get one quest type and its quests by id."""
        return await self._get("static", f"/data/wow/quest/type/{type_id}", QuestType)
