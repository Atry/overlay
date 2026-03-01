"""Create an async handler function that dispatches to Request."""

from collections.abc import Awaitable, Callable
from typing import Protocol

from starlette.requests import Request
from starlette.responses import Response

from mixinv2 import public, resource


class _RequestScopeInstance(Protocol):
    response: Awaitable[Response]


class _RequestScopeFactory(Protocol):
    def __call__(self, request: Request) -> _RequestScopeInstance: ...


@public
@resource
def handlerClass(Request: _RequestScopeFactory) -> Callable:
    async def handler(request: Request) -> Response:
        request_scope = Request(request=request)
        response = await request_scope.response
        return response

    return handler
