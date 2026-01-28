"""A child module within regular_pkg."""

from mixinject import public, resource


@public
@resource
def child_value() -> str:
    return "from_child"
