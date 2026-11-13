"""Models for the Media Search API."""

from wow.models._common import MediaAsset, Model

__all__ = ["MediaSearchData"]


class MediaSearchData(Model):
    """One media document as indexed for search: no ``_links``."""

    id: int
    assets: tuple[MediaAsset, ...]
