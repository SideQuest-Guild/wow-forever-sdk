from typing import TYPE_CHECKING

import httpx

from tests.conftest import load_fixture, mock_route

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_get_reads_spell_details(client: Client) -> None:
    spell = client.spells.get(11070)

    assert spell.name == "Improved Frostbolt"
    assert spell.description == "Reduces the casting time of your Frostbolt spell by 0.1 sec."
    assert spell.media is not None
    assert spell.media.id == 11070


def test_media_points_at_the_forever_render_path(client: Client) -> None:
    media = client.spells.media(11070)

    assert media.id == 11070
    assert media.assets[0].key == "icon"
    assert "/forever-us/" in media.assets[0].value


def test_search_matches_a_name(client: Client) -> None:
    page = client.spells.search(name="Frost", page_size=5)

    assert page.results[0].data.name["en_US"] == "Frost Channeling"


def test_search_all_pages_across_every_page(client: Client, battlenet: respx.MockRouter) -> None:
    fixture = load_fixture("static/search/spell")["body"]
    results = fixture["results"]
    page_one = {**fixture, "page": 1, "pageCount": 2, "pageSize": 1, "results": results[:1]}
    page_two = {**fixture, "page": 2, "pageCount": 2, "pageSize": 1, "results": results[1:]}
    route = mock_route(battlenet, "/data/wow/search/spell")
    route.side_effect = [httpx.Response(200, json=page_one), httpx.Response(200, json=page_two)]

    ids = [result.data.id for result in client.spells.search_all(page_size=1)]

    assert ids == [result["data"]["id"] for result in results]
    assert route.call_count == 2
