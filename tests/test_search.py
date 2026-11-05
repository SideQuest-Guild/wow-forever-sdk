from typing import TYPE_CHECKING

import pytest

from tests.conftest import mock_route
from wow import Not, Range
from wow.search import FilterValue, encode_search

if TYPE_CHECKING:
    import respx

    from wow import Client


def encode(
    filters: dict[str, FilterValue], *, order_by: str | list[str] | None = None, page: int = 1, page_size: int = 100
) -> dict[str, str | int]:
    return encode_search(filters, order_by=order_by, page=page, page_size=page_size)


@pytest.mark.parametrize(
    ("resource", "document", "namespace"),
    [
        ("items", "item", "static-forever-us"),
        ("mounts", "mount", "static-forever-us"),
        ("realms", "realm", "dynamic-forever-us"),
    ],
)
def test_search_reads_its_document_in_the_client_locale(
    client: Client, battlenet: respx.MockRouter, resource: str, document: str, namespace: str
) -> None:
    route = mock_route(battlenet, f"/data/wow/search/{document}")
    route.respond(json={"page": 2, "pageSize": 5, "maxPageSize": 5, "pageCount": 2, "results": []})

    page = getattr(client, resource).search(
        name="Horse", filters={"id": Range(1, 10)}, order_by="id", page=2, page_size=5
    )

    assert (page.page, page.page_count, page.results) == (2, 2, ())
    assert dict(route.calls.last.request.url.params) == {
        "namespace": namespace,
        "locale": "en_US",
        "name.en_US": "Horse",
        "id": "[1,10]",
        "orderby": "id",
        "_page": "2",
        "_pageSize": "5",
    }


def test_filters_use_blizzards_query_syntax() -> None:
    params = encode(
        {
            "item_class.id": 2,
            "quality.type": ["EPIC", "LEGENDARY"],
            "required_level": Range(50, 60),
            "level": Range(max=77, inclusive=False),
            "inventory_type.type": Not("SHIELD"),
            "is_equippable": True,
        }
    )

    assert params == {
        "_page": 1,
        "_pageSize": 100,
        "item_class.id": "2",
        "quality.type": "EPIC||LEGENDARY",
        "required_level": "[50,60]",
        "level": "(,77)",
        "inventory_type.type!": "SHIELD",
        "is_equippable": "true",
    }


@pytest.mark.parametrize(("order_by", "expected"), [("id", "id"), (["level:desc", "id:asc"], "level:desc,id:asc")])
def test_order_by_accepts_one_or_many_fields(order_by: str | list[str], expected: str) -> None:
    assert encode({}, order_by=order_by)["orderby"] == expected


@pytest.mark.parametrize(
    ("page", "page_size", "message"),
    [
        (0, 100, "page must be at least 1"),
        (1, 0, "page_size must be between 1 and 1000"),
        (1, 1001, "page_size must be between 1 and 1000"),
    ],
)
def test_paging_limits_are_checked_before_sending(page: int, page_size: int, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        encode({}, page=page, page_size=page_size)


def test_empty_any_of_filter_is_rejected() -> None:
    with pytest.raises(ValueError, match="empty list"):
        encode({"quality.type": []})


def test_range_needs_a_bound() -> None:
    with pytest.raises(ValueError, match="at least one bound"):
        Range()
