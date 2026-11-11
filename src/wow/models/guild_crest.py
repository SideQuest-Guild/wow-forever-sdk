"""Models for the Guild Crest API."""

from wow.models._common import Document, IdRef, Model
from wow.models.character import GuildCrestColor

__all__ = ["GuildCrestComponent", "GuildCrestComponentColors", "GuildCrestComponentsIndex"]


class GuildCrestComponent(Model):
    """One selectable guild crest emblem or border: its catalog id and rendered media."""

    id: int
    media: IdRef


class GuildCrestComponentColors(Model):
    """Every selectable crest color, grouped by the part of the crest it colors."""

    emblems: tuple[GuildCrestColor, ...]
    borders: tuple[GuildCrestColor, ...]
    backgrounds: tuple[GuildCrestColor, ...]


class GuildCrestComponentsIndex(Document):
    """Every emblem, border and color a guild crest can use."""

    emblems: tuple[GuildCrestComponent, ...]
    borders: tuple[GuildCrestComponent, ...]
    colors: GuildCrestComponentColors
