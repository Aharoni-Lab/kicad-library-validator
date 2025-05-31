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
from kicad_lib_validator.validator import ValidationResult


def _find_matching_entry(symbol: Symbol, structure: LibraryStructure) -> Optional[ComponentEntry]:
    """Find the matching component entry in the structure for a symbol."""
    if not structure.components:
        return None
    for entry in structure.components:
        # Ensure entry is a ComponentEntry
        if not isinstance(entry, ComponentEntry):
            continue
        if entry.categories and symbol.categories:
            if all(cat in symbol.categories for cat in entry.categories):
                return entry
    return None


def validate_symbol(symbol: Symbol, structure: LibraryStructure) -> ValidationResult:
    """Validate a symbol against the library structure."""
    result = ValidationResult()
    required_fields = ["Reference", "Value", "Footprint", "Datasheet", "Description", "ki_keywords"]
    for field in required_fields:
        if field not in symbol.properties:
            result.add_error(f"Missing required field: {field}")
    entry = _find_matching_entry(symbol, structure)
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
        if entry.pins.count is not None and len(symbol.pins) != entry.pins.count:
            result.add_error(f"Expected {entry.pins.count} pins, found {len(symbol.pins)}")
        else:
            result.add_success(f"Pin count matches expected: {len(symbol.pins)}")
        if entry.pins.required_names:
            for pin_name in entry.pins.required_names:
                if not any(pin.name == pin_name for pin in symbol.pins):
                    result.add_error(f"Missing required pin: {pin_name}")
                else:
                    result.add_success(f"Found required pin: {pin_name}")
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
