"""Routes of the Recipe API."""

from wow._async._resource import AsyncResource
from wow.models._common import Media
from wow.models.recipe import Recipe

__all__ = ["AsyncRecipes"]


class AsyncRecipes(AsyncResource):
    """``client.recipes``: profession recipes. A profession's skill tiers list their recipes."""

    __slots__ = ()

    async def get(self, recipe_id: int) -> Recipe:
        """Get one recipe by id, with what it makes and its reagents."""
        return await self._get("static", f"/data/wow/recipe/{recipe_id}", Recipe)

    async def media(self, recipe_id: int) -> Media:
        """Get a recipe's icon."""
        return await self._get("static", f"/data/wow/media/recipe/{recipe_id}", Media)
