"""Step 2: @patch applies a transformation to a @resource value."""

from typing import Callable

from mixinv2 import patch, public, resource, scope


# [docs:step2-patch]
@scope
class Base:
    @public
    @resource
    def maxConnections() -> int:
        return 10

@scope
class HighLoad:
    """Patch for high-load environments: double the connection limit."""

    @patch
    def maxConnections() -> Callable[[int], int]:
        return lambda previous: previous * 2
# [/docs:step2-patch]
