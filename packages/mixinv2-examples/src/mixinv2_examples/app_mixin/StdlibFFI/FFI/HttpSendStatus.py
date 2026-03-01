"""request.send_response(statusCode) -> request"""

from http.server import BaseHTTPRequestHandler

from mixinv2 import extern, public, resource


@extern
def request() -> BaseHTTPRequestHandler: ...


@extern
def statusCode() -> int: ...


@public
@resource
def sent(request: BaseHTTPRequestHandler, statusCode: int) -> BaseHTTPRequestHandler:
    request.send_response(statusCode)
    return request
