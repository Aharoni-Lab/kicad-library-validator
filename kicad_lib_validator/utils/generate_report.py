#!/usr/bin/env python3
"""
Generate a validation report for a KiCad library based on its structure definition.
"""

import argparse
from pathlib import Path
from typing import Optional

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
) -> Path:
    """
    Generate a validation report for a KiCad library.

    Args:
        library_dir: Path to the library directory
        structure_file: Path to the structure YAML file (defaults to finding it in library_dir)
        output_path: Path where to save the report (defaults to library_dir/library_report.md)

    Returns:
        Path to the generated report
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
    reporter.generate_report(output_path=output_path)

    return output_path


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
        "--verbose",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    # Generate report
    output_path = generate_report(
        args.library_dir,
        args.structure_file,
        args.output_path,
    )

    print(f"Report generated at {output_path}")
    if args.verbose:
        print("\n--- Markdown Output ---\n")
        print(output_path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
