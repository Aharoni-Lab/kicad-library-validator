"""
Symbol validator module.
"""

import re
from typing import Any, Dict, List, Optional

from kicad_lib_validator.models.structure import (
    ComponentEntry,
    ComponentGroup,
    LibraryStructure,
)
from kicad_lib_validator.models.symbol import Symbol


def validate_symbol(symbol: Symbol, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate a symbol against the library structure.

    Args:
        symbol: Symbol to validate
        structure: Library structure definition

    Returns:
        Dictionary containing lists of errors, warnings, and successes
    """
    result = {"errors": [], "warnings": [], "successes": []}

    # Require categories for lookup
    if (
        not symbol.categories
        or not isinstance(symbol.categories, list)
        or len(symbol.categories) == 0
    ):
        result["errors"].append("Symbol must specify a non-empty categories list for validation.")
        return result

    # Traverse the nested structure using categories
    group = structure.symbols
    entry = None
    path = symbol.categories.copy()
    while path:
        key = path.pop(0)
        if isinstance(group, dict):
            if key not in group:
                result["errors"].append(f"Unknown group: {key}")
                return result
            group = group[key]
        elif isinstance(group, ComponentGroup):
            if group.subgroups and key in group.subgroups:
                group = group.subgroups[key]
            elif group.entries and key in group.entries:
                entry = group.entries[key]
                break
            else:
                result["errors"].append(f"Unknown subgroup or entry: {key}")
                return result
        else:
            result["errors"].append(f"Invalid group structure at: {key}")
            return result

    if entry is None:
        # If we ended on a ComponentGroup with only one entry, use it
        if isinstance(group, ComponentGroup) and group.entries and len(group.entries) == 1:
            entry = next(iter(group.entries.values()))
        else:
            result["errors"].append(
                "Could not resolve a ComponentEntry for the given categories path."
            )
            return result

    # Validate symbol name
    if entry.naming and entry.naming.pattern:
        pattern = entry.naming.pattern
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        if not pattern.match(symbol.name):
            result["errors"].append(
                f"Symbol name '{symbol.name}' does not match pattern: {entry.naming.pattern}"
            )
        else:
            result["successes"].append(
                f"Symbol name '{symbol.name}' matches pattern: {entry.naming.pattern}"
            )

    # Validate required properties
    if entry.required_properties:
        for prop_name, prop_def in entry.required_properties.items():
            if prop_name not in symbol.properties:
                result["errors"].append(f"Missing required property: {prop_name}")
            elif prop_def.pattern:
                pattern = prop_def.pattern
                if isinstance(pattern, str):
                    pattern = re.compile(pattern)
                if not pattern.match(symbol.properties[prop_name]):
                    result["errors"].append(
                        f"Property '{prop_name}' value '{symbol.properties[prop_name]}' does not match pattern: {prop_def.pattern}"
                    )

    # Check for unknown properties
    if entry.required_properties:
        for prop_name in symbol.properties:
            if prop_name not in entry.required_properties:
                result["warnings"].append(f"Unknown property: {prop_name}")

    return result


def validate_symbol_name(name: str, structure: LibraryStructure, category: str) -> bool:
    """Validate a symbol name against the structure rules for the given category."""
    # TODO: Implement symbol name validation logic
    return True


def validate_symbol_property(
    property_name: str, value: str, structure: LibraryStructure, category: str
) -> bool:
    """Validate a symbol property value against the structure rules for the given category."""
    # TODO: Implement symbol property validation logic
    return True
