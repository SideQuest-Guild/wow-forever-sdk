"""Routes of the Reputation API."""

from wow._async._resource import AsyncResource
from wow.models.reputation import (
    ReputationFaction,
    ReputationFactionIndex,
    ReputationTierSet,
    ReputationTierSetIndex,
)

__all__ = ["AsyncReputationFactions", "AsyncReputationTiers"]


class AsyncReputationFactions(AsyncResource):
    """``client.reputation_factions``: reputation factions such as cities, tribes and armies."""

    __slots__ = ()

    async def index(self) -> ReputationFactionIndex:
        """List every reputation faction."""
        return await self._get("static", "/data/wow/reputation-faction/index", ReputationFactionIndex)

    async def get(self, faction_id: int) -> ReputationFaction:
        """Get one reputation faction by id."""
        return await self._get("static", f"/data/wow/reputation-faction/{faction_id}", ReputationFaction)


class AsyncReputationTiers(AsyncResource):
    """``client.reputation_tiers``: the standing levels a faction's reputation can reach."""

    __slots__ = ()

    async def index(self) -> ReputationTierSetIndex:
        """List every reputation tier set."""
        return await self._get("static", "/data/wow/reputation-tiers/index", ReputationTierSetIndex)

    async def get(self, tiers_id: int) -> ReputationTierSet:
        """Get one reputation tier set by id."""
        return await self._get("static", f"/data/wow/reputation-tiers/{tiers_id}", ReputationTierSet)
