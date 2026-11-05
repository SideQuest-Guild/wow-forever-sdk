from typing import TYPE_CHECKING

import httpx

from tests.conftest import load_fixture, mock_route

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_index_lists_every_mount(client: Client) -> None:
    index = client.mounts.index()

    assert len(index.mounts) == 141
    assert index.mounts[0].name == "Swift Hyjal Stag"


def test_get_reads_mount_details(client: Client) -> None:
    mount = client.mounts.get(2978)

    assert mount.name == "Swift Hyjal Stag"
    assert mount.description is None
    assert mount.creature_displays[0].key.href.endswith(
        "/media/creature-display/144186?namespace=static-1.60.1_70399-forever-us"
    )


def test_search_all_pages_across_every_page(client: Client, battlenet: respx.MockRouter) -> None:
    fixture = load_fixture("static/search/mount")["body"]
    results = fixture["results"]
    page_one = {**fixture, "page": 1, "pageCount": 2, "pageSize": 3, "results": results[:3]}
    page_two = {**fixture, "page": 2, "pageCount": 2, "pageSize": 3, "results": results[3:]}
    route = mock_route(battlenet, "/data/wow/search/mount")
    route.side_effect = [httpx.Response(200, json=page_one), httpx.Response(200, json=page_two)]

    names = [result.data.name["en_US"] for result in client.mounts.search_all(page_size=3)]

    assert names == [result["data"]["name"]["en_US"] for result in results]
    assert route.call_count == 2
