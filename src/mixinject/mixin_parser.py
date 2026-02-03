"""
Parser for MIXIN specification files (YAML/JSON/TOML).

This module provides parsing of MIXIN files into Definition objects that can be
evaluated by the mixinject runtime.
"""

from __future__ import annotations

import json
import tomllib
from collections.abc import Hashable, Iterator, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias, final

import yaml

from mixinject import (
    Definition,
    LexicalReference,
    QualifiedThisReference,
    ResourceReference,
    ScopeDefinition,
)

# JSON-compatible type aliases
JsonScalar: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonScalar | list["JsonValue"] | dict[str, "JsonValue"]


@final
@dataclass(frozen=True, kw_only=True, slots=True, weakref_slot=True)
class FileMixinDefinition(ScopeDefinition):
    """
    Definition for a mixin parsed from a MIXIN file.

    This holds the parsed properties from the file. The `underlying` field
    stores the raw parsed data, and properties are resolved lazily via
    __iter__ and __getitem__.
    """

    underlying: Mapping[str, JsonValue]
    """The parsed properties from the mixin definition."""

    scalar_values: tuple[JsonScalar, ...]
    """Scalar values inherited by this mixin."""

    source_file: Path
    """Path to the source file for error reporting."""

    def __iter__(self) -> Iterator[Hashable]:
        """Yield property names from this mixin."""
        yield from self.underlying.keys()

    def __len__(self) -> int:
        return len(self.underlying)

    def __getitem__(self, key: Hashable) -> Sequence[Definition]:
        """Get child definitions by property name."""
        assert isinstance(key, str)
        if key not in self.underlying:
            raise KeyError(key)

        value = self.underlying[key]
        parsed = parse_mixin_value(value, source_file=self.source_file)
        return (
            FileMixinDefinition(
                bases=parsed.inheritances,
                is_public=True,
                underlying=parsed.properties,
                scalar_values=parsed.scalar_values,
                source_file=self.source_file,
            ),
        )


@final
@dataclass(frozen=True, kw_only=True, slots=True, weakref_slot=True)
class ParsedMixinValue:
    """Result of parsing a single mixin value."""

    inheritances: tuple[ResourceReference, ...]
    """Inheritance references (bases)."""

    properties: Mapping[str, JsonValue]
    """Property definitions."""

    scalar_values: tuple[JsonScalar, ...]
    """Scalar values."""


def parse_reference(array: list[JsonValue]) -> ResourceReference:
    """
    Parse a MIXIN array reference into a ResourceReference.

    Distinguishes between:
    - Regular inheritance: [str, str, ...] → LexicalReference
    - Qualified this: [str, null, str, ...] → QualifiedThisReference

    :param array: The array from the MIXIN file.
    :return: A ResourceReference.
    :raises ValueError: If the array is empty or has invalid format.
    """
    if not array:
        raise ValueError("Reference array must not be empty")

    # Check for qualified this: [str, null, str, ...]
    if len(array) >= 2 and array[1] is None:
        self_name = array[0]
        if not isinstance(self_name, str):
            raise ValueError(
                f"Qualified this self_name must be a string, got {type(self_name).__name__}"
            )
        path_elements: list[str] = []
        for element in array[2:]:
            if not isinstance(element, str):
                raise ValueError(
                    f"Reference path element must be a string, got {type(element).__name__}: {element!r}"
                )
            path_elements.append(element)
        return QualifiedThisReference(self_name=self_name, path=tuple(path_elements))

    # Regular inheritance: all elements must be strings
    path_elements = []
    for element in array:
        if not isinstance(element, str):
            raise ValueError(
                f"Reference path element must be a string, got {type(element).__name__}: {element!r}"
            )
        path_elements.append(element)
    return LexicalReference(path=tuple(path_elements))


def parse_mixin_value(
    value: JsonValue,
    source_file: Path,  # noqa: ARG001 - reserved for future error messages
) -> ParsedMixinValue:
    """
    Parse a MIXIN value into inheritances, properties, and scalar values.

    A mixin value can be:
    - An array containing inheritance references, property objects, and scalars
    - An object containing only properties
    - A scalar value

    :param value: The parsed JSON value from the mixin file.
    :param source_file: Path to source file for error reporting.
    :return: ParsedMixinValue with separated components.
    """
    del source_file  # Reserved for future error messages
    inheritances: list[ResourceReference] = []
    properties: dict[str, JsonValue] = {}
    scalar_values: list[JsonScalar] = []

    if isinstance(value, list):
        # Array format: can contain inheritances, properties, and scalars
        for item in value:
            if isinstance(item, list):
                # Inheritance reference
                inheritances.append(parse_reference(item))
            elif isinstance(item, dict):
                # Property definition(s)
                for prop_name, prop_value in item.items():
                    if prop_name in properties:
                        # Merge properties with same name
                        existing = properties[prop_name]
                        if isinstance(existing, dict) and isinstance(prop_value, dict):
                            merged = dict(existing)
                            merged.update(prop_value)
                            properties[prop_name] = merged
                        else:
                            # For non-dict values, later definition wins
                            properties[prop_name] = prop_value
                    else:
                        properties[prop_name] = prop_value
            elif isinstance(item, str | int | float | bool) or item is None:
                # Scalar value
                scalar_values.append(item)
            else:
                raise ValueError(f"Unexpected item type in mixin array: {type(item).__name__}")
    elif isinstance(value, dict):
        # Object format: all properties, no inheritances
        properties = dict(value)
    elif isinstance(value, str | int | float | bool) or value is None:
        # Single scalar value
        scalar_values.append(value)
    else:
        raise ValueError(f"Unexpected mixin value type: {type(value).__name__}")

    return ParsedMixinValue(
        inheritances=tuple(inheritances),
        properties=properties,
        scalar_values=tuple(scalar_values),
    )


def parse_mixin_file(file_path: Path) -> Mapping[str, FileMixinDefinition]:
    """
    Parse a MIXIN file (YAML/JSON/TOML) into definitions.

    :param file_path: Path to the mixin file.
    :return: Mapping of top-level mixin names to their definitions.
    :raises ValueError: If the file format is not recognized or parsing fails.
    """
    content = file_path.read_text(encoding="utf-8")

    # Determine format from the full filename pattern
    name = file_path.name.lower()
    if name.endswith(".mixin.yaml") or name.endswith(".mixin.yml"):
        data = yaml.safe_load(content)
    elif name.endswith(".mixin.json"):
        data = json.loads(content)
    elif name.endswith(".mixin.toml"):
        data = tomllib.loads(content)
    else:
        raise ValueError(
            f"Unrecognized MIXIN file format: {file_path.name}. "
            f"Expected .mixin.yaml, .mixin.json, or .mixin.toml"
        )

    if not isinstance(data, dict):
        raise ValueError(
            f"MIXIN file must contain a mapping at top level, got {type(data).__name__}"
        )

    result: dict[str, FileMixinDefinition] = {}
    for mixin_name, mixin_value in data.items():
        if not isinstance(mixin_name, str):
            raise ValueError(f"Mixin name must be a string, got {type(mixin_name).__name__}")

        parsed = parse_mixin_value(mixin_value, source_file=file_path)
        result[mixin_name] = FileMixinDefinition(
            bases=parsed.inheritances,
            is_public=True,
            underlying=parsed.properties,
            scalar_values=parsed.scalar_values,
            source_file=file_path,
        )

    return result
