import re
from typing import Dict, List


def validate_documentation(doc: Documentation, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate documentation against the library structure.

    Args:
        doc: Documentation to validate
        structure: Library structure definition

    Returns:
        Dictionary containing validation results
    """
    results = {"errors": [], "warnings": [], "successes": []}

    # Find matching category
    if not structure.documentation:
        return results

    for type_name, component_type in structure.documentation.items():
        if not component_type.categories:
            continue

        for category_name, category in component_type.categories.items():
            # Check if documentation matches category
            if not _matches_category(doc, category):
                continue

            # Validate required properties
            if category.required_properties:
                for prop_name, prop_def in category.required_properties.items():
                    if prop_name not in doc.properties:
                        if not prop_def.optional:
                            results["errors"].append(f"Missing required property: {prop_name}")
                    else:
                        value = doc.properties[prop_name]
                        if prop_def.pattern and not re.match(prop_def.pattern, value):
                            results["errors"].append(
                                f"Property {prop_name} value '{value}' does not match pattern: {prop_def.pattern}"
                            )

            # Validate naming
            if category.naming:
                if category.naming.pattern and not re.match(category.naming.pattern, doc.name):
                    results["errors"].append(
                        f"Documentation name '{doc.name}' does not match pattern: {category.naming.pattern}"
                    )
                if category.naming.description_pattern and hasattr(doc, "description"):
                    if not re.match(category.naming.description_pattern, doc.description):
                        results["errors"].append(
                            f"Documentation description '{doc.description}' does not match pattern: {category.naming.description_pattern}"
                        )

            # If we found a matching category and passed all validations, add a success message
            results["successes"].append(
                f"Documentation matches category {type_name}/{category_name}"
            )
            return results

    # If no matching category was found
    results["warnings"].append("Documentation does not match any defined category")
    return results


def _matches_category(doc: Documentation, category: ComponentCategory) -> bool:
    """
    Check if documentation matches a category based on its properties.

    Args:
        doc: Documentation to check
        category: Category to match against

    Returns:
        True if the documentation matches the category, False otherwise
    """
    # Check prefix if specified
    if category.prefix:
        if not doc.name.startswith(category.prefix):
            return False

    # Check required properties
    if category.required_properties:
        for prop_name, prop_def in category.required_properties.items():
            if not prop_def.optional and prop_name not in doc.properties:
                return False

    return True
