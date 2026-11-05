"""Routes of the Toy API."""

from wow._async._resource import AsyncResource
from wow.models.toy import Toy, ToyIndex

__all__ = ["AsyncToys"]


class AsyncToys(AsyncResource):
    """``client.toys``: toy-box toys."""

    __slots__ = ()

    async def index(self) -> ToyIndex:
        """List every toy."""
        return await self._get("static", "/data/wow/toy/index", ToyIndex)

    async def get(self, toy_id: int) -> Toy:
        """Get one toy by id."""
        return await self._get("static", f"/data/wow/toy/{toy_id}", Toy)
