"""
Main validator class for KiCad libraries.
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Any

from kicad_lib_validator.models import (
    Documentation,
    Footprint,
    KiCadLibrary,
    LibraryStructure,
    Model3D,
    Symbol,
)
from kicad_lib_validator.parser.library_parser import (
    _find_documentation,
    _find_footprints,
    _find_models_3d,
    _find_symbols,
)
from kicad_lib_validator.parser.structure_parser import parse_library_structure
from kicad_lib_validator.validators.document_validator import validate_documentation
from kicad_lib_validator.validators.footprint_validator import validate_footprint
from kicad_lib_validator.validators.model3d_validator import validate_model3d
from kicad_lib_validator.validators.symbol_validator import validate_symbol


class ValidationResult:
    """Holds validation results."""

    def __init__(self) -> None:
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_success(self, message: str) -> None:
        """Add a success message."""
        self.successes.append(message)

    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    def is_valid(self) -> bool:
        """Check if validation passed (no errors)."""
        return len(self.errors) == 0


class KiCadLibraryValidator:
    """Main validator class for KiCad libraries."""

    def __init__(self, library_path: Path, structure_file: Optional[Path] = None) -> None:
        self.library_path = Path(library_path)
        if structure_file is None:
            self.structure_file = self.library_path / "library_structure.yaml"
        else:
            self.structure_file = Path(structure_file)
        self.structure: Optional[LibraryStructure] = None
        self.result = ValidationResult()
        self.logger = logging.getLogger(__name__)

    def validate(self) -> ValidationResult:
        """
        Run all validation steps.

        Returns:
            ValidationResult containing all validation messages
        """
        self.logger.info(f"Starting validation of library at {self.library_path}")

        try:
            self._parse_structure()
            self._validate_directory_structure()
            self._validate_symbols()
            self._validate_footprints()
            self._validate_3d_models()
            self._validate_documentation()
        except Exception as e:
            self.logger.error(f"Validation failed with error: {e}")
            self.result.add_error(f"Validation failed: {str(e)}")

        return self.result

    def _parse_structure(self) -> None:
        """Parse the library structure YAML file."""
        self.logger.info("Parsing library structure file")
        try:
            self.structure = parse_library_structure(self.structure_file)
            self.logger.info("Successfully parsed library structure")
        except Exception as e:
            self.logger.error(f"Failed to parse structure file: {e}")
            self.result.add_error(f"Failed to parse structure file: {e}")
            raise

    def _validate_directory_structure(self) -> None:
        """Validate the library directory structure."""
        self.logger.info("Validating directory structure")
        if not self.structure:
            self.result.add_error("Cannot validate directory structure: structure not parsed")
            return

        # Validate required directories
        required_dirs: Dict[str, Optional[str]] = {
            "symbols": self.structure.library.directories.symbols,
            "footprints": self.structure.library.directories.footprints,
            "3dmodels": self.structure.library.directories.models_3d,
            "documentation": self.structure.library.directories.documentation,
        }

        for dir_type, dir_name in required_dirs.items():
            if dir_name is None:
                continue
            dir_path = self.library_path / dir_name
            if not dir_path.exists():
                self.result.add_error(f"Required {dir_type} directory not found: {dir_path}")
            elif not dir_path.is_dir():
                self.result.add_error(f"Required {dir_type} path is not a directory: {dir_path}")

    def _validate_symbols(self) -> None:
        """Validate symbol files."""
        self.logger.info("Validating symbols")
        if not self.structure:
            self.result.add_error("Cannot validate symbols: structure not parsed")
            return

        # Parse and validate symbols
        symbols = _find_symbols(self.library_path, self.structure)
        for symbol in symbols:
            results = validate_symbol(symbol, self.structure)
            self._add_validation_results(results, f"Symbol '{symbol.name}'")

    def _validate_footprints(self) -> None:
        """Validate footprint files."""
        self.logger.info("Validating footprints")
        if not self.structure:
            self.result.add_error("Cannot validate footprints: structure not parsed")
            return

        # Parse and validate footprints
        footprints = _find_footprints(self.library_path, self.structure)
        for footprint in footprints:
            results = validate_footprint(footprint, self.structure)
            self._add_validation_results(results, f"Footprint '{footprint.name}'")

    def _validate_3d_models(self) -> None:
        """Validate 3D model files."""
        self.logger.info("Validating 3D models")
        if not self.structure:
            self.result.add_error("Cannot validate 3D models: structure not parsed")
            return

        # Parse and validate 3D models
        models = _find_models_3d(self.library_path, self.structure)
        for model in models:
            results = validate_model3d(model, self.structure)
            self._add_validation_results(results, f"3D Model '{model.name}'")

    def _validate_documentation(self) -> None:
        """Validate documentation files."""
        self.logger.info("Validating documentation")
        if not self.structure:
            self.result.add_error("Cannot validate documentation: structure not parsed")
            return

        # Parse and validate documentation
        docs = _find_documentation(self.library_path, self.structure)
        for doc in docs:
            results = validate_documentation(doc, self.structure)
            self._add_validation_results(results, f"Documentation '{doc.name}'")

    def _add_validation_results(self, results: Dict[str, List[str]], context: str) -> None:
        """Add validation results to the overall result."""
        for error in results.get("errors", []):
            self.result.add_error(f"{context}: {error}")
        for warning in results.get("warnings", []):
            self.result.add_warning(f"{context}: {warning}")
        for success in results.get("successes", []):
            self.result.add_success(f"{context}: {success}")
