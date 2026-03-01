# MIXINv2 Examples

Example case studies demonstrating MIXINv2's DI and composition capabilities.

## Running the HTTP Server Examples

All server examples implement the same application: a user lookup
service backed by an in-memory SQLite database. Each demonstrates a
different composition style.

### MIXIN sync (OYAML + stdlib `http.server`)

Declarative OYAML composition with synchronous stdlib FFI adapters:

```
uv run mixinv2-example app_mixin Apps memoryApp serveForever
```

### MIXIN async (OYAML + Starlette/uvicorn)

Same declarative OYAML composition, but with async FFI adapters — the
business logic (`Library.mixin.yaml`) is identical:

```
uv run mixinv2-example app_mixin AsyncApps memoryApp serveForever
```

### Module version (Python packages + `@extend`)

Python package-based composition using `@scope`, `@resource`, and `@extend`
decorators. Each concern lives in its own Python package (`SqliteDatabase`,
`UserRepository`, `HttpHandlers`, `NetworkServer`) and they are composed
via `@extend`. Requires passing `@extern` parameters at instantiation:

```python
import mixinv2_examples.app_di as app_di
from mixinv2._runtime import evaluate

app = evaluate(app_di, modules_public=True).Step4App(
    databasePath=":memory:",
    host="127.0.0.1",
    port=0,
)
app.serveForever
```

### Decorator version (inline `@scope` classes)

All four concerns defined as inline `@scope` classes in a single file,
composed via `@extend`. See
`src/mixinv2_examples/app_decorator/step4_http_server.py` for the full
definitions. Requires passing `@extern` parameters at instantiation:

```python
import mixinv2_examples.app_decorator.step4_http_server as step4_http_server
from mixinv2._runtime import evaluate

app_instance = evaluate(step4_http_server, modules_public=True).App(
    databasePath=":memory:",
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
