"""Routes of the Pet API."""

from wow._async._resource import AsyncResource
from wow.models.pet import Pet, PetIndex

__all__ = ["AsyncPets"]


class AsyncPets(AsyncResource):
    """``client.pets``: battle pet species."""

    __slots__ = ()

    async def index(self) -> PetIndex:
        """List every battle pet species."""
        return await self._get("static", "/data/wow/pet/index", PetIndex)

    async def get(self, pet_id: int) -> Pet:
        """Get one battle pet species by id."""
        return await self._get("static", f"/data/wow/pet/{pet_id}", Pet)
