"""
Footprint validation logic for KiCad libraries.
"""

import re
from typing import Dict, List

from kicad_lib_validator.models.footprint import Footprint
from kicad_lib_validator.models.structure import ComponentEntry, ComponentGroup, LibraryStructure


def validate_footprint_name(name: str, structure: LibraryStructure, category: str) -> bool:
    """Validate a footprint name against the structure rules for the given category."""
    # TODO: Implement footprint name validation logic
    return True


def validate_footprint_property(
    property_name: str, value: str, structure: LibraryStructure, category: str
) -> bool:
    """Validate a footprint property value against the structure rules for the given category."""
    # TODO: Implement footprint property validation logic
    return True


def validate_footprint(footprint: Footprint, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate a footprint against the library structure.

    Args:
        footprint: Footprint to validate
        structure: Library structure definition

    Returns:
        Dictionary containing validation results
    """
    result: Dict[str, List[str]] = {"errors": [], "warnings": [], "successes": []}

    # Require categories for lookup
    if (
        not footprint.categories
        or not isinstance(footprint.categories, list)
        or len(footprint.categories) == 0
    ):
        result["errors"].append(
            "Footprint must specify a non-empty categories list for validation."
        )
        return result

    # Traverse the nested structure using categories
    group = structure.footprints
    entry = None
    path = footprint.categories.copy()
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

    # Validate footprint name
    if entry.naming and entry.naming.pattern:
        pattern = entry.naming.pattern
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        if not pattern.match(footprint.name):
            result["errors"].append(
                f"Footprint name '{footprint.name}' does not match pattern: {entry.naming.pattern}"
            )
        else:
            result["successes"].append(
                f"Footprint name '{footprint.name}' matches pattern: {entry.naming.pattern}"
            )

    # Validate required properties
    if entry.required_properties:
        for prop_name, prop_def in entry.required_properties.items():
            if prop_name not in footprint.properties:
                result["errors"].append(f"Missing required property: {prop_name}")
            elif prop_def.pattern:
                pattern = prop_def.pattern
                if isinstance(pattern, str):
                    pattern = re.compile(pattern)
                if not pattern.match(footprint.properties[prop_name]):
                    result["errors"].append(
                        f"Property '{prop_name}' value '{footprint.properties[prop_name]}' does not match pattern: {prop_def.pattern}"
                    )

    # Check for unknown properties
    if entry.required_properties:
        for prop_name in footprint.properties:
            if prop_name not in entry.required_properties:
                result["warnings"].append(f"Unknown property: {prop_name}")

    # Validate required layers
    if entry.required_layers:
        missing_layers = []
        for layer_name in entry.required_layers:
            if layer_name not in footprint.layers:
                missing_layers.append(layer_name)
        if missing_layers:
            result["errors"].append(f"Missing required layers: {', '.join(missing_layers)}")
        else:
            result["successes"].append(
                f"Footprint contains all required layers: {', '.join(entry.required_layers)}"
            )

    # Validate required pads
    if entry.required_pads:
        pad_count = len(footprint.pads)
        min_count = entry.required_pads.min_count
        max_count = entry.required_pads.max_count
        if min_count is not None:
            if pad_count < min_count:
                result["errors"].append(
                    f"Footprint has {pad_count} pads, but minimum required is {min_count}"
                )
        if max_count is not None:
            if pad_count > max_count:
                result["errors"].append(
                    f"Footprint has {pad_count} pads, but maximum allowed is {max_count}"
                )

    # Validate description pattern if present
    if entry.naming and entry.naming.description_pattern and hasattr(footprint, "description"):
        pattern = entry.naming.description_pattern
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        if not pattern.match(getattr(footprint, "description", "")):
            result["errors"].append(
                f"Footprint description '{getattr(footprint, 'description', '')}' does not match pattern: {entry.naming.description_pattern}"
            )
        else:
            result["successes"].append(
                f"Footprint description '{getattr(footprint, 'description', '')}' matches pattern: {entry.naming.description_pattern}"
            )

    return result
