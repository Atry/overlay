"""int(request.path.split(pathSeparator)[-1]) -> userId"""

from typing import Protocol

from mixinv2 import extern, public, resource


class _RequestWithPath(Protocol):
    path: str


@extern
def request() -> _RequestWithPath: ...


@extern
def pathSeparator() -> str: ...


@public
@resource
def userId(request: _RequestWithPath, pathSeparator: str) -> int:
    return int(request.path.split(pathSeparator)[-1])
