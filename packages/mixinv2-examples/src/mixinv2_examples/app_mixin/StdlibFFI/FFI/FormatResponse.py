"""template.format(total=userCount, current=currentUserName).encode() -> responseBody"""

from mixinv2 import extern, public, resource


@extern
def responseTemplate() -> str: ...


@extern
def userCount() -> int: ...


@extern
def currentUserName() -> str: ...


@public
@resource
def responseBody(responseTemplate: str, userCount: int, currentUserName: str) -> bytes:
    return responseTemplate.format(total=userCount, current=currentUserName).encode()
