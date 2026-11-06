"""Routes of the Playable Specialization API."""

from wow._async._resource import AsyncResource
from wow.models._common import Media
from wow.models.playable_specialization import PlayableSpecialization, PlayableSpecializationIndex

__all__ = ["AsyncPlayableSpecializations"]


class AsyncPlayableSpecializations(AsyncResource):
    """``client.playable_specializations``: class specializations such as Fury or Restoration."""

    __slots__ = ()

    async def index(self) -> PlayableSpecializationIndex:
        """List every playable specialization."""
        return await self._get("static", "/data/wow/playable-specialization/index", PlayableSpecializationIndex)

    async def get(self, spec_id: int) -> PlayableSpecialization:
        """Get one playable specialization by id."""
        return await self._get("static", f"/data/wow/playable-specialization/{spec_id}", PlayableSpecialization)

    async def media(self, spec_id: int) -> Media:
        """Get a specialization's icon."""
        return await self._get("static", f"/data/wow/media/playable-specialization/{spec_id}", Media)
