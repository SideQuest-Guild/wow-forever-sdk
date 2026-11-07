"""Models for the Auction House API.

Forever has fifteen auction houses per ruleset, in five Alliance, Horde and Blackwater groups; every ruleset lists
the same fifteen. ``client.auctions`` reads them.
"""

from typing import Literal

from wow.models._common import Document, Link, Model, Ref

__all__ = [
    "AuctionEntry",
    "AuctionHouse",
    "AuctionHouseIndex",
    "AuctionItem",
    "AuctionItemModifier",
    "AuctionTimeLeft",
    "CommodityEntry",
    "CommodityHouse",
]

type AuctionTimeLeft = Literal["SHORT", "MEDIUM", "LONG", "VERY_LONG"]
"""How much longer an auction has to run, as a coarse band rather than a timestamp."""


class AuctionItemModifier(Model):
    """One modifier on an auctioned item, such as the context a dungeon or raid drop came from."""

    type: int
    value: int


class AuctionItem(Model):
    """The item an auction sells: its id plus whatever bonuses and modifiers make one stack differ from another."""

    id: int
    context: int | None = None
    bonus_lists: tuple[int, ...] = ()
    modifiers: tuple[AuctionItemModifier, ...] = ()


class AuctionEntry(Model):
    """One posted auction: a buyout, a starting bid, or both."""

    id: int
    item: AuctionItem
    quantity: int
    time_left: AuctionTimeLeft
    bid: int | None = None
    buyout: int | None = None


class AuctionHouseIndex(Document):
    """Every auction house for one ruleset."""

    auctions: tuple[Ref, ...]


class AuctionHouse(Document):
    """One auction house, with its posted, non-stackable auctions.

    Attributes:
        ruleset: The ruleset the request was made through, not necessarily the house's own ruleset; Battle.net
            echoes whichever ruleset id you asked with.
        auctions: An empty house, such as house 112, carries none.
    """

    id: int
    name: str
    commodities: Link
    ruleset: Link
    auctions: tuple[AuctionEntry, ...] = ()


class CommodityEntry(Model):
    """One posted stack of a commodity, sold at a fixed unit price with no bidding."""

    id: int
    item: AuctionItem
    quantity: int
    unit_price: int
    time_left: AuctionTimeLeft


class CommodityHouse(Document):
    """The commodities listed at one auction house: stackable items with no item modifiers, sold at a fixed price."""

    auctions: tuple[CommodityEntry, ...] = ()
