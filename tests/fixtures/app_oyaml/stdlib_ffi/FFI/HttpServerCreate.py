"""HTTPServer((host, port), handler_class)"""

from http.server import HTTPServer

from overlay.language import extern, public, resource


@extern
def host() -> str: ...


@extern
def port() -> int: ...


@extern
def handler_class() -> type: ...


@public
@resource
def server(host: str, port: int, handler_class: type) -> HTTPServer:
    return HTTPServer((host, port), handler_class)
