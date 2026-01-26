import gc

from mixinject import (
    Mixin,
    MixinSymbol,
    Nested,
    evaluate,
    resource,
    scope,
    ScopeDefinition,
)


def _empty_definition() -> ScopeDefinition:
    """Create a minimal empty scope definition for testing."""
    return ScopeDefinition(bases=(), underlying=object())


def _root_symbol(definition: ScopeDefinition) -> MixinSymbol:
    """Create a root scope symbol for testing."""
    return MixinSymbol(origin=(definition,))


class TestRoot:
    """Test root dependency graph behavior."""

    def test_root_hasintern_pool(self) -> None:
        scope_def = _empty_definition()
        root = _root_symbol(scope_def)
        assert root._nested is not None

    def test_different_roots_have_different_pools(self) -> None:
        scope_def1 = _empty_definition()
        scope_def2 = _empty_definition()
        root1 = _root_symbol(scope_def1)
        root2 = _root_symbol(scope_def2)
        assert root1._nested is not root2._nested


class TestInterning:
    """Test interning behavior for O(1) equality.

    Note: Interning now happens in scope_factory and mount, not in __new__.
    Direct instantiation creates new objects each time.
    """

    def test_direct_instantiation_creates_new_objects(self) -> None:
        """Direct instantiation without going through scope_factory creates new objects."""
        scope_def = _empty_definition()
        root = _root_symbol(scope_def)
        child1 = MixinSymbol(origin=Nested(outer=root, key="test1"))
        child2 = MixinSymbol(origin=Nested(outer=root, key="test2"))
        # Without interning, these are different objects
        assert child1 is not child2

    def test_different_parent_different_object(self) -> None:
        scope_def = _empty_definition()
        root1 = _root_symbol(scope_def)
        root2 = _root_symbol(scope_def)
        child1 = MixinSymbol(origin=Nested(outer=root1, key="test"))
        child2 = MixinSymbol(origin=Nested(outer=root2, key="test"))
        assert child1 is not child2

    def test_each_node_has_ownintern_pool(self) -> None:
        scope_def = _empty_definition()
        root = _root_symbol(scope_def)
        child1 = MixinSymbol(origin=Nested(outer=root, key="child1"))
        child2 = MixinSymbol(origin=Nested(outer=child1, key="child2"))
        assert child1._nested is not root._nested
        assert child2._nested is not child1._nested
        assert child2._nested is not root._nested

    def test_interning_via_mount(self) -> None:
        """Interning happens when using mount."""
        @scope
        class Root:
            @resource
            def foo() -> int:
                return 42

        root1 = evaluate(Root)
        root2 = evaluate(Root)

        # Different mount calls create different scopes
        assert root1 is not root2
        # But they should have different mixins since each mount creates a new root

    def test_interning_via_nested_scope_access(self) -> None:
        """Accessing the same nested scope multiple times returns scopes with the same mixin."""
        @scope
        class Root:
            @scope
            class Inner:
                @resource
                def foo() -> int:
                    return 42

        root = evaluate(Root)
        inner1 = root.Inner
        inner2 = root.Inner

        # Cached scope should return the same object
        assert inner1 is inner2
        # Therefore same mixin
        assert isinstance(inner1, Mixin)
        assert isinstance(inner2, Mixin)
        assert inner1.symbol is inner2.symbol


class TestWeakReference:
    """Test weak reference behavior of intern pool."""

    def test_intern_pool_supports_weak_references(self) -> None:
        """The intern pool is a WeakValueDictionary."""
        scope_def = _empty_definition()
        root = _root_symbol(scope_def)
        # Add an entry manually to the pool
        child = MixinSymbol(origin=Nested(outer=root, key="test"))
        root._nested["test_key"] = child

        pool_size_before = len(root._nested)
        assert pool_size_before == 1

        del child
        gc.collect()

        pool_size_after = len(root._nested)
        assert pool_size_after < pool_size_before


class TestSubclass:
    """Test isinstance/issubclass behavior."""

    def test_symbol_is_concrete(self) -> None:
        """MixinSymbol is now a concrete class (no longer ABC)."""
        # MixinSymbol can be instantiated directly
        scope_def = _empty_definition()
        root = _root_symbol(scope_def)
        assert isinstance(root, MixinSymbol)

    def test_root_instance_is_instance_of_symbol(self) -> None:
        scope_def = _empty_definition()
        root = _root_symbol(scope_def)
        assert isinstance(root, MixinSymbol)

    def test_child_instance_is_instance_of_symbol(self) -> None:
        scope_def = _empty_definition()
        root = _root_symbol(scope_def)
        child = MixinSymbol(origin=Nested(outer=root, key="test"))
        assert isinstance(child, MixinSymbol)
