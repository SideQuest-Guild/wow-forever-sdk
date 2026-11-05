"""Routes of the Profession API."""

from wow._async._resource import AsyncResource
from wow.models._common import Media
from wow.models.profession import Profession, ProfessionIndex, ProfessionSkillTier

__all__ = ["AsyncProfessions"]


class AsyncProfessions(AsyncResource):
    """``client.professions``: professions such as Tailoring and Cooking."""

    __slots__ = ()

    async def index(self) -> ProfessionIndex:
        """List every profession."""
        return await self._get("static", "/data/wow/profession/index", ProfessionIndex)

    async def get(self, profession_id: int) -> Profession:
        """Get one profession by id."""
        return await self._get("static", f"/data/wow/profession/{profession_id}", Profession)

    async def media(self, profession_id: int) -> Media:
        """Get a profession's icon."""
        return await self._get("static", f"/data/wow/media/profession/{profession_id}", Media)

    async def skill_tier(self, profession_id: int, skill_tier_id: int) -> ProfessionSkillTier:
        """Get one skill tier of a profession, with every recipe in it. A profession lists its tiers' ids."""
        return await self._get(
            "static", f"/data/wow/profession/{profession_id}/skill-tier/{skill_tier_id}", ProfessionSkillTier
        )
