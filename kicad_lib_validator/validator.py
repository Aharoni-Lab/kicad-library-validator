"""
Main validator class for KiCad library validation.
"""

from pathlib import Path
from typing import List, Optional, Dict, Any
import logging
from dataclasses import dataclass, field

from .parser.structure_parser import parse_library_structure
from .models.structure import LibraryStructure


@dataclass
class ValidationResult:
    """Container for validation results."""

    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    info: List[str] = field(default_factory=list)

    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)

    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)

    def add_info(self, message: str) -> None:
        """Add an info message."""
        self.info.append(message)

    @property
    def has_errors(self) -> bool:
        """Check if there are any errors."""
        return len(self.errors) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings."""
        return len(self.warnings) > 0


class KiCadLibraryValidator:
    """Main validator class for KiCad libraries."""

    def __init__(
        self,
        library_path: Path,
        structure_file: Optional[Path] = None,
        log_level: int = logging.INFO,
    ):
        """
        Initialize the validator.

        Args:
            library_path: Path to the KiCad library directory
            structure_file: Optional path to the library structure YAML file.
                If not provided, will look for 'library_structure.yaml' in the library root.
            log_level: Logging level for the validator
        """
        self.library_path = Path(library_path)
        self.structure_file = structure_file or self.library_path / "library_structure.yaml"
        self.structure: Optional[LibraryStructure] = None
        self.result = ValidationResult()

        # Set up logging
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

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
        required_dirs = {
            "symbols": self.structure.library.directories.symbols,
            "footprints": self.structure.library.directories.footprints,
            "3dmodels": self.structure.library.directories.models_3d,
            "documentation": self.structure.library.directories.documentation,
        }

        for dir_type, dir_name in required_dirs.items():
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

        # TODO: Implement symbol validation
        pass

    def _validate_footprints(self) -> None:
        """Validate footprint files."""
        self.logger.info("Validating footprints")
        if not self.structure:
            self.result.add_error("Cannot validate footprints: structure not parsed")
            return

        # TODO: Implement footprint validation
        pass

    def _validate_3d_models(self) -> None:
        """Validate 3D model files."""
        self.logger.info("Validating 3D models")
        if not self.structure:
            self.result.add_error("Cannot validate 3D models: structure not parsed")
            return

        # TODO: Implement 3D model validation
        pass

    def _validate_documentation(self) -> None:
        """Validate documentation files."""
        self.logger.info("Validating documentation")
        if not self.structure:
            self.result.add_error("Cannot validate documentation: structure not parsed")
            return

        # TODO: Implement documentation validation
        pass
