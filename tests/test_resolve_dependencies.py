from collections import ChainMap
from typing import Any, Callable, Iterator
from unittest.mock import Mock

import pytest
from mixinject import (
    LexicalScope,
    Proxy,
    _resolve_dependencies_jit,
    _resolve_dependencies_kwargs,
)


def test_resolve_dependencies_consistency():
    def lexical_scope() -> Iterator[Proxy]:
        yield from []

    mock_proxy = Mock(spec=Proxy)

    # Mock symbol table
    symbol_table = ChainMap(
        {
            "a": lambda ls: 1,
            "b": lambda ls: 2,
            "c": lambda ls: 3,
        }
    )

    test_cases: list[Callable[..., Any]] = [
        # No arguments
        lambda: "no args",
        # Only proxy (positional only)
        lambda p, /: f"proxy only: {p}",
        # Only proxy (name not in symbol table)
        lambda proxy: f"proxy only: {proxy}",
        # Mixed proxy and dependencies
        lambda p, /, a, b: f"p={p}, a={a}, b={b}",
        lambda proxy, a, b: f"proxy={proxy}, a={a}, b={b}",
        # Only dependencies
        lambda a, b: f"a={a}, b={b}",
        # Dependency named as proxy but it IS in symbol table
        lambda a: f"a={a}",
    ]

    for func in test_cases:
        resolved_kwargs = _resolve_dependencies_kwargs(symbol_table, func, "dummy")
        resolved_jit = _resolve_dependencies_jit(symbol_table, func, "dummy")

        result_kwargs = resolved_kwargs((mock_proxy, *lexical_scope))
        result_jit = resolved_jit((mock_proxy, *lexical_scope))

        assert result_kwargs == result_jit, f"Consistency failed for {func}"
        if "no args" in str(result_kwargs):
            assert result_kwargs == "no args"
        elif "proxy only" in str(result_kwargs):
            # Check if mock_proxy or its string representation is in result
            assert str(mock_proxy) in str(result_kwargs)


def test_resolve_dependencies_complex_signatures():
    def lexical_scope() -> Iterator[Proxy]:
        yield from []

    mock_proxy = Mock(spec=Proxy)
    symbol_table = ChainMap({"a": lambda ls: 10, "b": lambda ls: 20})

    # Positional only argument named 'a' which is in symbol table
    # Since it is positional only, it should be treated as proxy.
    def func1(a, /, b):
        return (a, b)

    res_kwargs = _resolve_dependencies_kwargs(symbol_table, func1, "dummy")
    res_jit = _resolve_dependencies_jit(symbol_table, func1, "dummy")

    assert res_kwargs((mock_proxy, *lexical_scope)) == (mock_proxy, 20)
    assert res_jit((mock_proxy, *lexical_scope)) == (mock_proxy, 20)

    # Positional or keyword argument named 'a' which is in symbol table
    # It should NOT be treated as proxy.
    def func2(a, b):
        return (a, b)

    res_kwargs = _resolve_dependencies_kwargs(symbol_table, func2, "dummy")
    res_jit = _resolve_dependencies_jit(symbol_table, func2, "dummy")

    assert res_kwargs((mock_proxy, *lexical_scope)) == (10, 20)
    assert res_jit((mock_proxy, *lexical_scope)) == (10, 20)


def test_resolve_dependencies_same_name():
    lexical_scope: LexicalScope = ()
    mock_proxy = Mock(spec=Proxy)

    # Layered symbol table
    inner_table = {"a": lambda ls: "inner_a"}
    outer_table = {"a": lambda ls: "outer_a"}
    symbol_table = ChainMap(inner_table, outer_table)

    # When param name is 'a', and resource_name is also 'a'
    # It should look up 'a' in symbol_table.parents (outer_table)
    def func(a):
        return a

    # Test kwargs implementation
    res_kwargs = _resolve_dependencies_kwargs(symbol_table, func, "a")
    assert res_kwargs((mock_proxy, *lexical_scope)) == "outer_a"

    # Test jit implementation
    res_jit = _resolve_dependencies_jit(symbol_table, func, "a")
    assert res_jit((mock_proxy, *lexical_scope)) == "outer_a"

    # When resource_name is different, it should use inner_table
    res_kwargs_diff = _resolve_dependencies_kwargs(symbol_table, func, "other")
    assert res_kwargs_diff((mock_proxy, *lexical_scope)) == "inner_a"

    res_jit_diff = _resolve_dependencies_jit(symbol_table, func, "other")
    assert res_jit_diff((mock_proxy, *lexical_scope)) == "inner_a"
