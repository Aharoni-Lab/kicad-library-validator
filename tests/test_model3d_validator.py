import pytest

from kicad_lib_validator.models.model3d import Model3D
from kicad_lib_validator.models.structure import (
    ComponentEntry,
    ComponentGroup,
    ComponentNaming,
    LibraryDirectories,
    LibraryInfo,
    LibraryNaming,
    LibraryStructure,
    NamingConvention,
    PropertyDefinition,
)
from kicad_lib_validator.validators.model3d_validator import validate_model3d


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
        footprints={},
        models_3d={
            "mechanical": ComponentGroup(
                description="Mechanical Models",
                subgroups={
                    "mounts": ComponentGroup(
                        description="Mounting Models",
                        entries={
                            "standard": ComponentEntry(
                                naming=ComponentNaming(
                                    pattern=r"^MNT[0-9]+$",
                                    description_pattern=r"^[0-9]+ Mount$",
                                ),
                                required_properties={
                                    "Material": PropertyDefinition(
                                        type="string",
                                        pattern=r"^[A-Za-z]+$",
                                        description="Material name",
                                    ),
                                },
                            )
                        },
                    )
                },
            )
        },
        documentation={},
    )


def test_valid_model3d() -> None:
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/MNT123.step",
        properties={"Material": "Steel"},
        categories=["mechanical", "mounts"],
    )
    result = validate_model3d(model, structure)
    assert not result["errors"]
    assert not result["warnings"]
    assert any("matches pattern" in s for s in result["successes"])


def test_invalid_model3d_name() -> None:
    structure = make_structure()
    model = Model3D(
        name="BAD123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/BAD123.step",
        properties={"Material": "Steel"},
        categories=["mechanical", "mounts"],
    )
    result = validate_model3d(model, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_missing_required_property() -> None:
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/MNT123.step",
        properties={},
        categories=["mechanical", "mounts"],
    )
    result = validate_model3d(model, structure)
    assert any("Missing required property" in e for e in result["errors"])


def test_property_value_pattern_fail() -> None:
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/MNT123.step",
        properties={"Material": "123Steel"},
        categories=["mechanical", "mounts"],
    )
    result = validate_model3d(model, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_unknown_property_warning() -> None:
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/MNT123.step",
        properties={"Material": "Steel", "Extra": "foo"},
        categories=["mechanical", "mounts"],
    )
    result = validate_model3d(model, structure)
    assert any("Unknown property" in w for w in result["warnings"])


def test_invalid_format() -> None:
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="obj",
        units="mm",
        file_path="/models/MNT123.obj",
        properties={"Material": "Steel"},
        categories=["mechanical", "mounts"],
    )
    result = validate_model3d(model, structure)
    assert any("unsupported format" in e for e in result["errors"])


def test_invalid_units() -> None:
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="cm",
        file_path="/models/MNT123.step",
        properties={"Material": "Steel"},
        categories=["mechanical", "mounts"],
    )
    result = validate_model3d(model, structure)
    assert any("unsupported units" in e for e in result["errors"])
