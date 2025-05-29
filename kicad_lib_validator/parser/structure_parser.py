"""
Parser for KiCad library structure YAML files.
"""

from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
from pydantic import ValidationError

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

    return parse_library_structure_from_yaml(yaml_content, library_root)


def parse_library_structure_from_yaml(
    yaml_content: Dict[str, Any], library_root: Optional[Union[str, Path]] = None
) -> LibraryStructure:
    """
    Parse a library structure from a YAML dictionary and validate it against the LibraryStructure model.

    Args:
        yaml_content: Dictionary containing the YAML content
        library_root: Optional root directory of the library. If not provided, skips directory validation.

    Returns:
        LibraryStructure: Validated library structure

    Raises:
        ValueError: If the structure is invalid
    """
    try:
        structure = LibraryStructure(**yaml_content)
    except ValidationError as e:
        raise ValueError(f"Invalid library structure: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error parsing library structure: {e}")

    # Only validate directory structure if library_root is provided
    if library_root is not None:
        _validate_directory_structure(structure, Path(library_root))

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
    if not structure.library.directories:
        raise ValueError("Library directories configuration is missing")

    # Validate symbols directory
    if structure.library.directories.symbols:
        symbols_dir = library_root / structure.library.directories.symbols
        if not symbols_dir.exists():
            raise ValueError(f"Symbols directory not found: {symbols_dir}")
        if not symbols_dir.is_dir():
            raise ValueError(f"Symbols path is not a directory: {symbols_dir}")

    # Validate footprints directory
    if structure.library.directories.footprints:
        footprints_dir = library_root / structure.library.directories.footprints
        if not footprints_dir.exists():
            raise ValueError(f"Footprints directory not found: {footprints_dir}")
        if not footprints_dir.is_dir():
            raise ValueError(f"Footprints path is not a directory: {footprints_dir}")

    # Validate 3D models directory if specified
    if structure.library.directories.models_3d:
        models_dir = library_root / structure.library.directories.models_3d
        if not models_dir.exists():
            raise ValueError(f"3D models directory not found: {models_dir}")
        if not models_dir.is_dir():
            raise ValueError(f"3D models path is not a directory: {models_dir}")

    # Validate documentation directory if specified
    if structure.library.directories.documentation:
        docs_dir = library_root / structure.library.directories.documentation
        if not docs_dir.exists():
            raise ValueError(f"Documentation directory not found: {docs_dir}")
        if not docs_dir.is_dir():
            raise ValueError(f"Documentation path is not a directory: {docs_dir}")

    # Validate tables directory if specified
    if structure.library.directories.tables:
        tables_dir = library_root / structure.library.directories.tables
        if not tables_dir.exists():
            raise ValueError(f"Tables directory not found: {tables_dir}")
        if not tables_dir.is_dir():
            raise ValueError(f"Tables path is not a directory: {tables_dir}")
