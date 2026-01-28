"""Grandchild module (two levels deep)."""
from mixinject import public, resource


@public
@resource
def grandchild_value() -> str:
    return "from_grandchild"
