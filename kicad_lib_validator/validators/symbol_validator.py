"""
Symbol validation logic for KiCad libraries.
"""

import re
from typing import Any, Dict, List

from kicad_lib_validator.models.structure import ComponentCategory, ComponentType, LibraryStructure
from kicad_lib_validator.models.symbol import Symbol


def validate_symbol(symbol: Symbol, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate a symbol against the library structure.

    Args:
        symbol: Symbol to validate
        structure: Library structure definition

    Returns:
        Dictionary containing validation results
    """
    results: Dict[str, List[str]] = {"errors": [], "warnings": [], "successes": []}

    # Check if the symbol's category and subcategory are recognized
    if not structure.symbols or symbol.category not in structure.symbols:
        results["errors"].append("Could not determine symbol category")
        return results

    component_type = structure.symbols[symbol.category]
    if not component_type.categories or symbol.subcategory not in component_type.categories:
        results["errors"].append("Could not determine symbol category")
        return results

    category_obj = component_type.categories[symbol.subcategory]
    has_errors = False

    # Check naming pattern first
    if category_obj.naming and category_obj.naming.pattern:
        if not re.match(category_obj.naming.pattern, symbol.name):
            results["errors"].append(
                f"Symbol name '{symbol.name}' does not match pattern: {category_obj.naming.pattern}"
            )
            has_errors = True
        else:
            results["successes"].append(
                f"Symbol name '{symbol.name}' matches pattern: {category_obj.naming.pattern}"
            )

    # Check required properties
    if category_obj.required_properties:
        # Check for unknown properties
        known_properties = set(category_obj.required_properties.keys())
        for prop_name in symbol.properties:
            if prop_name not in known_properties:
                results["warnings"].append(f"Unknown property: {prop_name}")

        for prop_name, prop_def in category_obj.required_properties.items():
            if prop_name not in symbol.properties:
                if not prop_def.optional:
                    results["errors"].append(f"Missing required property: {prop_name}")
                    has_errors = True
            else:
                value = symbol.properties[prop_name]
                if prop_def.pattern and not re.match(prop_def.pattern, value):
                    results["errors"].append(
                        f"Property {prop_name} value '{value}' does not match pattern: {prop_def.pattern}"
                    )
                    has_errors = True
                else:
                    results["successes"].append(
                        f"Property {prop_name} value '{value}' matches pattern: {prop_def.pattern}"
                    )

    # Validate pin requirements
    if category_obj.pins:
        pin_count = len(symbol.pins)
        min_count = category_obj.pins.min_count
        max_count = category_obj.pins.max_count
        if min_count is not None:
            if pin_count < min_count:
                results["errors"].append(
                    f"Symbol has {pin_count} pins, but minimum required is {min_count}"
                )
                has_errors = True
        if max_count is not None:
            if pin_count > max_count:
                results["errors"].append(
                    f"Symbol has {pin_count} pins, but maximum allowed is {max_count}"
                )
                has_errors = True

        # Validate pin types
        if category_obj.pins.required_types:
            for pin in symbol.pins:
                if pin.type not in category_obj.pins.required_types:
                    results["warnings"].append(
                        f"Pin {pin.name} has type {pin.type}, but allowed types are: {', '.join(category_obj.pins.required_types)}"
                    )

    # Validate description pattern if present
    if (
        category_obj.naming
        and category_obj.naming.description_pattern
        and hasattr(symbol, "description")
    ):
        if not re.match(category_obj.naming.description_pattern, symbol.description):
            results["errors"].append(
                f"Symbol description '{symbol.description}' does not match pattern: {category_obj.naming.description_pattern}"
            )
            has_errors = True
        else:
            results["successes"].append(
                f"Symbol description '{symbol.description}' matches pattern: {category_obj.naming.description_pattern}"
            )

    if not has_errors:
        results["successes"].append(
            f"Symbol matches category {symbol.category}/{symbol.subcategory}"
        )

    return results


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


def _matches_category(symbol: Symbol, category: ComponentCategory) -> bool:
    """
    Check if a symbol matches a category based on its properties.

    Args:
        symbol: Symbol to check
        category: Category to match against

    Returns:
        True if the symbol matches the category, False otherwise
    """
    # Check prefix if specified
    if category.prefix:
        if not symbol.name.startswith(category.prefix):
            return False

    # Check required properties
    if category.required_properties:
        for prop_name, prop_def in category.required_properties.items():
            if not prop_def.optional and prop_name not in symbol.properties:
                return False

    # Check pin requirements
    if category.pins:
        pin_count = len(symbol.pins)
        min_count = category.pins.min_count
        max_count = category.pins.max_count
        if min_count is not None and pin_count < min_count:
            return False
        if max_count is not None and pin_count > max_count:
            return False

    return True
