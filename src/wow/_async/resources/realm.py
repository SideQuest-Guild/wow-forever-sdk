"""Routes of the Realm API.

Realm has not been recorded live; see :mod:`wow.models.realm` for sourcing.
"""

from typing import TYPE_CHECKING
from urllib.parse import quote

from wow._async._resource import AsyncResource
from wow.models.realm import Realm, RealmIndex, RealmSearchData
from wow.search import MAX_PAGE_SIZE

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, Sequence

    from wow.models._common import SearchPage, SearchResult
    from wow.search import FilterValue

__all__ = ["AsyncRealms"]


class AsyncRealms(AsyncResource):
    """``client.realms``: WoW Forever realms. Shape from community probing; Blizzard has not documented it."""

    __slots__ = ()

    async def index(self) -> RealmIndex:
        """List every realm."""
        return await self._get("dynamic", "/data/wow/realm/index", RealmIndex)

    async def get(self, realm_slug: str) -> Realm:
        """Get one realm by its slug or id."""
        return await self._get("dynamic", f"/data/wow/realm/{quote(realm_slug, safe='')}", Realm)

    async def search(
        self,
        *,
        name: str | None = None,
        filters: Mapping[str, FilterValue] | None = None,
        order_by: str | Sequence[str] | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> SearchPage[RealmSearchData]:
        """Search realms.

        Args:
            name: Match this name in the client's locale.
            filters: Additional search filters.
            order_by: Field or fields to sort by.
            page: The page to fetch, starting at 1.
            page_size: Results per page.
        """
        return await self._search(
            "dynamic",
            "realm",
            RealmSearchData,
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
    ) -> AsyncIterator[SearchResult[RealmSearchData]]:
        """Iterate over every result across pages (Battle.net stops at 1,000)."""
        return self._search_all(
            "dynamic",
            "realm",
            RealmSearchData,
            filters=self._localized_name(name, filters),
            order_by=order_by,
            page_size=page_size,
        )
