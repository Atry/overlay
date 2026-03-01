"""int(request.url.path.split(pathSeparator)[-1]) -> userId"""

from collections.abc import Awaitable
from typing import Protocol

from mixinv2 import extern, public, resource

from ._async_resource import async_resource


class _URL(Protocol):
    path: str


class _RequestWithURL(Protocol):
    url: _URL


@extern
def request() -> Awaitable[_RequestWithURL]: ...


@extern
def pathSeparator() -> Awaitable[str]: ...


@public
@resource
@async_resource
async def userId(request: _RequestWithURL, pathSeparator: str) -> int:
    return int(request.url.path.split(pathSeparator)[-1])
