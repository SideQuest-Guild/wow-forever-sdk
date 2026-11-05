"""Routes of the Item, Item Class and Item Set APIs."""

from typing import TYPE_CHECKING

from wow._async._resource import AsyncResource
from wow.models._common import Media
from wow.models.item import Item, ItemClass, ItemClassIndex, ItemSearchData, ItemSet, ItemSetIndex
from wow.search import MAX_PAGE_SIZE

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, Sequence

    from wow.models._common import SearchPage, SearchResult
    from wow.search import FilterValue

__all__ = ["AsyncItemClasses", "AsyncItemSets", "AsyncItems"]


class AsyncItems(AsyncResource):
    """``client.items``: items."""

    __slots__ = ()

    async def get(self, item_id: int) -> Item:
        """Get one item by id."""
        return await self._get("static", f"/data/wow/item/{item_id}", Item)

    async def media(self, item_id: int) -> Media:
        """Get an item's icon."""
        return await self._get("static", f"/data/wow/media/item/{item_id}", Media)

    async def search(
        self,
        *,
        name: str | None = None,
        filters: Mapping[str, FilterValue] | None = None,
        order_by: str | Sequence[str] | None = None,
        page: int = 1,
        page_size: int = 100,
    ) -> SearchPage[ItemSearchData]:
        """Search items.

        Args:
            name: Match this text in the client's locale.
            filters: Field filters, such as ``{"item_class.id": 2}``.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page: The page to fetch, starting at 1.
            page_size: Results per page.
        """
        return await self._search(
            "static",
            "item",
            ItemSearchData,
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
    ) -> AsyncIterator[SearchResult[ItemSearchData]]:
        """Iterate over every result across pages (Battle.net stops at 1,000).

        Args:
            name: Match this text in the client's locale.
            filters: Field filters, such as ``{"item_class.id": 2}``.
            order_by: Field name(s) to sort by, each optionally suffixed ``:desc``.
            page_size: Results per page.
        """
        return self._search_all(
            "static",
            "item",
            ItemSearchData,
            filters=self._localized_name(name, filters),
            order_by=order_by,
            page_size=page_size,
        )


class AsyncItemClasses(AsyncResource):
    """``client.item_classes``: item classes such as Weapon and Consumable."""

    __slots__ = ()

    async def index(self) -> ItemClassIndex:
        """List every item class."""
        return await self._get("static", "/data/wow/item-class/index", ItemClassIndex)

    async def get(self, class_id: int) -> ItemClass:
        """Get one item class by id."""
        return await self._get("static", f"/data/wow/item-class/{class_id}", ItemClass)


class AsyncItemSets(AsyncResource):
    """``client.item_sets``: equipment sets."""

    __slots__ = ()

    async def index(self) -> ItemSetIndex:
        """List every item set."""
        return await self._get("static", "/data/wow/item-set/index", ItemSetIndex)

    async def get(self, set_id: int) -> ItemSet:
        """Get one item set by id."""
        return await self._get("static", f"/data/wow/item-set/{set_id}", ItemSet)
