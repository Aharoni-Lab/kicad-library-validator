"""
Tests for the library parser.
"""

from pathlib import Path

import pytest

from kicad_lib_validator.models import Documentation, Footprint, KiCadLibrary, Model3D, Symbol
from kicad_lib_validator.parser.library_parser import parse_library
from kicad_lib_validator.parser.structure_parser import parse_library_structure


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
    assert len(library.symbol_libraries) > 0
    assert len(library.footprint_libraries) > 0
    assert len(library.model3d_libraries) > 0
    assert len(library.documentation_libraries) > 0


def test_parse_symbols(test_data_dir, test_structure):
    """Test parsing symbols from the library."""
    library = parse_library(test_data_dir, test_structure)
    assert any(len(lib.symbols) > 0 for lib in library.symbol_libraries.values())
    assert any(
        isinstance(symbol, Symbol)
        for lib in library.symbol_libraries.values()
        for symbol in lib.symbols
    )


def test_parse_footprints(test_data_dir, test_structure):
    """Test parsing footprints from the library."""
    library = parse_library(test_data_dir, test_structure)
    assert any(len(lib.footprints) > 0 for lib in library.footprint_libraries.values())
    assert any(
        isinstance(footprint, Footprint)
        for lib in library.footprint_libraries.values()
        for footprint in lib.footprints
    )


def test_parse_models_3d(test_data_dir, test_structure):
    """Test parsing 3D models from the library."""
    library = parse_library(test_data_dir, test_structure)
    assert any(len(lib.models) > 0 for lib in library.model3d_libraries.values())
    assert any(
        isinstance(model, Model3D)
        for lib in library.model3d_libraries.values()
        for model in lib.models
    )


def test_parse_documentation(test_data_dir, test_structure):
    """Test parsing documentation from the library."""
    library = parse_library(test_data_dir, test_structure)
    assert any(len(lib.docs) > 0 for lib in library.documentation_libraries.values())
    assert any(
        isinstance(doc, Documentation)
        for lib in library.documentation_libraries.values()
        for doc in lib.docs
    )


def test_structure_subgroups_and_entries(test_structure):
    """Test that the structure contains the expected subgroups and entries."""
    # Symbols
    assert "passives" in test_structure.symbols
    assert "resistors" in test_structure.symbols["passives"].subgroups
    assert "standard" in test_structure.symbols["passives"].subgroups["resistors"].entries
    # Footprints
    assert "smd" in test_structure.footprints
    assert "resistors" in test_structure.footprints["smd"].subgroups
    assert "standard" in test_structure.footprints["smd"].subgroups["resistors"].entries
    # Models 3D
    assert "passives" in test_structure.models_3d
    assert "capacitors" in test_structure.models_3d["passives"].subgroups
    assert "standard" in test_structure.models_3d["passives"].subgroups["capacitors"].entries
    # Documentation
    assert "passives" in test_structure.documentation
    assert "datasheets" in test_structure.documentation["passives"].subgroups
    assert "standard" in test_structure.documentation["passives"].subgroups["datasheets"].entries
