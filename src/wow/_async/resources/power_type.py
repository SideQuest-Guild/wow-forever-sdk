"""Routes of the Power Type API."""

from wow._async._resource import AsyncResource
from wow.models.power_type import PowerType, PowerTypeIndex

__all__ = ["AsyncPowerTypes"]


class AsyncPowerTypes(AsyncResource):
    """``client.power_types``: power types such as Mana and Rage."""

    __slots__ = ()

    async def index(self) -> PowerTypeIndex:
        """List every power type."""
        return await self._get("static", "/data/wow/power-type/index", PowerTypeIndex)

    async def get(self, power_type_id: int) -> PowerType:
        """Get one power type by id."""
        return await self._get("static", f"/data/wow/power-type/{power_type_id}", PowerType)
