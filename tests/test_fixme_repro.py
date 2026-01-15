import pytest
from mixinject import resource, resolve_root


class TestIssueReproduction:
    @pytest.mark.xfail(reason="known bug")
    def test_nested_lexical_scope_lookup_failure(self):
        """
        Non-same-name parameters cannot be looked up in outer lexical scope.
        """

        class Outer:
            @resource
            def outer_val() -> str:
                return "outer"

            class Inner:
                @resource
                def inner_val(outer_val: str) -> str:
                    # This depends on 'outer_val' which is in Outer scope.
                    # Current implementation only looks up 'outer_val' in Inner scope (current proxy)
                    # unless the parameter name matches the resource name (which is not the case).
                    return f"inner-{outer_val}"

        root = resolve_root(Outer)

        # This is expected to fail currently because Inner scope doesn't see Outer scope's outer_val.
        # Ideally, it should resolve to "inner-outer".
        assert root.Inner.inner_val == "inner-outer"
