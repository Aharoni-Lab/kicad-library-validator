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
    is_3d_model: bool = False,
    is_documentation: bool = False,
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
        is_3d_model: Whether this is a 3D model directory
        is_documentation: Whether this is a documentation directory
    """
    # Create directory for current group
    current_dir = base_dir / "/".join(current_path)
    if not current_dir.exists():
        if dry_run:
            logger.info(f"Would create directory: {current_dir}")
        else:
            logger.info(f"Creating directory: {current_dir}")
            current_dir.mkdir(parents=True, exist_ok=True)
            # Add README.md to ensure directory is tracked by git
            readme_path = current_dir / "README.md"
            readme_content = (
                f"# {current_path[-1]}\n\nThis directory contains {current_path[-1]} components."
            )
            if dry_run:
                logger.info(f"Would create README.md: {readme_path}")
            else:
                logger.info(f"Creating README.md: {readme_path}")
                readme_path.write_text(readme_content)

    # Process entries: create a subdirectory for each entry
    if group.entries:
        for entry_name in group.entries:
            entry_dir = current_dir / entry_name
            if not entry_dir.exists():
                if dry_run:
                    logger.info(f"Would create entry directory: {entry_dir}")
                else:
                    logger.info(f"Creating entry directory: {entry_dir}")
                    entry_dir.mkdir(parents=True, exist_ok=True)
                    # Add README.md to ensure directory is tracked by git
                    readme_path = entry_dir / "README.md"
                    readme_content = (
                        f"# {entry_name}\n\nThis directory contains {entry_name} components."
                    )
                    if dry_run:
                        logger.info(f"Would create README.md: {readme_path}")
                    else:
                        logger.info(f"Creating README.md: {readme_path}")
                        readme_path.write_text(readme_content)
            # For symbols, create .kicad_sym file in the final entry directory
            if is_symbol:
                sym_file = entry_dir / f"{entry_name}.kicad_sym"
                if not sym_file.exists():
                    if dry_run:
                        logger.info(f"Would create empty symbol library file: {sym_file}")
                    else:
                        logger.info(f"Creating empty symbol library file: {sym_file}")
                        sym_file.write_text(
                            "(kicad_symbol_lib (version 20211014) (generator kicad_symbol_editor)\n)\n"
                        )
            # For footprints, rename the final entry directory to end with .pretty
            elif not is_symbol and not is_3d_model and not is_documentation:
                pretty_dir = entry_dir.with_name(f"{entry_name}.pretty")
                if not pretty_dir.exists():
                    if dry_run:
                        logger.info(f"Would rename directory to: {pretty_dir}")
                    else:
                        logger.info(f"Renaming directory to: {pretty_dir}")
                        entry_dir.rename(pretty_dir)
                        # Add README.md to ensure directory is tracked by git
                        readme_path = pretty_dir / "README.md"
                        readme_content = f"# {entry_name}\n\nThis directory contains {entry_name} footprint components."
                        if dry_run:
                            logger.info(f"Would create README.md: {readme_path}")
                        else:
                            logger.info(f"Creating README.md: {readme_path}")
                            readme_path.write_text(readme_content)
            # For 3D models, rename the final entry directory to end with .3dshapes
            elif is_3d_model and not is_documentation:
                shapes_dir = entry_dir.with_name(f"{entry_name}.3dshapes")
                if not shapes_dir.exists():
                    if dry_run:
                        logger.info(f"Would rename directory to: {shapes_dir}")
                    else:
                        logger.info(f"Renaming directory to: {shapes_dir}")
                        entry_dir.rename(shapes_dir)
                        # Add README.md to ensure directory is tracked by git
                        readme_path = shapes_dir / "README.md"
                        readme_content = f"# {entry_name}\n\nThis directory contains {entry_name} 3D model components."
                        if dry_run:
                            logger.info(f"Would create README.md: {readme_path}")
                        else:
                            logger.info(f"Creating README.md: {readme_path}")
                            readme_path.write_text(readme_content)

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
                is_3d_model,
                is_documentation,
            )


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

    # Create main directories and their READMEs
    for dir_type, dir_name in directories.items():
        dir_path = library_root / dir_name
        if not dir_path.exists():
            if dry_run:
                logger.info(f"Would create directory: {dir_path}")
            else:
                logger.info(f"Creating directory: {dir_path}")
                dir_path.mkdir(parents=True, exist_ok=True)

        # Add README.md to 3dmodels and docs directories
        if dir_type in ["models_3d", "documentation"]:
            readme_path = dir_path / "README.md"
            if not readme_path.exists():
                readme_content = (
                    f"# {dir_name}\n\nThis directory contains {dir_name} for the KiCad library."
                )
                if dry_run:
                    logger.info(f"Would create README.md: {readme_path}")
                else:
                    logger.info(f"Creating README.md: {readme_path}")
                    readme_path.write_text(readme_content)

    # Create component directories for each type
    dir_type_to_field = {
        "symbols": "symbols",
        "footprints": "footprints",
        "models_3d": "models_3d",
        "documentation": "documentation",
    }

    for dir_type in ["symbols", "footprints", "models_3d", "documentation"]:
        if dir_type not in directories:
            continue

        base_dir = library_root / directories[dir_type]
        if not base_dir.exists():
            continue

        # Get component groups from the structure
        groups = getattr(structure, dir_type_to_field[dir_type], {})

        # Create directories for each top-level group
        for group_name, group in groups.items():
            create_component_directories(
                base_dir,
                group,
                [group_name],
                dry_run,
                logger,
                is_symbol=(dir_type == "symbols"),
                is_3d_model=(dir_type == "models_3d"),
                is_documentation=(dir_type == "documentation"),
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
