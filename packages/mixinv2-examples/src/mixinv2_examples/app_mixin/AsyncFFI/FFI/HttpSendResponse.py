"""Construct a starlette Response -> written.

In the async/starlette model, we return a Response object instead of
mutating a request handler.  The resource name stays `written` for
compatibility with Library.mixin.yaml's `response: [Request, ~, written]`.
"""

from collections.abc import Awaitable

from starlette.requests import Request
from starlette.responses import Response

from mixinv2 import extern, public, resource

from ._async_resource import async_resource


@extern
def request() -> Awaitable[Request]: ...


@extern
def statusCode() -> int: ...


@extern
def body() -> Awaitable[bytes]: ...


@public
@resource
@async_resource
async def written(request: Request, statusCode: int, body: bytes) -> Response:
    return Response(content=body, status_code=statusCode)
