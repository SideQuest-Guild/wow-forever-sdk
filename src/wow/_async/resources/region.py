"""Routes of the Region API."""

from wow._async._resource import AsyncResource
from wow.models.region import RegionIndex, RegionInfo

__all__ = ["AsyncRegions"]


class AsyncRegions(AsyncResource):
    """``client.regions``: Battle.net API regions."""

    __slots__ = ()

    async def index(self) -> RegionIndex:
        """List every region reachable from this host."""
        return await self._get("dynamic", "/data/wow/region/index", RegionIndex)

    async def get(self, region_id: int) -> RegionInfo:
        """Get one region by id."""
        return await self._get("dynamic", f"/data/wow/region/{region_id}", RegionInfo)
