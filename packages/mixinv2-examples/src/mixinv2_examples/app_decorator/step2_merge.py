"""Step 2: @merge defines the aggregation strategy for collected @patch values."""

from typing import Callable, Iterator

from mixinv2 import merge, patch, public, scope


# [docs:step2-merge]
@scope
class PragmaBase:
    @public
    @merge
    def startupPragmas() -> Callable[[Iterator[str]], frozenset[str]]:
        return frozenset                  # aggregation strategy: collect into frozenset

@scope
class WalMode:
    @patch
    def startupPragmas() -> str:
        return "PRAGMA journal_mode=WAL"

@scope
class ForeignKeys:
    @patch
    def startupPragmas() -> str:
        return "PRAGMA foreign_keys=ON"
# [/docs:step2-merge]
