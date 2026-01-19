from collections import ChainMap
from dataclasses import dataclass
from inspect import signature
from typing import Any, Callable, Final, Iterator, ParamSpec, TypeVar
from unittest.mock import Mock

import pytest
from mixinject import (
    CapturedScopes,
    Scope,
    SymbolTable,
    _resolve_dependencies_jit,
    _Symbol,
)

P = ParamSpec("P")
T = TypeVar("T")


class _MockDefinition:
    """Mock definition for testing."""
    pass


_MOCK_DEFINITION = _MockDefinition()


@dataclass(kw_only=True, slots=True, weakref_slot=True)
class _MockSymbol(_Symbol):
    """Mock symbol for testing that wraps a getter function."""

    _getter_func: Final[Callable[[CapturedScopes], Any]]
    _depth: Final[int] = 0
    _resource_name: Final[str] = ""
    definition: Any = _MOCK_DEFINITION  # type: ignore[misc]

    def __post_init__(self) -> None:
        # Override the getter with our custom function instead of using the parent's JIT getter
        object.__setattr__(self, "getter", self._getter_func)

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def resource_name(self) -> str:
        return self._resource_name

    def compile(self, mixin: Any, /) -> Any:
        raise NotImplementedError("_MockSymbol is not compilable")


def _make_mock_symbol_table(mapping: dict[str, Callable[[CapturedScopes], Any]]) -> SymbolTable:
    """Create a symbol table from a dict of name -> getter function."""
    symbols: dict[str, _Symbol] = {
        name: _MockSymbol(_getter_func=getter) for name, getter in mapping.items()
    }
    return ChainMap(symbols)


def _resolve_dependencies_kwargs(
    symbol_table: SymbolTable,
    function: Callable[P, T],
    name: str,
) -> Callable[[CapturedScopes], T]:
    """
    Resolve dependencies for a function using standard keyword arguments.
    (Testing version)
    """
    sig = signature(function)
    params = tuple(sig.parameters.values())

    has_scope = False
    if params:
        p0 = params[0]
        if (p0.kind == p0.POSITIONAL_ONLY) or (
            p0.kind == p0.POSITIONAL_OR_KEYWORD and p0.name not in symbol_table
        ):
            has_scope = True
            kw_params = params[1:]
        else:
            kw_params = params
    else:
        kw_params = []

    def resolved_function(captured_scopes: CapturedScopes) -> T:
        kwargs = {
            param.name: (
                symbol_table.parents[param.name].getter(captured_scopes)
                if param.name == name
                else symbol_table[param.name].getter(captured_scopes)
            )
            for param in kw_params
        }

        if has_scope:
            return function(captured_scopes[0], **kwargs)  # type: ignore
        else:
            return function(**kwargs)  # type: ignore

    return resolved_function


def test_resolve_dependencies_consistency():
    captured_scopes: CapturedScopes = ()

    mock_scope = Mock(spec=Scope)

    # Mock symbol table
    symbol_table = _make_mock_symbol_table(
        {
            "a": lambda ls: 1,
            "b": lambda ls: 2,
            "c": lambda ls: 3,
        }
    )

    test_cases: list[Callable[..., Any]] = [
        # No arguments
        lambda: "no args",
        # Only scope (positional only)
        lambda p, /: f"scope only: {p}",
        # Only scope (name not in symbol table)
        lambda scope: f"scope only: {scope}",
        # Mixed scope and dependencies
        lambda p, /, a, b: f"p={p}, a={a}, b={b}",
        lambda scope, a, b: f"scope={scope}, a={a}, b={b}",
        # Only dependencies
        lambda a, b: f"a={a}, b={b}",
        # Dependency named as scope but it IS in symbol table
        lambda a: f"a={a}",
    ]

    for func in test_cases:
        resolved_kwargs = _resolve_dependencies_kwargs(symbol_table, func, "dummy")
        resolved_jit = _resolve_dependencies_jit(symbol_table, func, "dummy")

        result_kwargs = resolved_kwargs((mock_scope, *captured_scopes))
        result_jit = resolved_jit((mock_scope, *captured_scopes))

        assert result_kwargs == result_jit, f"Consistency failed for {func}"
        if "no args" in str(result_kwargs):
            assert result_kwargs == "no args"
        elif "scope only" in str(result_kwargs):
            # Check if mock_scope or its string representation is in result
            assert str(mock_scope) in str(result_kwargs)


def test_resolve_dependencies_complex_signatures():
    captured_scopes: CapturedScopes = ()

    mock_scope = Mock(spec=Scope)
    symbol_table = _make_mock_symbol_table({"a": lambda ls: 10, "b": lambda ls: 20})

    # Positional only argument named 'a' which is in symbol table
    # Since it is positional only, it should be treated as scope.
    def func1(a, /, b):
        return (a, b)

    res_kwargs = _resolve_dependencies_kwargs(symbol_table, func1, "dummy")
    res_jit = _resolve_dependencies_jit(symbol_table, func1, "dummy")

    assert res_kwargs((mock_scope, *captured_scopes)) == (mock_scope, 20)
    assert res_jit((mock_scope, *captured_scopes)) == (mock_scope, 20)

    # Positional or keyword argument named 'a' which is in symbol table
    # It should NOT be treated as scope.
    def func2(a, b):
        return (a, b)

    res_kwargs = _resolve_dependencies_kwargs(symbol_table, func2, "dummy")
    res_jit = _resolve_dependencies_jit(symbol_table, func2, "dummy")

    assert res_kwargs((mock_scope, *captured_scopes)) == (10, 20)
    assert res_jit((mock_scope, *captured_scopes)) == (10, 20)


def test_resolve_dependencies_same_name():
    captured_scopes: CapturedScopes = ()
    mock_scope = Mock(spec=Scope)

    # Layered symbol table
    inner_symbols: dict[str, _Symbol] = {
        "a": _MockSymbol(_getter_func=lambda ls: "inner_a")
    }
    outer_symbols: dict[str, _Symbol] = {
        "a": _MockSymbol(_getter_func=lambda ls: "outer_a")
    }
    symbol_table: SymbolTable = ChainMap(inner_symbols, outer_symbols)

    # When param name is 'a', and name is also 'a'
    # It should look up 'a' in symbol_table.parents (outer_table)
    def func(a):
        return a

    # Test kwargs implementation
    res_kwargs = _resolve_dependencies_kwargs(symbol_table, func, "a")
    assert res_kwargs((mock_scope, *captured_scopes)) == "outer_a"

    # Test jit implementation
    res_jit = _resolve_dependencies_jit(symbol_table, func, "a")
    assert res_jit((mock_scope, *captured_scopes)) == "outer_a"

    # When name is different, it should use inner_table
    res_kwargs_diff = _resolve_dependencies_kwargs(symbol_table, func, "other")
    assert res_kwargs_diff((mock_scope, *captured_scopes)) == "inner_a"

    res_jit_diff = _resolve_dependencies_jit(symbol_table, func, "other")
    assert res_jit_diff((mock_scope, *captured_scopes)) == "inner_a"
