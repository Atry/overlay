"""Package/module-based equivalents of all code examples shown in README.md.

Each test mirrors a corresponding test in test_readme_examples.py, but uses
Python module files instead of @scope-decorated classes. The example packages
live in mixinv2_examples.app_di and mixinv2_examples.app_mixin.

The DI semantics are identical — only the declaration style differs:
  @scope class SQLiteDatabase: ...   →   SqliteDatabase.py module
  @scope class UserRepository: ...   →   UserRepository/ package
  nested @scope class Request         →   Request/ subpackage
"""

import tempfile
import threading
import urllib.request
from pathlib import Path

import pytest

import mixinv2_examples.app_decorator.remove_prefix as remove_prefix
import mixinv2_examples.app_di as app_di
import mixinv2_examples.app_di.EagerDatabase as EagerDatabase
import mixinv2_examples.app_di.Pragmas.Base as pragma_base
import mixinv2_examples.app_di.Pragmas.ForeignKeys as foreign_keys
import mixinv2_examples.app_di.Pragmas.UserVersion as user_version
import mixinv2_examples.app_di.Pragmas.WalMode as wal_mode
import mixinv2_examples.app_mixin as app_mixin

from mixinv2._mixin_directory import DirectoryMixinDefinition
from mixinv2._runtime import evaluate


# ---------------------------------------------------------------------------
# Step 1 – Define services (module equivalents)
# ---------------------------------------------------------------------------


class TestStep1ModuleServices:
    """Module/package equivalents of README Step 1 examples."""

    def test_extern_and_flat_composition(self) -> None:
        """Step1App composes SqliteDatabase + UserRepository via @extend."""
        app = evaluate(app_di, modules_public=True).Step1App(
            databasePath=":memory:",
        )
        assert app.userCount == 2
        app.connection.close()


# ---------------------------------------------------------------------------
# Step 2 – @patch and @merge (module equivalents)
# ---------------------------------------------------------------------------


class TestStep2ModulePatchAndMerge:
    """Module/package equivalents of README Step 2 examples."""

    def test_patch_overrides_resource(self) -> None:
        """WalMode.py patches startupPragmas defined in Base.py."""
        root = evaluate(pragma_base, wal_mode, modules_public=True)
        assert "PRAGMA journal_mode=WAL" in root.startupPragmas

    def test_merge_collects_patches_into_frozenset(self) -> None:
        """ForeignKeys.py and WalMode.py both patch startupPragmas."""
        root = evaluate(pragma_base, wal_mode, foreign_keys, modules_public=True)
        assert root.startupPragmas == frozenset(
            {"PRAGMA journal_mode=WAL", "PRAGMA foreign_keys=ON"}
        )

    def test_patch_with_dependency_injection(self) -> None:
        """UserVersion.py patch declares @extern schemaVersion."""
        app = evaluate(pragma_base, user_version, modules_public=True)(schemaVersion=3)
        assert app.startupPragmas == frozenset({"PRAGMA user_version=3"})


# ---------------------------------------------------------------------------
# Step 3 – @eager (module equivalent)
# ---------------------------------------------------------------------------


class TestStep3ModuleEager:
    """Module/package equivalents of README Step 3 examples."""

    def test_eager_runs_schema_migration_at_startup(self) -> None:
        """EagerDatabase.py: @eager @resource evaluated before evaluate() returns."""
        root = evaluate(EagerDatabase, modules_public=True)
        tables = root.connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        assert ("users",) in tables
        root.connection.close()


# ---------------------------------------------------------------------------
# Step 4 – App scope vs request scope (module equivalents)
# ---------------------------------------------------------------------------


class TestStep4ModuleHttpServer:
    """Module/package equivalents of README Step 4 examples."""

    def test_app_and_request_scope(self) -> None:
        """Step4App composes all four modules via @extend; request scopes union-mounted automatically."""
        app = evaluate(app_di, modules_public=True).Step4App(
            databasePath=":memory:",
            host="127.0.0.1",
            port=0,
        )

        server = app.server
        server_thread = threading.Thread(target=server.handle_request, daemon=True)
        server_thread.start()

        assigned_port = server.server_address[1]
        response = urllib.request.urlopen(f"http://127.0.0.1:{assigned_port}/users/1")
        assert response.read() == b"total=2 current=alice"

        server_thread.join(timeout=2)
        server.server_close()
        app.connection.close()

    def test_request_scope_created_fresh_per_request(self) -> None:
        """Each call to Request(...) produces an independent InstanceScope."""
        from typing import Protocol

        app = evaluate(app_di, modules_public=True).Step4RequestApp(
            databasePath=":memory:",
        )

        class _RequestWithPath(Protocol):
            path: str

        class FakeRequest:
            path = "/users/1"

        scope_a = app.Request(request=FakeRequest())
        scope_b = app.Request(request=FakeRequest())

        assert scope_a.currentUser.userId == 1
        assert scope_a.currentUser.name == "alice"
        assert scope_b.currentUser.userId == 1
        assert scope_a is not scope_b

        app.connection.close()


