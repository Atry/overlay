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

import mixinv2_examples.app_decorator.step4_write_op as step4_write_op
import mixinv2_examples.app_decorator.step4_http_server as step4_http_server
from mixinv2 import extern, public, resource, scope
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


# ---------------------------------------------------------------------------
# Step 1 – Define services with @scope and @resource
# ---------------------------------------------------------------------------


class TestStep1BasicServices:
    """Tutorial Step 1: @scope, @resource, @public, @extern, evaluate()."""

    def test_extern_and_flat_composition(self) -> None:
        """@extern + multi-scope union-mount: each scope owns its own config."""

        app = evaluate(Step1SQLiteDatabase, Step1UserRepository)
        root = app(databasePath=":memory:")
        assert root.userCount == 0
        root.connection.close()


# ---------------------------------------------------------------------------
# Step 2 – Layer cross-cutting concerns with @patch and @merge
# ---------------------------------------------------------------------------


class TestStep2PatchAndMerge:
    """Tutorial Step 2: @patch applies a transformation; @merge sets aggregation."""

    def test_patch_overrides_resource(self) -> None:
        """A @patch wraps a @resource value with a transformation."""

        root = evaluate(Base, HighLoad)
        assert root.maxConnections == 20         # 10 * 2

    def test_merge_collects_patches_into_frozenset(self) -> None:
        """@merge defines the aggregation strategy for collected @patch values."""

        root = evaluate(MergePragmaBase, WalMode, ForeignKeys)
        assert root.startupPragmas == frozenset(
            {"PRAGMA journal_mode=WAL", "PRAGMA foreign_keys=ON"}
        )

    def test_patch_with_dependency_injection(self) -> None:
        """A @patch can itself declare @extern dependencies, provided as kwargs."""

        app = evaluate(ExternPragmaBase, UserVersionPragma)
        root = app(schemaVersion=3)
        assert root.startupPragmas == frozenset({"PRAGMA user_version=3"})


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
# SQLiteDatabase owns its own config (databasePath) and provides connection.
# AppServices declares @extern connection (its dependency on the DB layer),
# owns its own config (host, port), and contains Request as a nested
# scope because request lifetime differs from app lifetime.
#
# Each scope declares only the @extern it needs — no shared Config scope.
# ---------------------------------------------------------------------------


class TestStep4HttpServer:
    """Tutorial Step 4: app scope vs request scope."""

    def test_app_and_request_scope(self) -> None:
        """Three scopes union-mounted flat; each owns its config.
        UserRepository is a @scope providing business-level resources.
        UserRepository.Request provides per-request DB resources.
        HttpHandlers.Request extracts userId from the HTTP request.
        The union-mount wires userId → currentUser automatically.
        """

        app_instance = evaluate(step4_http_server, modules_public=True).App(
            databasePath=":memory:",
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
        """Each call to Request(...) produces an independent InstanceScope."""

        @scope
        class AppServices:
            @public
            @scope
            class Request:
                @extern
                def requestId() -> int: ...

                @public
                @resource
                def label(requestId: int) -> str:
                    return f"request-{requestId}"

        app = evaluate(AppServices)

        scope_a = app.Request(requestId=1)
        scope_b = app.Request(requestId=2)

        assert scope_a.label == "request-1"
        assert scope_b.label == "request-2"

    def test_write_operation_via_future_injection(self) -> None:
        """Write operations: inject a Future at call time; the resource resolves it."""
        app_instance = evaluate(step4_write_op, modules_public=True).App(
            databasePath=":memory:",
        )

        # Write: caller creates the Future, injects it, accesses the resource.
        future: Future[step4_write_op.User] = Future()
        request_scope = app_instance.Request(userCreatedFuture=future)
        request_scope.userCreated  # triggers the insert and resolves the future

        new_user = future.result()
        assert new_user == step4_write_op.User(user_id=1, name="alice")
        assert app_instance.userCount == 1  # app-scoped count is still cached from before insert

        app_instance.connection.close()
