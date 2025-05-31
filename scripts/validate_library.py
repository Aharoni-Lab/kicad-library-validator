#!/usr/bin/env python3
"""
Script to validate a KiCad library using the validator.
"""

import logging
import sys
from pathlib import Path

from kicad_lib_validator.validator import KiCadLibraryValidator
from kicad_lib_validator.utils.generate_report import generate_report
from kicad_lib_validator.utils.create_library_structure import create_directory_structure
from kicad_lib_validator.utils.generate_library_tables import generate_library_tables

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

def main():
    """Run the validation on the library."""
    # Get the library path from command line or use default
    if len(sys.argv) > 1:
        library_path = Path(sys.argv[1])
    else:
        library_path = Path("data")
    
    # Get the structure file path
    structure_file = library_path / "structure.yaml"
    
    # Check if expected directories exist
    expected_dirs = ["symbols", "footprints", "3dmodels", "docs", "tables"]
    missing_dirs = [d for d in expected_dirs if not (library_path / d).exists()]
    
    if missing_dirs:
        print(f"Missing directories: {', '.join(missing_dirs)}")
        print("Creating directory structure...")
        create_directory_structure(structure_file)
        print("Directory structure created.")
    
    # Generate tables
    print("\nGenerating library tables...")
    generate_library_tables(structure_file)
    print("Library tables generated.")
    
    # Create the validator
    validator = KiCadLibraryValidator(library_path, structure_file)
    
    # Run validation
    print("\nRunning validation...")
    result = validator.validate()
    
    # Generate report
    print("\nGenerating report...")
    report_path = library_path / "library_report.md"
    generate_report(
        library_dir=library_path,
        output_path=report_path,
        structure_file=structure_file,
    )
    print(f"Report saved to {report_path}")
    
    # Print summary
    print("\nValidation Summary:")
    print(f"Errors: {len(result.errors)}")
    print(f"Warnings: {len(result.warnings)}")
    print(f"Successes: {len(result.successes)}")
    
    if result.errors:
        print("\nErrors:")
        for error in result.errors:
            print(f"  - {error}")
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  - {warning}")

if __name__ == "__main__":
    main() 