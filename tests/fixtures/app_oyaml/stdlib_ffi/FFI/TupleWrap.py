"""(element,) -> 1-tuple"""

from overlay.language import extern, public, resource


@extern
def element() -> object: ...


@public
@resource
def wrapped(element: object) -> tuple:
    return (element,)
