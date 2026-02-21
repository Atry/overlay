"""Declares request as an extern - enables per-request injection via kwargs."""

from starlette.requests import Request

from overlay.language import extern


@extern
def request() -> Request: ...
