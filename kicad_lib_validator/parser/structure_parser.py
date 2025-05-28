"""
Parser for KiCad library structure YAML files.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

from ..models.structure import LibraryStructure


def parse_library_structure(
    file_path: Union[str, Path], library_root: Optional[Union[str, Path]] = None
) -> LibraryStructure:
    """
    Parse a library structure YAML file and validate it against the LibraryStructure model.

    Args:
        file_path: Path to the YAML file
        library_root: Optional root directory of the library. If not provided, uses the YAML file's directory.

    Returns:
        LibraryStructure: Validated library structure

    Raises:
        FileNotFoundError: If the YAML file doesn't exist
        yaml.YAMLError: If the YAML file is invalid
        ValueError: If the structure is invalid
    """
    file_path = Path(file_path)
    if not file_path.exists():
        raise FileNotFoundError(f"Library structure file not found: {file_path}")

    try:
        with open(file_path, "r") as f:
            yaml_content = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML in structure file: {e}")

    if library_root is None:
        library_root = file_path.parent
    else:
        library_root = Path(library_root)

    # Create and validate the library structure
    try:
        structure = LibraryStructure(**yaml_content)
    except Exception as e:
        raise ValueError(f"Invalid library structure: {e}")

    # Validate directory structure
    _validate_directory_structure(structure, library_root)

    return structure


def _validate_directory_structure(structure: LibraryStructure, library_root: Path) -> None:
    """
    Validate that all required directories exist and are valid.

    Args:
        structure: LibraryStructure instance
        library_root: Root directory of the library

    Raises:
        ValueError: If any required directory is missing or invalid
    """
    # Validate symbols directory
    symbols_dir = library_root / structure.library.directories.symbols
    if not symbols_dir.exists():
        raise ValueError(f"Symbols directory not found: {symbols_dir}")
    if not symbols_dir.is_dir():
        raise ValueError(f"Symbols path is not a directory: {symbols_dir}")

    # Validate footprints directory
    footprints_dir = library_root / structure.library.directories.footprints
    if not footprints_dir.exists():
        raise ValueError(f"Footprints directory not found: {footprints_dir}")
    if not footprints_dir.is_dir():
        raise ValueError(f"Footprints path is not a directory: {footprints_dir}")

    # Validate 3D models directory if specified
    if (
        hasattr(structure.library.directories, "models_3d")
        and structure.library.directories.models_3d
    ):
        models_dir = library_root / structure.library.directories.models_3d
        if not models_dir.exists():
            raise ValueError(f"3D models directory not found: {models_dir}")
        if not models_dir.is_dir():
            raise ValueError(f"3D models path is not a directory: {models_dir}")

    # Validate documentation directory if specified
    if (
        hasattr(structure.library.directories, "documentation")
        and structure.library.directories.documentation
    ):
        docs_dir = library_root / structure.library.directories.documentation
        if not docs_dir.exists():
            raise ValueError(f"Documentation directory not found: {docs_dir}")
        if not docs_dir.is_dir():
            raise ValueError(f"Documentation path is not a directory: {docs_dir}")


def validate_component_name(name: str, structure: LibraryStructure) -> bool:
    """
    Validate a component name against the library structure rules.

    Args:
        name: Component name to validate
        structure: LibraryStructure instance

    Returns:
        bool: True if the name is valid, False otherwise
    """
    # TODO: Implement name validation based on structure rules
    return True


def validate_property(property_name: str, value: Any, structure: LibraryStructure) -> bool:
    """
    Validate a property value against the library structure rules.

    Args:
        property_name: Name of the property
        value: Value to validate
        structure: LibraryStructure instance

    Returns:
        bool: True if the property is valid, False otherwise
    """
    # TODO: Implement property validation based on structure rules
    return True
