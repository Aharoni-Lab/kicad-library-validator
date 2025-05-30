"""
Utility script to append local library tables to KiCad's configuration.
"""

import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from kicad_lib_validator.models.structure import LibraryStructure
from kicad_lib_validator.parser.structure_parser import parse_library_structure


def get_kicad_config_path() -> Path:
    """
    Get the path to KiCad's configuration directory.

    Returns:
        Path to KiCad's configuration directory
    """
    # Try to get from environment variable first
    kicad_config = os.environ.get("KICAD_CONFIG_HOME")
    if kicad_config:
        return Path(kicad_config)

    # Fall back to default locations
    if os.name == "nt":  # Windows
        return Path(os.environ["APPDATA"]) / "kicad" / "9.0"
    else:  # Linux/Mac
        return Path.home() / ".config" / "kicad" / "9.0"


def parse_lib_table(table_path: Path) -> Dict[str, Dict[str, str]]:
    """
    Parse a KiCad library table file.

    Args:
        table_path: Path to the library table file

    Returns:
        Dictionary mapping library names to their configurations
    """
    if not table_path.exists():
        return {}

    libraries = {}
    current_lib = None
    current_config: Dict[str, str] = {}

    with open(table_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("("):
                continue

            if line.startswith("(lib"):
                if current_lib:
                    libraries[current_lib] = current_config
                current_lib = None
                current_config = {}
                continue

            if line.startswith("(name"):
                current_lib = line.split('"')[1]
            elif line.startswith("(type"):
                current_config["type"] = line.split('"')[1]
            elif line.startswith("(uri"):
                current_config["uri"] = line.split('"')[1]
            elif line.startswith("(options"):
                current_config["options"] = line.split('"')[1]
            elif line.startswith("(descr"):
                current_config["descr"] = line.split('"')[1]

    if current_lib:
        libraries[current_lib] = current_config

    return libraries


def write_lib_table(
    table_path: Path,
    libraries: Dict[str, Dict[str, str]],
    is_symbol_table: bool = False,
) -> None:
    """
    Write a KiCad library table file.

    Args:
        table_path: Path to the library table file
        libraries: Dictionary mapping library names to their configurations
        is_symbol_table: Whether this is a symbol library table (True) or footprint library table (False)
    """
    with open(table_path, "w", encoding="utf-8") as f:
        # Use correct root element based on table type
        root_element = "sym_lib_table" if is_symbol_table else "fp_lib_table"
        f.write(f"({root_element}\n")

        for lib_name, config in sorted(libraries.items()):
            f.write(f'  (lib (name "{lib_name}")\n')
            for key, value in config.items():
                f.write(f'    ({key} "{value}")\n')
            f.write("  )\n")
        f.write(")\n")


def update_kicad_tables(
    yaml_path: Path,
    dry_run: bool = False,
    log_level: int = logging.INFO,
) -> Dict[str, List[str]]:
    """
    Append local library tables to KiCad's configuration.

    Args:
        yaml_path: Path to the library structure YAML file
        dry_run: If True, only print what would be done without making changes
        log_level: Logging level

    Returns:
        Dictionary containing lists of added libraries and modified files
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    # Get KiCad config path
    kicad_config = get_kicad_config_path()
    if not kicad_config.exists():
        raise ValueError(f"KiCad configuration directory not found: {kicad_config}")

    # Parse the library structure
    structure = parse_library_structure(yaml_path)
    library_root = yaml_path.parent

    # Get paths to local tables
    if not structure.library.directories or not structure.library.directories.tables:
        raise ValueError("Library directories or tables directory not defined")

    tables_dir = library_root / structure.library.directories.tables
    local_sym_table = tables_dir / "sym-lib-table"
    local_fp_table = tables_dir / "fp-lib-table"

    if not local_sym_table.exists() or not local_fp_table.exists():
        raise ValueError(
            "Local library tables not found. Please run generate_library_tables.py first."
        )

    # Track changes for summary
    changes: Dict[str, List[str]] = {"symbol_libs": [], "footprint_libs": [], "modified_files": []}

    # Update symbol library table
    sym_lib_table = kicad_config / "sym-lib-table"
    existing_sym_libs = parse_lib_table(sym_lib_table)
    local_sym_libs = parse_lib_table(local_sym_table)

    # Add new symbol libraries
    for lib_name, config in local_sym_libs.items():
        if lib_name not in existing_sym_libs:
            if dry_run:
                logger.info(f"Would add symbol library: {lib_name}")
            else:
                logger.info(f"Adding symbol library: {lib_name}")
                existing_sym_libs[lib_name] = config
                changes["symbol_libs"].append(lib_name)

    if not dry_run and changes["symbol_libs"]:
        write_lib_table(sym_lib_table, existing_sym_libs, is_symbol_table=True)
        changes["modified_files"].append(str(sym_lib_table))

    # Update footprint library table
    fp_lib_table = kicad_config / "fp-lib-table"
    existing_fp_libs = parse_lib_table(fp_lib_table)
    local_fp_libs = parse_lib_table(local_fp_table)

    # Add new footprint libraries
    for lib_name, config in local_fp_libs.items():
        if lib_name not in existing_fp_libs:
            if dry_run:
                logger.info(f"Would add footprint library: {lib_name}")
            else:
                logger.info(f"Adding footprint library: {lib_name}")
                existing_fp_libs[lib_name] = config
                changes["footprint_libs"].append(lib_name)

    if not dry_run and changes["footprint_libs"]:
        write_lib_table(fp_lib_table, existing_fp_libs, is_symbol_table=False)
        changes["modified_files"].append(str(fp_lib_table))

    # Print summary of changes
    if changes["symbol_libs"] or changes["footprint_libs"]:
        logger.info("\nSummary of Changes:")
        if changes["symbol_libs"]:
            logger.info("\nAdded Symbol Libraries:")
            for lib in changes["symbol_libs"]:
                logger.info(f"- {lib}")
        if changes["footprint_libs"]:
            logger.info("\nAdded Footprint Libraries:")
            for lib in changes["footprint_libs"]:
                logger.info(f"- {lib}")
        if changes["modified_files"]:
            logger.info("\nModified Files:")
            for file in changes["modified_files"]:
                logger.info(f"- {file}")
    else:
        logger.info("\nNo changes were made to the library tables.")

    return changes


def main() -> None:
    """Command line interface for updating KiCad tables."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Append local library tables to KiCad's configuration."
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
    update_kicad_tables(args.yaml_path, args.dry_run, log_level)


if __name__ == "__main__":
    main()
