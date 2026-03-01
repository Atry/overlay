"""NetworkServer: HTTP server, owns host/port config, no business logic."""

from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable

from mixinv2 import extern, public, resource


@extern
def host() -> str: ...


@extern
def port() -> int: ...


@public
@resource
def server(host: str, port: int, Request: Callable) -> HTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            Request(request=self).responseSent

        def log_message(self, format: str, *arguments: object) -> None:
            pass

    return HTTPServer((host, port), Handler)


@public
@resource
def serveForever(server: HTTPServer) -> None:
    host, port = server.server_address
    print(f"Serving on http://{host}:{port}")
    server.serve_forever()
