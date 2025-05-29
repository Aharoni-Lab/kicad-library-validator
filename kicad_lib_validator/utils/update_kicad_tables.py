"""
Utility script to update KiCad's library tables based on the YAML configuration.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set

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
        return Path(os.environ["APPDATA"]) / "kicad" / "8.0"
    else:  # Linux/Mac
        return Path.home() / ".config" / "kicad" / "8.0"


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
    current_config = {}

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


def get_library_path_variable(prefix: str) -> str:
    """
    Get the environment variable name for the library path based on the prefix.

    Args:
        prefix: The library prefix (e.g. "MyLib")

    Returns:
        Environment variable name (e.g. "MYLIB_DIR")
    """
    return f"{prefix.upper()}_DIR"


def write_lib_table(
    table_path: Path,
    libraries: Dict[str, Dict[str, str]],
    is_symbol_table: bool = False,
    prefix: str = "",
) -> None:
    """
    Write a KiCad library table file.

    Args:
        table_path: Path to the library table file
        libraries: Dictionary mapping library names to their configurations
        is_symbol_table: Whether this is a symbol library table (True) or footprint library table (False)
        prefix: The library prefix to use for environment variable paths
    """
    with open(table_path, "w", encoding="utf-8") as f:
        # Use correct root element based on table type
        root_element = "sym_lib_table" if is_symbol_table else "fp_lib_table"
        f.write(f"({root_element}\n")

        for lib_name, config in sorted(libraries.items()):
            f.write(f'  (lib (name "{lib_name}")\n')
            for key, value in config.items():
                if key == "uri" and prefix:
                    # Convert the path to use the environment variable
                    path_var = get_library_path_variable(prefix)
                    rel_path = value.replace("\\", "/")  # Ensure forward slashes
                    value = f"${{{path_var}}}/{rel_path}"
                f.write(f'    ({key} "{value}")\n')
            f.write("  )\n")
        f.write(")\n")


def update_kicad_tables(
    yaml_path: Path,
    dry_run: bool = False,
    log_level: int = logging.INFO,
    output_dir: Optional[Path] = None,
) -> None:
    """
    Update KiCad's library tables based on the YAML configuration.

    Args:
        yaml_path: Path to the library structure YAML file
        dry_run: If True, only print what would be done without making changes
        log_level: Logging level
        output_dir: Optional path to write the tables instead of the real KiCad config directory
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

    # Determine output directory for tables
    if output_dir is not None:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        kicad_config = output_dir
    else:
        kicad_config = get_kicad_config_path()
        if not kicad_config.exists():
            logger.error(f"KiCad configuration directory not found: {kicad_config}")
            return

    # Update symbol library table
    sym_lib_table = kicad_config / "sym-lib-table"
    existing_sym_libs = parse_lib_table(sym_lib_table)

    # Find all symbol libraries (.kicad_sym files)
    symbols_dir = library_root / structure.library.directories.symbols
    if symbols_dir.exists():
        for file in symbols_dir.rglob("*.kicad_sym"):
            rel_path = file.relative_to(library_root)
            lib_name = structure.library.prefix
            if structure.library.naming.symbols.include_categories:
                # Get category and subcategory from path
                parts = rel_path.parts
                if len(parts) >= 3:  # symbols/category/subcategory/file.kicad_sym
                    category = parts[1]
                    subcategory = parts[2]
                    lib_name += (
                        structure.library.naming.symbols.category_separator + category.capitalize()
                    )
                    lib_name += (
                        structure.library.naming.symbols.category_separator
                        + subcategory.capitalize()
                    )

            if lib_name not in existing_sym_libs:
                if dry_run:
                    logger.info(f"Would add symbol library: {lib_name}")
                else:
                    logger.info(f"Adding symbol library: {lib_name}")
                    existing_sym_libs[lib_name] = {
                        "type": "KiCad",
                        "uri": str(rel_path),
                        "options": "",
                        "descr": f"Symbol library for {lib_name}",
                    }

    if not dry_run:
        write_lib_table(
            sym_lib_table, existing_sym_libs, is_symbol_table=True, prefix=structure.library.prefix
        )

    # Update footprint library table
    fp_lib_table = kicad_config / "fp-lib-table"
    existing_fp_libs = parse_lib_table(fp_lib_table)

    # Find all footprint libraries (.pretty directories)
    footprints_dir = library_root / structure.library.directories.footprints
    if footprints_dir.exists():
        for dir_path in footprints_dir.rglob("*.pretty"):
            if dir_path.is_dir():
                rel_path = dir_path.relative_to(library_root)
                lib_name = structure.library.prefix
                if structure.library.naming.footprints.include_categories:
                    # Get category and subcategory from path
                    parts = rel_path.parts
                    if len(parts) >= 3:  # footprints/category/subcategory.pretty
                        category = parts[1]
                        subcategory = parts[2].replace(".pretty", "")
                        lib_name += (
                            structure.library.naming.footprints.category_separator
                            + category.capitalize()
                        )
                        lib_name += (
                            structure.library.naming.footprints.category_separator
                            + subcategory.capitalize()
                        )

                if lib_name not in existing_fp_libs:
                    if dry_run:
                        logger.info(f"Would add footprint library: {lib_name}")
                    else:
                        logger.info(f"Adding footprint library: {lib_name}")
                        existing_fp_libs[lib_name] = {
                            "type": "KiCad",
                            "uri": str(rel_path),
                            "options": "",
                            "descr": f"Footprint library for {lib_name}",
                        }

    if not dry_run:
        write_lib_table(
            fp_lib_table, existing_fp_libs, is_symbol_table=False, prefix=structure.library.prefix
        )


def main():
    """Command line interface for updating KiCad tables."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Update KiCad's library tables based on YAML configuration."
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
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional output directory for the generated library tables (sym-lib-table, fp-lib-table)",
    )

    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    update_kicad_tables(args.yaml_path, args.dry_run, log_level, args.output_dir)


if __name__ == "__main__":
    main()
