"""
Document validation logic for KiCad libraries.
"""

import re
from typing import Dict, List, Optional, Union, cast

from kicad_lib_validator.models.documentation import Documentation
from kicad_lib_validator.models.structure import ComponentEntry, ComponentGroup, LibraryStructure

ValidationResult = Union[bool, str]  # True for success, str for error message


def validate_document_name(name: str, structure: LibraryStructure, category: str) -> bool:
    """
    Validate a document name against the structure definition.

    Args:
        name: Document name to validate
        structure: Library structure definition
        category: Component category

    Returns:
        True if valid, False otherwise
    """
    naming = getattr(structure.library, "naming", None)
    documentation_naming = getattr(naming, "documentation", None)
    if not documentation_naming or not hasattr(documentation_naming, "pattern"):
        return True
    pattern = documentation_naming.pattern
    if not pattern:
        return True
    return bool(re.match(pattern, name))


def validate_document_property(
    property_name: str, value: str, structure: LibraryStructure, category: str
) -> bool:
    """Validate a document property value against the structure rules for the given category."""
    # TODO: Implement document property validation logic
    return True


def validate_documentation(
    documentation: Documentation, structure: LibraryStructure
) -> Dict[str, List[str]]:
    """
    Validate documentation against the structure definition.

    Args:
        documentation: Documentation to validate
        structure: Library structure definition

    Returns:
        Dictionary containing validation results
    """
    result: Dict[str, List[str]] = {"errors": [], "warnings": [], "successes": []}

    # Validate format
    supported_formats = ["pdf", "html"]
    if documentation.format.lower() not in supported_formats:
        result["errors"].append(f"unsupported format: {documentation.format}")

    # Require categories for lookup
    if (
        not documentation.categories
        or not isinstance(documentation.categories, list)
        or len(documentation.categories) == 0
    ):
        result["errors"].append(
            "Documentation must specify a non-empty categories list for validation."
        )
        return result

    # Traverse the nested structure using categories
    group = structure.documentation
    entry = None
    path = documentation.categories.copy()
    while path:
        key = path.pop(0)
        if isinstance(group, dict):
            if key not in group:
                result["errors"].append(f"Unknown group: {key}")
                return result
            group = group[key]
        elif isinstance(group, ComponentGroup):
            if group.subgroups and key in group.subgroups:
                group = group.subgroups[key]
            elif group.entries and key in group.entries:
                entry = group.entries[key]
                break
            else:
                result["errors"].append(f"Unknown subgroup or entry: {key}")
                return result
        else:
            result["errors"].append(f"Invalid group structure at: {key}")
            return result

    if entry is None:
        # If we ended on a ComponentGroup with only one entry, use it
        if isinstance(group, ComponentGroup) and group.entries and len(group.entries) == 1:
            entry = next(iter(group.entries.values()))
        else:
            result["errors"].append(
                "Could not resolve a ComponentEntry for the given categories path."
            )
            return result

    # Validate document name
    if entry.naming and entry.naming.pattern:
        pattern_str = entry.naming.pattern
        pattern = re.compile(pattern_str) if isinstance(pattern_str, str) else pattern_str
        if not pattern.match(documentation.name):
            result["errors"].append(
                f"Document name '{documentation.name}' does not match pattern: {entry.naming.pattern}"
            )
        else:
            result["successes"].append(
                f"Document name '{documentation.name}' matches pattern: {entry.naming.pattern}"
            )

    # Validate required properties
    if entry.required_properties:
        for prop_name, prop_def in entry.required_properties.items():
            if prop_name not in documentation.properties:
                result["errors"].append(f"Missing required property: {prop_name}")
            elif prop_def.pattern:
                prop_pattern_str = prop_def.pattern
                prop_pattern = (
                    re.compile(prop_pattern_str)
                    if isinstance(prop_pattern_str, str)
                    else prop_pattern_str
                )
                if not prop_pattern.match(documentation.properties[prop_name]):
                    result["errors"].append(
                        f"Property '{prop_name}' value '{documentation.properties[prop_name]}' does not match pattern: {prop_def.pattern}"
                    )

    # Check for unknown properties
    if entry.required_properties:
        for prop_name in documentation.properties:
            if prop_name not in entry.required_properties:
                result["warnings"].append(f"Unknown property: {prop_name}")

    return result


class DocumentValidator:
    """Validator for documentation files."""

    def __init__(self, structure: LibraryStructure):
        """
        Initialize the validator.

        Args:
            structure: Library structure definition
        """
        self.structure = structure

    def validate(self, documentation: Documentation) -> ValidationResult:
        """
        Validate a documentation file.

        Args:
            documentation: Documentation to validate

        Returns:
            True if valid, error message if invalid
        """
        result = validate_documentation(documentation, self.structure)
        if result["errors"]:
            return "\n".join(result["errors"])
        return True
