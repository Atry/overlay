"""Step 3: @eager resources are evaluated immediately on scope creation."""

import sqlite3

from mixinv2 import eager, public, resource, scope


# [docs:step3-eager]
@scope
class SQLiteDatabase:
    @public
    @eager
    @resource
    def connection() -> sqlite3.Connection:
        db = sqlite3.connect(":memory:")
        db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
        db.commit()
        return db
# [/docs:step3-eager]
