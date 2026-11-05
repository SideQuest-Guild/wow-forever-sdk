"""Routes of the Creature Family and Creature Type APIs."""

from wow._async._resource import AsyncResource
from wow.models.creature import CreatureFamily, CreatureFamilyIndex, CreatureType, CreatureTypeIndex

__all__ = ["AsyncCreatureFamilies", "AsyncCreatureTypes"]


class AsyncCreatureFamilies(AsyncResource):
    """``client.creature_families``: pet families such as Bat and Wolf."""

    __slots__ = ()

    async def index(self) -> CreatureFamilyIndex:
        """List every creature family."""
        return await self._get("static", "/data/wow/creature-family/index", CreatureFamilyIndex)

    async def get(self, family_id: int) -> CreatureFamily:
        """Get one creature family by id."""
        return await self._get("static", f"/data/wow/creature-family/{family_id}", CreatureFamily)


class AsyncCreatureTypes(AsyncResource):
    """``client.creature_types``: creature types such as Beast and Dragonkin."""

    __slots__ = ()

    async def index(self) -> CreatureTypeIndex:
        """List every creature type."""
        return await self._get("static", "/data/wow/creature-type/index", CreatureTypeIndex)

    async def get(self, type_id: int) -> CreatureType:
        """Get one creature type by id."""
        return await self._get("static", f"/data/wow/creature-type/{type_id}", CreatureType)
