"""Models for the Region API."""

from wow.models._common import Document, Link

__all__ = ["RegionIndex", "RegionInfo"]


class RegionIndex(Document):
    """Every API region reachable from this host. Forever publishes one region per regional host."""

    regions: tuple[Link, ...]


class RegionInfo(Document):
    """A Battle.net API region."""

    id: int
    name: str
    tag: str
    patch_string: str
