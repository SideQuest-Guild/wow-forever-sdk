"""Models for the Reputation API."""

from wow.models._common import Document, IdRef, Model, Ref, TypedName

__all__ = [
    "ReputationFaction",
    "ReputationFactionIndex",
    "ReputationTier",
    "ReputationTierSet",
    "ReputationTierSetIndex",
]


class ReputationFactionIndex(Document):
    """Every reputation faction. ``root_factions`` are the top-level entries shown in the reputation pane."""

    factions: tuple[Ref, ...]
    root_factions: tuple[Ref, ...]


class ReputationFaction(Document):
    """A reputation faction, such as a city, tribe or army."""

    id: int
    name: str
    reputation_tiers: IdRef
    description: str | None = None
    player_faction: TypedName | None = None
    is_header: bool = False
    factions: tuple[Ref, ...] = ()


class ReputationTier(Model):
    """One standing level within a reputation tier set, such as Honored."""

    id: int
    name: str
    min_value: int
    max_value: int


class ReputationTierSetIndex(Document):
    """Every reputation tier set. Battle.net calls this document ``reputation-tiers``."""

    reputation_tiers: tuple[IdRef, ...]


class ReputationTierSet(Document):
    """One reputation tier set: the standing levels a faction's reputation can reach.

    Battle.net calls this document ``reputation-tiers``; it is named ``ReputationTierSet`` here so it does not
    collide with :class:`~wow._async.resources.reputation.AsyncReputationTiers`'s generated sync twin.
    """

    id: int
    tiers: tuple[ReputationTier, ...]
