"""sqlite3.connect(databasePath, check_same_thread=False)"""

import sqlite3

from mixinv2 import extern, public, resource


@extern
def databasePath() -> str: ...


@public
@resource
def connection(databasePath: str) -> sqlite3.Connection:
    return sqlite3.connect(databasePath, check_same_thread=False)
