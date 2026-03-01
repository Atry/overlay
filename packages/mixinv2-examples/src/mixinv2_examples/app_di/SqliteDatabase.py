"""SQLiteDatabase module: owns databasePath config, provides connection."""

import sqlite3

from mixinv2 import extern, public, resource


@extern
def databasePath() -> str: ...


@public
@resource
def connection(databasePath: str) -> sqlite3.Connection:
    db = sqlite3.connect(databasePath, check_same_thread=False)
    db.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    db.execute("INSERT INTO users VALUES (1, 'alice')")
    db.execute("INSERT INTO users VALUES (2, 'bob')")
    db.commit()
    return db
