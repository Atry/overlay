"""int(string) -> int"""

from overlay.language import extern, public, resource


@extern
def string() -> str: ...


@public
@resource
def value(string: str) -> int:
    return int(string)
