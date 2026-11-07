from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from wow import Client


def test_houses_lists_every_auction_house(client: Client) -> None:
    index = client.auctions.houses(2)

    assert len(index.auctions) == 15
    assert index.auctions[0].id == 110
    assert index.auctions[0].name == "Alliance Auction House"


def test_get_reads_an_auction_house_with_its_auctions(client: Client) -> None:
    house = client.auctions.get(2, 125)

    assert house.id == 125
    assert house.name == "Blackwater Auction House"
    assert house.ruleset.href.endswith("/data/wow/ruleset/2?namespace=dynamic-forever-us")
    assert len(house.auctions) == 103

    first = house.auctions[0]
    assert first.item.id == 2079
    assert first.item.bonus_lists == (12729,)
    assert first.buyout == 1200
    assert first.time_left == "MEDIUM"

    modified = next(entry for entry in house.auctions if entry.item.modifiers)
    assert modified.item.context == 1
    assert modified.item.modifiers[0].type == 28
    assert modified.item.modifiers[0].value == 5254


def test_get_reads_a_house_with_no_auctions(client: Client) -> None:
    house = client.auctions.get(2, 112)

    assert house.name == "Alliance Auction House"
    assert house.auctions == ()


def test_commodities_lists_stackable_auctions(client: Client) -> None:
    commodities = client.auctions.commodities(2, 125)

    assert len(commodities.auctions) == 227
    first = commodities.auctions[0]
    assert first.item.id == 5075
    assert first.quantity == 10
    assert first.unit_price == 600
    assert first.time_left == "LONG"


def test_commodities_reads_an_empty_house(client: Client) -> None:
    commodities = client.auctions.commodities(2, 112)

    assert commodities.auctions == ()
