from pathlib import Path
from typing import Any, Dict

import pytest

from kicad_lib_validator.models.structure import LibraryStructure
from kicad_lib_validator.parser.structure_parser import parse_library_structure_from_yaml


def get_valid_base_structure() -> Dict[str, Any]:
    """Return a valid base library structure that can be modified for different test cases."""
    return {
        "version": "1.0",
        "description": "KiCad Library Structure Definition",
        "library": {
            "prefix": "Test",
            "description": "Example library for testing",
            "maintainer": "Dr. Test <email@example.com>",
            "license": "MIT",
            "directories": {
                "symbols": "symbols",
                "footprints": "footprints",
                "models_3d": "3dmodels",
                "documentation": "docs",
            },
            "naming": {
                "symbols": {
                    "prefix": True,
                    "separator": "_",
                    "case": "upper",
                    "include_categories": True,
                    "category_separator": "_",
                },
                "footprints": {
                    "prefix": True,
                    "separator": "_",
                    "case": "upper",
                    "include_categories": True,
                    "category_separator": "_",
                },
                "models_3d": {
                    "prefix": False,
                    "separator": "_",
                    "case": "lower",
                    "include_categories": False,
                    "category_separator": "_",
                },
            },
        },
    }


def test_parse_library_structure():
    """Test parsing a valid library structure with multiple categories."""
    yaml_content = get_valid_base_structure()

    # Add multiple symbol categories
    yaml_content["symbols"] = {
        "passives": {
            "description": "Passive components",
            "categories": {
                "resistors": {
                    "description": "Resistors",
                    "reference_prefix": "R",
                    "naming": {
                        "pattern": "^R[0-9]+$",
                        "description_pattern": "^[0-9.]+[kM]?[Ω]? Resistor$",
                    },
                    "required_properties": {
                        "Reference": {
                            "type": "string",
                            "pattern": "^R[0-9]+$",
                            "description": "Component reference designator",
                        },
                        "Value": {
                            "type": "string",
                            "pattern": "^[0-9.]+[kM]?[Ω]?$",
                            "description": "Resistance value",
                        },
                    },
                },
                "capacitors": {
                    "description": "Capacitors",
                    "reference_prefix": "C",
                    "naming": {
                        "pattern": "^C[0-9]+$",
                        "description_pattern": "^[0-9.]+[pnu]F Capacitor$",
                    },
                    "required_properties": {
                        "Reference": {
                            "type": "string",
                            "pattern": "^C[0-9]+$",
                            "description": "Component reference designator",
                        },
                        "Value": {
                            "type": "string",
                            "pattern": "^[0-9.]+[pnu]F$",
                            "description": "Capacitance value",
                        },
                    },
                },
            },
        },
        "actives": {
            "description": "Active components",
            "categories": {
                "ics": {
                    "description": "Integrated Circuits",
                    "reference_prefix": "U",
                    "naming": {"pattern": "^U[0-9]+$", "description_pattern": "^[A-Z0-9-]+ IC$"},
                    "required_properties": {
                        "Reference": {
                            "type": "string",
                            "pattern": "^U[0-9]+$",
                            "description": "Component reference designator",
                        },
                        "Value": {
                            "type": "string",
                            "pattern": "^[A-Z0-9-]+$",
                            "description": "Part number",
                        },
                    },
                }
            },
        },
    }

    # Add multiple footprint categories
    yaml_content["footprints"] = {
        "smd": {
            "description": "Surface Mount Devices",
            "categories": {
                "resistors": {
                    "description": "SMD Resistors",
                    "naming": {
                        "pattern": "^SMD_[0-9]+$",
                        "description_pattern": "^[0-9]+ SMD Resistor$",
                    },
                    "required_layers": ["F.Cu", "B.Cu", "F.SilkS", "F.Mask"],
                    "required_properties": {
                        "Reference": {
                            "type": "string",
                            "pattern": "^R[0-9]+$",
                            "description": "Component reference designator",
                        }
                    },
                },
                "capacitors": {
                    "description": "SMD Capacitors",
                    "naming": {
                        "pattern": "^SMD_[0-9]+$",
                        "description_pattern": "^[0-9]+ SMD Capacitor$",
                    },
                    "required_layers": ["F.Cu", "B.Cu", "F.SilkS", "F.Mask"],
                    "required_properties": {
                        "Reference": {
                            "type": "string",
                            "pattern": "^C[0-9]+$",
                            "description": "Component reference designator",
                        }
                    },
                },
            },
        },
        "tht": {
            "description": "Through Hole Technology",
            "categories": {
                "resistors": {
                    "description": "THT Resistors",
                    "naming": {
                        "pattern": "^THT_[0-9.]+mm$",
                        "description_pattern": "^[0-9.]+mm THT Resistor$",
                    },
                    "required_layers": ["F.Cu", "B.Cu", "F.SilkS", "*.Cu"],
                    "required_properties": {
                        "Reference": {
                            "type": "string",
                            "pattern": "^R[0-9]+$",
                            "description": "Component reference designator",
                        }
                    },
                }
            },
        },
    }

    structure = parse_library_structure_from_yaml(yaml_content)

    assert isinstance(structure, LibraryStructure)
    assert structure.version == "1.0"
    assert structure.description == "KiCad Library Structure Definition"

    # Test library info
    assert structure.library.prefix == "Test"
    assert structure.library.description == "Example library for testing"
    assert structure.library.maintainer == "Dr. Test <email@example.com>"
    assert structure.library.license == "MIT"

    # Test directory structure
    assert structure.library.directories.symbols == "symbols"
    assert structure.library.directories.footprints == "footprints"
    assert structure.library.directories.models_3d == "3dmodels"
    assert structure.library.directories.documentation == "docs"

    # Test multiple symbol categories
    assert "passives" in structure.symbols
    assert "actives" in structure.symbols
    assert "resistors" in structure.symbols["passives"].categories
    assert "capacitors" in structure.symbols["passives"].categories
    assert "ics" in structure.symbols["actives"].categories

    # Test multiple footprint categories
    assert "smd" in structure.footprints
    assert "tht" in structure.footprints
    assert "resistors" in structure.footprints["smd"].categories
    assert "capacitors" in structure.footprints["smd"].categories
    assert "resistors" in structure.footprints["tht"].categories


