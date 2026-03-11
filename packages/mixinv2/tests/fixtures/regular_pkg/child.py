"""A child module within regular_pkg."""

from mixinv2 import public, resource


@public
@resource
def child_value() -> str:
    return "from_child"
