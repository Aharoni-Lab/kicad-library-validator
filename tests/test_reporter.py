"""
Tests for the LibraryReporter class.
"""
import pytest
from pathlib import Path
from kicad_library_validator.reporter import LibraryReporter
from kicad_library_validator.validator import KiCadLibraryValidator
from kicad_library_validator.parser.library_parser import parse_library
from kicad_library_validator.parser.structure_parser import parse_library_structure


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
    assert any(symbol.name in report_content for symbol in library.symbols)
    assert any(footprint.name in report_content for footprint in library.footprints)
    assert any(model.name in report_content for model in library.models_3d)
    assert any(doc.name in report_content for doc in library.documentation) 