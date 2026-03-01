"""HttpHandlers.Request: extracts request-scoped values from the HTTP request."""

from http.server import BaseHTTPRequestHandler
from typing import Protocol

from mixinv2 import extern, public, resource


class _RequestWithPath(Protocol):
    path: str


@extern
def request() -> BaseHTTPRequestHandler: ...


@extern
def currentUser() -> object: ...


@public
@resource
def userId(request: _RequestWithPath) -> int:
    return int(request.path.split("/")[-1])


@public
@resource
def responseBody(userCount: int, currentUser: object) -> bytes:
    return f"total={userCount} current={currentUser.name}".encode()


@public
@resource
def responseSent(
    request: BaseHTTPRequestHandler,
    responseBody: bytes,
) -> None:
    request.send_response(200)
    request.end_headers()
    request.wfile.write(responseBody)
