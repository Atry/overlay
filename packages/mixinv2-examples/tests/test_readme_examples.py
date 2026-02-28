"""Runnable versions of all code examples shown in the RST tutorial.

Each test function mirrors a section in the tutorial walkthrough so the
examples are guaranteed to be correct and up-to-date.

Examples use standard-library modules only:
- `sqlite3` for the database layer
- `http.server` for the HTTP layer
"""

import sqlite3
import threading
import urllib.request
from concurrent.futures import Future
from dataclasses import dataclass
from types import ModuleType
from mixinv2 import LexicalReference
from mixinv2 import extend, extern, public, resource, scope
from mixinv2._runtime import evaluate

from mixinv2_examples.app_decorator.step1_services import (
    SQLiteDatabase as Step1SQLiteDatabase,
    UserRepository as Step1UserRepository,
)
from mixinv2_examples.app_decorator.step2_patch import Base, HighLoad
from mixinv2_examples.app_decorator.step2_merge import (
    ForeignKeys,
    PragmaBase as MergePragmaBase,
    WalMode,
)
from mixinv2_examples.app_decorator.step2_patch_extern import (
    PragmaBase as ExternPragmaBase,
    UserVersionPragma,
)
from mixinv2_examples.app_decorator.step3_eager import (
    SQLiteDatabase as EagerSQLiteDatabase,
)
from mixinv2_examples.app_decorator.step4_http_server import (
    HttpHandlers,
    NetworkServer,
    SQLiteDatabase as Step4SQLiteDatabase,
    UserRepository as Step4UserRepository,
    app as step4_app,
)


# ---------------------------------------------------------------------------
# Step 1 – Define services with @scope and @resource
# ---------------------------------------------------------------------------


class TestStep1BasicServices:
    """Tutorial Step 1: @scope, @resource, @public, @extern, evaluate()."""

    def test_extern_and_flat_composition(self) -> None:
        """@extern + multi-scope union-mount: each scope owns its own config."""

        app = evaluate(Step1SQLiteDatabase, Step1UserRepository)
        root = app(database_path=":memory:")
        assert root.user_count == 0
        root.connection.close()


# ---------------------------------------------------------------------------
# Step 2 – Layer cross-cutting concerns with @patch and @merge
# ---------------------------------------------------------------------------


class TestStep2PatchAndMerge:
    """Tutorial Step 2: @patch applies a transformation; @merge sets aggregation."""

    def test_patch_overrides_resource(self) -> None:
        """A @patch wraps a @resource value with a transformation."""

        root = evaluate(Base, HighLoad)
        assert root.max_connections == 20         # 10 * 2

    def test_merge_collects_patches_into_frozenset(self) -> None:
        """@merge defines the aggregation strategy for collected @patch values."""

        root = evaluate(MergePragmaBase, WalMode, ForeignKeys)
        assert root.startup_pragmas == frozenset(
            {"PRAGMA journal_mode=WAL", "PRAGMA foreign_keys=ON"}
        )

    def test_patch_with_dependency_injection(self) -> None:
        """A @patch can itself declare @extern dependencies, provided as kwargs."""

        app = evaluate(ExternPragmaBase, UserVersionPragma)
        root = app(schema_version=3)
        assert root.startup_pragmas == frozenset({"PRAGMA user_version=3"})


# ---------------------------------------------------------------------------
# Step 3 – @eager: force evaluation at startup
# ---------------------------------------------------------------------------


class TestStep3Eager:
    """Tutorial Step 3: @eager resources are evaluated immediately on scope creation."""

    def test_eager_runs_schema_migration_at_startup(self) -> None:
        """Schema migration runs immediately when evaluate() returns."""

        root = evaluate(EagerSQLiteDatabase)
        tables = root.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        assert ("users",) in tables
        root.connection.close()

    def test_lazy_connection_not_opened_until_accessed(self) -> None:
        opened: list[str] = []

        @scope
        class SQLiteDatabase:
            @public
            @resource  # no @eager
            def connection() -> sqlite3.Connection:
                opened.append("opened")
                return sqlite3.connect(":memory:")

        root = evaluate(SQLiteDatabase)
        assert opened == []  # connection not opened yet

        conn = root.connection
        assert opened == ["opened"]
        conn.close()


