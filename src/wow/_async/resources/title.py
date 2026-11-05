"""Routes of the Title API."""

from wow._async._resource import AsyncResource
from wow.models.title import Title, TitleIndex

__all__ = ["AsyncTitles"]


class AsyncTitles(AsyncResource):
    """``client.titles``: character titles such as Commander."""

    __slots__ = ()

    async def index(self) -> TitleIndex:
        """List every title."""
        return await self._get("static", "/data/wow/title/index", TitleIndex)

    async def get(self, title_id: int) -> Title:
        """Get one title by id."""
        return await self._get("static", f"/data/wow/title/{title_id}", Title)
