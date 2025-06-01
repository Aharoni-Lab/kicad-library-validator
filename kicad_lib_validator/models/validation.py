"""
Validation result model for KiCad library validation.
"""

from typing import Dict, List, Optional


class ValidationResult:
    """Class to store validation results."""

    def __init__(self) -> None:
        """Initialize validation result."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.successes: List[str] = []

    def add_error(self, category: str, message: str) -> None:
        """
        Add an error message.

        Args:
            category: Category of the error
            message: Error message
        """
        self.errors.append(f"{category}: {message}")

    def add_warning(self, category: str, message: str) -> None:
        """
        Add a warning message.

        Args:
            category: Category of the warning
            message: Warning message
        """
        self.warnings.append(f"{category}: {message}")

    def add_success(self, category: str, message: str) -> None:
        """
        Add a success message.

        Args:
            category: Category of the success
            message: Success message
        """
        self.successes.append(f"{category}: {message}")

    def has_errors(self) -> bool:
        """
        Check if there are any errors.

        Returns:
            True if there are errors, False otherwise
        """
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """
        Check if there are any warnings.

        Returns:
            True if there are warnings, False otherwise
        """
        return len(self.warnings) > 0

    def get_summary(self) -> Dict[str, int]:
        """
        Get a summary of validation results.

        Returns:
            Dictionary with counts of errors, warnings, and successes
        """
        return {
            "errors": len(self.errors),
            "warnings": len(self.warnings),
            "successes": len(self.successes),
        }

    def get_formatted_report(self) -> str:
        """
        Get a formatted report of validation results.

        Returns:
            Formatted report string
        """
        report = []
        if self.errors:
            report.append("Errors:")
            for error in self.errors:
                report.append(f"  - {error}")
        if self.warnings:
            report.append("\nWarnings:")
            for warning in self.warnings:
                report.append(f"  - {warning}")
        if self.successes:
            report.append("\nSuccesses:")
            for success in self.successes:
                report.append(f"  - {success}")
        return "\n".join(report)
