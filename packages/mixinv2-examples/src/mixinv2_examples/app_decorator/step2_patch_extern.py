"""Step 2: @patch with @extern dependencies, provided as kwargs."""

from typing import Callable, Iterator

from mixinv2 import extern, merge, patch, public, scope


# [docs:step2-patch-extern]
@scope
class PragmaBase:
    @public
    @merge
    def startup_pragmas() -> Callable[[Iterator[str]], frozenset[str]]:
        return frozenset

@scope
class UserVersionPragma:
    @extern
    def schema_version() -> int: ...     # provided as a kwarg at call time

    @patch
    def startup_pragmas(schema_version: int) -> str:
        return f"PRAGMA user_version={schema_version}"
# [/docs:step2-patch-extern]
