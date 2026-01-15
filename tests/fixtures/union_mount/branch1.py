"""Branch 1: Provides tag1 patch and another_dependency resource."""

from mixinject import Mixin, patch, resource, simple_mixin


@patch
def deduplicated_tags() -> str:
    return "tag1"


@resource
def another_dependency() -> str:
    return "dependency_value"


@patch
def union_mount_point() -> Mixin:
    return simple_mixin(foo="foo")
