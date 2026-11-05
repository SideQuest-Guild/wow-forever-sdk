"""Routes of the Playable Class API."""

from wow._async._resource import AsyncResource
from wow.models._common import Media
from wow.models.playable_class import PlayableClass, PlayableClassIndex

__all__ = ["AsyncPlayableClasses"]


class AsyncPlayableClasses(AsyncResource):
    """``client.playable_classes``: classes such as Warrior and Mage."""

    __slots__ = ()

    async def index(self) -> PlayableClassIndex:
        """List every playable class."""
        return await self._get("static", "/data/wow/playable-class/index", PlayableClassIndex)

    async def get(self, class_id: int) -> PlayableClass:
        """Get one playable class by id."""
        return await self._get("static", f"/data/wow/playable-class/{class_id}", PlayableClass)

    async def media(self, class_id: int) -> Media:
        """Get a playable class's icon."""
        return await self._get("static", f"/data/wow/media/playable-class/{class_id}", Media)
