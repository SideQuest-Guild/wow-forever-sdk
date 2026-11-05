"""Models for the Guild API.

Forever guilds have no realm: a guild's address is its slug alone, such as ``/data/wow/guild/sidequest``. The guild's
activity and achievements documents answer, but hold nothing beyond a link back to the guild yet.
"""

from wow.models._common import Document, IdRef, Link, Model, Ref, TypedName

__all__ = ["FactionType", "Guild", "GuildMember", "GuildRef", "GuildRoster", "GuildRosterCharacter"]


class GuildRef(Model):
    """A link to a guild, as characters and rosters carry it."""

    key: Link
    id: int
    name: str
    slug: str
    faction: TypedName


class Guild(Document):
    """A guild: its faction, ruleset, size and links to its roster.

    Attributes:
        name_search: The name as Battle.net indexes it for lookups.
        created_timestamp: When the guild was founded, in Unix milliseconds.
    """

    id: int
    name: str
    slug: str
    name_search: str
    faction: TypedName
    ruleset: Ref
    achievement_points: int
    member_count: int
    created_timestamp: int
    roster: Link
    achievements: Link
    activity: Link


class FactionType(Model):
    """A faction constant with no label, such as ``{"type": "ALLIANCE"}``, as roster entries carry it."""

    type: str


class GuildRosterCharacter(Model):
    """A character as a guild roster lists it. Class and race carry only their ids."""

    key: Link
    id: int
    name: str
    surname: str
    slug: str
    level: int
    playable_class: IdRef
    playable_race: IdRef
    faction: FactionType


class GuildMember(Model):
    """One roster entry. ``rank`` 0 is the Guild Master; each higher number is a lower rank."""

    character: GuildRosterCharacter
    rank: int


class GuildRoster(Document):
    """Every member of a guild."""

    guild: GuildRef
    members: tuple[GuildMember, ...] = ()
