"""Routes of the Creature, Creature Family and Creature Type APIs."""

from typing import TYPE_CHECKING

from wow._async._resource import AsyncResource
from wow.models._common import Media
from wow.models.creature import (
    Creature,
    CreatureFamily,
    CreatureFamilyIndex,
    CreatureSearchData,
    CreatureType,
    CreatureTypeIndex,
)
from wow.search import MAX_PAGE_SIZE

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, Sequence

    from wow.models._common import SearchPage, SearchResult
    from wow.search import FilterValue

__all__ = ["AsyncCreatureFamilies", "AsyncCreatureTypes", "AsyncCreatures"]


class AsyncCreatureFamilies(AsyncResource):
    """``client.creature_families``: pet families such as Bat and Wolf."""

    __slots__ = ()

    async def index(self) -> CreatureFamilyIndex:
        """List every creature family."""
        return await self._get("static", "/data/wow/creature-family/index", CreatureFamilyIndex)

    async def get(self, family_id: int) -> CreatureFamily:
        """Get one creature family by id."""
        return await self._get("static", f"/data/wow/creature-family/{family_id}", CreatureFamily)


class AsyncCreatureTypes(AsyncResource):
    """``client.creature_types``: creature types such as Beast and Dragonkin."""

    __slots__ = ()

    async def index(self) -> CreatureTypeIndex:
        """List every creature type."""
        return await self._get("static", "/data/wow/creature-type/index", CreatureTypeIndex)

    async def get(self, type_id: int) -> CreatureType:
        """Get one creature type by id."""
        return await self._get("static", f"/data/wow/creature-type/{type_id}", CreatureType)


class AsyncCreatures(AsyncResource):
    """``client.creatures``: creatures, Forest Spider included."""

    __slots__ = ()

    async def get(self, creature_id: int) -> Creature:
        """Get one creature by id."""
        return await self._get("static", f"/data/wow/creature/{creature_id}", Creature)

    async def display_media(self, display_id: int) -> Media:
        """Get a creature display's rendered image."""
        return await self._get("static", f"/data/wow/media/creature-display/{display_id}", Media)

    async def search(
        self,
        *,
        name: str | None = None,
        filters: Mapping[str, FilterValue] | None = None,
        order_by: str | Sequence[str] | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> SearchPage[CreatureSearchData]:
        """Search creatures.

        Args:
            name: Match this text in the client's locale.
            filters: Field filters, such as ``{"is_tameable": True}``.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page: The page to fetch, starting at 1.
            page_size: Results per page.
        """
        return await self._search(
            "static",
            "creature",
            CreatureSearchData,
            filters=self._localized_name(name, filters),
            order_by=order_by,
            page=page,
            page_size=page_size,
        )

    def search_all(
        self,
        *,
        name: str | None = None,
        filters: Mapping[str, FilterValue] | None = None,
        order_by: str | Sequence[str] | None = None,
        page_size: int = MAX_PAGE_SIZE,
    ) -> AsyncIterator[SearchResult[CreatureSearchData]]:
        """Iterate over every result across pages (Battle.net stops at 1,000).

        Args:
            name: Match this text in the client's locale.
            filters: Field filters, such as ``{"is_tameable": True}``.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page_size: Results per page.
        """
        return self._search_all(
            "static",
            "creature",
            CreatureSearchData,
            filters=self._localized_name(name, filters),
            order_by=order_by,
            page_size=page_size,
        )
