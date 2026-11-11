"""Routes of the Guild Crest API."""

from wow._async._resource import AsyncResource
from wow.models._common import Media
from wow.models.guild_crest import GuildCrestComponentsIndex

__all__ = ["AsyncGuildCrests"]


class AsyncGuildCrests(AsyncResource):
    """``client.guild_crests``: the emblems, borders and colors guild crests use."""

    __slots__ = ()

    async def index(self) -> GuildCrestComponentsIndex:
        """List every selectable emblem, border and color."""
        return await self._get("static", "/data/wow/guild-crest/index", GuildCrestComponentsIndex)

    async def border_media(self, border_id: int) -> Media:
        """Get a crest border's rendered image."""
        return await self._get("static", f"/data/wow/media/guild-crest/border/{border_id}", Media)

    async def emblem_media(self, emblem_id: int) -> Media:
        """Get a crest emblem's rendered image."""
        return await self._get("static", f"/data/wow/media/guild-crest/emblem/{emblem_id}", Media)
