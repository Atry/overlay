"""
The Overlay language: A dependency injection framework with pytest-fixture-like semantics.

Public API
==========

Decorators:
    - :func:`scope`
    - :func:`resource`
    - :func:`patch`
    - :func:`patch_many`
    - :func:`merge`
    - :func:`extern`
    - :func:`public`
    - :func:`eager`
    - :func:`extend`

Runtime:
    - :func:`evaluate`
"""

# Public API: decorators and evaluate
from overlay.language._core import eager as eager
from overlay.language._core import extend as extend
from overlay.language._core import extern as extern
from overlay.language._core import merge as merge
from overlay.language._core import patch as patch
from overlay.language._core import patch_many as patch_many
from overlay.language._core import public as public
from overlay.language._core import resource as resource
from overlay.language._core import scope as scope
from overlay.language._runtime import evaluate as evaluate

# Reference types (public: used as parameters to @extend)
from overlay.language._core import AbsoluteReference as AbsoluteReference
from overlay.language._core import LexicalReference as LexicalReference
from overlay.language._core import QualifiedThisReference as QualifiedThisReference
from overlay.language._core import RelativeReference as RelativeReference
from overlay.language._core import ResourceReference as ResourceReference
