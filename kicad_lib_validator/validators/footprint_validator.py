"""
Footprint validation logic for KiCad libraries.
"""

import re
from typing import Any, Dict, List, Optional

from kicad_lib_validator.models.footprint import Footprint
from kicad_lib_validator.models.structure import ComponentEntry, ComponentGroup, LibraryStructure
from kicad_lib_validator.models.validation import ValidationResult


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


def _find_matching_entry(
    footprint: Footprint, structure: LibraryStructure
) -> Optional[ComponentEntry]:
    """Find the matching component entry in the structure for a footprint."""
    if not structure.footprints:
        print("[DEBUG] No footprints found in the structure.")
        return None

    # Get categories from the footprint
    categories = footprint.categories or []
    print(f"[DEBUG] Extracted categories from footprint: {categories}")

    # Start with the root footprints group
    current_group = structure.footprints

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
    last_category = categories[-1] if categories else None
    if not last_category or last_category not in current_group.entries:
        print(f"[DEBUG] Entry '{last_category}' not found in group.")
        return None

    entry = current_group.entries[last_category]
    print(f"[DEBUG] Found matching entry: {last_category}")
    return entry


def validate_footprint(footprint: Footprint, structure: LibraryStructure) -> ValidationResult:
    """Validate a footprint against the library structure."""
    result = ValidationResult()

    # Required fields for footprints
    required_fields = ["Reference", "Value", "Datasheet", "Description"]
    for field in required_fields:
        if field not in footprint.properties:
            result.add_error(f"Missing required field: {field}")

    # Find matching entry based on categories
    entry = _find_matching_entry(footprint, structure)
    if not entry:
        result.add_warning(f"No matching component entry found for footprint {footprint.name}")
        return result

    # Validate required properties from the entry
    if entry.required_properties:
        for prop_name, prop_def in entry.required_properties.items():
            prop_value = None
            if prop_def.ki_field_name and prop_def.ki_field_name in footprint.properties:
                prop_value = footprint.properties[prop_def.ki_field_name]
            elif prop_name in footprint.properties:
                prop_value = footprint.properties[prop_name]
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

    # Validate reference pattern if specified
    if entry.reference_pattern and "Reference" in footprint.properties:
        ref_value = footprint.properties["Reference"]
        if not re.match(entry.reference_pattern, ref_value):
            result.add_error(
                f"Reference '{ref_value}' does not match required pattern: {entry.reference_pattern}"
            )
        else:
            result.add_success(
                f"Reference '{ref_value}' matches required pattern: {entry.reference_pattern}"
            )

    # Validate required layers
    if entry.required_layers:
        for layer in entry.required_layers:
            if layer not in footprint.layers:
                result.add_error(f"Missing required layer: {layer}")
            else:
                result.add_success(f"Found required layer: {layer}")

    # Validate required pads
    if entry.required_pads:
        if (
            entry.required_pads.count is not None
            and len(footprint.pads) != entry.required_pads.count
        ):
            result.add_error(
                f"Expected {entry.required_pads.count} pads, found {len(footprint.pads)}"
            )
        else:
            result.add_success(f"Pad count matches expected: {len(footprint.pads)}")
        if entry.required_pads.required_names:
            for pad_name in entry.required_pads.required_names:
                if not any(pad.number == pad_name for pad in footprint.pads):
                    result.add_error(f"Missing required pad: {pad_name}")
                else:
                    result.add_success(f"Found required pad: {pad_name}")

    # Check for unknown properties
    known_props = set(required_fields)
    if entry.required_properties:
        known_props.update(entry.required_properties.keys())
        known_props.update(
            prop.ki_field_name for prop in entry.required_properties.values() if prop.ki_field_name
        )
    for prop_name in footprint.properties:
        if prop_name not in known_props and not prop_name.startswith("ki_"):
            result.add_warning(f"Unknown property: {prop_name}")

    return result