# ---------------------------------------------------------------------------
# Step 4 – App scope vs request scope: HTTP server with SQLite
#
# SQLiteDatabase owns its own config (database_path) and provides connection.
# AppServices declares @extern connection (its dependency on the DB layer),
# owns its own config (host, port), and contains RequestScope as a nested
# scope because request lifetime differs from app lifetime.
#
# Each scope declares only the @extern it needs — no shared Config scope.
# ---------------------------------------------------------------------------


class TestStep4HttpServer:
    """Tutorial Step 4: app scope vs request scope."""

    def test_app_and_request_scope(self) -> None:
        """Three scopes union-mounted flat; each owns its config.
        UserRepository is a @scope providing business-level resources.
        UserRepository.RequestScope provides per-request DB resources.
        HttpHandlers.RequestScope extracts user_id from the HTTP request.
        The union-mount wires user_id → current_user automatically.
        """

        module = ModuleType("step4_app_module")
        module.SQLiteDatabase = Step4SQLiteDatabase  # type: ignore[attr-defined]
        module.UserRepository = Step4UserRepository  # type: ignore[attr-defined]
        module.HttpHandlers = HttpHandlers  # type: ignore[attr-defined]
        module.NetworkServer = NetworkServer  # type: ignore[attr-defined]
        module.app = step4_app  # type: ignore[attr-defined]

        app_instance = evaluate(module, modules_public=True).app(
            database_path=":memory:",
            host="127.0.0.1",
            port=0,  # OS assigns a free port
        )

        server = app_instance.server
        server_thread = threading.Thread(target=server.handle_request, daemon=True)
        server_thread.start()

        assigned_port = server.server_address[1]
        response = urllib.request.urlopen(
            f"http://127.0.0.1:{assigned_port}/users/1"
        )
        assert response.read() == b"total=2 current=alice"

        server_thread.join(timeout=2)
        server.server_close()
        app_instance.connection.close()

    def test_request_scope_created_fresh_per_request(self) -> None:
        """Each call to RequestScope(...) produces an independent InstanceScope."""

        @scope
        class AppServices:
            @public
            @scope
            class RequestScope:
                @extern
                def request_id() -> int: ...

                @public
                @resource
                def label(request_id: int) -> str:
                    return f"request-{request_id}"

        app = evaluate(AppServices)

        scope_a = app.RequestScope(request_id=1)
        scope_b = app.RequestScope(request_id=2)

        assert scope_a.label == "request-1"
        assert scope_b.label == "request-2"

    def test_write_operation_via_future_injection(self) -> None:
        """Write operations: inject a Future at call time; the resource resolves it."""

        @dataclass
        class User:
            user_id: int
            name: str

        @scope
        class SQLiteDatabase:
            @extern
            def database_path() -> str: ...

            @public
            @resource
            def connection(database_path: str) -> sqlite3.Connection:
                db = sqlite3.connect(database_path, check_same_thread=False)
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
            def user_count(connection: sqlite3.Connection) -> int:
                (count,) = connection.execute(
                    "SELECT COUNT(*) FROM users"
                ).fetchone()
                return count

            @public
            @scope
            class RequestScope:
                # Caller creates a Future and passes it in; this resource resolves it.
                @extern
                def user_created_future() -> "Future[User]": ...

                @public
                @resource
                def user_created(
                    connection: sqlite3.Connection,
                    user_created_future: "Future[User]",
                ) -> None:
                    cursor = connection.execute(
                        "INSERT INTO users (name) VALUES (?)", ("alice",)
                    )
                    connection.commit()
                    user_created_future.set_result(
                        User(user_id=cursor.lastrowid, name="alice")
                    )

        @extend(
            LexicalReference(path=("SQLiteDatabase",)),
            LexicalReference(path=("UserRepository",)),
        )
        @public
        @scope
        class app:
            pass

        module = ModuleType("write_op_module")
        module.SQLiteDatabase = SQLiteDatabase  # type: ignore[attr-defined]
        module.UserRepository = UserRepository  # type: ignore[attr-defined]
        module.app = app  # type: ignore[attr-defined]

        app_instance = evaluate(module, modules_public=True).app(
            database_path=":memory:",
        )

        # Write: caller creates the Future, injects it, accesses the resource.
        future: Future[User] = Future()
        request_scope = app_instance.RequestScope(user_created_future=future)
        request_scope.user_created  # triggers the insert and resolves the future

        new_user = future.result()
        assert new_user == User(user_id=1, name="alice")
        assert app_instance.user_count == 1  # app-scoped count is still cached from before insert

        app_instance.connection.close()
