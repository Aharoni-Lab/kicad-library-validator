"""
Utility script to create and update the library directory structure based on the YAML configuration.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional

from kicad_lib_validator.parser.structure_parser import parse_library_structure


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
    directories = structure.library.directories.model_dump()

    # Create main directories
    for dir_type, dir_name in directories.items():
        dir_path = library_root / dir_name
        if not dir_path.exists():
            if dry_run:
                logger.info(f"Would create directory: {dir_path}")
            else:
                logger.info(f"Creating directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)

    # Create category and subcategory directories for each type
    for dir_type in ["symbols", "footprints", "models_3d", "documentation"]:
        if dir_type not in directories:
            continue

        base_dir = library_root / directories[dir_type]
        if not base_dir.exists():
            continue

        # Get categories and subcategories from the structure
        categories = getattr(structure, dir_type, {})

        # Create category directories
        for category, subcategories in categories.items():
            category_dir = base_dir / category
            if not category_dir.exists():
                if dry_run:
                    logger.info(f"Would create category directory: {category_dir}")
                else:
                    logger.info(f"Creating category directory: {category_dir}")
                    category_dir.mkdir(parents=True, exist_ok=True)

            # Create subcategory directories
            if hasattr(subcategories, "categories"):
                for subcategory in subcategories.categories:
                    subcategory_dir = category_dir / subcategory
                    if not dry_run:
                        subcategory_dir.mkdir(exist_ok=True)
                    logger.info(f"Creating subcategory directory: {subcategory_dir}")

                    # For symbols, create empty .kicad_sym file
                    if dir_type == "symbols":
                        sym_file = subcategory_dir / f"{subcategory}.kicad_sym"
                        if not sym_file.exists():
                            if dry_run:
                                logger.info(f"Would create empty symbol library file: {sym_file}")
                            else:
                                logger.info(f"Creating empty symbol library file: {sym_file}")
                                sym_file.write_text(
                                    "(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)\n)\n"
                                )

                    # For footprints, rename directory to end with .pretty
                    elif dir_type == "footprints":
                        pretty_dir = subcategory_dir.with_name(f"{subcategory}.pretty")
                        if subcategory_dir != pretty_dir:
                            if dry_run:
                                logger.info(f"Would rename directory to: {pretty_dir}")
                            else:
                                logger.info(f"Renaming directory to: {pretty_dir}")
                                subcategory_dir.rename(pretty_dir)


def main():
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
