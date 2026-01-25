"""Tests for nested lexical scope functionality.

Ported from the original test_nested_lexical_scope.py to work with the new
Mixin-based architecture (lexical_outer_index instead of CapturedScopes).
"""

from dataclasses import dataclass
from typing import Any, Final, Iterator, final, override

import pytest

from mixinject import (
    Definition,
    EvaluatorDefinition,
    EvaluatorSymbol,
    Merger,
    MergerSymbol,
    Mixin,
    OuterSentinel,
    Patcher,
    PatcherSymbol,
    RelativeReference,
    Semigroup,
    SemigroupSymbol,
    MixinSymbol,
    evaluate,
    extend,
    extern,
    resource,
    scope,
)

R = RelativeReference


# =============================================================================
# Test helpers for custom Merger/Patcher/Semigroup tests
# =============================================================================


@dataclass(kw_only=True, frozen=True)
class _TestDefinition(Definition):
    """Data holder definition for test symbols (not compiled directly)."""

    value: Final[str]


# -----------------------------------------------------------------------------
# Dual (Semigroup) - both Merger and Patcher
# -----------------------------------------------------------------------------


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True)
class _Dual(Semigroup[Any]):
    """
    Test helper: Semigroup (both Merger and Patcher) with a configurable value.

    As Merger: Returns "merger-{value}-{sorted patches joined by -}"
    As Patcher: Yields "patch-{value}"
    """

    evaluator_getter: "_DualSymbol"

    @property
    def value(self) -> str:
        return self.evaluator_getter.definition.value

    @override
    def merge(self, patches: Iterator[Any]) -> str:
        return f"merger-{self.value}-" + "-".join(sorted(str(p) for p in patches))

    @override
    def __iter__(self) -> Iterator[str]:
        yield f"patch-{self.value}"


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True)
class _DualSymbol(SemigroupSymbol[Any]):
    """EvaluatorSymbol that returns a _Dual (Semigroup)."""

    definition: _TestDefinition

    @override
    def bind(self, mixin: Mixin) -> _Dual:
        return _Dual(mixin=mixin, evaluator_getter=self)


@dataclass(kw_only=True, frozen=True)
class _DualDefinition(EvaluatorDefinition):
    """Definition that creates a _DualSymbol."""

    value: str

    @override
    def compile(self, symbol: MixinSymbol, /) -> _DualSymbol:
        return _DualSymbol(
            symbol=symbol,
            definition=_TestDefinition(bases=(), value=self.value),
        )


# -----------------------------------------------------------------------------
# Pure Merger - only Merger, not Patcher
# -----------------------------------------------------------------------------


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True)
class _PureMerger(Merger[Any, str]):
    """
    Test helper: Pure Merger (not a Patcher) with a configurable value.

    Returns "pure-{value}-{sorted patches joined by -}"
    """

    evaluator_getter: "_PureMergerSymbol"

    @property
    def value(self) -> str:
        return self.evaluator_getter.definition.value

    @override
    def merge(self, patches: Iterator[Any]) -> str:
        return f"pure-{self.value}-" + "-".join(sorted(str(p) for p in patches))


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True)
class _PureMergerSymbol(MergerSymbol[Any, str]):
    """EvaluatorSymbol that returns a _PureMerger (pure Merger)."""

    definition: _TestDefinition

    @override
    def bind(self, mixin: Mixin) -> _PureMerger:
        return _PureMerger(mixin=mixin, evaluator_getter=self)


@dataclass(kw_only=True, frozen=True)
class _PureMergerDefinition(EvaluatorDefinition):
    """Definition that creates a _PureMergerSymbol."""

    value: str

    @override
    def compile(self, symbol: MixinSymbol, /) -> _PureMergerSymbol:
        return _PureMergerSymbol(
            symbol=symbol,
            definition=_TestDefinition(bases=(), value=self.value),
        )


# -----------------------------------------------------------------------------
# Pure Patcher - only Patcher, not Merger
# -----------------------------------------------------------------------------


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True)
class _PurePatcher(Patcher[str]):
    """
    Test helper: Pure Patcher (not a Merger) with a configurable value.

    Yields "patch-{value}"
    """

    evaluator_getter: "_PurePatcherSymbol"

    @property
    def value(self) -> str:
        return self.evaluator_getter.definition.value

    @override
    def __iter__(self) -> Iterator[str]:
        yield f"patch-{self.value}"


@final
@dataclass(kw_only=True, slots=True, weakref_slot=True, frozen=True)
class _PurePatcherSymbol(PatcherSymbol[str]):
    """EvaluatorSymbol that returns a _PurePatcher (pure Patcher)."""

    definition: _TestDefinition

    @override
    def bind(self, mixin: Mixin) -> _PurePatcher:
        return _PurePatcher(mixin=mixin, evaluator_getter=self)


