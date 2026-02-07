"""Nested package for testing lazy import de_bruijn_index."""
from mixinject import public, resource


@public
@resource
def root_value() -> str:
    return "from_root"
