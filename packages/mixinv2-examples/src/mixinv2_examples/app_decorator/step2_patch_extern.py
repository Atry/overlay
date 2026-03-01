"""Step 2: @patch with @extern dependencies, provided as kwargs."""

from typing import Callable, Iterator

from mixinv2 import extern, merge, patch, public, scope


# [docs:step2-patch-extern]
@scope
class PragmaBase:
    @public
    @merge
    def startupPragmas() -> Callable[[Iterator[str]], frozenset[str]]:
        return frozenset

@scope
class UserVersionPragma:
    @extern
    def schemaVersion() -> int: ...     # provided as a kwarg at call time

    @patch
    def startupPragmas(schemaVersion: int) -> str:
        return f"PRAGMA user_version={schemaVersion}"
# [/docs:step2-patch-extern]
