"""app_mixin: MIXINv2 web-app example.

Library.mixin.yaml — business logic + abstract FFI declarations.
StdlibFFI/FFI/ — Python stdlib FFI adapters (one module per scope).
AsyncFFI/FFI/ — Async FFI adapters using aiosqlite + starlette.
Apps.mixin.yaml — sync integration entry points (inherits StdlibFFI + Library).
AsyncApps.mixin.yaml — async integration entry points (inherits AsyncFFI + Library).
"""