class TestMixinScopeClassComposition:
    """Tests mixin.yaml scalar field values overriding @extern definitions
    inside a @scope class.
    """

    def test_scope_class_with_mixin_yaml_scalar_fields(self) -> None:
        """Inherit a @scope class in mixin.yaml and provide scalar field values."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "App.mixin.yaml").write_text(
                "_greeting:\n"
                "  - [RemovePrefix]\n"
                '  - this: "Hello World"\n'
                '    prefix: "Hello "\n'
                "greeting: [_greeting, prefixRemoved]\n"
            )

            directory_definition = DirectoryMixinDefinition(
                inherits=(),
                is_public=True,
                underlying=Path(tmpdir),
            )

            root = evaluate(remove_prefix, directory_definition, modules_public=True)
            assert root.App.greeting == "World"  # type: ignore[union-attr]


# ---------------------------------------------------------------------------
# Step 4 – App scope vs request scope (mixin.yaml equivalents)
# ---------------------------------------------------------------------------


class TestMixinHttpApp:
    """Mixin.yaml equivalents of README Step 4 examples.

    Apps.mixin.yaml inherits StdlibFFI (real FFI) + Library.mixin.yaml (business logic)
    and defines memoryApp as the integration entry point.
    """

    def test_mixin_app_http_request(self) -> None:
        """memoryApp in Apps.mixin.yaml serves correct response for GET /users/1."""
        root = evaluate(app_mixin, modules_public=True)
        composed_app = root.Apps.memoryApp  # type: ignore[union-attr]

        server = composed_app.server
        server_thread = threading.Thread(target=server.handle_request, daemon=True)
        server_thread.start()

        assigned_port = server.server_address[1]
        response = urllib.request.urlopen(
            f"http://127.0.0.1:{assigned_port}/users/1"
        )
        assert response.read() == b"total=2 current=alice"

        server_thread.join(timeout=2)
        server.server_close()
        composed_app.connection.close()

    def test_mixin_app_request_scope_created_fresh_per_request(self) -> None:
        """Each call to Request(...) produces an independent scope instance."""
        from typing import Protocol

        root = evaluate(app_mixin, modules_public=True)
        composed_app = root.Apps.memoryApp  # type: ignore[union-attr]

        class _RequestWithPath(Protocol):
            path: str

        class FakeRequest:
            path = "/users/1"

        scope_a = composed_app.Request(request=FakeRequest())
        scope_b = composed_app.Request(request=FakeRequest())

        assert scope_a.currentUser.userId == 1
        assert scope_a.currentUser.name == "alice"
        assert scope_b.currentUser.userId == 1
        assert scope_a is not scope_b

        composed_app.connection.close()


# ---------------------------------------------------------------------------
# Step 4 – App scope vs request scope (async mixin.yaml equivalents)
# ---------------------------------------------------------------------------


class TestAsyncMixinHttpApp:
    """Async mixin.yaml equivalents using aiosqlite + starlette.

    AsyncApps.mixin.yaml inherits AsyncFFI (async FFI) + Library.mixin.yaml (same
    business logic) and defines memoryApp as the async integration entry.
    """

    @pytest.mark.asyncio
    async def test_async_mixin_app_http_request(self) -> None:
        """memoryApp in AsyncApps.mixin.yaml serves correct response for GET /users/1."""
        import asyncio

        import httpx

        root = evaluate(app_mixin, modules_public=True)
        composed_app = root.AsyncApps.memoryApp  # type: ignore[union-attr]

        uvicorn_server = composed_app.server
        serve_task = asyncio.create_task(uvicorn_server.serve())

        # Wait for server to start listening.
        while not uvicorn_server.started:
            await asyncio.sleep(0.01)

        host, port = uvicorn_server.servers[0].sockets[0].getsockname()

        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://{host}:{port}/users/1")

        assert response.content == b"total=2 current=alice"

        uvicorn_server.should_exit = True
        await serve_task

        connection = await composed_app.connection
        await connection.close()

    @pytest.mark.asyncio
    async def test_async_mixin_app_request_scope_values(self) -> None:
        """Async memoryApp resolves userCount correctly."""
        root = evaluate(app_mixin, modules_public=True)
        composed_app = root.AsyncApps.memoryApp  # type: ignore[union-attr]

        user_count = await composed_app.userCount
        assert user_count == 2

        connection = await composed_app.connection
        await connection.close()
