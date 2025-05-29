import pytest

from kicad_lib_validator.models.structure import (
    ComponentCategory,
    ComponentNaming,
    ComponentType,
    LibraryDirectories,
    LibraryInfo,
    LibraryNaming,
    LibraryStructure,
    NamingConvention,
    PropertyDefinition,
)
from kicad_lib_validator.models.symbol import Symbol
from kicad_lib_validator.validators.symbol_validator import validate_symbol


def make_structure() -> LibraryStructure:
    # Use correct Pydantic submodels for all nested fields
    return LibraryStructure(
        version="1.0",
        description="Test structure",
        library=LibraryInfo(
            prefix="Test",
            description="Test lib",
            maintainer="Test <test@example.com>",
            license="MIT",
            directories=LibraryDirectories(),
            naming=LibraryNaming(
                symbols=NamingConvention(),
                footprints=NamingConvention(),
                models_3d=NamingConvention(),
            ),
        ),
        symbols={
            "passives": ComponentType(
                description="Passive components",
                categories={
                    "resistors": ComponentCategory(
                        description="Resistors",
                        prefix="R",
                        naming=ComponentNaming(
                            pattern=r"^R[0-9]+$",
                            description_pattern=r"^[0-9.]+[kM]?[Ω]? Resistor$",
                        ),
                        required_properties={
                            "Reference": PropertyDefinition(
                                type="string",
                                pattern=r"^R[0-9]+$",
                                description="Component reference designator",
                            ),
                            "Value": PropertyDefinition(
                                type="string",
                                pattern=r"^[0-9.]+[kM]?[Ω]?$",
                                description="Resistance value",
                            ),
                        },
                    )
                },
            )
        },
        footprints={},
        models_3d={},
        documentation={},
    )


def test_valid_symbol():
    structure = make_structure()
    symbol = Symbol(
        name="R10",
        library_name="Test",
        properties={"Reference": "R10", "Value": "10k"},
        category="passives",
        subcategory="resistors",
    )
    result = validate_symbol(symbol, structure)
    assert not result["errors"]
    assert not result["warnings"]
    assert any("matches pattern" in s for s in result["successes"])


def test_invalid_symbol_name():
    structure = make_structure()
    symbol = Symbol(
        name="X10",
        library_name="Test",
        properties={"Reference": "R10", "Value": "10k"},
        category="passives",
        subcategory="resistors",
    )
    result = validate_symbol(symbol, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_missing_required_property():
    structure = make_structure()
    symbol = Symbol(
        name="R10",
        library_name="Test",
        properties={"Reference": "R10"},  # Missing Value
        category="passives",
        subcategory="resistors",
    )
    result = validate_symbol(symbol, structure)
    assert any("Missing required property" in e for e in result["errors"])


def test_property_value_pattern_fail():
    structure = make_structure()
    symbol = Symbol(
        name="R10",
        library_name="Test",
        properties={"Reference": "R10", "Value": "badvalue"},
        category="passives",
        subcategory="resistors",
    )
    result = validate_symbol(symbol, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_unknown_property_warning():
    structure = make_structure()
    symbol = Symbol(
        name="R10",
        library_name="Test",
        properties={"Reference": "R10", "Value": "10k", "Extra": "foo"},
        category="passives",
        subcategory="resistors",
    )
    result = validate_symbol(symbol, structure)
    assert any("Unknown property" in w for w in result["warnings"])


def test_unrecognized_reference_prefix():
    structure = make_structure()
    symbol = Symbol(
        name="Q1",
        library_name="Test",
        properties={"Reference": "Q1", "Value": "NPN"},
        category="passives",
        subcategory="resistors",
    )
    result = validate_symbol(symbol, structure)
    assert any("does not match pattern" in e for e in result["errors"])
    assert any("Reference" in e for e in result["errors"])
