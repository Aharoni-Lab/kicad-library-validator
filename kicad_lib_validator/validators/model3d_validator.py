"""
3D model validation logic for KiCad libraries.
"""

import re
from typing import Dict, List

from kicad_lib_validator.models.model3d import Model3D
from kicad_lib_validator.models.structure import ComponentCategory, ComponentType, LibraryStructure


def validate_model3d_name(name: str, structure: LibraryStructure, category: str) -> bool:
    """Validate a 3D model name against the structure rules for the given category."""
    # TODO: Implement 3D model name validation logic
    return True


def validate_model3d_property(
    property_name: str, value: str, structure: LibraryStructure, category: str
) -> bool:
    """Validate a 3D model property value against the structure rules for the given category."""
    # TODO: Implement 3D model property validation logic
    return True


def validate_model3d(model: Model3D, structure: LibraryStructure) -> Dict[str, List[str]]:
    """
    Validate a Model3D against the library structure definition.
    Returns a dict with keys: 'errors', 'warnings', 'successes'.
    """
    errors: List[str] = []
    warnings: List[str] = []
    successes: List[str] = []

    # 1. Determine the model's category using the category/subcategory fields
    model_category: ComponentType | ComponentCategory | None = None
    model_category_name = None
    if model.category and model.subcategory:
        try:
            model_category = structure.models_3d[model.category].categories[model.subcategory]
            model_category_name = f"{model.category}/{model.subcategory}"
        except Exception:
            warnings.append(
                f"Category/subcategory '{model.category}/{model.subcategory}' not found in structure for model '{model.name}'"
            )
    elif model.category:
        try:
            model_category = structure.models_3d[model.category]
            model_category_name = model.category
        except Exception:
            warnings.append(
                f"Category '{model.category}' not found in structure for model '{model.name}'"
            )
    else:
        warnings.append(f"No category information for model '{model.name}'")

    # If no category found, just warn (3D models may not always be categorized)
    if not model_category:
        warnings.append(f"Could not determine 3D model category for model '{model.name}'")
    else:
        # 2. Validate model name against naming pattern
        naming = getattr(model_category, "naming", None)
        if naming and hasattr(naming, "pattern"):
            pattern = naming.pattern
            if not re.match(pattern, model.name):
                errors.append(
                    f"3D model name '{model.name}' does not match pattern '{pattern}' for category {model_category_name}"
                )
            else:
                successes.append(f"3D model name '{model.name}' matches pattern '{pattern}'")
        else:
            warnings.append(f"No naming pattern defined for category {model_category_name}")

        # 3. Validate required properties
        required_props = getattr(model_category, "required_properties", {})
        for prop_name, prop_rule in required_props.items():
            if prop_name not in model.properties:
                errors.append(f"Missing required property '{prop_name}' for model '{model.name}'")
                continue
            value = model.properties[prop_name]
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

    # 4. Validate format and units (if specified)
    if hasattr(model, "format") and model.format.lower() not in {"step", "stp", "wrl"}:
        errors.append(f"3D model '{model.name}' has unsupported format '{model.format}'")
    if hasattr(model, "units") and model.units.lower() not in {"mm", "inch"}:
        errors.append(f"3D model '{model.name}' has unsupported units '{model.units}'")

    # 5. Optionally, check for extra/unknown properties
    allowed_props = (
        set(getattr(model_category, "required_properties", {}).keys()) if model_category else set()
    )
    for prop in model.properties:
        if prop not in allowed_props:
            warnings.append(f"Unknown property '{prop}' in 3D model '{model.name}'")

    return {"errors": errors, "warnings": warnings, "successes": successes}
