"""A regular module (not a package) for testing."""

from mixinv2 import resource


@resource
def value() -> int:
    return 123
