"""CLI entry point for navigating the MIXINv2 examples scope tree.

Usage::

    mixinv2-example app_oyaml Apps memory_app server
    mixinv2-example app_di step1_app
"""

import sys

import mixinv2_examples
import mixinv2_library
from mixinv2._runtime import evaluate


def main() -> None:
    path = sys.argv[1:]
    if not path:
        raise SystemExit("Usage: mixinv2-example <path...>")

    root = evaluate(mixinv2_library, mixinv2_examples, modules_public=True)
    current = root
    for segment in path:
        current = getattr(current, segment)

    print(current)
