"""
Footprint validation logic for KiCad libraries.
"""

import re
from typing import Dict, List

from kicad_lib_validator.models.footprint import Footprint
from kicad_lib_validator.models.structure import ComponentCategory, ComponentType, LibraryStructure


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


def _matches_category(footprint: Footprint, category: ComponentCategory) -> bool:
    """
    Check if a footprint matches a category based on its properties.

    Args:
        footprint: Footprint to check
        category: Category to match against

    Returns:
        True if the footprint matches the category, False otherwise
    """
    # Check prefix if specified
    if category.prefix:
        if not footprint.name.startswith(category.prefix):
            return False

    # Check required properties
    if category.required_properties:
        for prop_name, prop_def in category.required_properties.items():
            if not prop_def.optional and prop_name not in footprint.properties:
                return False

    # Check required pads
    if category.required_pads:
        pad_count = len(footprint.pads)
        if pad_count < category.required_pads.min_count:
            return False
        if category.required_pads.max_count and pad_count > category.required_pads.max_count:
            return False

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
    results = {"errors": [], "warnings": [], "successes": []}

    # Check if the footprint's category and subcategory are recognized
    if not structure.footprints or footprint.category not in structure.footprints:
        results["errors"].append("Could not determine footprint category")
        return results

    component_type = structure.footprints[footprint.category]
    if not component_type.categories or footprint.subcategory not in component_type.categories:
        results["errors"].append("Could not determine footprint category")
        return results

    category_obj = component_type.categories[footprint.subcategory]
    has_errors = False

    # Check naming pattern first
    if category_obj.naming and category_obj.naming.pattern:
        if not re.match(category_obj.naming.pattern, footprint.name):
            results["errors"].append(
                f"Footprint name '{footprint.name}' does not match pattern: {category_obj.naming.pattern}"
            )
            has_errors = True
        else:
            results["successes"].append(
                f"Footprint name '{footprint.name}' matches pattern: {category_obj.naming.pattern}"
            )

    # Check required properties
    if category_obj.required_properties:
        # Check for unknown properties
        known_properties = set(category_obj.required_properties.keys())
        for prop_name in footprint.properties:
            if prop_name not in known_properties:
                results["warnings"].append(f"Unknown property: {prop_name}")

        for prop_name, prop_def in category_obj.required_properties.items():
            if prop_name not in footprint.properties:
                if not prop_def.optional:
                    results["errors"].append(f"Missing required property: {prop_name}")
                    has_errors = True
            else:
                value = footprint.properties[prop_name]
                if prop_def.pattern and not re.match(prop_def.pattern, value):
                    results["errors"].append(
                        f"Property {prop_name} value '{value}' does not match pattern: {prop_def.pattern}"
                    )
                    has_errors = True
                else:
                    results["successes"].append(
                        f"Property {prop_name} value '{value}' matches pattern: {prop_def.pattern}"
                    )

    # Validate required layers
    if category_obj.required_layers:
        missing_layers = []
        for layer_name in category_obj.required_layers:
            if layer_name not in footprint.layers:
                missing_layers.append(layer_name)
        if missing_layers:
            results["errors"].append(f"missing required layers: {', '.join(missing_layers)}")
            has_errors = True
        else:
            results["successes"].append(
                f"Footprint contains all required layers: {', '.join(category_obj.required_layers)}"
            )

    # Validate required pads
    if category_obj.required_pads:
        pad_count = len(footprint.pads)
        if pad_count < category_obj.required_pads.min_count:
            results["errors"].append(
                f"Footprint has {pad_count} pads, but minimum required is {category_obj.required_pads.min_count}"
            )
            has_errors = True
        if (
            category_obj.required_pads.max_count
            and pad_count > category_obj.required_pads.max_count
        ):
            results["errors"].append(
                f"Footprint has {pad_count} pads, but maximum allowed is {category_obj.required_pads.max_count}"
            )
            has_errors = True

    # Validate description pattern if present
    if (
        category_obj.naming
        and category_obj.naming.description_pattern
        and hasattr(footprint, "description")
    ):
        if not re.match(category_obj.naming.description_pattern, footprint.description):
            results["errors"].append(
                f"Footprint description '{footprint.description}' does not match pattern: {category_obj.naming.description_pattern}"
            )
            has_errors = True
        else:
            results["successes"].append(
                f"Footprint description '{footprint.description}' matches pattern: {category_obj.naming.description_pattern}"
            )

    if not has_errors:
        results["successes"].append(
            f"Footprint matches category {footprint.category}/{footprint.subcategory}"
        )

    return results
