"""ForeignKeys: contributes foreign key enforcement pragma."""

from mixinv2 import patch


@patch
def startupPragmas() -> str:
    return "PRAGMA foreign_keys=ON"
