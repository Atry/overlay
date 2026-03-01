"""Step 1: @scope, @resource, @public, @extern, evaluate()."""

import sqlite3

from mixinv2 import extern, public, resource, scope


# [docs:step1-define-services]
@scope
class SQLiteDatabase:
    @extern
    def databasePath() -> str: ...       # caller must provide this

    @public
    @resource
    def connection(databasePath: str) -> sqlite3.Connection:
        return sqlite3.connect(databasePath)

@scope
class UserRepository:
    @public
    @resource
    def userCount(connection: sqlite3.Connection) -> int:
        connection.execute(
            "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)"
        )
        (count,) = connection.execute("SELECT COUNT(*) FROM users").fetchone()
        return count
# [/docs:step1-define-services]
