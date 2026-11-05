"""Typed sync and async client for the World of Warcraft: Forever Battle.net API.

>>> from wow import Client
>>> with Client(client_id="...", client_secret="...") as client:  # doctest: +SKIP
...     client.playable_classes.get(1).name
'Warrior'
"""

from wow._async._client import AsyncClient
from wow._base import OAuthToken
from wow._exceptions import (
    APIConnectionError,
    APIError,
    APIResponseValidationError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    WowError,
)
from wow._response import APIResponse
from wow._sync._client import Client
from wow._types import Locale, NamespaceKind, Region
from wow.search import Not, Range

__all__ = [
    "APIConnectionError",
    "APIError",
    "APIResponse",
    "APIResponseValidationError",
    "APIStatusError",
    "APITimeoutError",
    "AsyncClient",
    "AuthenticationError",
    "BadRequestError",
    "Client",
    "InternalServerError",
    "Locale",
    "NamespaceKind",
    "Not",
    "NotFoundError",
    "OAuthToken",
    "PermissionDeniedError",
    "Range",
    "RateLimitError",
    "Region",
    "WowError",
]
