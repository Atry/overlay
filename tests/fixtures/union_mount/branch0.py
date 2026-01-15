"""Branch 0: Defines aggregators for deduplicated_tags and union_mount_point."""

from typing import Callable, Iterator

from mixinject import CachedProxy, Mixin, aggregator


@aggregator
def deduplicated_tags() -> Callable[[Iterator[str]], frozenset[str]]:
    return frozenset


@aggregator
def union_mount_point() -> Callable[[Iterator[Mixin]], CachedProxy]:
    def create_proxy(mixins: Iterator[Mixin]) -> CachedProxy:
        return CachedProxy(mixins=frozenset(mixins))

    return create_proxy