@dataclass(kw_only=True, frozen=True)
class _PurePatcherDefinition(EvaluatorDefinition):
    """Definition that creates a _PurePatcherSymbol."""

    value: str

    @override
    def compile(self, symbol: MixinSymbol, /) -> _PurePatcherSymbol:
        return _PurePatcherSymbol(
            symbol=symbol,
            definition=_TestDefinition(bases=(), value=self.value),
        )


# =============================================================================
# Tests
# =============================================================================


class TestNestedCapturedScopes:
    """Tests for nested scope lookup and lexical scope resolution."""

    def test_nested_captured_scopes_lookup(self) -> None:
        """
        Non-same-name parameters can be looked up in outer lexical scope.
        """

        @scope
        class Outer:
            @resource
            def outer_val() -> str:
                return "outer"

            @scope
            class Inner:
                @resource
                def inner_val(outer_val: str) -> str:
                    # This depends on 'outer_val' which is in Outer scope.
                    return f"inner-{outer_val}"

        root = evaluate(Outer)
        assert root.Inner.inner_val == "inner-outer"

    def test_scope_as_patch(self) -> None:
        """Test: @scope used as a patch for another @scope.

        When Extension depends on resources from Base, it must declare
        those dependencies using @extern to make them visible at compile time.
        """

        @scope
        class Root:
            @scope
            class Base:
                @resource
                def val() -> str:
                    return "base"

            @scope
            class Extension:
                @extern
                def val() -> str:
                    """Declare that val is expected to be provided by Base."""
                    ...

                @resource
                def extended_val(val: str) -> str:
                    return f"{val}-extended"

                @resource
                def extra() -> str:
                    return "extra"

            @extend(
                R(levels_up=0, path=("Base",)),
                R(levels_up=0, path=("Extension",)),
            )
            @scope
            class Combined:
                pass

        root = evaluate(Root)
        assert root.Combined.extended_val == "base-extended"
        assert root.Combined.extra == "extra"


class TestMergerElection:
    """Tests for merger election algorithm."""

    def test_evaluate_resource_dual_role_single(self) -> None:
        """Test: Single Dual item -> selected as Merger."""

        @scope
        class Namespace:
            target = _DualDefinition(bases=(), value="A")

        root = evaluate(Namespace)
        assert root.target == "merger-A-"

    def test_evaluate_resource_dual_and_patch(self) -> None:
        """Test: Dual + Dual -> One is Merger, other is Patch."""

        @scope
        class Root:
            @scope
            class N1:
                target = _DualDefinition(bases=(), value="A")

            @scope
            class N2:
                target = _DualDefinition(bases=(), value="B")

            @extend(
                R(levels_up=0, path=("N1",)),
                R(levels_up=0, path=("N2",)),
            )
            @scope
            class Combined:
                pass

        root = evaluate(Root)
        value = root.Combined.target
        # Either merger-A-patch-B or merger-B-patch-A
        assert value == "merger-A-patch-B" or value == "merger-B-patch-A"

    def test_evaluate_resource_pure_merger_and_dual(self) -> None:
        """Test: Pure Merger + Dual -> Pure Merger selected, Dual is Patch."""

        @scope
        class Root:
            @scope
            class N1:
                target = _PureMergerDefinition(bases=(), value="P")

            @scope
            class N2:
                target = _DualDefinition(bases=(), value="D")

            @extend(
                R(levels_up=0, path=("N1",)),
                R(levels_up=0, path=("N2",)),
            )
            @scope
            class Combined:
                pass

        root = evaluate(Root)
        # Pure P is merger. Dual D is patch.
        assert root.Combined.target == "pure-P-patch-D"

    def test_evaluate_resource_multiple_pure_mergers_error(self) -> None:
        """Test: Multiple pure mergers -> ValueError."""

        @scope
        class Root:
            @scope
            class N1:
                target = _PureMergerDefinition(bases=(), value="A")

            @scope
            class N2:
                target = _PureMergerDefinition(bases=(), value="B")

            @extend(
                R(levels_up=0, path=("N1",)),
                R(levels_up=0, path=("N2",)),
            )
            @scope
            class Combined:
                pass

        root = evaluate(Root)
        with pytest.raises(ValueError, match="Multiple pure merger definitions found"):
            _ = root.Combined.target

    def test_evaluate_resource_no_merger_error(self) -> None:
        """Test: Only patches (no merger) -> NotImplementedError when not in instance scope."""

        @scope
        class N1:
            target = _PurePatcherDefinition(bases=(), value="A")

        root = evaluate(N1)
        with pytest.raises(NotImplementedError, match="requires instance scope"):
            _ = root.target
