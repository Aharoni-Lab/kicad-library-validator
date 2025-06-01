"""
Validator for 3D model files in the library.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, cast

from kicad_lib_validator.models.model3d import Model3D
from kicad_lib_validator.models.structure import ComponentEntry, ComponentGroup, LibraryStructure
from kicad_lib_validator.models.validation import ValidationResult


def _find_matching_entry(model: Model3D, structure: LibraryStructure) -> Optional[ComponentEntry]:
    """Find the matching component entry in the structure for a 3D model."""
    if not structure.models_3d:
        print("[DEBUG] No 3D models found in the structure.")
        return None

    categories = model.categories or []
    print(f"[DEBUG] Extracted categories from model: {categories}")

    current_group: ComponentGroup = structure.models_3d  # type: ignore
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


def validate_model3d(model: Model3D, structure: LibraryStructure) -> ValidationResult:
    """Validate a 3D model against the library structure."""
    result = ValidationResult()

    # Find matching entry based on categories
    entry = _find_matching_entry(model, structure)
    if not entry:
        result.add_warning("3D Model", f"No matching component entry found for model {model.file_path}")
        return result

    # Validate format
    model_path = Path(model.file_path)
    if model_path.suffix.lower() not in ['.step', '.wrl']:
        result.add_error("3D Model", f"Invalid model format: {model_path.suffix}. Must be .step or .wrl")
    else:
        result.add_success("3D Model", f"Model format {model_path.suffix} is valid")

    # Validate name pattern if specified
    if entry.naming and entry.naming.pattern:
        if not re.match(entry.naming.pattern, model_path.stem):
            result.add_error(
                "3D Model",
                f"Model name '{model_path.stem}' does not match pattern: {entry.naming.pattern}",
            )
        else:
            result.add_success(
                "3D Model",
                f"Model name '{model_path.stem}' matches pattern: {entry.naming.pattern}",
            )

    return result


class Model3DValidator:
    """Validator for 3D model files."""
    def __init__(self, structure: LibraryStructure) -> None:
        """Initialize the validator.

        Args:
            structure: Library structure definition
        """
        self.structure = structure
        self.result = ValidationResult()

    def validate(self) -> ValidationResult:
        """Validate all 3D model files."""
        if not self.structure.library.directories or not self.structure.library.directories.models_3d:
            self.result.add_error("3D Model", "3D models directory not configured in structure")
            return self.result

        models_3d_dir = Path(self.structure.library.directories.models_3d)
        if not models_3d_dir.exists():
            self.result.add_error("3D Model", "3D models directory not found")
            return self.result

        # Find all .step and .wrl files
        for model_path in models_3d_dir.rglob("*.step"):
            # Get categories from path, handling .3dshapes directory
            rel_path = model_path.relative_to(models_3d_dir)
            categories = []
            
            # Process each part of the path
            for part in rel_path.parts[:-1]:  # Exclude the filename
                if part.endswith('.3dshapes'):
                    # Use the directory name without .3dshapes as the category
                    category = part[:-9].lower()  # Remove '.3dshapes' and convert to lowercase
                    if category not in categories:
                        categories.append(category)
                else:
                    categories.append(part.lower())

            model = Model3D(
                name=model_path.stem,
                library_name=self.structure.library.prefix,
                format="step",
                units="mm",
                file_path=str(rel_path),  # Use relative path
                properties={},
                categories=categories
            )
            result = validate_model3d(model, self.structure)
            self.result.merge(result)

        for model_path in models_3d_dir.rglob("*.wrl"):
            # Get categories from path, handling .3dshapes directory
            rel_path = model_path.relative_to(models_3d_dir)
            categories = []
            
            # Process each part of the path
            for part in rel_path.parts[:-1]:  # Exclude the filename
                if part.endswith('.3dshapes'):
                    # Use the directory name without .3dshapes as the category
                    category = part[:-9].lower()  # Remove '.3dshapes' and convert to lowercase
                    if category not in categories:
                        categories.append(category)
                else:
                    categories.append(part.lower())

            model = Model3D(
                name=model_path.stem,
                library_name=self.structure.library.prefix,
                format="wrl",
                units="mm",
                file_path=str(rel_path),  # Use relative path
                properties={},
                categories=categories
            )
            result = validate_model3d(model, self.structure)
            self.result.merge(result)

        return self.result
