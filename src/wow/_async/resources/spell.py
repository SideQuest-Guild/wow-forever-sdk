"""Routes of the Spell API."""

from typing import TYPE_CHECKING

from wow._async._resource import AsyncResource
from wow.models._common import Media
from wow.models.spell import Spell, SpellSearchData
from wow.search import MAX_PAGE_SIZE

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, Sequence

    from wow.models._common import SearchPage, SearchResult
    from wow.search import FilterValue

__all__ = ["AsyncSpells"]


class AsyncSpells(AsyncResource):
    """``client.spells``: spells, such as talents and abilities."""

    __slots__ = ()

    async def get(self, spell_id: int) -> Spell:
        """Get one spell by id."""
        return await self._get("static", f"/data/wow/spell/{spell_id}", Spell)

    async def media(self, spell_id: int) -> Media:
        """Get a spell's icon."""
        return await self._get("static", f"/data/wow/media/spell/{spell_id}", Media)

    async def search(
        self,
        *,
        name: str | None = None,
        filters: Mapping[str, FilterValue] | None = None,
        order_by: str | Sequence[str] | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> SearchPage[SpellSearchData]:
        """Search spells.

        Args:
            name: Match this text in the client's locale.
            filters: Field filters, such as ``{"id": 11070}``.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page: The page to fetch, starting at 1.
            page_size: Results per page.
        """
        return await self._search(
            "static",
            "spell",
            SpellSearchData,
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
    ) -> AsyncIterator[SearchResult[SpellSearchData]]:
        """Iterate over every result across pages (Battle.net stops at 1,000).

        Args:
            name: Match this text in the client's locale.
            filters: Field filters, such as ``{"id": 11070}``.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page_size: Results per page.
        """
        return self._search_all(
            "static",
            "spell",
            SpellSearchData,
            filters=self._localized_name(name, filters),
            order_by=order_by,
            page_size=page_size,
        )
