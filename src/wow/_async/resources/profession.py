"""Routes of the Profession API."""

from wow._async._resource import AsyncResource
from wow.models.profession import Profession, ProfessionIndex

__all__ = ["AsyncProfessions"]


class AsyncProfessions(AsyncResource):
    """``client.professions``: professions such as Tailoring and Cooking."""

    __slots__ = ()

    async def index(self) -> ProfessionIndex:
        """List every profession."""
        return await self._get("static", "/data/wow/profession/index", ProfessionIndex)

    async def get(self, profession_id: int) -> Profession:
        """Get one profession by id."""
        return await self._get("static", f"/data/wow/profession/{profession_id}", Profession)
