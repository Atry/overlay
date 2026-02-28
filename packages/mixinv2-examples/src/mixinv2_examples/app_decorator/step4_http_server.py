"""Step 4: app scope vs request scope — full HTTP server with SQLite."""

import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Callable, Protocol

from mixinv2 import LexicalReference
from mixinv2 import extend, extern, public, resource, scope


@scope
class SQLiteDatabase:
    @extern
    def database_path() -> str: ...    # database owns its own config

    # App-scoped: one connection for the entire process lifetime.
    # check_same_thread=False: created in main thread, used in handler threads.
    @public
    @resource
    def connection(database_path: str) -> sqlite3.Connection:
        db = sqlite3.connect(database_path, check_same_thread=False)
        db.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"
        )
        db.execute("INSERT INTO users VALUES (1, 'alice')")
        db.execute("INSERT INTO users VALUES (2, 'bob')")
        db.commit()
        return db

@scope
class UserRepository:
    @extern
    def connection() -> sqlite3.Connection: ...

    # @scope as a composable dataclass — fields are @extern, constructed via DI.
    @public
    @scope
    class User:
        @public
        @extern
        def user_id() -> int: ...

        @public
        @extern
        def name() -> str: ...

    # App-scoped: total count across all requests.
    @public
    @resource
    def user_count(connection: sqlite3.Connection) -> int:
        (count,) = connection.execute(
            "SELECT COUNT(*) FROM users"
        ).fetchone()
        return count

    # Request-scoped: per-request DB resources, wired by overlay union-mount.
    @public
    @scope
    class RequestScope:
        @extern
        def user_id() -> int: ...  # provided by HttpHandlers.RequestScope

        @public
        @resource
        def current_user(
            connection: sqlite3.Connection, user_id: int, User: Callable
        ) -> object:
            row = connection.execute(
                "SELECT id, name FROM users WHERE id = ?", (user_id,)
            ).fetchone()
            assert row is not None, f"no user with id={user_id}"
            identifier, name = row
            return User(user_id=identifier, name=name)

@scope
class HttpHandlers:
    @extern
    def user_count() -> int: ...

    # RequestScope is nested because its lifetime is per-request,
    # not per-application.
    @public
    @scope
    class RequestScope:
        class _RequestWithPath(Protocol):
            path: str

        @extern
        def request() -> BaseHTTPRequestHandler: ...

        @extern
        def current_user() -> object: ...

        # user_id is extracted from the request and injected into
        # UserRepository.RequestScope.current_user automatically.
        @public
        @resource
        def user_id(request: _RequestWithPath) -> int:
            return int(request.path.split("/")[-1])

        @public
        @resource
        def response_body(user_count: int, current_user: object) -> bytes:
            return (
                f"total={user_count} current={current_user.name}"
            ).encode()

        # IO resource: sends the HTTP response as a side effect.
        @public
        @resource
        def response_sent(
            request: BaseHTTPRequestHandler,
            response_body: bytes,
        ) -> None:
            request.send_response(200)
            request.end_headers()
            request.wfile.write(response_body)

@scope
class NetworkServer:
    @extern
    def host() -> str: ...             # network layer owns its own config

    @extern
    def port() -> int: ...

    @scope
    class RequestScope:
        pass

    # RequestScope is injected by name as a Callable (StaticScope).
    # Calling RequestScope(request=handler) returns a fresh InstanceScope.
    @public
    @resource
    def server(host: str, port: int, RequestScope: Callable) -> HTTPServer:
        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                RequestScope(request=self).response_sent

            def log_message(self, format: str, *arguments: object) -> None:
                pass

        return HTTPServer((host, port), Handler)

@extend(
    LexicalReference(path=("SQLiteDatabase",)),
    LexicalReference(path=("UserRepository",)),
    LexicalReference(path=("HttpHandlers",)),
    LexicalReference(path=("NetworkServer",)),
)
@public
@scope
class app:
    pass
