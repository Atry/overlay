"""RemovePrefix: a @scope class with @extern fields for mixin.yaml composition."""

from mixinv2 import extern, public, resource, scope


@public
@scope
class RemovePrefix:
    @extern
    def this() -> str: ...

    @extern
    def prefix() -> str: ...

    @public
    @resource
    def prefixRemoved(this: str, prefix: str) -> str:
        return this.removeprefix(prefix)
