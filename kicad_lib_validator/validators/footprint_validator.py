"""
Footprint validation logic for KiCad libraries.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

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

    categories = footprint.categories or []
    print(f"[DEBUG] Extracted categories from footprint: {categories}")

    current_group: ComponentGroup = structure.footprints  # type: ignore
    for category in categories[:-1]:
        if category not in current_group:
            print(f"[DEBUG] Category '{category}' not found in structure.")
            return None
        current_group = current_group[category]
        if not isinstance(current_group, ComponentGroup):
            print(f"[DEBUG] Expected ComponentGroup for '{category}', got {type(current_group)}")
            return None
        current_group = cast(ComponentGroup, current_group)
    current_group = cast(ComponentGroup, current_group)

    last_category = categories[-1] if categories else None
    if (
        last_category
        and hasattr(current_group, "entries")
        and isinstance(current_group.entries, dict)
    ):
        if last_category in current_group.entries:
            entry = current_group.entries[last_category]
            print(f"[DEBUG] Found matching entry: {last_category}")
            return entry
        else:
            print(f"[DEBUG] Entry '{last_category}' not found in group.")
            return None
    print(f"[DEBUG] current_group has no entries attribute or entries is not a dict.")
    return None


def validate_footprint(footprint: Footprint, structure: LibraryStructure) -> ValidationResult:
    """Validate a footprint against the library structure."""
    result = ValidationResult()

    # Required fields for footprints
    required_fields = ["Reference", "Value", "Datasheet", "Description"]
    for field in required_fields:
        if field not in footprint.properties:
            result.add_error("Footprint", f"Missing required field: {field}")

    # Find matching entry based on categories
    entry = _find_matching_entry(footprint, structure)
    if not entry:
        result.add_warning(
            "Footprint", f"No matching component entry found for footprint {footprint.name}"
        )
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
                    result.add_error("Footprint", f"Missing required property: {prop_name}")
                continue
            if prop_def.pattern:
                if not prop_def.validate_pattern(prop_value):
                    result.add_error(
                        "Footprint",
                        f"Property '{prop_name}' value '{prop_value}' does not match pattern: {prop_def.pattern}",
                    )
                else:
                    result.add_success(
                        "Footprint",
                        f"Property '{prop_name}' value '{prop_value}' matches pattern: {prop_def.pattern}",
                    )

    # Validate reference pattern if specified
    if entry.reference_pattern and "Reference" in footprint.properties:
        ref_value = footprint.properties["Reference"]
        if not re.match(entry.reference_pattern, ref_value):
            result.add_error(
                "Footprint",
                f"Reference '{ref_value}' does not match required pattern: {entry.reference_pattern}",
            )
        else:
            result.add_success(
                "Footprint",
                f"Reference '{ref_value}' matches required pattern: {entry.reference_pattern}",
            )

    # Validate required layers
    if entry.required_layers:
        for layer in entry.required_layers:
            if layer not in footprint.layers:
                result.add_error("Footprint", f"Missing required layer: {layer}")
            else:
                result.add_success("Footprint", f"Found required layer: {layer}")

    # Validate required pads
    if entry.required_pads:
        if (
            entry.required_pads.count is not None
            and len(footprint.pads) != entry.required_pads.count
        ):
            result.add_error(
                "Footprint",
                f"Expected {entry.required_pads.count} pads, found {len(footprint.pads)}",
            )
        else:
            result.add_success("Footprint", f"Pad count matches expected: {len(footprint.pads)}")
        if entry.required_pads.required_names:
            for pad_name in entry.required_pads.required_names:
                if not any(pad.number == pad_name for pad in footprint.pads):
                    result.add_error("Footprint", f"Missing required pad: {pad_name}")
                else:
                    result.add_success("Footprint", f"Found required pad: {pad_name}")

    # Check for unknown properties
    known_props = set(required_fields)
    if entry.required_properties:
        known_props.update(entry.required_properties.keys())
        known_props.update(
            prop.ki_field_name for prop in entry.required_properties.values() if prop.ki_field_name
        )
    for prop_name in footprint.properties:
        if prop_name not in known_props and not prop_name.startswith("ki_"):
            result.add_warning("Footprint", f"Unknown property: {prop_name}")

    return result


class FootprintValidator:
    """Validator for footprint files."""

    def __init__(self, structure: LibraryStructure) -> None:
        """
        Initialize the validator.

        Args:
            structure: Library structure definition
        """
        self.structure = structure
        self.result = ValidationResult()

    def validate(self) -> ValidationResult:
        """Validate all footprint files."""
        for group_name, group in self.structure.footprint_groups.items():
            self._validate_group(group_name, group)
        return self.result

    def _validate_group(self, group_name: str, group: ComponentGroup) -> None:
        """
        Validate a footprint group.

        Args:
            group_name: Name of the group
            group: Group definition
        """
        group_path = Path("footprints") / group_name
        if not group_path.exists():
            self.result.add_error(
                "Footprint", f"Footprint group directory '{group_name}' does not exist"
            )
            return

        if not hasattr(group, "entries") or not isinstance(group.entries, dict):
            self.result.add_error("Footprint", f"Footprint group '{group_name}' has no entries")
            return

        for entry_name, entry in group.entries.items():
            self._validate_entry(group_name, entry)

    def _validate_entry(self, group_name: str, entry: ComponentEntry) -> None:
        """
        Validate a footprint entry.

        Args:
            group_name: Name of the group
            entry: Entry definition
        """
        footprint_path = Path("footprints") / group_name / f"{entry.name}.kicad_mod"
        if not footprint_path.exists():
            self.result.add_error(
                "Footprint", f"Footprint file '{entry.name}.kicad_mod' does not exist"
            )
            return

        content = footprint_path.read_text()
        if not content.strip():
            self.result.add_error("Footprint", f"Footprint file '{entry.name}.kicad_mod' is empty")
            return

        # Check for required fields
        required_fields = ["Datasheet", "Description"]
        for field in required_fields:
            if field not in content:
                self.result.add_error(
                    "Footprint", f"Footprint '{entry.name}' is missing required field: {field}"
                )

        # Check for keywords
        if entry.keywords and "Keywords" not in content:
            self.result.add_warning("Footprint", f"Footprint '{entry.name}' is missing keywords")

        # Check for 3D model
        if entry.model_3d:
            model_path = Path("3d") / entry.model_3d
            if not model_path.exists():
                self.result.add_error(
                    "Footprint",
                    f"3D model '{entry.model_3d}' for footprint '{entry.name}' does not exist",
                )

        # Check for pad definitions
        if "pad" not in content.lower():
            self.result.add_error("Footprint", f"Footprint '{entry.name}' has no pad definitions")

        # Check for courtyard
        if "courtyard" not in content.lower():
            self.result.add_warning(
                "Footprint", f"Footprint '{entry.name}' has no courtyard definition"
            )

        # Check for silkscreen
        if "silkscreen" not in content.lower():
            self.result.add_warning(
                "Footprint", f"Footprint '{entry.name}' has no silkscreen definition"
            )

        self.result.add_success("Footprint", f"Footprint '{entry.name}' validation passed")
