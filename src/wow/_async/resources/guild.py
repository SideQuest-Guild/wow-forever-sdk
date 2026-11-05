"""Routes of the Guild API."""

from urllib.parse import quote

from wow._async._resource import AsyncResource
from wow.models.guild import Guild, GuildRoster

__all__ = ["AsyncGuilds"]


def _path(slug: str, document: str = "") -> str:
    return f"/data/wow/guild/{quote(slug.lower(), safe='')}{document}"


class AsyncGuilds(AsyncResource):
    """``client.guilds``: any guild and its roster. An app token is enough.

    Each method takes the guild's slug, such as ``sidequest``: its name in lowercase, with spaces as hyphens.
    """

    __slots__ = ()

    async def get(self, slug: str) -> Guild:
        """Get a guild's faction, ruleset and size."""
        return await self._get("profile", _path(slug), Guild)

    async def roster(self, slug: str) -> GuildRoster:
        """Get every member of a guild, with their rank, level, class and race."""
        return await self._get("profile", _path(slug, "/roster"), GuildRoster)
