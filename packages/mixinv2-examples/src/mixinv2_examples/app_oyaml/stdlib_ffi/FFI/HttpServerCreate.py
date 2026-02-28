"""HTTPServer((host, port), handler_class)"""

from http.server import HTTPServer

from mixinv2 import extern, public, resource


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


@public
@resource
def serve_forever(server: HTTPServer) -> None:
    host, port = server.server_address
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()
