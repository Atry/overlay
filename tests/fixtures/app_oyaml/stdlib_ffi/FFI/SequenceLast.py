"""sequence[-1] -> last element"""

from overlay.language import extern, public, resource


@extern
def sequence() -> tuple: ...


@public
@resource
def element(sequence: tuple) -> object:
    *_, last = sequence
    return last
