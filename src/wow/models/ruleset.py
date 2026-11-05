"""Models for the Ruleset API.

Forever players pick a ruleset, such as Normal or PvP, rather than a realm. Characters and guilds link to their
ruleset in the ``dynamic`` namespace.
"""

from wow.models._common import Document, IdRef, Link, TypedName

__all__ = ["Ruleset", "RulesetIndex"]


class RulesetIndex(Document):
    """Every ruleset. Index entries carry only an id."""

    rulesets: tuple[IdRef, ...]


class Ruleset(Document):
    """A ruleset, such as Normal, PvP, Roleplay or Roleplay PvP, and whether its servers are up.

    Attributes:
        status: ``UP`` or another state, with its label.
        auctions: A link to the ruleset's auction house. Battle.net does not serve it yet.
    """

    id: int
    name: str
    status: TypedName
    auctions: Link
