"""Raw access to a Battle.net response for callers who need headers or untyped JSON."""

import email.utils
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from wow._base import parse_model

if TYPE_CHECKING:
    from datetime import datetime

    import httpx

__all__ = ["APIResponse"]


class APIResponse:
    """A successful response from :meth:`Client.get <wow.Client.get>`.

    Typed resource methods return models directly; this wrapper is for headers, documents the package has no model
    for yet, and links followed by hand.
    """

    __slots__ = ("http_response",)

    http_response: httpx.Response
    """The underlying ``httpx`` response."""

    def __init__(self, http_response: httpx.Response) -> None:
        self.http_response = http_response

    @property
    def status_code(self) -> int:
        """The HTTP status code."""
        return self.http_response.status_code

    @property
    def url(self) -> str:
        """The URL that was requested, including query parameters."""
        return str(self.http_response.url)

    @property
    def headers(self) -> httpx.Headers:
        """The response headers."""
        return self.http_response.headers

    @property
    def namespace(self) -> str | None:
        """The namespace Battle.net resolved, such as ``static-1.60.1_70399-forever-us`` for ``static-forever-us``."""
        return self.headers.get("battlenet-namespace")

    @property
    def last_modified(self) -> datetime | None:
        """When the document last changed, from the ``Last-Modified`` header."""
        header = self.headers.get("last-modified")
        return email.utils.parsedate_to_datetime(header) if header else None

    def json(self) -> Any:  # noqa: ANN401 - arbitrary JSON, like httpx.Response.json
        """Decode the body as JSON."""
        return self.http_response.json()

    def parse[ModelT: BaseModel](self, model: type[ModelT]) -> ModelT:
        """Validate the body into ``model``.

        Raises:
            APIResponseValidationError: The body does not match ``model``.
        """
        return parse_model(self.http_response, model)
