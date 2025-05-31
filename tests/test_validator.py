"""
Tests for the KiCadLibraryValidator class.
"""

from pathlib import Path

import pytest

from kicad_lib_validator.models.validation import ValidationResult
from kicad_lib_validator.validator import KiCadLibraryValidator


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "test_kicad_lib"


@pytest.fixture
def test_structure_file(test_data_dir) -> Path:
    """Return the path to the test library structure file."""
    return test_data_dir / "test_library_structure.yaml"


def test_validator_initialization(test_data_dir, test_structure_file) -> None:
    """Test validator initialization."""
    validator = KiCadLibraryValidator(test_data_dir, test_structure_file)
    assert validator.library_path == test_data_dir
    assert validator.structure_file == test_structure_file
    assert validator.structure is None
    assert isinstance(validator.result, ValidationResult)


def test_validation_result() -> None:
    """Test ValidationResult class."""
    result = ValidationResult()

    # Test adding messages
    result.add_error("Test error")
    result.add_warning("Test warning")
    result.add_success("Test success")

    # Test message lists
    assert "Test error" in result.errors
    assert "Test warning" in result.warnings
    assert "Test success" in result.successes

    # Test has_errors property
    assert result.has_errors
    result.errors.clear()
    assert not result.has_errors


def test_validate_directory_structure(test_data_dir, test_structure_file, tmp_path) -> None:
    """Test directory structure validation."""
    # Test with missing directories
    validator = KiCadLibraryValidator(tmp_path, test_structure_file)
    result = validator.validate()
    assert result.has_errors
    assert any("directory not found" in error for error in result.errors)

    # Test with valid directory structure
    for dir_name in ["symbols", "footprints", "3dmodels", "docs"]:
        (test_data_dir / dir_name).mkdir(exist_ok=True)

    validator = KiCadLibraryValidator(test_data_dir, test_structure_file)
    result = validator.validate()
    assert not any("directory not found" in error for error in result.errors)


def test_validate_with_invalid_structure_file(test_data_dir, tmp_path) -> None:
    """Test validation with invalid structure file."""
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("invalid: yaml: content: [")

    validator = KiCadLibraryValidator(test_data_dir, invalid_yaml)
    result = validator.validate()
    assert result.has_errors
    assert any("Failed to parse structure file" in error for error in result.errors)


def test_validate_with_missing_structure_file(test_data_dir) -> None:
    """Test validation with missing structure file."""
    validator = KiCadLibraryValidator(test_data_dir)
    result = validator.validate()
    assert result.has_errors
    assert any("Failed to parse structure file" in error for error in result.errors)
