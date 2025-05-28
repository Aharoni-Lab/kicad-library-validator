"""
Tests for the LibraryReporter class.
"""

import pytest
from pathlib import Path
from kicad_lib_validator.reporter import LibraryReporter
from kicad_lib_validator.validator import KiCadLibraryValidator
from kicad_lib_validator.parser.library_parser import parse_library
from kicad_lib_validator.parser.structure_parser import parse_library_structure


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "test_kicad_lib"


@pytest.fixture
def test_structure_file(test_data_dir) -> Path:
    """Return the path to the test library structure file."""
    return test_data_dir / "test_library_structure.yaml"


def test_reporter_initialization(test_data_dir, test_structure_file):
    """Test reporter initialization."""
    structure = parse_library_structure(test_structure_file)
    reporter = LibraryReporter(test_data_dir, structure)
    assert reporter.library_path == test_data_dir
    assert reporter.structure == structure


def test_generate_report(test_data_dir, test_structure_file, tmp_path):
    """Test report generation."""
    # First validate and parse the library
    validator = KiCadLibraryValidator(test_data_dir, test_structure_file)
    result = validator.validate()
    assert not result.has_errors, f"Validation failed: {result.errors}"

    # Parse the library
    library = parse_library(test_data_dir, validator.structure)
    assert library is not None

    # Create reporter and generate report
    reporter = LibraryReporter(test_data_dir, validator.structure)
    output_path = tmp_path / "library_report.md"
    reporter.generate_library_report(library, output_path)

    # Check that the report was generated
    assert output_path.exists()
    report_content = output_path.read_text()

    # Basic content checks
    assert "# KiCad Library Report" in report_content
    assert "## Symbols" in report_content
    assert "## Footprints" in report_content
    assert "## 3D Models" in report_content
    assert "## Documentation" in report_content

    # Check for actual content
    for library_name, symbol_library in library.symbol_libraries.items():
        for symbol in symbol_library.symbols:
            assert symbol.name in report_content
    for library_name, footprint_library in library.footprint_libraries.items():
        for footprint in footprint_library.footprints:
            assert footprint.name in report_content
    for library_name, model3d_library in library.model3d_libraries.items():
        for model in model3d_library.models:
            assert model.name in report_content
    for library_name, doc_library in library.documentation_libraries.items():
        for doc in doc_library.docs:
            assert doc.name in report_content
