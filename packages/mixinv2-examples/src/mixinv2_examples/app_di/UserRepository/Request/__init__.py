"""UserRepository.Request: per-request DB resources wired via union-mount."""

import sqlite3
from typing import Callable

from mixinv2 import extern, public, resource


@extern
def userId() -> int: ...  # provided by HttpHandlers.Request


@public
@resource
def currentUser(
    connection: sqlite3.Connection, userId: int, User: Callable
) -> object:
    row = connection.execute(
        "SELECT id, name FROM users WHERE id = ?", (userId,)
    ).fetchone()
    assert row is not None, f"no user with id={userId}"
    identifier, name = row
    return User(userId=identifier, name=name)
