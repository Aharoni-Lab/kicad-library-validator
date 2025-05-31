"""
Footprint validation logic for KiCad libraries.
"""

import re
from typing import Any, Dict, List, Optional

from kicad_lib_validator.models.footprint import Footprint
from kicad_lib_validator.models.structure import ComponentEntry, LibraryStructure
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
        return None
    
    # Get the library name from the footprint
    library_name = footprint.library_name
    if not library_name or library_name not in structure.footprints:
        return None
    
    # Get the component group for this library
    component_group = structure.footprints[library_name]
    
    def check_entry_categories(entry_categories: List[str], footprint_categories: List[str]) -> bool:
        """Check if footprint categories match the entry categories hierarchy."""
        # If entry has no categories, it matches any footprint
        if not entry_categories:
            return True
        
        # If footprint has no categories, it only matches entries with no categories
        if not footprint_categories:
            return not entry_categories
        
        # Check if footprint categories start with the entry categories
        # This allows for hierarchical matching (e.g., "passive/capacitor" matches "passive")
        return all(
            footprint_cat == entry_cat 
            for footprint_cat, entry_cat in zip(footprint_categories, entry_categories)
        )
    
    # Extract categories from the file path
    # The path should be like "footprints/passive/capacitor_smd.pretty/C_0201_0603Metric.kicad_mod"
    path_parts = footprint.file_path.parts
    if len(path_parts) >= 3:  # We need at least footprints/category/subcategory
        # Skip the first part (footprints) and use the rest as categories
        # Also remove the .pretty suffix from the subcategory
        categories = []
        for part in path_parts[1:-1]:  # Remove first (footprints) and last (filename) parts
            if part.endswith('.pretty'):
                categories.append(part[:-7])  # Remove .pretty suffix
            else:
                categories.append(part)
    else:
        categories = []
    
    # Check entries in this group
    if component_group.entries:
        for entry_name, entry in component_group.entries.items():
            if check_entry_categories(entry.categories, categories):
                return entry
    
    # Check subgroups recursively
    if component_group.subgroups:
        for subgroup in component_group.subgroups.values():
            if subgroup.entries:
                for entry_name, entry in subgroup.entries.items():
                    if check_entry_categories(entry.categories, categories):
                        return entry
    
    return None


def validate_footprint(footprint: Footprint, structure: LibraryStructure) -> ValidationResult:
    """Validate a footprint against the library structure."""
    result = ValidationResult()
    required_fields = ["Reference", "Value", "Footprint", "Datasheet", "Description", "ki_keywords"]
    for field in required_fields:
        if field not in footprint.properties:
            result.add_error(f"Missing required field: {field}")
    entry = _find_matching_entry(footprint, structure)
    if not entry:
        result.add_warning(f"No matching component entry found for footprint {footprint.name}")
        return result
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
    if entry.required_layers:
        for layer in entry.required_layers:
            if layer not in footprint.layers:
                result.add_error(f"Missing required layer: {layer}")
            else:
                result.add_success(f"Found required layer: {layer}")
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
                if not any(pad == pad_name for pad in footprint.pads):
                    result.add_error(f"Missing required pad: {pad_name}")
                else:
                    result.add_success(f"Found required pad: {pad_name}")
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
