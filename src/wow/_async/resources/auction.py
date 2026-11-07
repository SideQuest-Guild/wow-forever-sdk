"""Routes of the Auction House API."""

from wow._async._resource import AsyncResource
from wow.models.auction import AuctionHouse, AuctionHouseIndex, CommodityHouse

__all__ = ["AsyncAuctions"]


class AsyncAuctions(AsyncResource):
    """``client.auctions``: the auction houses Forever's rulesets use in place of realm auction houses."""

    __slots__ = ()

    async def houses(self, ruleset_id: int) -> AuctionHouseIndex:
        """List every auction house for a ruleset. Every ruleset lists the same fifteen houses."""
        return await self._get("dynamic", f"/data/wow/ruleset/{ruleset_id}/auctions/", AuctionHouseIndex)

    async def get(self, ruleset_id: int, house_id: int) -> AuctionHouse:
        """Get one auction house's posted auctions. An empty house lists none."""
        return await self._get("dynamic", f"/data/wow/ruleset/{ruleset_id}/auctions/{house_id}", AuctionHouse)

    async def commodities(self, ruleset_id: int, house_id: int) -> CommodityHouse:
        """Get one auction house's commodities: stackable items sold at a fixed price."""
        return await self._get(
            "dynamic", f"/data/wow/ruleset/{ruleset_id}/auctions/{house_id}/commodities", CommodityHouse
        )
