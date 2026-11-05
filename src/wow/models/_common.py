"""Building blocks shared by every document model."""

from pydantic import BaseModel, ConfigDict, Field

__all__ = [
    "Document",
    "GenderedName",
    "IdName",
    "IdRef",
    "Link",
    "Links",
    "LocalizedString",
    "Media",
    "MediaAsset",
    "Model",
    "NamedLink",
    "Ref",
    "SearchPage",
    "SearchResult",
    "TypedName",
]

type LocalizedString = dict[str, str]
"""Text in every locale, keyed like ``{"en_US": "Sword", "de_DE": "Schwert"}``.

Search results always come back this way, whatever ``locale`` the client uses.
"""


class Model(BaseModel):
    """Base for every response model.

    Models are immutable and keep fields they do not declare, reachable through ``model_extra``, so a field Blizzard
    adds tomorrow is never lost or fatal.
    """

    model_config = ConfigDict(
        extra="allow",
        frozen=True,
        validate_by_alias=True,
        validate_by_name=True,
        serialize_by_alias=True,
    )


class Link(Model):
    """A link to another API document."""

    href: str


class Links(Model):
    """The ``_links`` block every document carries."""

    self_: Link = Field(alias="self")


class Document(Model):
    """A top-level API document."""

    links: Links = Field(alias="_links")


class IdName(Model):
    """An id and a localized name."""

    id: int
    name: str


class Ref(IdName):
    """A reference to another document: its id, name and link, as in every index."""

    key: Link


class IdRef(Model):
    """A reference that carries no name, such as a media or appearance link."""

    id: int
    key: Link


class NamedLink(Model):
    """A reference that carries no id, such as a talent tree link."""

    key: Link
    name: str


class TypedName(Model):
    """A constant plus its localized label, such as ``{"type": "HORDE", "name": "Horde"}``.

    ``type`` is kept as a plain string so values Blizzard adds later still validate.
    """

    type: str
    name: str


class GenderedName(Model):
    """A name with a male and a female form."""

    male: str
    female: str


class MediaAsset(Model):
    """One rendered asset.

    Attributes:
        key: The asset kind, such as ``icon``.
        value: Its URL on ``render.worldofwarcraft.com``. Forever assets live under ``/forever-{region}/``.
        file_data_id: The game client's file id.
    """

    key: str
    value: str
    file_data_id: int


class Media(Document):
    """A media document: the rendered assets for one item, class, or other entity."""

    id: int
    assets: tuple[MediaAsset, ...]


class SearchResult[DataT: BaseModel](Model):
    """One search hit: the link to the full document plus its indexed, all-locale data."""

    key: Link
    data: DataT


class SearchPage[DataT: BaseModel](Model):
    """One page of search results.

    Battle.net stops at 1,000 results per query however many pages that spans.
    """

    page: int
    page_size: int = Field(alias="pageSize")
    max_page_size: int = Field(alias="maxPageSize")
    page_count: int = Field(alias="pageCount")
    results: tuple[SearchResult[DataT], ...]
