# MIXINv2 Examples

Example case studies demonstrating MIXINv2's DI and composition capabilities.

## Running the HTTP Server Examples

All server examples implement the same application: a user lookup
service backed by an in-memory SQLite database. Each demonstrates a
different composition style.

### MIXIN sync (OYAML + stdlib `http.server`)

Declarative OYAML composition with synchronous stdlib FFI adapters:

```
uv run mixinv2-example app_oyaml Apps memory_app serve_forever
```

### MIXIN async (OYAML + Starlette/uvicorn)

Same declarative OYAML composition, but with async FFI adapters — the
business logic (`Library.oyaml`) is identical:

```
uv run mixinv2-example app_oyaml AsyncApps memory_app serve_forever
```

### Module version (Python packages + `@extend`)

Python package-based composition using `@scope`, `@resource`, and `@extend`
decorators. Each concern lives in its own Python package (`sqlite_database`,
`user_repository`, `http_handlers`, `network_server`) and they are composed
via `@extend`. Requires passing `@extern` parameters at instantiation:

```python
import mixinv2_examples.app_di as app_di
from mixinv2._runtime import evaluate

app = evaluate(app_di, modules_public=True).step4_app(
    database_path=":memory:",
    host="127.0.0.1",
    port=0,
)
app.serve_forever
```

### Decorator version (inline `@scope` classes)

All four concerns defined as inline `@scope` classes in a single file,
composed via `@extend`. See
`src/mixinv2_examples/app_decorator/step4_http_server.py` for the full
definitions. Requires passing `@extern` parameters at instantiation:

```python
from types import ModuleType

import mixinv2_examples.app_decorator.step4_http_server as step4
from mixinv2._runtime import evaluate

module = ModuleType("step4")
module.SQLiteDatabase = step4.SQLiteDatabase
module.UserRepository = step4.UserRepository
module.HttpHandlers = step4.HttpHandlers
module.NetworkServer = step4.NetworkServer
module.app = step4.app

app_instance = evaluate(module, modules_public=True).app(
    database_path=":memory:",
    host="127.0.0.1",
    port=0,
)
app_instance.server
```

### Testing the servers

Once a server is running, send a request:

```
curl http://127.0.0.1:<port>/users/1
```

Expected response: `total=2 current=alice`

Press Ctrl-C to stop.
