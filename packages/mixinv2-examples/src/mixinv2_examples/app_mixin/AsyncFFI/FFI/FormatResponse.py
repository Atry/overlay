"""template.format(total=userCount, current=currentUserName).encode() -> responseBody"""

from collections.abc import Awaitable

from mixinv2 import extern, public, resource

from ._async_resource import async_resource


@extern
def responseTemplate() -> Awaitable[str]: ...


@extern
def userCount() -> Awaitable[int]: ...


@extern
def currentUserName() -> Awaitable[str]: ...


@public
@resource
@async_resource
async def responseBody(
    responseTemplate: str, userCount: int, currentUserName: str
) -> bytes:
    return responseTemplate.format(
        total=userCount, current=currentUserName
    ).encode()
