import pytest

from kicad_lib_validator.models.footprint import Footprint
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
from kicad_lib_validator.validators.footprint_validator import validate_footprint


def make_structure() -> LibraryStructure:
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
        symbols={},
        footprints={
            "smd": ComponentType(
                description="Surface Mount Devices",
                categories={
                    "resistors": ComponentCategory(
                        description="SMD Resistors",
                        prefix="SMD",
                        naming=ComponentNaming(
                            pattern=r"^SMD[0-9]+$",
                            description_pattern=r"^[0-9]+ SMD Resistor$",
                        ),
                        required_properties={
                            "Reference": PropertyDefinition(
                                type="string",
                                pattern=r"^R[0-9]+$",
                                description="Component reference designator",
                            ),
                        },
                        required_layers=["F.Cu", "B.Cu", "F.SilkS", "F.Mask"],
                    )
                },
            )
        },
        models_3d={},
        documentation={},
    )


def test_valid_footprint():
    structure = make_structure()
    footprint = Footprint(
        name="SMD1234",
        library_name="Test",
        properties={"Reference": "R10"},
        layers=["F.Cu", "B.Cu", "F.SilkS", "F.Mask"],
        category="smd",
        subcategory="resistors",
    )
    result = validate_footprint(footprint, structure)
    assert not result["errors"]
    assert not result["warnings"]
    assert any("matches pattern" in s for s in result["successes"])
    assert any("contains all required layers" in s for s in result["successes"])


def test_invalid_footprint_name():
    structure = make_structure()
    footprint = Footprint(
        name="THT1234",
        library_name="Test",
        properties={"Reference": "R10"},
        layers=["F.Cu", "B.Cu", "F.SilkS", "F.Mask"],
        category="smd",
        subcategory="resistors",
    )
    result = validate_footprint(footprint, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_missing_required_property():
    structure = make_structure()
    footprint = Footprint(
        name="SMD1234",
        library_name="Test",
        properties={},  # Missing Reference
        layers=["F.Cu", "B.Cu", "F.SilkS", "F.Mask"],
        category="smd",
        subcategory="resistors",
    )
    result = validate_footprint(footprint, structure)
    assert any("Missing required property" in e for e in result["errors"])


def test_property_value_pattern_fail():
    structure = make_structure()
    footprint = Footprint(
        name="SMD1234",
        library_name="Test",
        properties={"Reference": "BADREF"},
        layers=["F.Cu", "B.Cu", "F.SilkS", "F.Mask"],
        category="smd",
        subcategory="resistors",
    )
    result = validate_footprint(footprint, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_unknown_property_warning():
    structure = make_structure()
    footprint = Footprint(
        name="SMD1234",
        library_name="Test",
        properties={"Reference": "R10", "Extra": "foo"},
        layers=["F.Cu", "B.Cu", "F.SilkS", "F.Mask"],
        category="smd",
        subcategory="resistors",
    )
    result = validate_footprint(footprint, structure)
    assert any("Unknown property" in w for w in result["warnings"])


def test_missing_required_layer():
    structure = make_structure()
    footprint = Footprint(
        name="SMD1234",
        library_name="Test",
        properties={"Reference": "R10"},
        layers=["F.Cu", "B.Cu", "F.SilkS"],  # Missing F.Mask
        category="smd",
        subcategory="resistors",
    )
    result = validate_footprint(footprint, structure)
    assert any("missing required layers" in e for e in result["errors"])
