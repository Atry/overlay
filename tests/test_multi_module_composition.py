"""Test multi-module composition with overlapping class definitions.

Tests scenarios:
1. Flat structure (reproduction of original bug).
2. Nested structure (reproduction of bug with nested scopes).
3. Diamond structure (composition reducing nesting depth).
4. Flatten structure (composition flattening multiple nesting levels).

All are minimal reproductions for known bugs where inheritance chains
should contain all non-synthetic MixinSymbol entries from constituent modules.
"""

from collections.abc import Hashable
from pathlib import Path
from typing import Any

import pytest

from syrupy.assertion import SnapshotAssertion

from mixinject import MixinSymbol
from mixinject.mixin_directory import DirectoryMixinDefinition
from mixinject.runtime import Scope, evaluate


FIXTURES_PATH = Path(__file__).parent / "fixtures"

CLASS_NAMES = frozenset({"Class1", "Class2", "Class3", "Class4"})


def _format_path(symbol: MixinSymbol) -> str:
    """Format a MixinSymbol's path as a dot-separated string."""
    return ".".join(str(segment) for segment in symbol.path)


def _collect_tree_ancestors(symbol: MixinSymbol) -> frozenset[MixinSymbol]:
    """Collect all ancestors of symbol following the .outer chain up to root."""
    ancestors: set[MixinSymbol] = set()
    current = symbol.outer
    while isinstance(current, MixinSymbol):
        ancestors.add(current)
        current = current.outer
    return frozenset(ancestors)


def _has_cyclic_inheritance(
    symbol: MixinSymbol, ancestors: frozenset[MixinSymbol]
) -> bool:
    """Check if symbol inherits from any ancestor (structural cycle)."""
    for strict_super in symbol.strict_supers:
        if strict_super in ancestors:
            return True
    return False


