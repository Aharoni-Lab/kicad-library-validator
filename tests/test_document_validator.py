import pytest

from kicad_lib_validator.models.documentation import Documentation
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
from kicad_lib_validator.validators.document_validator import validate_documentation


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
        models_3d={},
        documentation={
            "datasheets": ComponentGroup(
                description="Datasheets",
                subgroups={
                    "pdfs": ComponentGroup(
                        description="PDF Datasheets",
                        entries={
                            "standard": ComponentEntry(
                                naming=ComponentNaming(
                                    pattern=r"^DS[0-9]+$",
                                    description_pattern=r"^[0-9]+ Datasheet$",
                                ),
                                required_properties={
                                    "Language": PropertyDefinition(
                                        type="string",
                                        pattern=r"^[a-z]{2}$",
                                        description="Language code",
                                    ),
                                },
                            )
                        },
                    )
                },
            )
        },
    )


def test_valid_documentation() -> None:
    structure = make_structure()
    doc = Documentation(
        name="DS123",
        library_name="Test",
        format="pdf",
        file_path="/docs/DS123.pdf",
        properties={"Language": "en"},
        categories=["datasheets", "pdfs"],
    )
    result = validate_documentation(doc, structure)
    assert not result["errors"]
    assert not result["warnings"]
    assert any("matches pattern" in s for s in result["successes"])


def test_invalid_documentation_name() -> None:
    structure = make_structure()
    doc = Documentation(
        name="BAD123",
        library_name="Test",
        format="pdf",
        file_path="/docs/BAD123.pdf",
        properties={"Language": "en"},
        categories=["datasheets", "pdfs"],
    )
    result = validate_documentation(doc, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_missing_required_property() -> None:
    structure = make_structure()
    doc = Documentation(
        name="DS123",
        library_name="Test",
        format="pdf",
        file_path="/docs/DS123.pdf",
        properties={},
        categories=["datasheets", "pdfs"],
    )
    result = validate_documentation(doc, structure)
    assert any("Missing required property" in e for e in result["errors"])


def test_property_value_pattern_fail() -> None:
    structure = make_structure()
    doc = Documentation(
        name="DS123",
        library_name="Test",
        format="pdf",
        file_path="/docs/DS123.pdf",
        properties={"Language": "english"},
        categories=["datasheets", "pdfs"],
    )
    result = validate_documentation(doc, structure)
    assert any("does not match pattern" in e for e in result["errors"])


def test_unknown_property_warning() -> None:
    structure = make_structure()
    doc = Documentation(
        name="DS123",
        library_name="Test",
        format="pdf",
        file_path="/docs/DS123.pdf",
        properties={"Language": "en", "Extra": "foo"},
        categories=["datasheets", "pdfs"],
    )
    result = validate_documentation(doc, structure)
    assert any("Unknown property" in w for w in result["warnings"])


def test_invalid_format() -> None:
    structure = make_structure()
    doc = Documentation(
        name="DS123",
        library_name="Test",
        format="docx",
        file_path="/docs/DS123.docx",
        properties={"Language": "en"},
        categories=["datasheets", "pdfs"],
    )
    result = validate_documentation(doc, structure)
    assert any("unsupported format" in e for e in result["errors"])


def test_missing_categories() -> None:
    structure = make_structure()
    doc = Documentation(
        name="DS123",
        library_name="Test",
        format="pdf",
        file_path="/docs/DS123.pdf",
        properties={"Language": "en"},
        categories=None,
    )
    result = validate_documentation(doc, structure)
    assert any("must specify a non-empty categories list" in e for e in result["errors"])


def test_invalid_category_path() -> None:
    structure = make_structure()
    doc = Documentation(
        name="DS123",
        library_name="Test",
        format="pdf",
        file_path="/docs/DS123.pdf",
        properties={"Language": "en"},
        categories=["invalid", "path"],
    )
    result = validate_documentation(doc, structure)
    assert any("Unknown group" in e for e in result["errors"])
