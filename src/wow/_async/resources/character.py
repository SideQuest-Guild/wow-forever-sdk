"""Routes of the Character Profile API."""

from urllib.parse import quote

from wow._async._resource import AsyncResource
from wow.models.character import (
    CharacterAchievements,
    CharacterAchievementStatistics,
    CharacterAppearance,
    CharacterCollections,
    CharacterCompletedQuests,
    CharacterEquipment,
    CharacterHunterPets,
    CharacterMedia,
    CharacterMounts,
    CharacterPets,
    CharacterProfessions,
    CharacterProfile,
    CharacterPvpSummary,
    CharacterQuests,
    CharacterReputations,
    CharacterSpecializations,
    CharacterStatistics,
    CharacterStatus,
    CharacterToys,
    CharacterTransmogs,
)

__all__ = ["AsyncCharacters"]


def _path(slug: str, document: str = "") -> str:
    return f"/profile/wow/character/{quote(slug.lower(), safe='')}{document}"


class AsyncCharacters(AsyncResource):
    """``client.characters``: any character's public profile. An app token is enough.

    Each method takes the character's slug: its name and surname joined by a hyphen, such as
    ``psyence-spiritbound``, in any case. Battle.net has no character search; a character that does not exist, or has
    not logged out since it was made, raises :class:`~wow.NotFoundError`.
    """

    __slots__ = ()

    async def get(self, slug: str) -> CharacterProfile:
        """Get a character's summary: class, race, level, guild, item level and links to the rest of its profile."""
        return await self._get("profile", _path(slug), CharacterProfile)

    async def status(self, slug: str) -> CharacterStatus:
        """Check that a character still exists, and whether it is the character with the id you stored."""
        return await self._get("profile", _path(slug, "/status"), CharacterStatus)

    async def media(self, slug: str) -> CharacterMedia:
        """Get a character's rendered images, such as its avatar."""
        return await self._get("profile", _path(slug, "/character-media"), CharacterMedia)

    async def equipment(self, slug: str) -> CharacterEquipment:
        """Get the items a character wears."""
        return await self._get("profile", _path(slug, "/equipment"), CharacterEquipment)

    async def appearance(self, slug: str) -> CharacterAppearance:
        """Get a character's rendered appearance: its gear, customizations and guild crest."""
        return await self._get("profile", _path(slug, "/appearance"), CharacterAppearance)

    async def statistics(self, slug: str) -> CharacterStatistics:
        """Get a character's stats sheet."""
        return await self._get("profile", _path(slug, "/statistics"), CharacterStatistics)

    async def specializations(self, slug: str) -> CharacterSpecializations:
        """Get a character's talent loadouts."""
        return await self._get("profile", _path(slug, "/specializations"), CharacterSpecializations)

    async def professions(self, slug: str) -> CharacterProfessions:
        """Get a character's professions, skill levels and known recipes."""
        return await self._get("profile", _path(slug, "/professions"), CharacterProfessions)

    async def reputations(self, slug: str) -> CharacterReputations:
        """Get a character's standing with every faction it has met."""
        return await self._get("profile", _path(slug, "/reputations"), CharacterReputations)

    async def pvp_summary(self, slug: str) -> CharacterPvpSummary:
        """Get a character's honorable kills and PvP rank."""
        return await self._get("profile", _path(slug, "/pvp-summary"), CharacterPvpSummary)

    async def achievements(self, slug: str) -> CharacterAchievements:
        """Get a character's achievements and achievement points."""
        return await self._get("profile", _path(slug, "/achievements"), CharacterAchievements)

    async def achievement_statistics(self, slug: str) -> CharacterAchievementStatistics:
        """Get a character's statistics pane, such as total kills and deaths."""
        return await self._get("profile", _path(slug, "/achievements/statistics"), CharacterAchievementStatistics)

    async def quests(self, slug: str) -> CharacterQuests:
        """Get the quests in a character's quest log."""
        return await self._get("profile", _path(slug, "/quests"), CharacterQuests)

    async def completed_quests(self, slug: str) -> CharacterCompletedQuests:
        """Get every quest a character has completed."""
        return await self._get("profile", _path(slug, "/quests/completed"), CharacterCompletedQuests)

    async def collections(self, slug: str) -> CharacterCollections:
        """Get links to a character's collections."""
        return await self._get("profile", _path(slug, "/collections"), CharacterCollections)

    async def mounts(self, slug: str) -> CharacterMounts:
        """Get the mounts a character has collected."""
        return await self._get("profile", _path(slug, "/collections/mounts"), CharacterMounts)

    async def pets(self, slug: str) -> CharacterPets:
        """Get the battle pets a character has collected."""
        return await self._get("profile", _path(slug, "/collections/pets"), CharacterPets)

    async def toys(self, slug: str) -> CharacterToys:
        """Get the toys a character has collected."""
        return await self._get("profile", _path(slug, "/collections/toys"), CharacterToys)

    async def transmogs(self, slug: str) -> CharacterTransmogs:
        """Get the appearances a character has collected."""
        return await self._get("profile", _path(slug, "/collections/transmogs"), CharacterTransmogs)

    async def hunter_pets(self, slug: str) -> CharacterHunterPets:
        """Get a hunter's tamed pets. Only hunters have this document; :class:`~wow.NotFoundError` otherwise."""
        return await self._get("profile", _path(slug, "/hunter-pets"), CharacterHunterPets)
