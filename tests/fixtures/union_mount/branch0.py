"""Branch 0: Defines merges for deduplicated_tags and union_mount_point."""

from typing import Callable, Iterator

from mixinject import CachedProxy, Mixin, merge


@merge
def deduplicated_tags() -> Callable[[Iterator[str]], frozenset[str]]:
    return frozenset


@merge
def union_mount_point() -> Callable[[Iterator[Mixin]], CachedProxy]:
    def create_proxy(mixins: Iterator[Mixin]) -> CachedProxy:
        return CachedProxy(mixins=frozenset(mixins))

    return create_proxy
