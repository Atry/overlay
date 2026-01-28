"""
MixinV2 and ScopeV2 implementation for proper is_public and is_eager support.

This module provides a cleaner architecture with:
- Single lazy evaluation level (at MixinV2.evaluated only)
- Frozen ScopeV2 containers
- Proper circular dependency support via two-phase construction
- Correct is_public and is_eager semantics (private by default)

NOTE: This module does NOT include dynamic class generation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from functools import cached_property, reduce
from typing import (
    TYPE_CHECKING,
    Callable,
    Final,
    Generic,
    Hashable,
    Iterable,
    Iterator,
    Mapping,
    TypeVar,
    final,
)

from mixinject import HasDict


class KwargsSentinel(Enum):
    """Sentinel for distinguishing static scopes from instance scopes."""

    STATIC = auto()
    """No kwargs - this is a static scope (created via evaluate_v2 or nested scope access)."""

if TYPE_CHECKING:
    from mixinject import (
        EndofunctionMergerSymbol,
        FunctionalMergerSymbol,
        MixinSymbol,
        MultiplePatcherSymbol,
        OuterSentinel,
        ResolvedReference,
        SinglePatcherSymbol,
        SymbolIndexSentinel,
    )


T = TypeVar("T")
TPatch_co = TypeVar("TPatch_co", covariant=True)
TPatch_contra = TypeVar("TPatch_contra", contravariant=True)
TResult_co = TypeVar("TResult_co", covariant=True)
TResult = TypeVar("TResult")


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, eq=False)
class MixinV2(HasDict):
    """
    Lazy evaluation wrapper for resources and scopes.

    MixinV2 is mutable (NOT frozen) to support two-phase construction
    for circular dependencies within the same ScopeV2.

    All lazy evaluation happens ONLY at MixinV2.evaluated level.
    Dynamically decides whether to evaluate to a resource value or ScopeV2.

    .. note::

       Does NOT inherit from Node/Mixin - completely separate hierarchy.
       Inherits from HasDict to support @cached_property with slots=True.

    .. todo:: Dynamic slots for sibling dependencies

       Currently sibling dependencies are stored in ``HasDict.__dict__`` via setattr.
       For better performance, future implementation should use ``make_dataclass``
       to dynamically generate MixinV2 subclasses with slots for each dependency.

       Example future design::

           DynamicMixinV2 = make_dataclass(
               "DynamicMixinV2",
               [("foo", MixinV2), ("bar", MixinV2)],  # sibling dependency slots
               bases=(MixinV2,),
               slots=True,
           )

    .. todo:: Nephew-uncle dependency support

       Currently sibling dependencies only contains sibling-to-sibling dependencies
       within the same scope. Nephew-uncle dependencies (where a nested scope's resource
       depends on its parent's sibling, i.e., an "uncle") are NOT supported.

       This limitation exists because we want lazy compilation for nested scopes (nephews).
       If we were to include nephew-uncle dependencies, we would need to eagerly analyze
       all nested scopes at construction time, defeating laziness.

       Example of unsupported pattern::

           @scope
           class Outer:
               @local
               @resource
               def uncle() -> str:  # Uncle is @local
                   return "uncle_value"

               @scope
               class Inner:
                   @resource
                   def nephew(uncle: str) -> str:  # Nephew depends on uncle
                       return f"got_{uncle}"  # ERROR: uncle is @local, not accessible

       Future solution: Add a ``@friend`` decorator that marks a scope for Ahead-Of-Time
       analysis. When applied, the scope's nested resources would be analyzed at
       construction time, allowing nephew-uncle dependencies to be wired.
       This would enable nephews to access uncle's @local resources.
    """

    symbol: Final["MixinSymbol"]

    outer: Final["MixinV2 | OuterSentinel"]
    """
    The outer MixinV2 (parent scope), or OuterSentinel.ROOT for root.

    To find parent scope dependencies:

    - Evaluate outer.evaluated to get the parent ScopeV2
    - Then access the dependency from that ScopeV2
    """

    lexical_outer_index: Final["SymbolIndexSentinel | int"]
    """Index for lexical scope resolution."""

    kwargs: Final["Mapping[str, object] | KwargsSentinel"]
    """
    Keyword arguments for instance scope support.

    - KwargsSentinel.STATIC: This is a static scope (no instance kwargs)
    - Mapping[str, object]: This is an instance scope with the given kwargs

    Used by _evaluate_resource for PATCHER_ONLY resources to get base values.
    Propagated to nested scopes when MixinV2.evaluated creates a ScopeV2.
    """

    @cached_property
    def strict_super_mixins(self) -> tuple["MixinV2", ...]:
        """
        Get super MixinV2 instances for multiple inheritance support.

        Similar to V1's Mixin.strict_super_mixins.
        Returns MixinV2 instances corresponding to symbol.strict_super_indices.
        """
        return tuple(self._generate_strict_super_mixins())

    def _generate_strict_super_mixins(self) -> Iterator["MixinV2"]:
        """
        Generate super MixinV2 instances following V1's algorithm.

        For each nested_index in symbol.strict_super_indices:
        - OuterBaseIndex(i): Create child of outer's i-th super with lexical_outer_index=i
        - OwnBaseIndex(i): Resolve own base reference using self.lexical_outer_index
        - OWN: Return self

        NOTE: Super mixins do NOT use _sibling_dependencies because their
        lexical_outer_index != OWN. They always resolve dependencies via navigation.
        This is handled correctly in _evaluate_resource().
        """
        # Import here to avoid circular imports
        from mixinject import OuterBaseIndex, OwnBaseIndex, SymbolIndexSentinel

        for nested_index in self.symbol.strict_super_indices.values():
            match nested_index.primary_index:
                case OuterBaseIndex(index=index):
                    # Get the i-th super mixin from our outer
                    assert isinstance(self.outer, MixinV2)
                    base_mixin = self.outer.get_super(index)
                    # Find our symbol's counterpart in the base mixin's symbol
                    child_symbol = base_mixin.symbol[self.symbol.key]
                    # Create with lexical_outer_index=index (points to base_mixin)
                    # No _sibling_dependencies needed - super mixins resolve via navigation
                    direct_mixin = MixinV2(
                        symbol=child_symbol,
                        outer=self.outer,  # Same outer as us
                        lexical_outer_index=index,  # KEY: Different from OWN!
                        kwargs=self.kwargs,  # Propagate kwargs from parent
                    )

                case OwnBaseIndex(index=index):
                    # Resolve using our own base reference
                    resolved_reference = self.symbol.resolved_bases[index]
                    # Pass OUR lexical_outer_index to the resolution
                    direct_mixin = resolved_reference.get_mixin_v2(
                        outer=self,
                        lexical_outer_index=self.lexical_outer_index,
                    )

                case SymbolIndexSentinel.OWN:
                    direct_mixin = self

            # Navigate to the secondary index within the direct mixin
            yield direct_mixin.get_super(nested_index.secondary_index)

    def get_super(self, super_index: "SymbolIndexSentinel | int") -> "MixinV2":
        """
        Get a super mixin by index.

        :param super_index: OWN returns self, int returns strict_super_mixins[index]
        :return: The super MixinV2.
        """
        from mixinject import SymbolIndexSentinel

        match super_index:
            case SymbolIndexSentinel.OWN:
                return self
            case int() as index:
                return self.strict_super_mixins[index]

    @property
    def lexical_outer(self) -> "MixinV2":
        """
        Get the lexical outer MixinV2 for dependency resolution.

        - If lexical_outer_index is OWN: returns outer (or self for root)
        - If lexical_outer_index is int: returns outer.strict_super_mixins[index]
        """
        from mixinject import SymbolIndexSentinel

        match self.lexical_outer_index:
            case SymbolIndexSentinel.OWN:
                if isinstance(self.outer, MixinV2):
                    return self.outer
                return self  # Root mixin
            case int() as index:
                assert isinstance(self.outer, MixinV2)
                return self.outer.strict_super_mixins[index]

    def resolve_dependency(self, ref: "ResolvedReference") -> "MixinV2":
        """
        Resolve a dependency reference to a MixinV2.

        Returns MixinV2, NOT the evaluated value.
        The caller calls .evaluated when it actually needs the value.
        This preserves laziness - if the caller doesn't use a dependency,
        that dependency is never evaluated.

        :param ref: The resolved reference to resolve.
        :return: The target MixinV2 (call .evaluated for actual value).
        """
        from mixinject import SymbolIndexSentinel

        # Only use sibling dependency attributes when BOTH conditions are met:
        # 1. levels_up == 0 (same scope dependency)
        # 2. lexical_outer_index == OWN (we are a direct child, not a super mixin)
        if ref.levels_up == 0 and self.lexical_outer_index is SymbolIndexSentinel.OWN:
            # Direct child with same-scope dependency: use getattr
            # Sibling dependencies are stored as attributes on the MixinV2 instance
            attr_name = ref.target_symbol.attribute_name
            sibling_mixin = getattr(self, attr_name, None)
            if sibling_mixin is not None:
                # Returns MixinV2 directly (caller will call .evaluated when needed)
                return sibling_mixin
            # Fallback to navigation if not found as attribute (lazy scopes)

        # Super mixins (lexical_outer_index != OWN) OR parent scope deps:
        # Always resolve via navigation
        # Pass OUR lexical_outer_index to follow the correct inheritance chain
        return ref.get_mixin_v2(
            outer=self,
            lexical_outer_index=self.lexical_outer_index,
        )

    @cached_property
    def evaluated(self) -> "object | ScopeV2":
        """
        Evaluate this mixin.

        Dynamically decides based on symbol:
        - If symbol is a scope symbol: returns ScopeV2
        - If symbol is a resource symbol: returns evaluated value
        """
        if self.symbol.is_scope:
            # Scope: construct nested ScopeV2
            # Pass self as the outer_mixin for children of this scope
            # Propagate kwargs to nested scope
            return construct_scope_v2(
                symbol=self.symbol,
                outer_mixin=self,
                kwargs=self.kwargs,
            )
        else:
            # Resource: merge patches and return value
            return self._evaluate_resource()

    def _evaluate_resource(self) -> object:
        """
        Evaluate by resolving dependencies from _sibling_dependencies and outer.

        IMPORTANT: _sibling_dependencies is ONLY valid for direct children
        (where lexical_outer_index=OWN). Super mixins have lexical_outer_index=int
        and their levels_up=0 dependencies refer to siblings in the BASE scope,
        not our scope. They must always resolve via navigation.

        This mirrors V1's Resource.evaluated logic exactly.
        """
        from mixinject import (
            ElectedMerger,
            MergerElectionSentinel,
            SymbolIndexSentinel,
        )

        def build_evaluators_for_mixin(mixin: "MixinV2") -> tuple[EvaluatorV2, ...]:
            """Build evaluators for a given MixinV2."""
            return tuple(
                evaluator_symbol.bind_v2(mixin=mixin)
                for evaluator_symbol in mixin.symbol.evaluator_symbols
            )

        # Get elected merger info
        elected = self.symbol.elected_merger_index

        # Collect patches from all patchers (excluding elected if applicable)
        def generate_patches() -> Iterator[object]:
            match elected:
                case ElectedMerger(
                    symbol_index=elected_symbol_index,
                    evaluator_getter_index=elected_getter_index,
                ):
                    # Collect patches from own evaluators
                    own_evaluators = build_evaluators_for_mixin(self)
                    if elected_symbol_index is SymbolIndexSentinel.OWN:
                        # Exclude the elected evaluator from own
                        for evaluator_index, evaluator in enumerate(own_evaluators):
                            if evaluator_index != elected_getter_index and isinstance(
                                evaluator, PatcherV2
                            ):
                                yield from evaluator
                    else:
                        # Elected is from super, collect all from own
                        for evaluator in own_evaluators:
                            if isinstance(evaluator, PatcherV2):
                                yield from evaluator

                    # Collect patches from super mixins
                    for index, super_mixin in enumerate(self.strict_super_mixins):
                        super_evaluators = build_evaluators_for_mixin(super_mixin)
                        if index != elected_symbol_index:
                            for evaluator in super_evaluators:
                                if isinstance(evaluator, PatcherV2):
                                    yield from evaluator
                        else:
                            # Exclude the elected evaluator's patcher from super
                            for evaluator_index, evaluator in enumerate(
                                super_evaluators
                            ):
                                if evaluator_index != elected_getter_index and isinstance(
                                    evaluator, PatcherV2
                                ):
                                    yield from evaluator

                case MergerElectionSentinel.PATCHER_ONLY:
                    # Collect all patches from own and super
                    own_evaluators = build_evaluators_for_mixin(self)
                    for evaluator in own_evaluators:
                        if isinstance(evaluator, PatcherV2):
                            yield from evaluator
                    for super_mixin in self.strict_super_mixins:
                        super_evaluators = build_evaluators_for_mixin(super_mixin)
                        for evaluator in super_evaluators:
                            if isinstance(evaluator, PatcherV2):
                                yield from evaluator

        # Handle PATCHER_ONLY case (requires instance scope with kwargs)
        if elected is MergerElectionSentinel.PATCHER_ONLY:
            key = self.symbol.key
            # Check if we have kwargs (instance scope)
            if isinstance(self.kwargs, KwargsSentinel):
                raise ValueError(
                    f"Patcher-only resource '{key}' requires instance scope. "
                    f"Call scope(**kwargs) to create an instance scope with the required value."
                )
            # Get base value from kwargs
            if not isinstance(key, str) or key not in self.kwargs:
                raise ValueError(
                    f"Patcher-only resource '{key}' requires kwargs['{key}'] but it was not provided."
                )
            base_value = self.kwargs[key]

            # Collect all patches and apply as endofunctions
            patches = generate_patches()
            return reduce(
                lambda accumulator, endofunction: endofunction(accumulator),  # type: ignore[operator]
                patches,
                base_value,
            )

        # Get Merger evaluator from elected position
        assert isinstance(elected, ElectedMerger)
        elected_mixin = self.get_super(elected.symbol_index)
        elected_evaluators = build_evaluators_for_mixin(elected_mixin)
        merger_evaluator = elected_evaluators[elected.evaluator_getter_index]
        assert isinstance(merger_evaluator, MergerV2)

        return merger_evaluator.merge(generate_patches())


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True, eq=False)
class ScopeV2:
    """
    Frozen container for MixinV2 references.

    ScopeV2 does NOT inherit from MixinV2.

    _children ALWAYS stores MixinV2 references (never evaluated values).
    This provides consistency: all children are accessed the same way via .evaluated.

    For is_eager=True resources:
    - MixinV2 is stored in _children (same as lazy)
    - mixin.evaluated is called during construct_scope_v2() to trigger evaluation
    - The @cached_property caches the result, so subsequent access is instant

    Private resources (is_public=False) are NOT stored in _children.
    They exist only in _sibling_dependencies of MixinV2 instances that depend on them.
    """

    symbol: Final["MixinSymbol"]

    _outer_mixin: Final["MixinV2 | OuterSentinel"]
    """
    The outer MixinV2 that this scope was constructed from.
    Needed by __call__ to create instance scopes with the same outer context.
    """

    kwargs: Final["Mapping[str, object] | KwargsSentinel"]
    """
    Keyword arguments for instance scope support.

    - KwargsSentinel.STATIC: This is a static scope (can call __call__ to create instance)
    - Mapping[str, object]: This is an instance scope (cannot call __call__ again)
    """

    _children: Final[Mapping["MixinSymbol", "MixinV2"]]
    """
    Public child MixinV2 references keyed by MixinSymbol.
    - ALWAYS stores MixinV2 (never evaluated values)
    - is_eager=True: MixinV2.evaluated already called during construction (cached)
    - is_eager=False: MixinV2.evaluated called on first access (lazy)
    - is_public=False: NOT stored here (only in _sibling_dependencies of dependents)
    """

    def __getattr__(self, name: str) -> object:
        """Access child by attribute name."""
        if name.startswith("_"):
            raise AttributeError(name)
        # Find symbol by key
        child_symbol = self.symbol.get(name)
        if child_symbol is None:
            raise AttributeError(name)
        # Private resources are blocked from external access
        if not child_symbol.is_public:
            raise AttributeError(name)
        return self._children[child_symbol].evaluated

    def __getitem__(self, key: Hashable) -> object:
        """Access child by key."""
        child_symbol = self.symbol.get(key)
        if child_symbol is None:
            raise KeyError(key)
        # Private resources are blocked from external access
        if not child_symbol.is_public:
            raise KeyError(key)
        return self._children[child_symbol].evaluated

    def __dir__(self) -> list[str]:
        """Return list of accessible attribute names including resource names."""
        # Get standard dataclass attributes
        base_attrs = set(super(ScopeV2, self).__dir__())

        # Add resource attribute names from PUBLIC children only
        # Use .key which is the actual resource name (e.g., 'foo')
        for child_symbol in self._children:
            if child_symbol.is_public:
                key = child_symbol.key
                if isinstance(key, str):
                    base_attrs.add(key)

        return sorted(base_attrs)

    def __call__(self, **kwargs: object) -> "ScopeV2":
        """
        Create an instance scope with the given kwargs.

        Instance scopes allow PATCHER_ONLY resources (declared with @extern)
        to receive their base values from kwargs.

        :param kwargs: Keyword arguments providing values for @extern resources.
        :return: A new ScopeV2 instance with the provided kwargs.
        :raises TypeError: If called on an instance scope (cannot create instance from instance).
        """
        from mixinject import OuterSentinel, SymbolIndexSentinel

        if not isinstance(self.kwargs, KwargsSentinel):
            raise TypeError("Cannot create instance from an instance scope")

        # Create a new synthetic outer MixinV2 with instance kwargs.
        # This is needed so that children can navigate up and find kwargs
        # for PATCHER_ONLY resources. Without this, children would navigate
        # to the original static outer MixinV2 which has KwargsSentinel.STATIC.
        original_outer = self._outer_mixin
        if isinstance(original_outer, OuterSentinel):
            # Root scope: create synthetic root mixin with instance kwargs
            synthetic_outer: MixinV2 | OuterSentinel = MixinV2(
                symbol=self.symbol,
                outer=OuterSentinel.ROOT,
                lexical_outer_index=SymbolIndexSentinel.OWN,
                kwargs=kwargs,
            )
        else:
            # Nested scope: create synthetic outer with same outer chain but instance kwargs
            synthetic_outer = MixinV2(
                symbol=original_outer.symbol,
                outer=original_outer.outer,
                lexical_outer_index=original_outer.lexical_outer_index,
                kwargs=kwargs,
            )

        return construct_scope_v2(
            symbol=self.symbol,
            outer_mixin=synthetic_outer,
            kwargs=kwargs,
        )


def construct_scope_v2(
    symbol: "MixinSymbol",
    outer_mixin: "MixinV2 | OuterSentinel",
    kwargs: "Mapping[str, object] | KwargsSentinel",
) -> ScopeV2:
    """
    Two-phase construction for ScopeV2 with circular dependency support.

    Phase 1: Create all MixinV2 instances (enables circular dependency references)
    Phase 2: Wire _sibling_dependencies for dependency resolution
    Phase 3: Build _children dict (excluding local, eager values stored)

    :param symbol: The MixinSymbol for this scope.
    :param outer_mixin: The parent scope's MixinV2, or OuterSentinel.ROOT for root.
    :param kwargs: Keyword arguments for instance scope (KwargsSentinel.STATIC for static).
    :return: A ScopeV2 instance.
    """
    from mixinject import SymbolIndexSentinel

    # Phase 1: Create all MixinV2 instances
    # outer_mixin is shared by all children (they're all in the same scope)
    all_mixins: dict["MixinSymbol", MixinV2] = {
        (child_symbol := symbol[key]): MixinV2(
            symbol=child_symbol,
            outer=outer_mixin,
            lexical_outer_index=SymbolIndexSentinel.OWN,
            kwargs=kwargs,
        )
        for key in symbol
    }

    # Phase 2: Wire dependency references as attributes on each MixinV2
    # Each MixinV2 gets its sibling dependencies stored as attributes via setattr
    # Keyed by attribute_name (str) for future JIT optimization with make_dataclass
    for child_symbol, mixin in all_mixins.items():
        # Get dependency symbols from the symbol's same_scope_dependencies property
        dependency_symbols = child_symbol.same_scope_dependencies
        # Look up by attribute_name in all_mixins since dependency_symbol might be from
        # a different branch in union mounts
        for dependency_symbol in dependency_symbols:
            other_mixin = next(
                other_mixin
                for other_symbol, other_mixin in all_mixins.items()
                if other_symbol.attribute_name == dependency_symbol.attribute_name
            )
            setattr(mixin, dependency_symbol.attribute_name, other_mixin)

    # Phase 3: Build _children dict (ALL children, including private)
    # Private resources are accessible internally (for @extend navigation)
    # but external access is blocked by is_public check in __getattr__/__getitem__
    children: dict["MixinSymbol", MixinV2] = dict(all_mixins)

    # Trigger eager evaluation (result cached by @cached_property)
    for child_symbol, mixin in children.items():
        if child_symbol.is_eager:
            _ = mixin.evaluated

    # Phase 4: Create frozen ScopeV2
    return ScopeV2(
        symbol=symbol,
        _outer_mixin=outer_mixin,
        kwargs=kwargs,
        _children=children,
    )


# =============================================================================
# EvaluatorV2 Hierarchy
# =============================================================================


@dataclass(kw_only=True, frozen=True, eq=False)
class EvaluatorV2(ABC):
    """
    Base class for V2 resource evaluators.

    NOTE: Does NOT inherit from Node/Evaluator - completely separate hierarchy.

    Each evaluator stores the mixin it belongs to. To resolve dependencies,
    call self.mixin.resolve_dependency(ref) which returns MixinV2.
    Then call .evaluated on the returned MixinV2 to get the actual value.
    """

    mixin: MixinV2
    """
    The MixinV2 that holds this EvaluatorV2.

    To resolve dependencies, call self.mixin.resolve_dependency(ref).
    This returns MixinV2, NOT the evaluated value.
    The caller calls .evaluated when it actually needs the dependency value.
    """


@dataclass(kw_only=True, frozen=True, eq=False)
class MergerV2(EvaluatorV2, Generic[TPatch_contra, TResult_co], ABC):
    """EvaluatorV2 that merges patches to produce a result."""

    @abstractmethod
    def merge(self, patches: Iterator[TPatch_contra]) -> TResult_co:
        """Merge patches to produce the final result."""
        ...


@dataclass(kw_only=True, frozen=True, eq=False)
class PatcherV2(EvaluatorV2, Iterable[TPatch_co], Generic[TPatch_co], ABC):
    """EvaluatorV2 that provides patches."""


@dataclass(kw_only=True, frozen=True, eq=False)
class SemigroupV2(MergerV2[T, T], PatcherV2[T], Generic[T], ABC):
    """Both MergerV2 and PatcherV2."""


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True, eq=False)
class FunctionalMergerV2(MergerV2[TPatch_contra, TResult_co]):
    """V2 Evaluator for FunctionalMergerDefinition."""

    evaluator_getter: "FunctionalMergerSymbol[TPatch_contra, TResult_co]"

    def merge(self, patches: Iterator[TPatch_contra]) -> TResult_co:
        """Merge patches using the aggregation function.

        The function (e.g., @merge def tags() -> type[frozenset]: return frozenset)
        returns an aggregation function. We call that function with the patches.
        """
        # compiled_function_v2 returns a function that takes MixinV2 and returns
        # the aggregation function (e.g., frozenset, list, etc.)
        aggregation_function = self.evaluator_getter.compiled_function_v2(self.mixin)
        # Call it with the patches
        return aggregation_function(patches)  # type: ignore


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True, eq=False)
class EndofunctionMergerV2(MergerV2[Callable[[TResult], TResult], TResult]):
    """V2 Evaluator for EndofunctionMergerDefinition."""

    evaluator_getter: "EndofunctionMergerSymbol[TResult]"

    def merge(self, patches: Iterator[Callable[[TResult], TResult]]) -> TResult:
        """Merge endofunction patches by applying them to base value."""
        # compiled_function_v2 returns a function that takes MixinV2 and returns
        # the base value for endofunction application
        base_value: TResult = self.evaluator_getter.compiled_function_v2(self.mixin)

        return reduce(
            lambda accumulator, endofunction: endofunction(accumulator),
            patches,
            base_value,
        )


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True, eq=False)
class SinglePatcherV2(PatcherV2[TPatch_co]):
    """V2 Evaluator for SinglePatcherDefinition."""

    evaluator_getter: "SinglePatcherSymbol[TPatch_co]"

    def __iter__(self) -> Iterator[TPatch_co]:
        """Yield the single patch value."""
        # compiled_function_v2 returns a function that takes MixinV2 and returns
        # the patch value
        yield self.evaluator_getter.compiled_function_v2(self.mixin)


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True, eq=False)
class MultiplePatcherV2(PatcherV2[TPatch_co]):
    """V2 Evaluator for MultiplePatcherDefinition."""

    evaluator_getter: "MultiplePatcherSymbol[TPatch_co]"

    def __iter__(self) -> Iterator[TPatch_co]:
        """Yield multiple patch values."""
        # compiled_function_v2 returns a function that takes MixinV2 and returns
        # an iterable of patch values
        yield from self.evaluator_getter.compiled_function_v2(self.mixin)


def evaluate_v2(
    *namespaces: "ModuleType | ScopeDefinition",
    modules_public: bool = False,
) -> ScopeV2:
    """
    Resolves a ScopeV2 from the given namespaces.

    This is the V2 entrypoint that provides:
    - Single lazy evaluation level (at MixinV2.evaluated only)
    - Proper is_public semantics (private resources hidden from attributes)
    - Proper is_eager semantics (eager resources evaluated immediately)
    - Circular dependency support via two-phase construction

    When multiple namespaces are provided, they are union-mounted at the root level.
    Resources from all namespaces are merged according to the merger election algorithm.

    :param namespaces: Modules or namespace definitions (decorated with @scope) to resolve.
    :param modules_public: If True, modules are marked as public, making their submodules
        accessible via attribute access. Defaults to False (private by default).
    :return: The root ScopeV2.

    Example::

        root = evaluate_v2(MyNamespace)
        root = evaluate_v2(Base, Override)  # Union mount
        root = evaluate_v2(my_package, modules_public=True)  # Make modules accessible

    """
    from dataclasses import replace
    from types import ModuleType
    from typing import assert_never

    from mixinject import (
        MixinSymbol,
        OuterSentinel,
        ScopeDefinition,
        SymbolIndexSentinel,
        _parse_package,
    )

    assert namespaces, "evaluate_v2() requires at least one namespace"

    def to_scope_definition(
        namespace: ModuleType | ScopeDefinition,
    ) -> ScopeDefinition:
        if isinstance(namespace, ScopeDefinition):
            return namespace
        if isinstance(namespace, ModuleType):
            definition = _parse_package(namespace)
            if modules_public:
                return replace(definition, is_public=True)
            return definition
        assert_never(namespace)

    definitions = tuple(to_scope_definition(namespace) for namespace in namespaces)

    root_symbol = MixinSymbol(origin=definitions)

    # Create a synthetic root MixinV2 to enable lexical scope navigation
    # This is needed so that children of the root scope can navigate up
    # to find parent scope dependencies (via get_mixin_v2)
    root_mixin = MixinV2(
        symbol=root_symbol,
        outer=OuterSentinel.ROOT,
        lexical_outer_index=SymbolIndexSentinel.OWN,
        kwargs=KwargsSentinel.STATIC,  # Root is always static
    )

    # Evaluate the root mixin to get the ScopeV2
    result = root_mixin.evaluated
    assert isinstance(result, ScopeV2)
    return result


# Re-export types needed by TYPE_CHECKING imports
if TYPE_CHECKING:
    from types import ModuleType

    from mixinject import ScopeDefinition
