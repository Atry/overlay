"""int(request.path.split(path_separator)[-1]) -> user_id"""

from http.server import BaseHTTPRequestHandler

from overlay.language import extern, public, resource


@extern
def request() -> BaseHTTPRequestHandler: ...


@extern
def path_separator() -> str: ...


@public
@resource
def user_id(request: BaseHTTPRequestHandler, path_separator: str) -> int:
    return int(request.path.split(path_separator)[-1])
