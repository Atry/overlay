"""Union mount fixtures demonstrating merge and patches use cases."""

from mixinv2 import LexicalReference
from mixinv2 import extend, public, scope


@extend(
    LexicalReference(path=("branch0",)),
    LexicalReference(path=("branch1",)),
    LexicalReference(path=("branch2",)),
)
@public
@scope
class combined:
    """Combined scope that extends branch0, branch1, and branch2 modules."""

    pass
