"""
Symbol validation logic for KiCad libraries.
"""

import re
from typing import Any, Dict, List

from kicad_lib_validator.models.structure import ComponentCategory, ComponentType, LibraryStructure
from kicad_lib_validator.models.symbol import Symbol


def validate_symbol(symbol: Symbol, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate a Symbol against the library structure definition.

    Returns a dict with keys: 'errors', 'warnings', 'successes'.
    """
    errors: List[str] = []
    warnings: List[str] = []
    successes: List[str] = []

    # 1. Determine the symbol's category using the category/subcategory fields
    symbol_category: ComponentType | ComponentCategory | None = None
    symbol_category_name = None
    if symbol.category and symbol.subcategory:
        try:
            symbol_category = structure.symbols[symbol.category].categories[symbol.subcategory]
            symbol_category_name = f"{symbol.category}/{symbol.subcategory}"
        except Exception:
            errors.append(
                f"Category/subcategory '{symbol.category}/{symbol.subcategory}' not found in structure for symbol '{symbol.name}'"
            )
            return {"errors": errors, "warnings": warnings, "successes": successes}
    elif symbol.category:
        try:
            symbol_category = structure.symbols[symbol.category]
            symbol_category_name = symbol.category
        except Exception:
            errors.append(
                f"Category '{symbol.category}' not found in structure for symbol '{symbol.name}'"
            )
            return {"errors": errors, "warnings": warnings, "successes": successes}
    else:
        # Try to determine category from reference prefix
        ref_prefix = (
            symbol.properties.get("Reference", "")[0] if symbol.properties.get("Reference") else ""
        )
        for category, cat_type in structure.symbols.items():
            for subcat, subcat_type in cat_type.categories.items():
                if subcat_type.prefix == ref_prefix:
                    symbol_category = subcat_type
                    symbol_category_name = f"{category}/{subcat}"
                    break
            if symbol_category:
                break
        if not symbol_category:
            errors.append(f"Could not determine symbol category for symbol '{symbol.name}'")
            return {"errors": errors, "warnings": warnings, "successes": successes}

    # 2. Validate symbol name against naming pattern
    naming = getattr(symbol_category, "naming", None)
    if naming and hasattr(naming, "pattern"):
        pattern = naming.pattern
        if not isinstance(pattern, (str, type(re.compile("")))):
            warnings.append(
                f"Naming pattern for category {symbol_category_name} is not a string or regex: {pattern}"
            )
        else:
            if not re.match(pattern, symbol.name):
                errors.append(
                    f"Symbol name '{symbol.name}' does not match pattern '{pattern}' for category {symbol_category_name}"
                )
            else:
                successes.append(f"Symbol name '{symbol.name}' matches pattern '{pattern}'")
    else:
        warnings.append(f"No naming pattern defined for category {symbol_category_name}")

    # 3. Validate required properties
    required_props = getattr(symbol_category, "required_properties", {})
    for prop_name, prop_rule in required_props.items():
        if prop_name not in symbol.properties:
            errors.append(f"Missing required property '{prop_name}' for symbol '{symbol.name}'")
            continue
        value = symbol.properties[prop_name]
        # Type check (only string supported for now)
        if hasattr(prop_rule, "type") and prop_rule.type != "string":
            warnings.append(
                f"Property '{prop_name}' type checking not implemented (expected {prop_rule.type})"
            )
        # Pattern check
        if hasattr(prop_rule, "pattern"):
            prop_pattern = prop_rule.pattern
            if not isinstance(prop_pattern, (str, type(re.compile("")))):
                warnings.append(
                    f"Property '{prop_name}' pattern is not a string or regex: {prop_pattern}"
                )
            else:
                if not re.match(prop_pattern, value):
                    errors.append(
                        f"Property '{prop_name}' value '{value}' does not match pattern '{prop_pattern}'"
                    )
                else:
                    successes.append(
                        f"Property '{prop_name}' value '{value}' matches pattern '{prop_pattern}'"
                    )

    # 4. Optionally, check for extra/unknown properties
    allowed_props = set(required_props.keys())
    for prop in symbol.properties:
        if prop not in allowed_props:
            warnings.append(f"Unknown property '{prop}' in symbol '{symbol.name}'")

    return {"errors": errors, "warnings": warnings, "successes": successes}


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
