"""
Document validation logic for KiCad libraries.
"""

import re
from typing import Dict, List

from kicad_lib_validator.models.documentation import Documentation
from kicad_lib_validator.models.structure import ComponentCategory, ComponentType, LibraryStructure


def validate_document_name(name: str, structure: LibraryStructure, category: str) -> bool:
    """Validate a document name against the structure rules for the given category."""
    # TODO: Implement document name validation logic
    return True


def validate_document_property(
    property_name: str, value: str, structure: LibraryStructure, category: str
) -> bool:
    """Validate a document property value against the structure rules for the given category."""
    # TODO: Implement document property validation logic
    return True


def validate_documentation(doc: Documentation, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate a Documentation object against the library structure definition.
    Returns a dict with keys: 'errors', 'warnings', 'successes'.
    """
    errors: List[str] = []
    warnings: List[str] = []
    successes: List[str] = []

    # 1. Determine the doc's category using the category/subcategory fields
    doc_category: ComponentType | ComponentCategory | None = None
    doc_category_name = None
    if doc.category and doc.subcategory and structure.documentation:
        try:
            doc_type = structure.documentation.get(doc.category)
            if doc_type and doc_type.categories and doc.subcategory in doc_type.categories:
                doc_category = doc_type.categories[doc.subcategory]
                doc_category_name = f"{doc.category}/{doc.subcategory}"
            else:
                warnings.append(
                    f"Category/subcategory '{doc.category}/{doc.subcategory}' not found in structure for document '{doc.name}'"
                )
        except Exception:
            warnings.append(
                f"Category/subcategory '{doc.category}/{doc.subcategory}' not found in structure for document '{doc.name}'"
            )
    elif doc.category and structure.documentation:
        try:
            doc_type = structure.documentation.get(doc.category)
            if doc_type:
                doc_category = doc_type
                doc_category_name = doc.category
            else:
                warnings.append(
                    f"Category '{doc.category}' not found in structure for document '{doc.name}'"
                )
        except Exception:
            warnings.append(
                f"Category '{doc.category}' not found in structure for document '{doc.name}'"
            )
    else:
        warnings.append(f"No category information for document '{doc.name}'")

    # If no category found, just warn (docs may not always be categorized)
    if not doc_category:
        warnings.append(f"Could not determine documentation category for document '{doc.name}'")
    else:
        # 2. Validate doc name against naming pattern
        naming = getattr(doc_category, "naming", None)
        if naming and hasattr(naming, "pattern"):
            pattern = naming.pattern
            if not re.match(pattern, doc.name):
                errors.append(
                    f"Documentation name '{doc.name}' does not match pattern '{pattern}' for category {doc_category_name}"
                )
            else:
                successes.append(f"Documentation name '{doc.name}' matches pattern '{pattern}'")
        else:
            warnings.append(f"No naming pattern defined for category {doc_category_name}")

        # 3. Validate required properties
        required_props = getattr(doc_category, "required_properties", {})
        for prop_name, prop_rule in required_props.items():
            if prop_name not in doc.properties:
                errors.append(f"Missing required property '{prop_name}' for document '{doc.name}'")
                continue
            value = doc.properties[prop_name]
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

    # 4. Validate format (if specified)
    if hasattr(doc, "format") and doc.format.lower() not in {"pdf", "html"}:
        errors.append(f"Documentation '{doc.name}' has unsupported format '{doc.format}'")

    # 5. Optionally, check for extra/unknown properties
    allowed_props = (
        set(getattr(doc_category, "required_properties", {}).keys()) if doc_category else set()
    )
    for prop in doc.properties:
        if prop not in allowed_props:
            warnings.append(f"Unknown property '{prop}' in documentation '{doc.name}'")

    return {"errors": errors, "warnings": warnings, "successes": successes}
