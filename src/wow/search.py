"""Filters for Battle.net search endpoints.

Search methods take ``filters``, a mapping from a document field to a value::

    client.items.search(
        filters={
            "item_class.id": 2,  # equals
            "quality.type": ["EPIC", "LEGENDARY"],  # any of
            "required_level": Range(50, 60),  # 50 <= level <= 60
            "inventory_type.type": Not("SHIELD"),  # not equal
        },
        order_by=["level:desc", "id"],
    )

Field names follow the search document, with dots for nesting. Localized fields take a locale suffix, as in
``name.en_US``.
"""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Final

__all__ = ["MAX_PAGE_SIZE", "FilterValue", "Not", "Range", "encode_search"]

MAX_PAGE_SIZE: Final = 1000
"""The largest ``page_size`` Battle.net accepts, and also the most results one query returns."""

type Scalar = str | int


@dataclass(frozen=True, slots=True)
class Range:
    """Match a numeric field between two bounds; leave one out for an open range.

    Attributes:
        min: The lower bound, or ``None`` for no lower bound.
        max: The upper bound, or ``None`` for no upper bound.
        inclusive: Whether the bounds themselves match.
    """

    min: int | None = None
    max: int | None = None
    inclusive: bool = True

    def __post_init__(self) -> None:
        if self.min is None and self.max is None:
            msg = "Range needs at least one bound"
            raise ValueError(msg)

    def encode(self) -> str:
        """Render Blizzard's range syntax, such as ``[50,60]`` or ``(,77)``."""
        low = "" if self.min is None else str(self.min)
        high = "" if self.max is None else str(self.max)
        opening, closing = ("[", "]") if self.inclusive else ("(", ")")
        return f"{opening}{low},{high}{closing}"


@dataclass(frozen=True, slots=True)
class Not:
    """Match documents whose field is not this value.

    Attributes:
        value: The value to exclude.
    """

    value: Scalar


type FilterValue = Scalar | bool | Range | Not | Sequence[Scalar]
"""A filter value: equals for a scalar, any-of for a sequence, plus :class:`Range` and :class:`Not`."""


def _scalar(value: Scalar) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def encode_search(
    filters: Mapping[str, FilterValue] | None,
    *,
    order_by: str | Sequence[str] | None,
    page: int,
    page_size: int,
) -> dict[str, str | int]:
    """Turn search arguments into query parameters.

    Raises:
        ValueError: ``page`` or ``page_size`` is out of range, or a sequence filter is empty.
    """
    if page < 1:
        msg = f"page must be at least 1, got {page}"
        raise ValueError(msg)
    if not 1 <= page_size <= MAX_PAGE_SIZE:
        msg = f"page_size must be between 1 and {MAX_PAGE_SIZE}, got {page_size}"
        raise ValueError(msg)
    params: dict[str, str | int] = {"_page": page, "_pageSize": page_size}
    if order_by:
        params["orderby"] = order_by if isinstance(order_by, str) else ",".join(order_by)
    for field, value in (filters or {}).items():
        match value:
            case Range():
                params[field] = value.encode()
            case Not():
                params[f"{field}!"] = _scalar(value.value)
            case str() | int():
                params[field] = _scalar(value)
            case _:
                if not value:
                    msg = f"filter {field!r} has an empty list of values"
                    raise ValueError(msg)
                params[field] = "||".join(_scalar(item) for item in value)
    return params
