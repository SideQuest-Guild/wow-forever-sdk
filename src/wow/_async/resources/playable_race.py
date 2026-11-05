"""Routes of the Playable Race API."""

from wow._async._resource import AsyncResource
from wow.models.playable_race import PlayableRace, PlayableRaceIndex

__all__ = ["AsyncPlayableRaces"]


class AsyncPlayableRaces(AsyncResource):
    """``client.playable_races``: races such as Human and Orc."""

    __slots__ = ()

    async def index(self) -> PlayableRaceIndex:
        """List every playable race."""
        return await self._get("static", "/data/wow/playable-race/index", PlayableRaceIndex)

    async def get(self, race_id: int) -> PlayableRace:
        """Get one playable race by id."""
        return await self._get("static", f"/data/wow/playable-race/{race_id}", PlayableRace)
