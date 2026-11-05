from typing import TYPE_CHECKING

import httpx

from tests.conftest import load_fixture, mock_route

if TYPE_CHECKING:
    import respx

    from wow import Client


def test_get_reads_item_details(client: Client) -> None:
    item = client.items.get(19019)

    assert item.name == "Thunderfury, Blessed Blade of the Windseeker"
    assert item.quality.type == "LEGENDARY"
    assert item.level == 80
    assert item.required_level == 60
    assert item.item_class.name == "Weapon"
    assert item.item_subclass.name == "Sword"
    assert item.inventory_type.type == "WEAPON"
    assert item.is_equippable is True
    assert item.is_stackable is False
    assert item.max_count == 1
    assert item.purchase_price == 1276777
    assert item.sell_price == 255355
    assert item.appearances[0].id == 68530

    preview = item.preview_item
    assert preview.quality.name == "Legendary"
    assert preview.binding is not None
    assert preview.binding.type == "ON_ACQUIRE"
    assert preview.unique_equipped == "Unique"
    assert preview.durability is not None
    assert preview.durability.value == 125
    assert preview.requirements is not None
    assert preview.requirements.level is not None
    assert preview.requirements.level.display_string == "Requires Level 60"
    assert preview.spells[0].spell.name == "Thunderfury"
    assert [stat.type and stat.type.type for stat in preview.stats] == [
        "AGILITY",
        "STAMINA",
        "FIRE_RESISTANCE",
        "NATURE_RESISTANCE",
    ]
    assert preview.stats[0].display.color.g == 255
    assert preview.weapon is not None
    assert preview.weapon.damage.min_value == 44
    assert preview.weapon.damage.max_value == 115
    assert preview.weapon.dps is not None
    assert preview.weapon.dps.value == 41.842102


def test_media_points_at_the_forever_render_path(client: Client) -> None:
    media = client.items.media(19019)

    assert media.assets[0].key == "icon"
    assert "/forever-us/" in media.assets[0].value


def test_item_classes_index_lists_every_class(client: Client) -> None:
    index = client.item_classes.index()

    assert len(index.item_classes) == 13
    assert index.item_classes[0].name == "Consumable"


def test_item_classes_get_reads_class_details(client: Client) -> None:
    item_class = client.item_classes.get(0)

    assert item_class.name == "Consumable"
    assert item_class.item_subclasses[1].name == "Explosives"


def test_item_sets_index_lists_every_set(client: Client) -> None:
    index = client.item_sets.index()

    assert len(index.item_sets) == 154
    assert index.item_sets[0].name == "Lieutenant Commander's Sanctuary"


def test_item_sets_get_reads_set_details(client: Client) -> None:
    item_set = client.item_sets.get(381)

    assert item_set.name == "Lieutenant Commander's Sanctuary"
    assert len(item_set.items) == 6
    assert item_set.effects[0].required_count == 2
    assert item_set.effects[0].display_string == "Set: +40 Attack Power."


def test_search_all_pages_across_every_page(client: Client, battlenet: respx.MockRouter) -> None:
    fixture = load_fixture("static/search/item")["body"]
    results = fixture["results"]
    page_one = {**fixture, "page": 1, "pageCount": 2, "pageSize": 1, "results": results[:1]}
    page_two = {**fixture, "page": 2, "pageCount": 2, "pageSize": 1, "results": results[1:]}
    route = mock_route(battlenet, "/data/wow/search/item")
    route.side_effect = [httpx.Response(200, json=page_one), httpx.Response(200, json=page_two)]

    ids = [result.data.id for result in client.items.search_all(page_size=1)]

    assert ids == [result["data"]["id"] for result in results]
    assert route.call_count == 2
