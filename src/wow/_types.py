"""Regions, locales and namespace kinds shared by every part of the client."""

from enum import StrEnum
from typing import Final, Literal, TypeIs, get_args

__all__ = ["DEFAULT_LOCALES", "LOCALES", "Locale", "NamespaceKind", "Region", "is_locale"]


class Region(StrEnum):
    """A Battle.net API region; each has its own host and its own namespaces.

    China is absent on purpose: it runs on a separate gateway with separate developer accounts, and WoW Forever has
    not been verified there.
    """

    US = "us"
    EU = "eu"
    KR = "kr"
    TW = "tw"


type Locale = Literal[
    "en_US",
    "es_MX",
    "pt_BR",
    "de_DE",
    "en_GB",
    "es_ES",
    "fr_FR",
    "it_IT",
    "ru_RU",
    "ko_KR",
    "zh_TW",
    "zh_CN",
]
"""A locale accepted by the ``locale`` query parameter."""

LOCALES: Final[frozenset[str]] = frozenset(get_args(Locale.__value__))

DEFAULT_LOCALES: Final[dict[Region, Locale]] = {
    Region.US: "en_US",
    Region.EU: "en_GB",
    Region.KR: "ko_KR",
    Region.TW: "zh_TW",
}
"""The locale used for a region when the client is not given one."""


def is_locale(value: str) -> TypeIs[Locale]:
    """Whether ``value`` is a locale Battle.net accepts."""
    return value in LOCALES


type NamespaceKind = Literal["static", "dynamic", "profile"]
"""Which family of documents a request reads.

``static`` holds game data that only changes with patches, ``dynamic`` holds live state such as realms, and
``profile`` holds player data. The wire namespace is ``{kind}-forever-{region}``.
"""
