import pytest
from pathlib import Path
from kicad_lib_validator.parser.structure_parser import parse_library_structure
from kicad_lib_validator.models.structure import LibraryStructure


@pytest.fixture
def test_data_dir() -> Path:
    """Return the path to the test data directory."""
    return Path(__file__).parent / "test_kicad_lib"


@pytest.fixture
def test_structure_file(test_data_dir) -> Path:
    """Return the path to the test library structure file."""
    return test_data_dir / "test_library_structure.yaml"


def test_parse_library_structure(test_structure_file):
    """Test parsing a valid library structure file."""
    structure = parse_library_structure(test_structure_file)
    
    assert isinstance(structure, LibraryStructure)
    assert structure.version == "1.0"
    assert structure.description == "KiCad Library Structure Definition"
    
    # Test library info
    assert structure.library.prefix == "Company"
    assert structure.library.description == "Description of the library"
    assert structure.library.maintainer == "Maintainer Name <email@example.com>"
    assert structure.library.license == "MIT"
    
    # Test directory structure
    assert structure.library.directories.symbols == "symbols"
    assert structure.library.directories.footprints == "footprints"
    assert structure.library.directories.models_3d == "3dmodels"
    assert structure.library.directories.documentation == "docs"


def test_parse_library_structure_invalid_file(test_data_dir):
    """Test parsing an invalid file."""
    with pytest.raises(FileNotFoundError):
        parse_library_structure(test_data_dir / "nonexistent.yaml")


def test_validate_component_name(test_structure_file):
    """Test component name validation."""
    structure = parse_library_structure(test_structure_file)
    
    # Test valid resistor name
    assert structure.validate_component_name("R1", "symbols", "resistor")
    
    # Test invalid resistor name
    assert not structure.validate_component_name("Invalid", "symbols", "resistor")
    
    # Test valid capacitor name
    assert structure.validate_component_name("C1", "symbols", "capacitor")
    
    # Test invalid component type
    with pytest.raises(ValueError, match="Component type must be 'symbols' or 'footprints'"):
        structure.validate_component_name("R1", "invalid", "resistor")


def test_validate_property(test_structure_file):
    """Test property validation."""
    structure = parse_library_structure(test_structure_file)
    
    # Test valid resistor value
    assert structure.validate_property("Value", "10k", "symbols", "resistor")
    
    # Test invalid resistor value
    assert not structure.validate_property("Value", "invalid", "symbols", "resistor")
    
    # Test valid capacitor value
    assert structure.validate_property("Value", "100nF", "symbols", "capacitor")
    
    # Test valid optional property
    assert structure.validate_property("Tolerance", "1%", "symbols", "resistor")
    
    # Test invalid component type
    with pytest.raises(ValueError, match="Component type must be 'symbols' or 'footprints'"):
        structure.validate_property("Value", "10k", "invalid", "resistor")


def test_validate_library_structure_invalid_yaml(test_data_dir, tmp_path):
    """Test parsing invalid YAML."""
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("invalid: yaml: content: [")
    
    with pytest.raises(ValueError, match="Invalid YAML in structure file"):
        parse_library_structure(invalid_yaml)


def test_validate_library_structure_missing_required_fields(test_data_dir, tmp_path):
    """Test parsing YAML with missing required fields."""
    invalid_yaml = tmp_path / "invalid.yaml"
    invalid_yaml.write_text("""
    version: "1.0"
    description: "Test"
    # Missing library field
    """)
    
    with pytest.raises(ValueError, match="Invalid library structure"):
        parse_library_structure(invalid_yaml) 