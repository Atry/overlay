"""Module A in namespace package."""

from mixinv2 import public, resource


@public
@resource
def value_a() -> str:
    return "a"
