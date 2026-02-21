"""sequence[index] -> element"""

from overlay.language import extern, public, resource


@extern
def sequence() -> object: ...


@extern
def index() -> int: ...


@public
@resource
def element(sequence: object, index: int) -> object:
    return sequence[index]  # type: ignore[index]
