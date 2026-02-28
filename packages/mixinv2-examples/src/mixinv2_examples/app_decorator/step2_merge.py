"""Step 2: @merge defines the aggregation strategy for collected @patch values."""

from typing import Callable, Iterator

from mixinv2 import merge, patch, public, scope


# [docs:step2-merge]
@scope
class PragmaBase:
    @public
    @merge
    def startup_pragmas() -> Callable[[Iterator[str]], frozenset[str]]:
        return frozenset                  # aggregation strategy: collect into frozenset

@scope
class WalMode:
    @patch
    def startup_pragmas() -> str:
        return "PRAGMA journal_mode=WAL"

@scope
class ForeignKeys:
    @patch
    def startup_pragmas() -> str:
        return "PRAGMA foreign_keys=ON"
# [/docs:step2-merge]
