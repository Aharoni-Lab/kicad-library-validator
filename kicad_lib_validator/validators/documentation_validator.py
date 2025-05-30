import re
from typing import Dict, List

from kicad_lib_validator.models.documentation import Documentation
from kicad_lib_validator.models.structure import ComponentEntry, LibraryStructure


def validate_documentation(doc: Documentation, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate documentation against the library structure.

    Args:
        doc: Documentation to validate
        structure: Library structure definition

    Returns:
        Dictionary containing validation results
    """
    results: Dict[str, List[str]] = {"errors": [], "warnings": [], "successes": []}

    # Find matching entry
    if not structure.documentation:
        return results

    for group_name, group in structure.documentation.items():
        if hasattr(group, "entries") and group.entries:
            for entry_name, entry in group.entries.items():
                if not _matches_entry(doc, entry):
                    continue

                # Validate required properties
                if entry.required_properties:
                    for prop_name, prop_def in entry.required_properties.items():
                        if prop_name not in doc.properties:
                            if not getattr(prop_def, "optional", False):
                                results["errors"].append(f"Missing required property: {prop_name}")
                        else:
                            value = doc.properties[prop_name]
                            if prop_def.pattern and not re.match(prop_def.pattern, value):
                                results["errors"].append(
                                    f"Property {prop_name} value '{value}' does not match pattern: {prop_def.pattern}"
                                )

                # Validate naming
                if entry.naming:
                    if entry.naming.pattern and not re.match(entry.naming.pattern, doc.name):
                        results["errors"].append(
                            f"Documentation name '{doc.name}' does not match pattern: {entry.naming.pattern}"
                        )
                    if entry.naming.description_pattern and hasattr(doc, "description"):
                        if not re.match(
                            entry.naming.description_pattern, getattr(doc, "description", "")
                        ):
                            results["errors"].append(
                                f"Documentation description '{getattr(doc, 'description', '')}' does not match pattern: {entry.naming.description_pattern}"
                            )

                # If we found a matching entry and passed all validations, add a success message
                results["successes"].append(
                    f"Documentation matches entry {group_name}/{entry_name}"
                )
                return results

    # If no matching entry was found
    results["warnings"].append("Documentation does not match any defined entry")
    return results


def _matches_entry(doc: Documentation, entry: ComponentEntry) -> bool:
    """
    Check if documentation matches an entry based on its properties.

    Args:
        doc: Documentation to check
        entry: Entry to match against

    Returns:
        True if the documentation matches the entry, False otherwise
    """
    # Check prefix if specified
    if entry.naming and entry.naming.pattern:
        if not re.match(entry.naming.pattern, doc.name):
            return False

    # Check required properties
    if entry.required_properties:
        for prop_name, prop_def in entry.required_properties.items():
            if not getattr(prop_def, "optional", False) and prop_name not in doc.properties:
                return False

    return True
