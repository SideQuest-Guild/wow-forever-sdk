from typing import TYPE_CHECKING

import httpx

from tests.conftest import load_fixture, mock_route

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_search_filters_by_tags(client: Client) -> None:
    page = client.media.search(tags="item", page_size=1)

    assert page.result_count_capped is True
    assert page.results[0].data.assets[0].key == "icon"
    assert "/forever-us/" in page.results[0].data.assets[0].value


def test_search_without_tags_uses_the_given_filters(client: Client) -> None:
    page = client.media.search(filters={"id": 10566}, page_size=1)

    assert page.results[0].data.id == 10566


def test_search_all_pages_across_every_page(client: Client, battlenet: respx.MockRouter) -> None:
    fixture = load_fixture("static/search/media")["body"]
    results = fixture["results"]
    page_one = {**fixture, "page": 1, "pageCount": 2, "pageSize": 3, "results": results[:3]}
    page_two = {**fixture, "page": 2, "pageCount": 2, "pageSize": 3, "results": results[3:]}
    route = mock_route(battlenet, "/data/wow/search/media")
    route.side_effect = [httpx.Response(200, json=page_one), httpx.Response(200, json=page_two)]

    ids = [result.data.id for result in client.media.search_all(tags="item", page_size=3)]

    assert ids == [result["data"]["id"] for result in results]
    assert route.call_count == 2
