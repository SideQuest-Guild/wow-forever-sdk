"""Routes of the Account Profile API.

Account profile has not been recorded live; see :mod:`wow.models.account` for sourcing.
"""

from wow._async._resource import AsyncResource
from wow.models.account import AccountProfile

__all__ = ["AsyncAccount"]


class AsyncAccount(AsyncResource):
    """``client.account``: the authenticated user's WoW Forever accounts and characters."""

    __slots__ = ()

    async def profile(self) -> AccountProfile:
        """Get the authenticated user's account profile. Needs a user token with the ``wow.profile`` scope."""
        return await self._get("profile", "/profile/user/wow", AccountProfile)
