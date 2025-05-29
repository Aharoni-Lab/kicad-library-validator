"""
3D model validation logic for KiCad libraries.
"""

import re
from typing import Dict, List

from kicad_lib_validator.models.model3d import Model3D
from kicad_lib_validator.models.structure import ComponentCategory, ComponentType, LibraryStructure


def validate_model3d_name(name: str, structure: LibraryStructure, category: str) -> bool:
    """Validate a 3D model name against the structure rules for the given category."""
    # TODO: Implement 3D model name validation logic
    return True


def validate_model3d_property(
    property_name: str, value: str, structure: LibraryStructure, category: str
) -> bool:
    """Validate a 3D model property value against the structure rules for the given category."""
    # TODO: Implement 3D model property validation logic
    return True


def _matches_category(model3d: Model3D, category: ComponentCategory) -> bool:
    """
    Check if a 3D model matches a category based on its properties.

    Args:
        model3d: 3D model to check
        category: Category to match against

    Returns:
        True if the 3D model matches the category, False otherwise
    """
    # Check prefix if specified
    if category.prefix:
        if not model3d.name.startswith(category.prefix):
            return False

    # Check required properties
    if category.required_properties:
        for prop_name, prop_def in category.required_properties.items():
            if not prop_def.optional and prop_name not in model3d.properties:
                return False

    return True


def validate_model3d(model3d: Model3D, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate a 3D model against the library structure.

    Args:
        model3d: 3D model to validate
        structure: Library structure definition

    Returns:
        Dictionary containing validation results
    """
    results: Dict[str, List[str]] = {"errors": [], "warnings": [], "successes": []}

    # Validate format
    supported_formats = ["step", "stp", "iges", "igs"]
    if model3d.format.lower() not in supported_formats:
        results["errors"].append(f"unsupported format: {model3d.format}")

    # Validate units
    supported_units = ["mm", "inch"]
    if model3d.units.lower() not in supported_units:
        results["errors"].append(f"unsupported units: {model3d.units}")

    # Find matching category
    if not structure.models_3d:
        return results

    for type_name, component_type in structure.models_3d.items():
        if not component_type.categories:
            continue

        for category_name, category in component_type.categories.items():
            has_errors = False

            # Check naming pattern first
            if category.naming and category.naming.pattern:
                if not re.match(category.naming.pattern, model3d.name):
                    results["errors"].append(
                        f"Model name '{model3d.name}' does not match pattern: {category.naming.pattern}"
                    )
                    has_errors = True
                else:
                    results["successes"].append(
                        f"Model name '{model3d.name}' matches pattern: {category.naming.pattern}"
                    )

            # Check required properties
            if category.required_properties:
                # Check for unknown properties
                known_properties = set(category.required_properties.keys())
                for prop_name in model3d.properties:
                    if prop_name not in known_properties:
                        results["warnings"].append(f"Unknown property: {prop_name}")

                for prop_name, prop_def in category.required_properties.items():
                    if prop_name not in model3d.properties:
                        if not prop_def.optional:
                            results["errors"].append(f"Missing required property: {prop_name}")
                            has_errors = True
                    else:
                        value = model3d.properties[prop_name]
                        if prop_def.pattern and not re.match(prop_def.pattern, value):
                            results["errors"].append(
                                f"Property {prop_name} value '{value}' does not match pattern: {prop_def.pattern}"
                            )
                            has_errors = True
                        else:
                            results["successes"].append(
                                f"Property {prop_name} value '{value}' matches pattern: {prop_def.pattern}"
                            )

            # If we have errors, continue to next category
            if has_errors:
                continue

            # Check if model matches category
            if not _matches_category(model3d, category):
                continue

            # Validate description pattern if present
            if (
                category.naming
                and category.naming.description_pattern
                and hasattr(model3d, "description")
            ):
                if not re.match(category.naming.description_pattern, model3d.description):
                    results["errors"].append(
                        f"Model description '{model3d.description}' does not match pattern: {category.naming.description_pattern}"
                    )
                    has_errors = True
                else:
                    results["successes"].append(
                        f"Model description '{model3d.description}' matches pattern: {category.naming.description_pattern}"
                    )

            # If we found a matching category and passed all validations, add a success message
            if not has_errors:
                results["successes"].append(f"Model matches category {type_name}/{category_name}")
                return results

    # If no matching category was found
    results["warnings"].append("Model does not match any defined category")
    return results
