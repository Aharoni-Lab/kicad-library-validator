"""
3D model validation logic for KiCad libraries.
"""

import re
from typing import Dict, List

from kicad_lib_validator.models.model3d import Model3D
from kicad_lib_validator.models.structure import ComponentEntry, ComponentGroup, LibraryStructure


def validate_model3d(model3d: Model3D, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate a 3D model against the library structure.

    Args:
        model3d: 3D model to validate
        structure: Library structure definition

    Returns:
        Dictionary containing validation results
    """
    result: Dict[str, List[str]] = {"errors": [], "warnings": [], "successes": []}

    # Validate format
    supported_formats = ["step", "stp", "iges", "igs"]
    if model3d.format.lower() not in supported_formats:
        result["errors"].append(f"unsupported format: {model3d.format}")

    # Validate units
    supported_units = ["mm", "inch"]
    if model3d.units.lower() not in supported_units:
        result["errors"].append(f"unsupported units: {model3d.units}")

    # Require categories for lookup
    if (
        not model3d.categories
        or not isinstance(model3d.categories, list)
        or len(model3d.categories) == 0
    ):
        result["errors"].append("Model3D must specify a non-empty categories list for validation.")
        return result

    # Traverse the nested structure using categories
    group = structure.models_3d
    entry = None
    path = model3d.categories.copy()
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

    # Validate model name
    if entry.naming and entry.naming.pattern:
        pattern_str = entry.naming.pattern
        pattern = re.compile(pattern_str) if isinstance(pattern_str, str) else pattern_str
        if not pattern.match(model3d.name):
            result["errors"].append(
                f"Model name '{model3d.name}' does not match pattern: {entry.naming.pattern}"
            )
        else:
            result["successes"].append(
                f"Model name '{model3d.name}' matches pattern: {entry.naming.pattern}"
            )

    # Validate required properties
    if entry.required_properties:
        for prop_name, prop_def in entry.required_properties.items():
            if prop_name not in model3d.properties:
                result["errors"].append(f"Missing required property: {prop_name}")
            elif prop_def.pattern:
                prop_pattern_str = prop_def.pattern
                prop_pattern = (
                    re.compile(prop_pattern_str)
                    if isinstance(prop_pattern_str, str)
                    else prop_pattern_str
                )
                if not prop_pattern.match(model3d.properties[prop_name]):
                    result["errors"].append(
                        f"Property '{prop_name}' value '{model3d.properties[prop_name]}' does not match pattern: {prop_def.pattern}"
                    )

    # Check for unknown properties
    if entry.required_properties:
        for prop_name in model3d.properties:
            if prop_name not in entry.required_properties:
                result["warnings"].append(f"Unknown property: {prop_name}")

    # Validate description pattern if present
    if entry.naming and entry.naming.description_pattern and hasattr(model3d, "description"):
        desc_pattern_str = entry.naming.description_pattern
        desc_pattern = (
            re.compile(desc_pattern_str) if isinstance(desc_pattern_str, str) else desc_pattern_str
        )
        if not desc_pattern.match(getattr(model3d, "description", "")):
            result["errors"].append(
                f"Model description '{getattr(model3d, 'description', '')}' does not match pattern: {entry.naming.description_pattern}"
            )
        else:
            result["successes"].append(
                f"Model description '{getattr(model3d, 'description', '')}' matches pattern: {entry.naming.description_pattern}"
            )

    return result
