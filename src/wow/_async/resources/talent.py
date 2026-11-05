"""Routes of the Talent and Talent Tree APIs."""

from wow._async._resource import AsyncResource
from wow.models.talent import Talent, TalentIndex, TalentTree, TalentTreeIndex

__all__ = ["AsyncTalentTrees", "AsyncTalents"]


class AsyncTalents(AsyncResource):
    """``client.talents``: individual talents across every class and specialization."""

    __slots__ = ()

    async def index(self) -> TalentIndex:
        """List every talent."""
        return await self._get("static", "/data/wow/talent/index", TalentIndex)

    async def get(self, talent_id: int) -> Talent:
        """Get one talent by id."""
        return await self._get("static", f"/data/wow/talent/{talent_id}", Talent)


class AsyncTalentTrees(AsyncResource):
    """``client.talent_trees``: class and specialization talent trees."""

    __slots__ = ()

    async def index(self) -> TalentTreeIndex:
        """List every class and specialization talent tree."""
        return await self._get("static", "/data/wow/talent-tree/index", TalentTreeIndex)

    async def get(self, tree_id: int, specialization_id: int) -> TalentTree:
        """Get one specialization's talent tree by its class tree id and specialization id."""
        return await self._get(
            "static",
            f"/data/wow/talent-tree/{tree_id}/playable-specialization/{specialization_id}",
            TalentTree,
        )