def _symbol_tree_snapshot(
    symbol: MixinSymbol,
    _ancestors: frozenset[MixinSymbol] | None = None,
) -> dict[str, Any]:
    """Build a snapshot dict of the symbol subtree.

    For each node, captures:
    - strict_super: list of paths of strict super symbols
    - children: recursive dict of child symbols (only for scope symbols)

    Detects cycles via _ancestors to avoid infinite recursion on
    self-referential symbols (e.g. Container with DeBruijnIndex0: [Container, ~]).
    Ancestors include both tree-walk ancestors and symbol-tree ancestors
    (via .outer chain) to catch back-references to distant parent scopes.
    """
    if _ancestors is None:
        _ancestors = _collect_tree_ancestors(symbol)

    strict_super = tuple(
        sorted(_format_path(super_symbol) for super_symbol in symbol.strict_supers)
    )

    children: dict[str, Any] = {}
    if symbol.is_scope:
        child_ancestors = _ancestors | {symbol}
        seen_keys: set[Hashable] = set()
        for key in symbol:
            if key in seen_keys:
                continue
            seen_keys.add(key)
            child = symbol[key]
            if _has_cyclic_inheritance(child, child_ancestors):
                children[str(key)] = {"strict_super": "<cycle>"}
                continue
            children[str(key)] = _symbol_tree_snapshot(child, child_ancestors)

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
        for super_symbol in current.strict_supers:
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
    """Test that Module3Flat.Class4's super chain contains all 10 non-synthetic MixinSymbols.

    Module1 defines: Class1, Class2 (2 definitions)
    Module2Flat defines: Class1, Class2, Class3, Class4 (4 definitions)
    Module3Flat inherits: [Module1], [Module2Flat]

    Expected super chain for Module3Flat.Class4 (including self):
      Definition-site symbols (7):
        1. Module3Flat.Class4 (self)
        2. Module2Flat.Class4
        3. Module2Flat.Class2
        4. Module1.Class2
        5. Module1.Class1
        6. Module2Flat.Class1
        7. Module2Flat.Class3
      Composition-site shell symbols (3):
        8. Module3Flat.Class1
        9. Module3Flat.Class2
       10. Module3Flat.Class3
    """

    def test_class4_super_chain_contains_all_classes(
        self, multi_module_scope: Scope
    ) -> None:
        module3 = multi_module_scope.Module3Flat
        assert isinstance(module3, Scope)

        class4_symbol = module3.symbol["Class4"]
        all_symbols = _collect_all_super_symbols(class4_symbol)

        non_synthetic = {symbol for symbol in all_symbols if symbol.key in CLASS_NAMES}
        non_synthetic_paths = sorted(
            ".".join(str(segment) for segment in symbol.path)
            for symbol in non_synthetic
        )

        assert len(non_synthetic) == 10, (
            f"Expected 10 non-synthetic MixinSymbols, got {len(non_synthetic)}: "
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
    """Test that Module3.Nested2.Class4's super chain contains all 10 non-synthetic MixinSymbols.

    Module1 defines: Class1, Class2 (2 definitions)
    Module2 defines: Class1, Class2, Nested1.Class3, Nested2.Class4 (4 definitions)
    Module3 inherits: [Module1], [Module2]

    Expected super chain for Module3.Nested2.Class4 (including self):
      Definition-site symbols (7):
        1. Module3.Nested2.Class4 (self)
        2. Module2.Nested2.Class4
        3. Module2.Class2
        4. Module1.Class2
        5. Module1.Class1
        6. Module2.Class1
        7. Module2.Nested1.Class3
      Composition-site shell symbols (3):
        8. Module3.Class1
        9. Module3.Class2
       10. Module3.Nested1.Class3
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

        non_synthetic = {symbol for symbol in all_symbols if symbol.key in CLASS_NAMES}
        non_synthetic_paths = sorted(
            ".".join(str(segment) for segment in symbol.path)
            for symbol in non_synthetic
        )

        assert len(non_synthetic) == 10, (
            f"Expected 10 non-synthetic MixinSymbols, got {len(non_synthetic)}: "
            f"{non_synthetic_paths}"
        )


class TestMultiModuleCompositionDiamond:
    """Test Module3Diamond with composition that reduces nesting depth.

    Module2Diamond.Nested2.Class4 extends [Class2] and [Nested3, ExtraNested, Class5].
    Module3Diamond = [Module1] + [Module2Diamond]

    The path [Nested3, ExtraNested, Class5] crosses multiple nesting levels,
    and Class5 itself extends [Class2] with de_bruijn=2. When composed into
    Module3Diamond, the composition-site depth differs from the origin depth.
    """

    def test_module3_diamond_symbol_tree(
        self, multi_module_scope: Scope, snapshot: SnapshotAssertion
    ) -> None:
        module3_diamond = multi_module_scope.Module3Diamond
        assert isinstance(module3_diamond, Scope)
        tree = _symbol_tree_snapshot(module3_diamond.symbol)
        assert tree == snapshot(name="module3_diamond_symbol_tree")


class TestMyRootFlatten:
    """Test MyRoot with flattening composition that compresses nesting levels.

    MyRoot:
      Target: []
      Target2: []
      Nested1:
        - [Nested2]
        - [Nested4]
      Nested2:
        Nested3:
          ReferenceToTarget: [Target]   # de_bruijn=2
      Nested4:
        Nested3:
          ReferenceToTarget: [Target2]  # de_bruijn=2
      Flatten: [Nested1, Nested3]

    For [MyRoot, Flatten, ReferenceToTarget] from [Nested2] path (de_bruijn=2):
      step 0: current=[MyRoot, Flatten], current_lexical=[MyRoot, Nested1, Nested3]
      step 1: current=[MyRoot, Nested1], current_lexical=[MyRoot, Nested2]
      step 2: current=[MyRoot], current_lexical=[MyRoot]
      Result: MyRoot["Target"] = [MyRoot, Target]

    For [MyRoot, Flatten, ReferenceToTarget] from [Nested4] path (de_bruijn=2):
      step 0: current=[MyRoot, Flatten], current_lexical=[MyRoot, Nested1, Nested3]
      step 1: current=[MyRoot, Nested1], current_lexical=[MyRoot, Nested4]
      step 2: current=[MyRoot], current_lexical=[MyRoot]
      Result: MyRoot["Target2"] = [MyRoot, Target2]
    """

    def test_my_root_symbol_tree(
        self, multi_module_scope: Scope, snapshot: SnapshotAssertion
    ) -> None:
        my_root = multi_module_scope.MyRoot
        assert isinstance(my_root, Scope)
        tree = _symbol_tree_snapshot(my_root.symbol)
        assert tree == snapshot(name="my_root_symbol_tree")

    def test_reroot_symbol_tree(
        self, multi_module_scope: Scope, snapshot: SnapshotAssertion
    ) -> None:
        reroot = multi_module_scope.Reroot
        assert isinstance(reroot, Scope)
        tree = _symbol_tree_snapshot(reroot.symbol)
        assert tree == snapshot(name="reroot_symbol_tree")

    def test_flatten_reference_to_target_outer_and_supers(
        self, multi_module_scope: Scope
    ) -> None:
        """Verify that outer and strict_supers are correctly set for the flatten case."""
        my_root = multi_module_scope.MyRoot
        assert isinstance(my_root, Scope)
        my_root_symbol = my_root.symbol

        flatten_symbol = my_root_symbol["Flatten"]
        reference_to_target_symbol = flatten_symbol["ReferenceToTarget"]

        # [MyRoot, Flatten, ReferenceToTarget].outer = [MyRoot, Flatten]
        assert reference_to_target_symbol.outer is flatten_symbol

        # The definition-site symbols that provide ReferenceToTarget through
        # different super paths should be strict supers of Flatten
        nested2_symbol = my_root_symbol["Nested2"]
        nested4_symbol = my_root_symbol["Nested4"]

        nested2_nested3_symbol = nested2_symbol["Nested3"]
        nested4_nested3_symbol = nested4_symbol["Nested3"]

        # Flatten inherits from [Nested1, Nested3]
        # Nested1 inherits from [Nested2] and [Nested4]
        # So Nested1.Nested3 merges Nested2.Nested3 and Nested4.Nested3
        # Both should be strict supers of Flatten (the composition-site parent)
        assert nested2_nested3_symbol in flatten_symbol.strict_supers
        assert nested4_nested3_symbol in flatten_symbol.strict_supers


class TestMergedValueOverride:
    """Test Merged with overridden Value definitions from different paths.

    MergedRoot:
      Foo:
        Value: []
        Bar: [Value]         # de_bruijn=1, origin_symbol=Foo
      Nested:
        Baz:
          - [Foo]
          - Value2: []
          - Value: [Value2]  # Baz overrides Value to depend on Value2
      Qux:
        - [Foo]
        - Value3: []
        - Value: [Value3]    # Qux overrides Value to depend on Value3
      Merged:
        - [Foo]
        - [Nested, Baz]
        - [Qux]

    Key question: When Merged.Bar resolves [Value] (de_bruijn=1),
    does the outer chain correctly navigate to the right Value?
    """

    def test_merged_root_symbol_tree(
        self, multi_module_scope: Scope, snapshot: SnapshotAssertion
    ) -> None:
        merged_root = multi_module_scope.MergedRoot
        assert isinstance(merged_root, Scope)
        tree = _symbol_tree_snapshot(merged_root.symbol)
        assert tree == snapshot(name="merged_root_symbol_tree")


class TestCompositionOuterChain:
    """Test that outer and strict_supers correctly map at each composition level.

    LexicalOuterConflict:
      GrandParent:
        Parent:
          Target: []
          Child:
            Ref: [Target]      # de_bruijn=1, origin_symbol=GrandParent.Parent.Child
      WrapperB:
        - [GrandParent]
        - Parent:
            Target2: []
            Target: [Target2]  # WrapperB overrides Target
      WrapperC:
        - [GrandParent]
        - Parent:
            Target3: []
            Target: [Target3]  # WrapperC overrides Target
      Merged:
        - [WrapperB]
        - [WrapperC]

    The outer chain at each level should reflect the composition-site structure:
      - Ref.outer is Merged.Parent.Child
      - Merged.Parent.Child.outer is Merged.Parent
      - Merged.Parent.outer is Merged

    And the definition-site symbols should appear as strict supers:
      - GrandParent.Parent.Child in Merged.Parent.Child.strict_supers
      - GrandParent.Parent in Merged.Parent.strict_supers
      - GrandParent in Merged.strict_supers
    """

    def test_outer_chain_maps_correctly(self, multi_module_scope: Scope) -> None:
        """Verify outer at each level is the correct composition-site parent."""
        conflict_root = multi_module_scope.LexicalOuterConflict
        assert isinstance(conflict_root, Scope)
        conflict_root_symbol = conflict_root.symbol

        grandparent_symbol = conflict_root_symbol["GrandParent"]
        grandparent_parent_symbol = grandparent_symbol["Parent"]
        grandparent_parent_child_symbol = grandparent_parent_symbol["Child"]

        merged_symbol = conflict_root_symbol["Merged"]
        merged_parent_symbol = merged_symbol["Parent"]
        merged_parent_child_symbol = merged_parent_symbol["Child"]
        ref_symbol = merged_parent_child_symbol["Ref"]

        # Level 1: Ref.outer is Merged.Parent.Child (structural parent)
        assert ref_symbol.outer is merged_parent_child_symbol
        assert (
            grandparent_parent_child_symbol in merged_parent_child_symbol.strict_supers
        )

        # Level 2: Merged.Parent.Child.outer is Merged.Parent
        assert merged_parent_child_symbol.outer is merged_parent_symbol
        assert grandparent_parent_symbol in merged_parent_symbol.strict_supers

        # Level 3: Merged.Parent.outer is Merged
        assert merged_parent_symbol.outer is merged_symbol
        assert grandparent_symbol in merged_symbol.strict_supers


class TestUnionMixinNavigation:
    """Test that _generate_strict_super_mixins handles union mixins correctly.

    Module3Flat.Class4 has 10 non-synthetic strict super symbols (verified by
    TestMultiModuleCompositionFlat). The union branch in
    _generate_strict_super_mixins navigates outer's strict_super_mixins
    to find parent scopes that have a child with the same key.
    """

    def test_strict_super_mixins_index_error(self, multi_module_scope: Scope) -> None:
        """Accessing strict_super_mixins on a composed scope's child Mixin triggers IndexError."""
        module3_flat = multi_module_scope.Module3Flat
        assert isinstance(module3_flat, Scope)

        # Get the Class4 symbol in the composition-site context
        class4_symbol = module3_flat.symbol["Class4"]

        # Verify precondition: Class4 has more than 1 strict super at composition-site
        strict_super_count = sum(1 for _ in class4_symbol.strict_supers)
        assert strict_super_count > 1, (
            f"Expected Class4 to have multiple strict supers at composition-site, "
            f"got {strict_super_count}"
        )

        # Access the Mixin for Class4 from the Scope's _children
        class4_mixin = module3_flat._children[class4_symbol]

        # This triggers _generate_strict_super_mixins which exercises
        # the union mixin navigation path
        _ = class4_mixin.strict_super_mixins


class TestFlattenedContainer:
    """Test that Library.Wrapper.IndirectFlatten flattens Types.Container via AltTypes."""

    def test_types_symbol_tree(
        self, multi_module_scope: Scope, snapshot: SnapshotAssertion
    ) -> None:
        library_symbol = multi_module_scope.symbol["Library"]
        types = library_symbol["Types"]
        assert snapshot(name="types_symbol_tree") == _symbol_tree_snapshot(types)

    def test_indirect_flatten_symbol_tree(
        self, multi_module_scope: Scope, snapshot: SnapshotAssertion
    ) -> None:
        library_symbol = multi_module_scope.symbol["Library"]
        wrapper = library_symbol["Wrapper"]
        indirect_flatten = wrapper["IndirectFlatten"]
        assert snapshot(name="indirect_flatten_symbol_tree") == _symbol_tree_snapshot(
            indirect_flatten
        )


class TestDeBruijnCompositionNavigation:
    """Test that de Bruijn references resolve correctly after composition flattening.

    Library:
      Types:
        Value: []
        Container:
          Content: [Value]
          DeBruijnIndex0: [Container, ~]    # de_bruijn=0
          DeBruijnIndex1: [Types, ~]      # de_bruijn=1
          DeBruijnIndex2: [Library, ~]      # de_bruijn=2
          DeBruijnIndex3: [multi_module_composition, ~]  # de_bruijn=3
      DirectFlatten:
        - [Types, Container]
        - DirectOnly: []
      Wrapper:
        AltTypes: [Types]
        IndirectFlatten:
          - [AltTypes, Container]
          - IndirectOnly: []
    Composed:
      - [Library, DirectFlatten]
      - [Library, Wrapper, IndirectFlatten]

    Composed flattens 3 levels (Library.Types.Container) into 1 level via two paths.
    Each reference uses a qualified-this reference [ScopeName, ~]
    which resolves to the scope itself at de_bruijn=N.

    Expected composition-site current at each de Bruijn level:
      de_bruijn=0 → Composed                      (= Container)
      de_bruijn=1 → ?                              (= Types)
      de_bruijn=2 → ?                              (= Library)
      de_bruijn=3 → multi_module_composition
    """

    def test_de_bruijn_references_resolve_after_flattening(
        self, multi_module_scope: Scope
    ) -> None:
        composed_symbol = multi_module_scope.symbol["Composed"]

        reference_symbol_0 = composed_symbol["DeBruijnIndex0"]
        strict_super_paths_0 = tuple(
            super_symbol.path for super_symbol in reference_symbol_0.strict_supers
        )
        assert ("multi_module_composition", "Composed") in strict_super_paths_0, (
            f"DeBruijnIndex0: expected multi_module_composition.Composed "
            f"in strict_super, got {['.'.join(str(s) for s in p) for p in strict_super_paths_0]}"
        )

        reference_symbol_1 = composed_symbol["DeBruijnIndex1"]
        strict_super_paths_1 = tuple(
            super_symbol.path for super_symbol in reference_symbol_1.strict_supers
        )
        assert (
            "multi_module_composition",
            "Library",
            "Wrapper",
            "AltTypes",
        ) in strict_super_paths_1
        assert (
            "multi_module_composition",
            "Library",
            "Wrapper2",
            "AltTypes2",
        ) in strict_super_paths_1, (
            f"DeBruijnIndex1: expected multi_module_composition.Library.Wrapper2.AltTypes2 "
            f"in strict_super, got {['.'.join(str(s) for s in p) for p in strict_super_paths_1]}"
        )

        reference_symbol_2 = composed_symbol["DeBruijnIndex2"]
        strict_super_paths_2 = tuple(
            super_symbol.path for super_symbol in reference_symbol_2.strict_supers
        )
        assert ("multi_module_composition", "Library") in strict_super_paths_2, (
            f"DeBruijnIndex2: expected multi_module_composition.Library "
            f"in strict_super, got {['.'.join(str(s) for s in p) for p in strict_super_paths_2]}"
        )

        reference_symbol_3 = composed_symbol["DeBruijnIndex3"]
        strict_super_paths_3 = tuple(
            super_symbol.path for super_symbol in reference_symbol_3.strict_supers
        )
        assert ("multi_module_composition",) in strict_super_paths_3, (
            f"DeBruijnIndex3: expected multi_module_composition "
            f"in strict_super, got {['.'.join(str(s) for s in p) for p in strict_super_paths_3]}"
        )
