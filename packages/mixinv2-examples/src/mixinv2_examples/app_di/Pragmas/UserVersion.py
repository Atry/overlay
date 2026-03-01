"""UserVersionPragma: contributes user_version pragma, depends on schemaVersion."""

from mixinv2 import extern, patch


@extern
def schemaVersion() -> int: ...


@patch
def startupPragmas(schemaVersion: int) -> str:
    return f"PRAGMA user_version={schemaVersion}"
