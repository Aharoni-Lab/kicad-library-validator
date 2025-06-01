"""
Document validation logic for KiCad libraries.
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from kicad_lib_validator.models.documentation import Documentation
from kicad_lib_validator.models.structure import ComponentEntry, ComponentGroup, LibraryStructure
from kicad_lib_validator.models.validation import ValidationResult


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
) -> ValidationResult:
    """
    Validate documentation against the structure definition.

    Args:
        documentation: Documentation to validate
        structure: Library structure definition

    Returns:
        ValidationResult containing validation results
    """
    result = ValidationResult()

    # Validate format
    supported_formats = ["pdf", "html"]
    if documentation.format.lower() not in supported_formats:
        result.add_error("Documentation", f"unsupported format: {documentation.format}")

    # Require categories for lookup
    if (
        not documentation.categories
        or not isinstance(documentation.categories, list)
        or len(documentation.categories) == 0
    ):
        result.add_error(
            "Documentation",
            "Documentation must specify a non-empty categories list for validation.",
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
                result.add_error("Documentation", f"Unknown group: {key}")
                return result
            group = group[key]
        elif isinstance(group, ComponentGroup):
            if group.subgroups and key in group.subgroups:
                group = group.subgroups[key]
            elif group.entries and key in group.entries:
                entry = group.entries[key]
                break
            else:
                result.add_error("Documentation", f"Unknown subgroup or entry: {key}")
                return result
        else:
            result.add_error("Documentation", f"Invalid group structure at: {key}")
            return result

    if entry is None:
        if isinstance(group, ComponentGroup) and group.entries and len(group.entries) == 1:
            entry = next(iter(group.entries.values()))
        else:
            result.add_error(
                "Documentation", "Could not resolve a ComponentEntry for the given categories path."
            )
            return result

    # Validate document name
    if entry.naming and entry.naming.pattern:
        pattern_str = entry.naming.pattern
        pattern = re.compile(pattern_str) if isinstance(pattern_str, str) else pattern_str
        if not pattern.match(documentation.name):
            result.add_error(
                "Documentation",
                f"Document name '{documentation.name}' does not match pattern: {entry.naming.pattern}",
            )
        else:
            result.add_success(
                "Documentation",
                f"Document name '{documentation.name}' matches pattern: {entry.naming.pattern}",
            )

    # Validate required properties
    if entry.required_properties:
        for prop_name, prop_def in entry.required_properties.items():
            if prop_name not in documentation.properties:
                result.add_error("Documentation", f"Missing required property: {prop_name}")
            elif prop_def.pattern:
                prop_pattern_str = prop_def.pattern
                prop_pattern = (
                    re.compile(prop_pattern_str)
                    if isinstance(prop_pattern_str, str)
                    else prop_pattern_str
                )
                if not prop_pattern.match(documentation.properties[prop_name]):
                    result.add_error(
                        "Documentation",
                        f"Property '{prop_name}' value '{documentation.properties[prop_name]}' does not match pattern: {prop_def.pattern}",
                    )

    # Check for unknown properties
    if entry.required_properties:
        for prop_name in documentation.properties:
            if prop_name not in entry.required_properties:
                result.add_warning("Documentation", f"Unknown property: {prop_name}")

    return result


class DocumentValidator:
    """Validator for documentation files."""

    def __init__(self, structure: LibraryStructure) -> None:
        """Initialize the validator with the library structure."""
        self.structure = structure
        self.result = ValidationResult()

    def validate(self) -> ValidationResult:
        """Validate documentation files."""
        # Validate README.md
        if not os.path.exists("README.md"):
            self.result.add_error("Documentation", "README.md not found")
        elif os.path.getsize("README.md") == 0:
            self.result.add_error("Documentation", "README.md is empty")
        else:
            self.result.add_success("Documentation", "README.md is valid")

        # Validate LICENSE
        if not os.path.exists("LICENSE"):
            self.result.add_warning("Documentation", "LICENSE not found")
        elif os.path.getsize("LICENSE") == 0:
            self.result.add_error("Documentation", "LICENSE is empty")
        else:
            self.result.add_success("Documentation", "LICENSE is valid")

        # Validate CONTRIBUTING.md
        if not os.path.exists("CONTRIBUTING.md"):
            self.result.add_warning("Documentation", "CONTRIBUTING.md not found")
        elif os.path.getsize("CONTRIBUTING.md") == 0:
            self.result.add_error("Documentation", "CONTRIBUTING.md is empty")
        else:
            self.result.add_success("Documentation", "CONTRIBUTING.md is valid")

        # Validate CODE_OF_CONDUCT.md
        if not os.path.exists("CODE_OF_CONDUCT.md"):
            self.result.add_warning("Documentation", "CODE_OF_CONDUCT.md not found")
        elif os.path.getsize("CODE_OF_CONDUCT.md") == 0:
            self.result.add_error("Documentation", "CODE_OF_CONDUCT.md is empty")
        else:
            self.result.add_success("Documentation", "CODE_OF_CONDUCT.md is valid")

        return self.result
