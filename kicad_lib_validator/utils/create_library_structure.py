"""
Utility script to create and update the library directory structure based on the YAML configuration.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

from kicad_lib_validator.models.structure import ComponentGroup
from kicad_lib_validator.parser.structure_parser import parse_library_structure


def create_component_directories(
    base_dir: Path,
    group: ComponentGroup,
    current_path: List[str],
    dry_run: bool,
    logger: logging.Logger,
    is_symbol: bool = False,
) -> None:
    """
    Recursively create directories for component groups.

    Args:
        base_dir: Base directory for the component type
        group: Component group to process
        current_path: Current path components
        dry_run: If True, only print what would be done
        logger: Logger instance
        is_symbol: Whether this is a symbol library
    """
    # Create directory for current group
    current_dir = base_dir / "/".join(current_path)
    if not current_dir.exists():
        if dry_run:
            logger.info(f"Would create directory: {current_dir}")
        else:
            logger.info(f"Creating directory: {current_dir}")
            current_dir.mkdir(parents=True, exist_ok=True)

    # Process subgroups
    if group.subgroups:
        for subgroup_name, subgroup in group.subgroups.items():
            create_component_directories(
                base_dir,
                subgroup,
                current_path + [subgroup_name],
                dry_run,
                logger,
                is_symbol,
            )

    # Process entries
    if group.entries:
        # For symbols, create .kicad_sym file in the current directory
        if is_symbol:
            sym_file = current_dir / f"{current_path[-1]}.kicad_sym"
            if not sym_file.exists():
                if dry_run:
                    logger.info(f"Would create empty symbol library file: {sym_file}")
                else:
                    logger.info(f"Creating empty symbol library file: {sym_file}")
                    sym_file.write_text(
                        "(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)\n)\n"
                    )
        # For footprints, rename the directory to end with .pretty
        elif current_dir.name != f"{current_path[-1]}.pretty":
            pretty_dir = current_dir.with_name(f"{current_path[-1]}.pretty")
            if dry_run:
                logger.info(f"Would rename directory to: {pretty_dir}")
            else:
                logger.info(f"Renaming directory to: {pretty_dir}")
                current_dir.rename(pretty_dir)


def create_directory_structure(
    yaml_path: Path,
    dry_run: bool = False,
    log_level: int = logging.INFO,
) -> None:
    """
    Create or update the library directory structure based on the YAML configuration.

    Args:
        yaml_path: Path to the library structure YAML file
        dry_run: If True, only print what would be done without making changes
        log_level: Logging level
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Parse the library structure
    structure = parse_library_structure(yaml_path)
    library_root = yaml_path.parent

    # Get all directories from the structure
    directories = (
        structure.library.directories.model_dump() if structure.library.directories else {}
    )

    # Create main directories
    for dir_type, dir_name in directories.items():
        dir_path = library_root / dir_name
        if not dir_path.exists():
            if dry_run:
                logger.info(f"Would create directory: {dir_path}")
            else:
                logger.info(f"Creating directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)

    # Create component directories for each type
    for dir_type in ["symbols", "footprints", "models_3d", "documentation"]:
        if dir_type not in directories:
            continue

        base_dir = library_root / directories[dir_type]
        if not base_dir.exists():
            continue

        # Get component groups from the structure
        groups = getattr(structure, dir_type, {})

        # Create directories for each top-level group
        for group_name, group in groups.items():
            create_component_directories(
                base_dir,
                group,
                [group_name],
                dry_run,
                logger,
                is_symbol=(dir_type == "symbols"),
            )


def main() -> None:
    """Command line interface for creating library structure."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Create or update KiCad library directory structure from YAML configuration."
    )
    parser.add_argument(
        "yaml_path",
        type=Path,
        help="Path to the library structure YAML file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print what would be done without making changes",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    create_directory_structure(args.yaml_path, args.dry_run, log_level)


if __name__ == "__main__":
    main()
