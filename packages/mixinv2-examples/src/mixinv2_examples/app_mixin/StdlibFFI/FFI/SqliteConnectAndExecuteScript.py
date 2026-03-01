"""sqlite3.connect(databasePath) + executescript(setupSql) -> connection"""

import sqlite3

from mixinv2 import extern, public, resource


@extern
def databasePath() -> str: ...


@extern
def setupSql() -> str: ...


@public
@resource
def connection(databasePath: str, setupSql: str) -> sqlite3.Connection:
    conn = sqlite3.connect(databasePath, check_same_thread=False)
    conn.executescript(setupSql)
    return conn
