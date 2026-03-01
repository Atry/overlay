"""Step 4 variant: Future-based injection for INSERT + commit."""

import sqlite3
from concurrent.futures import Future
from dataclasses import dataclass

from mixinv2 import LexicalReference
from mixinv2 import extend, extern, public, resource, scope


@dataclass
class User:
    user_id: int
    name: str


@scope
class SQLiteDatabase:
    @extern
    def databasePath() -> str: ...

    @public
    @resource
    def connection(databasePath: str) -> sqlite3.Connection:
        db = sqlite3.connect(databasePath, check_same_thread=False)
        db.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
        )
        db.commit()
        return db


@scope
class UserRepository:
    @extern
    def connection() -> sqlite3.Connection: ...

    @public
    @resource
    def userCount(connection: sqlite3.Connection) -> int:
        (count,) = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()
        return count

    @public
    @scope
    class Request:
        # Caller creates a Future and passes it in; this resource resolves it.
        @extern
        def userCreatedFuture() -> "Future[User]": ...

        @public
        @resource
        def userCreated(
            connection: sqlite3.Connection,
            userCreatedFuture: "Future[User]",
        ) -> None:
            cursor = connection.execute(
                "INSERT INTO users (name) VALUES (?)", ("alice",)
            )
            connection.commit()
            userCreatedFuture.set_result(
                User(user_id=cursor.lastrowid, name="alice")
            )


@extend(
    LexicalReference(path=("SQLiteDatabase",)),
    LexicalReference(path=("UserRepository",)),
)
@public
@scope
class App:
    pass
