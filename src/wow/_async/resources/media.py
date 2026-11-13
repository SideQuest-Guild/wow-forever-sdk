"""Routes of the Media Search API."""

from typing import TYPE_CHECKING

from wow._async._resource import AsyncResource
from wow.models.media import MediaSearchData
from wow.search import MAX_PAGE_SIZE

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, Sequence

    from wow.models._common import SearchPage, SearchResult
    from wow.search import FilterValue

__all__ = ["AsyncMedia"]


class AsyncMedia(AsyncResource):
    """``client.media``: media documents across every static type, searchable by tag."""

    __slots__ = ()

    def _tag_filter(
        self, tags: str | Sequence[str] | None, filters: Mapping[str, FilterValue] | None
    ) -> Mapping[str, FilterValue] | None:
        """Add a ``tags`` filter, such as ``item`` or ``spell``, when ``tags`` is given."""
        if tags is None:
            return filters
        return {**(filters or {}), "tags": tags}

    async def search(
        self,
        *,
        tags: str | Sequence[str] | None = None,
        filters: Mapping[str, FilterValue] | None = None,
        order_by: str | Sequence[str] | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> SearchPage[MediaSearchData]:
        """Search media documents.

        Args:
            tags: Match one or more media kinds, such as ``"item"`` or ``"spell"``.
            filters: Additional field filters.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page: The page to fetch, starting at 1.
            page_size: Results per page.
        """
        return await self._search(
            "static",
            "media",
            MediaSearchData,
            filters=self._tag_filter(tags, filters),
            order_by=order_by,
            page=page,
            page_size=page_size,
        )

    def search_all(
        self,
        *,
        tags: str | Sequence[str] | None = None,
        filters: Mapping[str, FilterValue] | None = None,
        order_by: str | Sequence[str] | None = None,
        page_size: int = MAX_PAGE_SIZE,
    ) -> AsyncIterator[SearchResult[MediaSearchData]]:
        """Iterate over every result across pages (Battle.net stops at 1,000).

        Args:
            tags: Match one or more media kinds, such as ``"item"`` or ``"spell"``.
            filters: Additional field filters.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page_size: Results per page.
        """
        return self._search_all(
            "static",
            "media",
            MediaSearchData,
            filters=self._tag_filter(tags, filters),
            order_by=order_by,
            page_size=page_size,
        )
