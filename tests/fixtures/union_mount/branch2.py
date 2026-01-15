"""Branch 2: Provides tag2 patch with dependency on another_dependency.

Note: @resource decorator returns a MergerDefinition object, not a function,
so @staticmethod is not needed (Python's descriptor protocol only applies to functions).
"""

from mixinject import Mixin, extern, patch, patch_many, mount, resource


@extern
def another_dependency() -> str:
    ...


@patch
def deduplicated_tags(another_dependency: str) -> str:
    return f"tag2_{another_dependency}"


class Mixin2:
    @extern
    def foo() -> str: ...

    @resource
    def bar(foo: str) -> str:
        return f"{foo}_bar"


@patch_many
def union_mount_point() -> frozenset[Mixin]:
    return mount(Mixin2).mixins
