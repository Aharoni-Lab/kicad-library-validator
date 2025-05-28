"""
Footprint validation logic for KiCad libraries.
"""

import re
from typing import Dict, List

from kicad_lib_validator.models.footprint import Footprint
from kicad_lib_validator.models.structure import LibraryStructure


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
    Validate a Footprint against the library structure definition.

    Returns a dict with keys: 'errors', 'warnings', 'successes'.
    """
    errors: List[str] = []
    warnings: List[str] = []
    successes: List[str] = []

    # 1. Determine the footprint's category using the category/subcategory fields
    footprint_category = None
    footprint_category_name = None
    if footprint.category and footprint.subcategory:
        try:
            footprint_category = structure.footprints[footprint.category].categories[
                footprint.subcategory
            ]
            footprint_category_name = f"{footprint.category}/{footprint.subcategory}"
        except Exception:
            errors.append(
                f"Category/subcategory '{footprint.category}/{footprint.subcategory}' not found in structure for footprint '{footprint.name}'"
            )
            return {"errors": errors, "warnings": warnings, "successes": successes}
    elif footprint.category:
        try:
            footprint_category = structure.footprints[footprint.category]
            footprint_category_name = footprint.category
        except Exception:
            errors.append(
                f"Category '{footprint.category}' not found in structure for footprint '{footprint.name}'"
            )
            return {"errors": errors, "warnings": warnings, "successes": successes}
    else:
        errors.append(f"No category information for footprint '{footprint.name}'")
        return {"errors": errors, "warnings": warnings, "successes": successes}

    # 2. Validate footprint name against naming pattern
    naming = getattr(footprint_category, "naming", None)
    if naming and hasattr(naming, "pattern"):
        pattern = str(naming.pattern)  # Ensure pattern is a string
        if not re.match(pattern, footprint.name):
            errors.append(
                f"Footprint name '{footprint.name}' does not match pattern '{pattern}' for category {footprint_category_name}"
            )
        else:
            successes.append(f"Footprint name '{footprint.name}' matches pattern '{pattern}'")
    else:
        warnings.append(f"No naming pattern defined for category {footprint_category_name}")

    # 3. Validate required properties
    required_props = getattr(footprint_category, "required_properties", {})
    for prop_name, prop_rule in required_props.items():
        if prop_name not in footprint.properties:
            errors.append(
                f"Missing required property '{prop_name}' for footprint '{footprint.name}'"
            )
            continue
        value = footprint.properties[prop_name]
        # Type check (only string supported for now)
        if hasattr(prop_rule, "type") and prop_rule.type != "string":
            warnings.append(
                f"Property '{prop_name}' type checking not implemented (expected {prop_rule.type})"
            )
        # Pattern check
        if hasattr(prop_rule, "pattern"):
            pattern = str(prop_rule.pattern)  # Ensure pattern is a string
            if not re.match(pattern, value):
                errors.append(
                    f"Property '{prop_name}' value '{value}' does not match pattern '{pattern}'"
                )
            else:
                successes.append(
                    f"Property '{prop_name}' value '{value}' matches pattern '{pattern}'"
                )

    # 4. Validate required layers
    required_layers = getattr(footprint_category, "required_layers", None)
    if required_layers:
        # Assume footprint has a 'layers' attribute (list of str)
        footprint_layers = set(getattr(footprint, "layers", []))
        missing_layers = set(required_layers) - footprint_layers
        if missing_layers:
            errors.append(
                f"Footprint '{footprint.name}' is missing required layers: {', '.join(missing_layers)}"
            )
        else:
            successes.append(f"Footprint '{footprint.name}' contains all required layers")

    # 5. Optionally, check for extra/unknown properties
    allowed_props = set(required_props.keys())
    for prop in footprint.properties:
        if prop not in allowed_props:
            warnings.append(f"Unknown property '{prop}' in footprint '{footprint.name}'")

    return {"errors": errors, "warnings": warnings, "successes": successes}
