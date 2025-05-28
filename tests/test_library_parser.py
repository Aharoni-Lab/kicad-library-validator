"""
Tests for the library parser.
"""
import pytest
from pathlib import Path
from kicad_library_validator.parser.library_parser import parse_library
from kicad_library_validator.parser.structure_parser import parse_library_structure
from kicad_library_validator.models import KiCadLibrary, Symbol, Footprint, Model3D, Documentation


@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "test_kicad_lib"


@pytest.fixture
def test_structure_file():
    return Path(__file__).parent / "test_kicad_lib" / "test_library_structure.yaml"


@pytest.fixture
def test_structure(test_structure_file):
    return parse_library_structure(test_structure_file)


def test_parse_library(test_data_dir, test_structure):
    """Test parsing the library structure and contents."""
    library = parse_library(test_data_dir, test_structure)
    assert isinstance(library, KiCadLibrary)
    assert len(library.symbols) > 0
    assert len(library.footprints) > 0
    assert len(library.models_3d) > 0
    assert len(library.documentation) > 0


def test_parse_symbols(test_data_dir, test_structure):
    """Test parsing symbols from the library."""
    library = parse_library(test_data_dir, test_structure)
    assert any(isinstance(symbol, Symbol) for symbol in library.symbols)


def test_parse_footprints(test_data_dir, test_structure):
    """Test parsing footprints from the library."""
    library = parse_library(test_data_dir, test_structure)
    assert any(isinstance(footprint, Footprint) for footprint in library.footprints)


def test_parse_models_3d(test_data_dir, test_structure):
    """Test parsing 3D models from the library."""
    library = parse_library(test_data_dir, test_structure)
    assert any(isinstance(model, Model3D) for model in library.models_3d)


def test_parse_documentation(test_data_dir, test_structure):
    """Test parsing documentation from the library."""
    library = parse_library(test_data_dir, test_structure)
    assert any(isinstance(doc, Documentation) for doc in library.documentation) 