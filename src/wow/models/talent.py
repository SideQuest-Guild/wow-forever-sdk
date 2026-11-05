"""Models for the Talent and Talent Tree APIs."""

from pydantic import Field

from wow.models._common import Document, Link, Model, NamedLink, Ref

__all__ = [
    "SpellTooltip",
    "Talent",
    "TalentIndex",
    "TalentRankDescription",
    "TalentTree",
    "TalentTreeIndex",
    "TalentTreeMedia",
    "TalentTreeNode",
    "TalentTreeNodeRank",
    "TalentTreeNodeRankTooltip",
    "TalentTreeNodeType",
]


class TalentRankDescription(Model):
    """The tooltip text for one rank of a talent."""

    rank: int
    description: str


class TalentIndex(Document):
    """Every talent across every class and specialization. Forever has 651 talents."""

    talents: tuple[Ref, ...]


class Talent(Document):
    """A single talent, with the spell it grants and its per-rank descriptions."""

    id: int
    playable_class: Ref
    playable_specialization: Ref
    spell: Ref
    rank_descriptions: tuple[TalentRankDescription, ...] = ()


class TalentTreeIndex(Document):
    """Every class and specialization talent tree. Forever has 9 class trees and 27 spec trees."""

    class_talent_trees: tuple[NamedLink, ...]
    spec_talent_trees: tuple[NamedLink, ...]


class TalentTreeMedia(Model):
    """A talent tree's media link, with no id of its own."""

    key: Link


class SpellTooltip(Model):
    """The rendered tooltip for one talent rank's spell."""

    cast_time: str
    description: str
    spell: Ref
    power_cost: str | None = None
    range_: str | None = Field(alias="range", default=None)


class TalentTreeNodeRankTooltip(Model):
    """The talent and spell shown for one rank of a talent tree node."""

    talent: Ref
    spell_tooltip: SpellTooltip


class TalentTreeNodeRank(Model):
    """One learnable rank of a talent tree node."""

    rank: int
    tooltip: TalentTreeNodeRankTooltip


class TalentTreeNodeType(Model):
    """A talent tree node's kind, such as an active talent."""

    id: int
    type: str


class TalentTreeNode(Model):
    """One node in a specialization's talent tree, positioned on its grid."""

    id: int
    display_row: int
    display_col: int
    raw_position_x: int
    raw_position_y: int
    node_type: TalentTreeNodeType
    ranks: tuple[TalentTreeNodeRank, ...]
    locked_by: tuple[int, ...] = ()
    unlocks: tuple[int, ...] = ()


class TalentTree(Document):
    """One specialization's talent tree: its nodes, positions and prerequisites."""

    id: int
    name: str
    media: TalentTreeMedia
    playable_class: Ref
    playable_specialization: Ref
    spec_talent_nodes: tuple[TalentTreeNode, ...]
