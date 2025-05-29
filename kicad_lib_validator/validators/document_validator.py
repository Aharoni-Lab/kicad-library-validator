"""
Document validation logic for KiCad libraries.
"""

import re
from typing import Dict, List, Optional, Union, cast

from kicad_lib_validator.models.documentation import Documentation
from kicad_lib_validator.models.structure import ComponentCategory, ComponentType, LibraryStructure

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
        Dictionary of validation results
    """
    errors = []
    warnings = []
    successes = []

    # 1. Determine the doc's category using the category/subcategory fields
    doc_category = None
    doc_category_name = None
    if (
        documentation.category
        and documentation.subcategory
        and getattr(structure, "documentation", None)
    ):
        doc_types = cast(Dict[str, ComponentType], structure.documentation)
        doc_type = doc_types.get(documentation.category)
        if (
            doc_type
            and hasattr(doc_type, "categories")
            and doc_type.categories is not None
            and documentation.subcategory in doc_type.categories
        ):
            doc_category = doc_type.categories[documentation.subcategory]
            doc_category_name = f"{documentation.category}/{documentation.subcategory}"
        else:
            warnings.append(
                f"Category/subcategory '{documentation.category}/{documentation.subcategory}' not found in structure for document '{documentation.name}'"
            )
    elif documentation.category and getattr(structure, "documentation", None):
        doc_types = cast(Dict[str, ComponentType], structure.documentation)
        doc_type = doc_types.get(documentation.category)
        if doc_type:
            doc_category = doc_type
            doc_category_name = documentation.category
        else:
            warnings.append(
                f"Category '{documentation.category}' not found in structure for document '{documentation.name}'"
            )
    else:
        warnings.append(f"No category information for document '{documentation.name}'")

    # If no category found, just warn (docs may not always be categorized)
    if not doc_category:
        warnings.append(
            f"Could not determine documentation category for document '{documentation.name}'"
        )
    else:
        # 2. Validate doc name against naming pattern
        naming = getattr(doc_category, "naming", None)
        if naming and hasattr(naming, "pattern") and naming.pattern:
            pattern = naming.pattern
            if not re.match(pattern, documentation.name):
                errors.append(
                    f"Documentation name '{documentation.name}' does not match pattern '{pattern}' for category {doc_category_name}"
                )
            else:
                successes.append(
                    f"Documentation name '{documentation.name}' matches pattern '{pattern}'"
                )
        else:
            warnings.append(f"No naming pattern defined for category {doc_category_name}")

        # 3. Validate required properties
        required_props = getattr(doc_category, "required_properties", {})
        for prop_name, prop_rule in required_props.items():
            if prop_name not in documentation.properties:
                errors.append(
                    f"Missing required property '{prop_name}' for document '{documentation.name}'"
                )
                continue
            value = documentation.properties[prop_name]
            if hasattr(prop_rule, "type") and prop_rule.type != "string":
                warnings.append(
                    f"Property '{prop_name}' type checking not implemented (expected {prop_rule.type})"
                )
            if hasattr(prop_rule, "pattern"):
                if not re.match(prop_rule.pattern, value):
                    errors.append(
                        f"Property '{prop_name}' value '{value}' does not match pattern '{prop_rule.pattern}'"
                    )
                else:
                    successes.append(
                        f"Property '{prop_name}' value '{value}' matches pattern '{prop_rule.pattern}'"
                    )

    # 4. Optionally, check for extra/unknown properties
    allowed_props = (
        set(getattr(doc_category, "required_properties", {}).keys()) if doc_category else set()
    )
    for prop in documentation.properties:
        if prop not in allowed_props:
            warnings.append(f"Unknown property '{prop}' in documentation '{documentation.name}'")

    # 5. Validate format (if specified)
    if (
        hasattr(documentation, "format")
        and documentation.format
        and documentation.format.lower() not in {"pdf", "html"}
    ):
        errors.append(
            f"Documentation '{documentation.name}' has unsupported format '{documentation.format}'"
        )

    return {"errors": errors, "warnings": warnings, "successes": successes}


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
        # Implementation here
        return True
