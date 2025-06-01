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
from kicad_lib_validator.models.validation import ValidationResult


def _find_matching_entry(symbol: Symbol, structure: LibraryStructure) -> Optional[ComponentEntry]:
    """Find the matching component entry in the structure for a symbol."""
    if not structure.symbols:
        print("[DEBUG] No symbols found in the structure.")
        return None

    # Get the library name from the symbol
    library_name = symbol.library_name
    if not library_name:
        print("[DEBUG] No library name found in symbol.")
        return None

    # Extract categories from the library name
    # Example: .Lab_Passive_Capacitor -> ["passive", "capacitor"]
    categories = [
        cat.lower() for cat in library_name.split("_")[1:]
    ]  # Skip the library prefix and convert to lowercase
    print(f"[DEBUG] Extracted categories from library name: {categories}")

    # Start with the root symbols group
    current_group = structure.symbols

    # Navigate through the categories
    for category in categories[:-1]:  # All but the last category are groups
        if category not in current_group:
            print(f"[DEBUG] Category '{category}' not found in structure.")
            return None
        current_group = current_group[category]
        if not isinstance(current_group, ComponentGroup):
            print(f"[DEBUG] Expected ComponentGroup for '{category}', got {type(current_group)}")
            return None

    # The last category should be an entry
    last_category = categories[-1]
    if last_category not in current_group.entries:
        print(f"[DEBUG] Entry '{last_category}' not found in group.")
        return None

    entry = current_group.entries[last_category]
    print(f"[DEBUG] Found matching entry: {last_category}")
    return entry


def validate_symbol(symbol: Symbol, structure: LibraryStructure) -> ValidationResult:
    """Validate a symbol against the library structure."""
    result = ValidationResult()
    required_fields = ["Reference", "Value", "Footprint", "Datasheet", "Description", "ki_keywords"]
    for field in required_fields:
        if field not in symbol.properties:
            result.add_error(f"Missing required field: {field}")
    entry = _find_matching_entry(symbol, structure)
    print(f"[DEBUG] Entry returned for symbol {symbol.name}: {entry}")
    if not entry:
        result.add_warning(f"No matching component entry found for symbol {symbol.name}")
        return result
    if entry.required_properties:
        for prop_name, prop_def in entry.required_properties.items():
            prop_value = None
            if prop_def.ki_field_name and prop_def.ki_field_name in symbol.properties:
                prop_value = symbol.properties[prop_def.ki_field_name]
            elif prop_name in symbol.properties:
                prop_value = symbol.properties[prop_name]
            if prop_value is None:
                if prop_def.required:
                    result.add_error(f"Missing required property: {prop_name}")
                continue
            if prop_def.pattern:
                if not prop_def.validate_pattern(prop_value):
                    result.add_error(
                        f"Property '{prop_name}' value '{prop_value}' does not match pattern: {prop_def.pattern}"
                    )
                else:
                    result.add_success(
                        f"Property '{prop_name}' value '{prop_value}' matches pattern: {prop_def.pattern}"
                    )
    if entry.reference_prefix and "Reference" in symbol.properties:
        ref_value = symbol.properties["Reference"]
        if not ref_value.startswith(entry.reference_prefix):
            result.add_error(
                f"Reference '{ref_value}' does not start with required prefix: {entry.reference_prefix}"
            )
        else:
            result.add_success(
                f"Reference '{ref_value}' has correct prefix: {entry.reference_prefix}"
            )
    if entry.pins:
        pin_count = len(symbol.pins)
        min_count = entry.pins.min_count if entry.pins.min_count is not None else 0
        max_count = entry.pins.max_count
        if min_count is not None and pin_count < min_count:
            result.add_error(f"Expected at least {min_count} pins, found {pin_count}")
        elif max_count is not None and pin_count > max_count:
            result.add_error(f"Expected at most {max_count} pins, found {pin_count}")
        else:
            result.add_success(f"Pin count matches expected: {pin_count}")
        if entry.pins.required_types:
            for pin_type in entry.pins.required_types:
                if not any(pin.type == pin_type for pin in symbol.pins):
                    result.add_error(f"Missing required pin type: {pin_type}")
                else:
                    result.add_success(f"Found required pin type: {pin_type}")
    known_props = set(required_fields)
    if entry.required_properties:
        known_props.update(entry.required_properties.keys())
        known_props.update(
            prop.ki_field_name for prop in entry.required_properties.values() if prop.ki_field_name
        )
    for prop_name in symbol.properties:
        if prop_name not in known_props and not prop_name.startswith("ki_"):
            result.add_warning(f"Unknown property: {prop_name}")
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
