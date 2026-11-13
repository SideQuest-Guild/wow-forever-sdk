from typing import TYPE_CHECKING

import httpx

from tests.conftest import load_fixture, mock_route

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_get_reads_appearance_details(client: Client) -> None:
    appearance = client.item_appearances.get(69351)

    assert appearance.slot.type == "HEAD"
    assert appearance.slot.name == "Head"
    assert appearance.item_class.name == "Armor"
    assert appearance.item_subclass.name == "Mail"
    assert appearance.item_display_info_id == 35801
    assert appearance.items[0].name == "Lieutenant Commander's Chain Helm"
    assert appearance.media.id == 133123


def test_set_index_lists_every_set(client: Client) -> None:
    index = client.item_appearances.set_index()

    assert len(index.appearance_sets) == 1
    assert index.appearance_sets[0].name == "Green Snugglefin Murloc Romper"


def test_set_reads_set_details(client: Client) -> None:
    appearance_set = client.item_appearances.set(3634)

    assert appearance_set.set_name == "Green Snugglefin Murloc Romper"
    assert len(appearance_set.appearances) == 7
    assert appearance_set.appearances[0].id == 91080


def test_slot_index_lists_every_slot(client: Client) -> None:
    index = client.item_appearances.slot_index()

    assert len(index.slots) == 23
    assert index.slots[0].key.href.endswith("/item-appearance/slot/HEAD?namespace=static-1.60.1_70399-forever-us")


def test_slot_reads_appearances_in_that_slot(client: Client) -> None:
    slot = client.item_appearances.slot("HEAD")

    assert slot.appearances[0].id == 6737


def test_search_filters_by_slot_type(client: Client) -> None:
    page = client.item_appearances.search(filters={"slot.type": "HEAD"}, page_size=5)

    assert page.results[0].data.slot.type == "HEAD"
    assert page.results[0].data.id == 69351


def test_search_all_pages_across_every_page(client: Client, battlenet: respx.MockRouter) -> None:
    fixture = load_fixture("static/search/item-appearance")["body"]
    results = fixture["results"]
    page_one = {**fixture, "page": 1, "pageCount": 2, "pageSize": 3, "results": results[:3]}
    page_two = {**fixture, "page": 2, "pageCount": 2, "pageSize": 3, "results": results[3:]}
    route = mock_route(battlenet, "/data/wow/search/item-appearance")
    route.side_effect = [httpx.Response(200, json=page_one), httpx.Response(200, json=page_two)]

    ids = [result.data.id for result in client.item_appearances.search_all(page_size=3)]

    assert ids == [result["data"]["id"] for result in results]
    assert route.call_count == 2
