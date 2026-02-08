"""Test multi-module composition with overlapping class definitions.

Tests two scenarios:
1. Flat structure (reproduction of original bug).
2. Nested structure (reproduction of bug with nested scopes).

Both are minimal reproductions for known bugs where inheritance chains
should contain all non-synthetic MixinSymbol entries from constituent modules.
"""

from collections.abc import Hashable
from pathlib import Path
from typing import Any

import pytest

from mixinject import MixinSymbol
from mixinject.mixin_directory import DirectoryMixinDefinition
from mixinject.runtime import Scope, evaluate


FIXTURES_PATH = Path(__file__).parent / "fixtures"

CLASS_NAMES = frozenset({"Class1", "Class2", "Class3", "Class4"})


def _format_path(symbol: MixinSymbol) -> str:
    """Format a MixinSymbol's path as a dot-separated string."""
    return ".".join(str(segment) for segment in symbol.path)


def _symbol_tree_snapshot(symbol: MixinSymbol) -> dict[str, Any]:
    """Build a snapshot dict of the symbol subtree.

    For each node, captures:
    - strict_super: list of paths of strict super symbols
    - children: recursive dict of child symbols (only for scope symbols)
    """
    strict_super = tuple(
        _format_path(super_symbol)
        for super_symbol in symbol.generate_strict_super()
    )

    children: dict[str, Any] = {}
    if symbol.is_scope:
        seen_keys: set[Hashable] = set()
        for key in symbol:
            if key in seen_keys:
                continue
            seen_keys.add(key)
            child = symbol[key]
            children[str(key)] = _symbol_tree_snapshot(child)

    result: dict[str, Any] = {"strict_super": strict_super}
    if children:
        result["children"] = children
    return result


def _collect_all_super_symbols(symbol: MixinSymbol) -> set[MixinSymbol]:
    """Recursively collect all MixinSymbols in the inheritance chain (including self)."""
    collected: set[MixinSymbol] = set()

    def walk(current: MixinSymbol) -> None:
        if current in collected:
            return
        collected.add(current)
        for super_symbol in current.generate_strict_super():
            walk(super_symbol)

    walk(symbol)
    return collected


@pytest.fixture
def multi_module_scope() -> Scope:
    """Load and evaluate the multi-module composition fixture."""
    fixtures_definition = DirectoryMixinDefinition(
        bases=(), is_public=True, underlying=FIXTURES_PATH
    )
    root = evaluate(fixtures_definition, modules_public=True)
    result = root.multi_module_composition
    assert isinstance(result, Scope)
    return result


class TestMultiModuleCompositionFlat:
    """Test that Module3Flat.Class4's super chain contains all 7 non-synthetic MixinSymbols.

    Module1 defines: Class1, Class2 (2 definitions)
    Module2Flat defines: Class1, Class2, Class3, Class4 (4 definitions)
    Module3Flat inherits: [Module1], [Module2Flat]

    Expected super chain for Module3Flat.Class4 (including self):
      1. Module3Flat.Class4 (self)
      2. Module2Flat.Class4
      3. Module2Flat.Class2
      4. Module1.Class2
      5. Module1.Class1
      6. Module2Flat.Class1
      7. Module2Flat.Class3
    """

    def test_class4_super_chain_contains_all_classes(
        self, multi_module_scope: Scope
    ) -> None:
        module3 = multi_module_scope.Module3Flat
        assert isinstance(module3, Scope)

        class4_symbol = module3.symbol["Class4"]
        all_symbols = _collect_all_super_symbols(class4_symbol)

        non_synthetic = {
            symbol for symbol in all_symbols if symbol.key in CLASS_NAMES
        }
        non_synthetic_paths = sorted(
            ".".join(str(segment) for segment in symbol.path)
            for symbol in non_synthetic
        )

        assert len(non_synthetic) == 7, (
            f"Expected 7 non-synthetic MixinSymbols, got {len(non_synthetic)}: "
            f"{non_synthetic_paths}"
        )


class TestMultiModuleCompositionSnapshot:
    """Snapshot tests capturing the full symbol tree of Module3 and Module3Flat."""

    def test_module3_symbol_tree(self, multi_module_scope: Scope, snapshot) -> None:
        module3 = multi_module_scope.Module3
        assert isinstance(module3, Scope)
        tree = _symbol_tree_snapshot(module3.symbol)
        assert tree == snapshot

    def test_module3_flat_symbol_tree(
        self, multi_module_scope: Scope, snapshot
    ) -> None:
        module3_flat = multi_module_scope.Module3Flat
        assert isinstance(module3_flat, Scope)
        tree = _symbol_tree_snapshot(module3_flat.symbol)
        assert tree == snapshot


class TestMultiModuleCompositionNested:
    """Test that Module3.Nested2.Class4's super chain contains all 7 non-synthetic MixinSymbols.

    Module1 defines: Class1, Class2 (2 definitions)
    Module2 defines: Class1, Class2, Nested1.Class3, Nested2.Class4 (4 definitions)
    Module3 inherits: [Module1], [Module2]

    Expected super chain for Module3.Nested2.Class4 (including self):
      1. Module3.Nested2.Class4 (self)
      2. Module2.Nested2.Class4
      3. Module2.Class2
      4. Module1.Class2
      5. Module1.Class1
      6. Module2.Class1
      7. Module2.Nested1.Class3
    """

    def test_class4_super_chain_contains_all_classes(
        self, multi_module_scope: Scope
    ) -> None:
        module3 = multi_module_scope.Module3
        assert isinstance(module3, Scope)

        nested2 = module3.Nested2
        assert isinstance(nested2, Scope)

        class4_symbol = nested2.symbol["Class4"]
        all_symbols = _collect_all_super_symbols(class4_symbol)

        # Filter to non-synthetic symbols (keys matching original class names)
        non_synthetic = {
            symbol for symbol in all_symbols if symbol.key in CLASS_NAMES
        }
        non_synthetic_paths = sorted(
            ".".join(str(segment) for segment in symbol.path)
            for symbol in non_synthetic
        )

        assert len(non_synthetic) == 7, (
            f"Expected 7 non-synthetic MixinSymbols, got {len(non_synthetic)}: "
            f"{non_synthetic_paths}"
        )