from typing import TYPE_CHECKING

import httpx
import pytest

from tests.conftest import mock_route
from wow import NotFoundError

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_index_lists_realms(client: Client) -> None:
    index = client.realms.index()

    assert [realm.slug for realm in index.realms] == [
        "camwow-us1-realm-1-pve",
        "camwow-us1-realm-2-pvp",
        "camwow-us1-realm-3-pve",
    ]
    assert index.realms[2].id == 6921


def test_get_reads_realm_details_by_slug(client: Client) -> None:
    realm = client.realms.get("camwow-us1-realm-3-pve")

    assert realm.id == 6921
    assert realm.name == "CAMWOW US1 Realm 3 PvE"
    assert realm.region.id == 91
    assert realm.region.name == "CAMWOW North America"
    assert realm.type.type == "NORMAL"
    assert realm.type.name == "Normal"
    assert realm.locale == "enUS"
    assert realm.timezone == "America/Chicago"
    assert realm.is_tournament is False
    assert realm.connected_realm.href.endswith("/data/wow/connected-realm/6921?namespace=dynamic-forever-us")


def test_search_all_pages_through_every_result(client: Client, battlenet: respx.MockRouter) -> None:
    route = mock_route(battlenet, "/data/wow/search/realm")
    realm_data = {
        "id": 6921,
        "name": {"en_US": "CAMWOW US1 Realm 3 PvE"},
        "category": {"en_US": "English"},
        "locale": "enUS",
        "timezone": "America/Chicago",
        "type": {"type": "NORMAL", "name": "Normal"},
        "is_tournament": False,
        "slug": "camwow-us1-realm-3-pve",
    }
    page_one = {
        "page": 1,
        "pageSize": 1,
        "maxPageSize": 1000,
        "pageCount": 2,
        "results": [{"key": {"href": "https://us.api.blizzard.com/data/wow/realm/6921"}, "data": realm_data}],
    }
    page_two = {
        "page": 2,
        "pageSize": 1,
        "maxPageSize": 1000,
        "pageCount": 2,
        "results": [{"key": {"href": "https://us.api.blizzard.com/data/wow/realm/6794"}, "data": realm_data}],
    }
    route.side_effect = [httpx.Response(200, json=page_one), httpx.Response(200, json=page_two)]

    results = list(client.realms.search_all(page_size=1))

    assert len(results) == 2
    assert route.calls.last.request.url.params["namespace"] == "dynamic-forever-us"
    assert all(result.data.name["en_US"] == "CAMWOW US1 Realm 3 PvE" for result in results)


def test_get_escapes_the_slug_into_one_path_segment(client: Client, battlenet: respx.MockRouter) -> None:
    with pytest.raises(NotFoundError):
        client.realms.get("../../profile/user/wow?_page=9")

    request = battlenet["api"].calls.last.request
    assert request.url.raw_path.startswith(b"/data/wow/realm/..%2F..%2Fprofile%2Fuser%2Fwow%3F_page%3D9?")
    assert "_page" not in request.url.params
