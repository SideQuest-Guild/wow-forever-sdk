"""Building blocks shared by every document model."""

from typing import dataclass_transform

from msgspec import Struct, field

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


# msgspec subclasses inherit ``frozen`` at runtime; this tells type checkers so (PEP 681).
@dataclass_transform(frozen_default=True, field_specifiers=(field,))
class Model(Struct, frozen=True):
    """Base for every response model.

    Models are immutable. Fields they do not declare are skipped, so a field Blizzard adds tomorrow is never fatal; read
    it from the raw document with :meth:`wow.Client.get` until a release models it.
    """


class Link(Model):
    """A link to another API document."""

    href: str


class Links(Model):
    """The ``_links`` block every document carries."""

    self_: Link = field(name="self")


class Document(Model):
    """A top-level API document."""

    links: Links = field(name="_links")


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


class SearchResult[DataT: Model](Model):
    """One search hit: the link to the full document plus its indexed, all-locale data."""

    key: Link
    data: DataT


class SearchPage[DataT: Model](Model):
    """One page of search results.

    Battle.net stops at 1,000 results per query however many pages that spans, and sets ``result_count_capped`` when
    it cut the results short.
    """

    page: int
    page_size: int = field(name="pageSize")
    max_page_size: int = field(name="maxPageSize")
    page_count: int = field(name="pageCount")
    results: tuple[SearchResult[DataT], ...]
    result_count_capped: bool = field(name="resultCountCapped", default=False)
