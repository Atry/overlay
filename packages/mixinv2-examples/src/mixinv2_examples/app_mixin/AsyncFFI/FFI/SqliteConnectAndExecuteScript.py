"""aiosqlite.connect(databasePath) + executescript(setupSql) -> connection"""

from collections.abc import Awaitable

import aiosqlite

from mixinv2 import extern, public, resource

from ._async_resource import async_resource


@extern
def databasePath() -> Awaitable[str]: ...


@extern
def setupSql() -> Awaitable[str]: ...


@public
@resource
@async_resource
async def connection(
    databasePath: str, setupSql: str
) -> aiosqlite.Connection:
    connection = await aiosqlite.connect(databasePath)
    await connection.executescript(setupSql)
    return connection
