import pytest

from kicad_lib_validator.models.model3d import Model3D
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
            "mechanical": ComponentType(
                description="Mechanical Models",
                categories={
                    "mounts": ComponentCategory(
                        description="Mounting Models",
                        prefix="MNT",
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
        documentation={},
    )


def test_valid_model3d():
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/MNT123.step",
        properties={"Material": "Steel"},
        category="mechanical",
        subcategory="mounts",
    )
    result = validate_model3d(model, structure)
    assert not result["errors"]
    assert not result["warnings"]
    assert any("matches pattern" in s for s in result["successes"])


def test_invalid_model3d_name():
    structure = make_structure()
    model = Model3D(
        name="BAD123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/BAD123.step",
        properties={"Material": "Steel"},
        category="mechanical",
        subcategory="mounts",
    )
    result = validate_model3d(model, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_missing_required_property():
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/MNT123.step",
        properties={},
        category="mechanical",
        subcategory="mounts",
    )
    result = validate_model3d(model, structure)
    assert any("Missing required property" in e for e in result["errors"])


def test_property_value_pattern_fail():
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/MNT123.step",
        properties={"Material": "123Steel"},
        category="mechanical",
        subcategory="mounts",
    )
    result = validate_model3d(model, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_unknown_property_warning():
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="mm",
        file_path="/models/MNT123.step",
        properties={"Material": "Steel", "Extra": "foo"},
        category="mechanical",
        subcategory="mounts",
    )
    result = validate_model3d(model, structure)
    assert any("Unknown property" in w for w in result["warnings"])


def test_invalid_format():
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="obj",
        units="mm",
        file_path="/models/MNT123.obj",
        properties={"Material": "Steel"},
        category="mechanical",
        subcategory="mounts",
    )
    result = validate_model3d(model, structure)
    assert any("unsupported format" in e for e in result["errors"])


def test_invalid_units():
    structure = make_structure()
    model = Model3D(
        name="MNT123",
        library_name="Test",
        format="step",
        units="cm",
        file_path="/models/MNT123.step",
        properties={"Material": "Steel"},
        category="mechanical",
        subcategory="mounts",
    )
    result = validate_model3d(model, structure)
    assert any("unsupported units" in e for e in result["errors"])
