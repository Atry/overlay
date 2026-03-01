"""WalMode: contributes WAL journal mode pragma."""

from mixinv2 import patch


@patch
def startupPragmas() -> str:
    return "PRAGMA journal_mode=WAL"
