"""Routes of the Ruleset API."""

from wow._async._resource import AsyncResource
from wow.models.ruleset import Ruleset, RulesetIndex

__all__ = ["AsyncRulesets"]


class AsyncRulesets(AsyncResource):
    """``client.rulesets``: the rulesets players choose from, such as Normal and PvP."""

    __slots__ = ()

    async def index(self) -> RulesetIndex:
        """List every ruleset."""
        return await self._get("dynamic", "/data/wow/ruleset/index", RulesetIndex)

    async def get(self, ruleset_id: int) -> Ruleset:
        """Get one ruleset by id, with its server status."""
        return await self._get("dynamic", f"/data/wow/ruleset/{ruleset_id}", Ruleset)
