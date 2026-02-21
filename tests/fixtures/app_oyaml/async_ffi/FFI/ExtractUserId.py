"""int(request.url.path.split(path_separator)[-1]) -> user_id"""

from collections.abc import Awaitable

from starlette.requests import Request

from overlay.language import extern, public, resource

from ._async_resource import async_resource


@extern
def request() -> Awaitable[Request]: ...


@extern
def path_separator() -> Awaitable[str]: ...


@public
@resource
@async_resource
async def user_id(request: Request, path_separator: str) -> int:
    return int(request.url.path.split(path_separator)[-1])
