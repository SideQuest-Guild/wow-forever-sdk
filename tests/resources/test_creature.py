from typing import TYPE_CHECKING

import httpx

from tests.conftest import load_fixture, mock_route

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_creature_families_index_lists_every_family(client: Client) -> None:
    index = client.creature_families.index()

    assert len(index.creature_families) == 27
    assert index.creature_families[0].name == "Bat"


def test_creature_families_get_reads_family_details(client: Client) -> None:
    family = client.creature_families.get(24)

    assert family.name == "Bat"
    assert family.media is not None
    assert family.media.id == 24


def test_creature_types_index_lists_every_type(client: Client) -> None:
    index = client.creature_types.index()

    assert len(index.creature_types) == 13
    assert index.creature_types[0].name == "Beast"


def test_creature_types_get_reads_type_details(client: Client) -> None:
    creature_type = client.creature_types.get(1)

    assert creature_type.name == "Beast"


def test_get_reads_creature_details(client: Client) -> None:
    creature = client.creatures.get(30)

    assert creature.name == "Forest Spider"
    assert creature.type.name == "Beast"
    assert creature.family is not None
    assert creature.family.name == "Spider"
    assert creature.is_tameable is True
    assert creature.creature_displays[0].id == 382


def test_display_media_reads_the_rendered_image(client: Client) -> None:
    media = client.creatures.display_media(382)

    assert media.id == 382
    assert media.assets[0].key == "zoom"
    assert "/forever-us/" in media.assets[0].value


def test_search_filters_by_tameability(client: Client) -> None:
    page = client.creatures.search(filters={"is_tameable": True}, page_size=5)

    assert page.results[0].data.is_tameable is True
    assert page.results[0].data.name["en_US"] == "Grizzled Timbermaw Bear"


def test_search_all_pages_across_every_page(client: Client, battlenet: respx.MockRouter) -> None:
    fixture = load_fixture("static/search/creature")["body"]
    results = fixture["results"]
    page_one = {**fixture, "page": 1, "pageCount": 2, "pageSize": 3, "results": results[:3]}
    page_two = {**fixture, "page": 2, "pageCount": 2, "pageSize": 3, "results": results[3:]}
    route = mock_route(battlenet, "/data/wow/search/creature")
    route.side_effect = [httpx.Response(200, json=page_one), httpx.Response(200, json=page_two)]

    ids = [result.data.id for result in client.creatures.search_all(page_size=3)]

    assert ids == [result["data"]["id"] for result in results]
    assert route.call_count == 2
