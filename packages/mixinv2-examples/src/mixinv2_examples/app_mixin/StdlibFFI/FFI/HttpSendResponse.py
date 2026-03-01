"""send_response(statusCode) + end_headers() + wfile.write(body) -> written"""

from http.server import BaseHTTPRequestHandler

from mixinv2 import extern, public, resource


@extern
def request() -> BaseHTTPRequestHandler: ...


@extern
def statusCode() -> int: ...


@extern
def body() -> bytes: ...


@public
@resource
def written(
    request: BaseHTTPRequestHandler, statusCode: int, body: bytes
) -> BaseHTTPRequestHandler:
    request.send_response(statusCode)
    request.end_headers()
    request.wfile.write(body)
    return request
