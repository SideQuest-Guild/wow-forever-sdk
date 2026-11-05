"""Routes of the Mount API."""

from typing import TYPE_CHECKING

from wow._async._resource import AsyncResource
from wow.models.mount import Mount, MountIndex, MountSearchData
from wow.search import MAX_PAGE_SIZE

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, Sequence

    from wow.models._common import SearchPage, SearchResult
    from wow.search import FilterValue

__all__ = ["AsyncMounts"]


class AsyncMounts(AsyncResource):
    """``client.mounts``: mounts."""

    __slots__ = ()

    async def index(self) -> MountIndex:
        """List every mount."""
        return await self._get("static", "/data/wow/mount/index", MountIndex)

    async def get(self, mount_id: int) -> Mount:
        """Get one mount by id."""
        return await self._get("static", f"/data/wow/mount/{mount_id}", Mount)

    async def search(
        self,
        *,
        name: str | None = None,
        filters: Mapping[str, FilterValue] | None = None,
        order_by: str | Sequence[str] | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> SearchPage[MountSearchData]:
        """Search mounts.

        Args:
            name: Match this text in the client's locale.
            filters: Field filters, such as ``{"faction.type": "ALLIANCE"}``.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page: The page to fetch, starting at 1.
            page_size: Results per page.
        """
        return await self._search(
            "static",
            "mount",
            MountSearchData,
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
    ) -> AsyncIterator[SearchResult[MountSearchData]]:
        """Iterate over every result across pages (Battle.net stops at 1,000).

        Args:
            name: Match this text in the client's locale.
            filters: Field filters, such as ``{"faction.type": "ALLIANCE"}``.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page_size: Results per page.
        """
        return self._search_all(
            "static",
            "mount",
            MountSearchData,
            filters=self._localized_name(name, filters),
            order_by=order_by,
            page_size=page_size,
        )
