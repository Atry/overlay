"""request.path -> str"""

from http.server import BaseHTTPRequestHandler

from overlay.language import extern, public, resource


@extern
def request() -> BaseHTTPRequestHandler: ...


@public
@resource
def path(request: BaseHTTPRequestHandler) -> str:
    return request.path
