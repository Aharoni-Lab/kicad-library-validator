"""
Validation result model for KiCad library validation.
"""

from typing import List


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
