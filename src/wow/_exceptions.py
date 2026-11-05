"""Exceptions raised by the client.

Everything derives from :class:`WowError`. HTTP failures carry the response, so callers can read headers such as
``battlenet-namespace`` from the error itself.
"""

from typing import TYPE_CHECKING, Any

import httpx

if TYPE_CHECKING:
    from msgspec import DecodeError

__all__ = [
    "APIConnectionError",
    "APIError",
    "APIResponseValidationError",
    "APIStatusError",
    "APITimeoutError",
    "AuthenticationError",
    "BadRequestError",
    "InternalServerError",
    "NotFoundError",
    "PermissionDeniedError",
    "RateLimitError",
    "WowError",
]


class WowError(Exception):
    """Base class for every error this package raises."""


class APIError(WowError):
    """A request to Battle.net failed.

    Attributes:
        request: The request that failed. Its ``Authorization`` header holds the live bearer token: ``repr`` hides
            it, but do not log or serialize ``request.headers`` wholesale.
    """

    request: httpx.Request

    def __init__(self, message: str, *, request: httpx.Request) -> None:
        super().__init__(message)
        self.request = request


class APIConnectionError(APIError):
    """The request never produced a response: DNS, TLS, refused or reset connections."""


class APITimeoutError(APIConnectionError):
    """The request timed out."""


class APIResponseValidationError(APIError):
    """The response did not match the model it was parsed into.

    Attributes:
        response: The response whose body failed validation.
    """

    response: httpx.Response

    def __init__(self, message: str, *, response: httpx.Response, error: DecodeError) -> None:
        super().__init__(message, request=response.request)
        self.response = response
        self.__cause__ = error


class APIStatusError(APIError):
    """Battle.net answered with a 4xx or 5xx status.

    Attributes:
        response: The error response.
        status_code: Its HTTP status.
        body: The decoded JSON body, or the raw text when it is not JSON.
        namespace: The ``battlenet-namespace`` header, which Battle.net sends only when it recognised the namespace.
    """

    response: httpx.Response
    status_code: int
    body: Any
    namespace: str | None

    def __init__(self, message: str, *, response: httpx.Response, body: Any) -> None:  # noqa: ANN401 - arbitrary JSON
        super().__init__(message, request=response.request)
        self.response = response
        self.status_code = response.status_code
        self.body = body
        self.namespace = response.headers.get("battlenet-namespace")


class BadRequestError(APIStatusError):
    """HTTP 400: a malformed request, such as an invalid search filter."""


class AuthenticationError(APIStatusError):
    """HTTP 401: the access token is missing, expired or revoked, or the client credentials were rejected."""


class PermissionDeniedError(APIStatusError):
    """HTTP 403: the namespace does not exist, or the token lacks the scope the route needs.

    Profile routes such as the account profile need a user token with the ``wow.profile`` scope.
    """


class NotFoundError(APIStatusError):
    """HTTP 404: no document at this path.

    When :attr:`namespace` is set the namespace exists and the document does not, which is how much of WoW Forever
    looks while Blizzard is still publishing it.
    """


class RateLimitError(APIStatusError):
    """HTTP 429: the client exceeded Battle.net's request quota, even after retrying."""


class InternalServerError(APIStatusError):
    """HTTP 5xx: Battle.net failed, even after retrying."""


_STATUS_ERRORS: dict[int, type[APIStatusError]] = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    429: RateLimitError,
}


def error_for_response(response: httpx.Response) -> APIStatusError:
    """Build the exception that matches a failed response."""
    try:
        body: Any = response.json()
    except ValueError:
        body = response.text
    detail = (body.get("detail") or body.get("error_description")) if isinstance(body, dict) else None
    message = f"{response.status_code} {detail or response.reason_phrase} for {response.request.url}"
    status = response.status_code
    cls = (
        InternalServerError
        if status >= httpx.codes.INTERNAL_SERVER_ERROR
        else _STATUS_ERRORS.get(status, APIStatusError)
    )
    return cls(message, response=response, body=body)
