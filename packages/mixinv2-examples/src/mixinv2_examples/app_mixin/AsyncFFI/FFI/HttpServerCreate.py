"""Starlette app + uvicorn.Server"""

import asyncio
from collections.abc import Callable

import uvicorn
from starlette.applications import Starlette
from starlette.routing import Route

from mixinv2 import extern, public, resource


@extern
def host() -> str: ...


@extern
def port() -> int: ...


@extern
def handlerClass() -> Callable: ...


@public
@resource
def server(host: str, port: int, handlerClass: Callable) -> uvicorn.Server:
    application = Starlette(
        routes=[Route("/{path:path}", handlerClass)],
    )
    configuration = uvicorn.Config(
        application, host=host, port=port, log_level="error",
    )
    return uvicorn.Server(configuration)


@public
@resource
def serveForever(server: uvicorn.Server) -> None:
    asyncio.run(server.serve())
