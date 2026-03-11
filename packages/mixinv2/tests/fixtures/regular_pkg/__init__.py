"""A regular package for testing."""

from mixinv2 import public, resource


@public
@resource
def pkg_value() -> str:
    return "from_pkg"