def test_parse_library_structure_invalid_yaml():
    """Test parsing invalid YAML."""
    invalid_yaml = {"invalid": "yaml: content: ["}

    with pytest.raises(ValueError, match="Invalid library structure"):
        parse_library_structure_from_yaml(invalid_yaml)


def test_parse_library_structure_missing_required_fields():
    """Test parsing YAML with missing required fields."""
    invalid_yaml = {
        "version": "1.0",
        "description": "Test",
        # Missing library field
    }

    with pytest.raises(ValueError, match="Invalid library structure"):
        parse_library_structure_from_yaml(invalid_yaml)


def test_parse_library_structure_invalid_version():
    """Test parsing YAML with invalid version format."""
    yaml_content = get_valid_base_structure()
    yaml_content["version"] = "invalid"

    with pytest.raises(ValueError, match="Version must be in format"):
        parse_library_structure_from_yaml(yaml_content)


def test_parse_library_structure_invalid_maintainer():
    """Test parsing YAML with invalid maintainer format."""
    yaml_content = get_valid_base_structure()
    yaml_content["library"]["maintainer"] = "invalid-email"

    with pytest.raises(ValueError, match="Maintainer must be in format"):
        parse_library_structure_from_yaml(yaml_content)


def test_parse_library_structure_invalid_directory_name():
    """Test parsing YAML with invalid directory name."""
    yaml_content = get_valid_base_structure()
    yaml_content["library"]["directories"]["symbols"] = "invalid/directory"

    with pytest.raises(ValueError, match="Directory name.*contains invalid characters"):
        parse_library_structure_from_yaml(yaml_content)


def test_parse_library_structure_invalid_naming_pattern():
    """Test parsing YAML with invalid naming pattern."""
    yaml_content = get_valid_base_structure()
    yaml_content["symbols"] = {
        "passives": {
            "description": "Passive components",
            "categories": {
                "resistors": {
                    "description": "Resistors",
                    "naming": {
                        "pattern": "[invalid pattern",  # Invalid regex
                        "description_pattern": "^[0-9.]+[kM]?[Ω]? Resistor$",
                    },
                }
            },
        }
    }

    with pytest.raises(ValueError, match="Invalid regex pattern"):
        parse_library_structure_from_yaml(yaml_content)


def test_parse_library_structure_invalid_property_type():
    """Test parsing YAML with invalid property type."""
    yaml_content = get_valid_base_structure()
    yaml_content["symbols"] = {
        "passives": {
            "description": "Passive components",
            "categories": {
                "resistors": {
                    "description": "Resistors",
                    "required_properties": {
                        "Value": {
                            "type": "invalid_type",  # Invalid type
                            "pattern": "^[0-9.]+[kM]?[Ω]?$",
                            "description": "Resistance value",
                        }
                    },
                }
            },
        }
    }

    with pytest.raises(ValueError, match="Property type must be one of"):
        parse_library_structure_from_yaml(yaml_content)


def test_parse_library_structure_invalid_layer():
    """Test parsing YAML with invalid layer name."""
    yaml_content = get_valid_base_structure()
    yaml_content["footprints"] = {
        "smd": {
            "description": "Surface Mount Devices",
            "categories": {
                "resistors": {
                    "description": "SMD Resistors",
                    "required_layers": ["Invalid.Layer"],  # Invalid layer
                    "required_properties": {
                        "Reference": {
                            "type": "string",
                            "pattern": "^R[0-9]+$",
                            "description": "Component reference designator",
                        }
                    },
                }
            },
        }
    }

    with pytest.raises(ValueError, match="Invalid layers"):
        parse_library_structure_from_yaml(yaml_content)
