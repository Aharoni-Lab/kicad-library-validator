"""
Symbol validator module.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

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
    categories = [cat.lower() for cat in library_name.split("_")[1:]]
    print(f"[DEBUG] Extracted categories from library name: {categories}")

    # Start with the root symbols group
    current_group: ComponentGroup = structure.symbols  # type: ignore

    # Traverse nested groups
    for category in categories[:-1]:
        if category not in current_group:
            print(f"[DEBUG] Category '{category}' not found in structure.")
            return None
        current_group = current_group[category]
        if not isinstance(current_group, ComponentGroup):
            print(f"[DEBUG] Expected ComponentGroup for '{category}', got {type(current_group)}")
            return None
        current_group = cast(ComponentGroup, current_group)

    # The last category should be an entry in the entries dict
    last_category = categories[-1]
    if hasattr(current_group, "entries") and isinstance(current_group.entries, dict):
        if last_category in current_group.entries:
            entry = current_group.entries[last_category]
            print(f"[DEBUG] Found matching entry: {last_category}")
            return entry
        else:
            print(f"[DEBUG] Entry '{last_category}' not found in group.")
            return None
    print(f"[DEBUG] current_group has no entries attribute or entries is not a dict.")
    return None


def validate_symbol(symbol: Symbol, structure: LibraryStructure) -> ValidationResult:
    """Validate a symbol against the library structure."""
    result = ValidationResult()
    required_fields = ["Reference", "Value", "Footprint", "Datasheet", "Description", "ki_keywords"]
    for field in required_fields:
        if field not in symbol.properties:
            result.add_error("Symbol", f"Missing required field: {field}")
    entry = _find_matching_entry(symbol, structure)
    print(f"[DEBUG] Entry returned for symbol {symbol.name}: {entry}")
    if not entry:
        result.add_warning("Symbol", f"No matching component entry found for symbol {symbol.name}")
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
                    result.add_error("Symbol", f"Missing required property: {prop_name}")
                continue
            if prop_def.pattern:
                if not prop_def.validate_pattern(prop_value):
                    result.add_error(
                        "Symbol",
                        f"Property '{prop_name}' value '{prop_value}' does not match pattern: {prop_def.pattern}",
                    )
                else:
                    result.add_success(
                        "Symbol",
                        f"Property '{prop_name}' value '{prop_value}' matches pattern: {prop_def.pattern}",
                    )
    if entry.reference_prefix and "Reference" in symbol.properties:
        ref_value = symbol.properties["Reference"]
        if not ref_value.startswith(entry.reference_prefix):
            result.add_error(
                "Symbol",
                f"Reference '{ref_value}' does not start with required prefix: {entry.reference_prefix}",
            )
        else:
            result.add_success(
                "Symbol", f"Reference '{ref_value}' has correct prefix: {entry.reference_prefix}"
            )
    if entry.pins:
        pin_count = len(symbol.pins)
        min_count = entry.pins.min_count if entry.pins.min_count is not None else 0
        max_count = entry.pins.max_count
        if min_count is not None and pin_count < min_count:
            result.add_error("Symbol", f"Expected at least {min_count} pins, found {pin_count}")
        elif max_count is not None and pin_count > max_count:
            result.add_error("Symbol", f"Expected at most {max_count} pins, found {pin_count}")
        else:
            result.add_success("Symbol", f"Pin count matches expected: {pin_count}")
        if entry.pins.required_types:
            for pin_type in entry.pins.required_types:
                if not any(pin.type == pin_type for pin in symbol.pins):
                    result.add_error("Symbol", f"Missing required pin type: {pin_type}")
                else:
                    result.add_success("Symbol", f"Found required pin type: {pin_type}")
    known_props = set(required_fields)
    if entry.required_properties:
        known_props.update(entry.required_properties.keys())
        known_props.update(
            prop.ki_field_name for prop in entry.required_properties.values() if prop.ki_field_name
        )
    for prop_name in symbol.properties:
        if prop_name not in known_props and not prop_name.startswith("ki_"):
            result.add_warning("Symbol", f"Unknown property: {prop_name}")
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


class SymbolValidator:
    """Validator for symbol files."""

    def __init__(self, structure: LibraryStructure) -> None:
        """
        Initialize the validator.

        Args:
            structure: Library structure definition
        """
        self.structure = structure
        self.result = ValidationResult()

    def validate(self) -> ValidationResult:
        """Validate all symbol files."""
        for group_name, group in self.structure.symbol_groups.items():
            self._validate_group(group_name, group)
        return self.result

    def _validate_group(self, group_name: str, group: ComponentGroup) -> None:
        """
        Validate a symbol group.

        Args:
            group_name: Name of the group
            group: Group definition
        """
        group_path = Path("symbols") / group_name
        if not group_path.exists():
            self.result.add_error("Symbol", f"Symbol group directory '{group_name}' does not exist")
            return

        if not hasattr(group, "entries") or not isinstance(group.entries, dict):
            self.result.add_error("Symbol", f"Symbol group '{group_name}' has no entries")
            return

        for entry_name, entry in group.entries.items():
            self._validate_entry(group_name, entry)

    def _validate_entry(self, group_name: str, entry: ComponentEntry) -> None:
        """
        Validate a symbol entry.

        Args:
            group_name: Name of the group
            entry: Entry definition
        """
        symbol_path = Path("symbols") / group_name / f"{entry.name}.kicad_sym"
        if not symbol_path.exists():
            self.result.add_error("Symbol", f"Symbol file '{entry.name}.kicad_sym' does not exist")
            return

        content = symbol_path.read_text()
        if not content.strip():
            self.result.add_error("Symbol", f"Symbol file '{entry.name}.kicad_sym' is empty")
            return

        # Check for required fields
        required_fields = ["Value", "Footprint", "Datasheet"]
        for field in required_fields:
            if field not in content:
                self.result.add_error(
                    "Symbol", f"Symbol '{entry.name}' is missing required field: {field}"
                )

        # Check for description
        if "Description" not in content:
            self.result.add_warning("Symbol", f"Symbol '{entry.name}' is missing description")

        # Check for keywords
        if entry.keywords and "Keywords" not in content:
            self.result.add_warning("Symbol", f"Symbol '{entry.name}' is missing keywords")

        # Check for footprint
        if entry.footprint and "Footprint" not in content:
            self.result.add_error("Symbol", f"Symbol '{entry.name}' is missing footprint")

        # Check for datasheet
        if entry.datasheet and "Datasheet" not in content:
            self.result.add_warning("Symbol", f"Symbol '{entry.name}' is missing datasheet")

        # Check for 3D model
        if entry.model_3d:
            model_path = Path("3d") / entry.model_3d
            if not model_path.exists():
                self.result.add_error(
                    "Symbol",
                    f"3D model '{entry.model_3d}' for symbol '{entry.name}' does not exist",
                )

        self.result.add_success("Symbol", f"Symbol '{entry.name}' validation passed")
