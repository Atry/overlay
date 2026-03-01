"""PragmaBase: defines the aggregation strategy for startupPragmas."""

from typing import Callable, Iterator

from mixinv2 import merge, public


@public
@merge
def startupPragmas() -> Callable[[Iterator[str]], frozenset[str]]:
    return frozenset
