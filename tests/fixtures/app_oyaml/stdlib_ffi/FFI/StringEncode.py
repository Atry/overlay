"""string.encode() -> bytes"""

from overlay.language import extern, public, resource


@extern
def string() -> str: ...


@public
@resource
def encoded(string: str) -> bytes:
    return string.encode()
