#!/usr/bin/env python3
"""
Generate a validation report for a KiCad library based on its structure definition.
"""

import argparse
from pathlib import Path
from typing import Any, Dict, Optional

from kicad_lib_validator.parser.structure_parser import parse_library_structure
from kicad_lib_validator.reporter import LibraryReporter


def find_structure_file(library_dir: Path) -> Path:
    """
    Find the structure YAML file in the library directory.
    Looks for common names like structure.yaml, library.yaml, etc.

    Args:
        library_dir: Path to the library directory

    Returns:
        Path to the found structure file

    Raises:
        FileNotFoundError: If no structure file is found
    """
    common_names = [
        "structure.yaml",
        "library.yaml",
        "test_library.yaml",  # For test libraries
    ]

    for name in common_names:
        path = library_dir / name
        if path.exists():
            return path

    raise FileNotFoundError(
        f"No structure file found in {library_dir}. " f"Looked for: {', '.join(common_names)}"
    )


def generate_report(
    library_dir: Path,
    structure_file: Optional[Path] = None,
    output_path: Optional[Path] = None,
    tables_updated: bool = False,
    structure_generated: bool = False,
) -> str:
    """
    Generate a validation report for a KiCad library.

    Args:
        library_dir: Path to the library directory
        structure_file: Path to the structure YAML file (defaults to finding it in library_dir)
        output_path: Path where to save the report (defaults to library_dir/library_report.md)
        tables_updated: Whether library tables were updated
        structure_generated: Whether directory structure was generated

    Returns:
        String containing the formatted report
    """
    # Set default paths if not provided
    if structure_file is None:
        structure_file = find_structure_file(library_dir)
    if output_path is None:
        output_path = library_dir / "library_report.md"

    # Parse structure
    structure = parse_library_structure(structure_file)

    # Generate report
    reporter = LibraryReporter(library_dir, structure)
    report_content = reporter.generate_report(output_path=output_path)

    # Format the report for GitHub PR comments
    formatted_report = []

    # Add directory structure section
    formatted_report.append("## Directory Structure")
    formatted_report.append("```")
    for dir_type in ["symbols", "footprints", "3dmodels", "docs"]:
        dir_path = library_dir / dir_type
        if dir_path.exists():
            formatted_report.append(f"📁 {dir_type}/")
            for item in sorted(dir_path.glob("**/*")):
                if item.is_file():
                    rel_path = item.relative_to(library_dir)
                    formatted_report.append(f"  └─ {rel_path}")
    formatted_report.append("```\n")

    # Add validation report section
    formatted_report.append("## Validation Report")
    formatted_report.append(report_content)

    # Add tables update section if applicable
    if tables_updated:
        formatted_report.append("\n## Library Tables Update")
        formatted_report.append("The following changes were made to the library tables:")
        formatted_report.append("```")
        tables_dir = library_dir / "tables"
        if tables_dir.exists():
            for table_file in sorted(tables_dir.glob("*.csv")):
                formatted_report.append(f"📄 {table_file.name}")
        formatted_report.append("```")

    # Add structure generation notice if applicable
    if structure_generated:
        formatted_report.append("\n## Directory Structure Generated")
        formatted_report.append(
            "The KiCad library directory structure was automatically generated from structure.yaml."
        )

    return "\n".join(formatted_report)


def main() -> None:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Generate a validation report for a KiCad library")
    parser.add_argument(
        "library_dir",
        type=Path,
        help="Path to the library directory",
    )
    parser.add_argument(
        "--structure-file",
        type=Path,
        help="Path to the structure YAML file (defaults to finding it in library_dir)",
    )
    parser.add_argument(
        "--output-path",
        type=Path,
        help="Path where to save the report (defaults to library_dir/library_report.md)",
    )
    parser.add_argument(
        "--tables-updated",
        action="store_true",
        help="Indicate that library tables were updated",
    )
    parser.add_argument(
        "--structure-generated",
        action="store_true",
        help="Indicate that directory structure was generated",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Generate report
    report_content = generate_report(
        args.library_dir,
        args.structure_file,
        args.output_path,
        args.tables_updated,
        args.structure_generated,
    )

    print(report_content)


if __name__ == "__main__":
    main()
