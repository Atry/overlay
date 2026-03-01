"""HTTPServer((host, port), handlerClass)"""

from http.server import HTTPServer

from mixinv2 import extern, public, resource


@extern
def host() -> str: ...


@extern
def port() -> int: ...


@extern
def handlerClass() -> type: ...


@public
@resource
def server(host: str, port: int, handlerClass: type) -> HTTPServer:
    return HTTPServer((host, port), handlerClass)


@public
@resource
def serveForever(server: HTTPServer) -> None:
    host, port = server.server_address
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()
