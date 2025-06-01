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

def main() -> None:
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'  # Simplified format for non-debug messages
    )
    
    # Create a separate debug logger that writes to stderr
    debug_logger = logging.getLogger('debug')
    debug_handler = logging.StreamHandler(sys.stderr)
    debug_handler.setLevel(logging.DEBUG)
    debug_logger.addHandler(debug_handler)
    debug_logger.setLevel(logging.DEBUG)
    
    # Redirect debug messages to stderr
    for logger_name in ['kicad_lib_validator.parser', 'kicad_lib_validator.validator']:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(debug_handler)
    
    try:
        # Generate library tables
        print("Generating library tables...")
        generate_library_tables(Path("data/structure.yaml"))
        print("Library tables generated.\n")
        
        # Run validation
        print("Running validation...")
        validator = KiCadLibraryValidator(
            library_path=Path("data"),
            structure_file=Path("data/structure.yaml")
        )
        result = validator.validate()
        
        print("\nGenerating report...")
        generate_report(Path("data"))
        print("\nReport saved to data/library_report.md")
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 