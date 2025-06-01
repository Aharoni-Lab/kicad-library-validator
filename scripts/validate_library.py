#!/usr/bin/env python3
"""
Script to validate a KiCad library against its structure definition.
"""

import argparse
import logging
import sys
from pathlib import Path

from kicad_lib_validator.validator import KiCadLibraryValidator
from kicad_lib_validator.utils.generate_report import generate_report
from kicad_lib_validator.utils.create_library_structure import create_directory_structure
from kicad_lib_validator.utils.generate_library_tables import generate_library_tables

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)

def main() -> int:
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Validate a KiCad library against its structure definition.")
    parser.add_argument(
        "library_path",
        type=str,
        help="Path to the library directory",
    )
    parser.add_argument(
        "--structure-file",
        type=str,
        default="library_structure.yaml",
        help="Name of the library structure file (default: library_structure.yaml)",
    )
    parser.add_argument(
        "--generate-tables",
        action="store_true",
        help="Generate library tables",
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Generate a markdown report of the validation results",
    )
    parser.add_argument(
        "--report-file",
        type=str,
        default="library_report.md",
        help="Path to save the markdown report (default: library_report.md)",
    )
    args = parser.parse_args()

    library_path = Path(args.library_path)
    if not library_path.exists():
        print(f"Error: Library path '{library_path}' does not exist")
        return 1

    validator = KiCadLibraryValidator(library_path, args.structure_file)
    if args.generate_tables:
        validator.generate_library_tables()

    result = validator.validate()
    
    # Generate markdown report if requested
    if args.generate_report:
        report_path = Path(args.report_file)
        generate_report(
            library_dir=library_path,
            structure_file=Path(args.structure_file),
            output_path=report_path,
            tables_updated=args.generate_tables
        )
        print(f"\nValidation report generated at: {report_path}")

    if result.has_errors():
        print("\nValidation Results:")
        print(result.get_formatted_report())
        return 1
    elif result.has_warnings():
        print("\nValidation Results:")
        print(result.get_formatted_report())
        return 0
    else:
        print("\nValidation Results:")
        print(result.get_formatted_report())
        return 0

if __name__ == "__main__":
    sys.exit(main()) 