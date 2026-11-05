"""Base class for resource namespaces such as ``client.items``."""

from typing import TYPE_CHECKING

from pydantic import BaseModel

from wow.models._common import SearchPage
from wow.search import encode_search

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Mapping, Sequence

    from wow._async._client import AsyncClient
    from wow._types import NamespaceKind
    from wow.models._common import SearchResult
    from wow.search import FilterValue

__all__ = ["AsyncResource"]


class AsyncResource:
    """A group of related routes, bound to the client that created it."""

    __slots__ = ("_client",)

    def __init__(self, client: AsyncClient) -> None:
        self._client = client

    async def _get[ModelT: BaseModel](self, namespace: NamespaceKind, path: str, model: type[ModelT]) -> ModelT:
        return await self._client._get_model(namespace, path, model)  # noqa: SLF001 - resources belong to the client

    def _localized_name(
        self, name: str | None, filters: Mapping[str, FilterValue] | None
    ) -> Mapping[str, FilterValue] | None:
        """Add a ``name.{locale}`` filter in the client's locale when ``name`` is given."""
        if name is None:
            return filters
        return {**(filters or {}), f"name.{self._client.locale}": name}

    async def _search[ModelT: BaseModel](
        self,
        namespace: NamespaceKind,
        document: str,
        model: type[ModelT],
        *,
        filters: Mapping[str, FilterValue] | None,
        order_by: str | Sequence[str] | None,
        page: int,
        page_size: int,
    ) -> SearchPage[ModelT]:
        params = encode_search(filters, order_by=order_by, page=page, page_size=page_size)
        return await self._client._get_model(  # noqa: SLF001 - resources belong to the client
            namespace, f"/data/wow/search/{document}", SearchPage[model], params
        )

    async def _search_all[ModelT: BaseModel](
        self,
        namespace: NamespaceKind,
        document: str,
        model: type[ModelT],
        *,
        filters: Mapping[str, FilterValue] | None,
        order_by: str | Sequence[str] | None,
        page_size: int,
    ) -> AsyncIterator[SearchResult[ModelT]]:
        page = 1
        while True:
            results = await self._search(
                namespace, document, model, filters=filters, order_by=order_by, page=page, page_size=page_size
            )
            for result in results.results:
                yield result
            if page >= results.page_count:
                return
            page += 1
