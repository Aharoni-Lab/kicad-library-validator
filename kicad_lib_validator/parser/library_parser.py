"""
Parser for the actual KiCad library contents, using the structure definition.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional

import sexpdata  # type: ignore

from kicad_lib_validator.models import (
    Documentation,
    Footprint,
    KiCadLibrary,
    LibraryStructure,
    Model3D,
    Symbol,
)

logger = logging.getLogger(__name__)


def parse_library(library_root: Path, structure: LibraryStructure) -> KiCadLibrary:
    """
    Parse the actual library contents based on the structure definition.

    Args:
        library_root: Path to the root of the library
        structure: Parsed LibraryStructure

    Returns:
        KiCadLibrary: The populated library model
    """
    library = KiCadLibrary(structure=structure)

    # Parse and add symbols
    symbols = _find_symbols(library_root, structure)
    for symbol in symbols:
        library.add_symbol(symbol)

    # Parse and add footprints
    footprints = _find_footprints(library_root, structure)
    for footprint in footprints:
        library.add_footprint(footprint)

    # Parse and add 3D models
    models_3d = _find_models_3d(library_root, structure)
    for model in models_3d:
        library.add_model3d(model)

    # Parse and add documentation
    documentation = _find_documentation(library_root, structure)
    for doc in documentation:
        library.add_documentation(doc)

    return library


def parse_symbol_file(
    file_path: Path, library_name: str, structure: LibraryStructure, library_root: Path
) -> List[Symbol]:
    """Parse a KiCad symbol file and extract symbols and their properties."""
    logging.debug(f"Parsing symbol file: {file_path}")
    symbols: List[Symbol] = []
    try:
        if structure.library.directories and structure.library.directories.symbols:
            symbols_dir = (library_root / structure.library.directories.symbols).resolve()
            try:
                rel_path = file_path.resolve().relative_to(symbols_dir)
                categories = str(rel_path.parent).replace("\\", "/").split("/")
                full_library_name = library_name
                if (
                    structure.library.naming
                    and structure.library.naming.symbols
                    and structure.library.naming.symbols.include_categories
                ):
                    for cat in categories:
                        if cat and structure.library.naming.symbols.category_separator:
                            full_library_name += (
                                structure.library.naming.symbols.category_separator
                                + cat.capitalize()
                            )
                with open(file_path, "r", encoding="utf-8") as f:
                    raw_data = f.read()
                    logging.debug(f"Raw file content: {raw_data[:200]}...")  # Print first 200 chars
                    data = sexpdata.loads(raw_data)
                    logging.debug(f"Parsed data type: {type(data)}")
                    logging.debug(f"Parsed data: {data}")
                    if isinstance(data, list) and data:
                        logging.debug(f"data[0] type: {type(data[0])}, value: {data[0]}")
                        if str(data[0]) == "kicad_symbol_lib":
                            for item in data[1:]:
                                if isinstance(item, list) and item:
                                    logging.debug(
                                        f"item[0] type: {type(item[0])}, value: {item[0]}"
                                    )
                                    if str(item[0]) == "symbol":
                                        symbol_name = str(item[1])
                                        properties = {}
                                        pins = []
                                        # Find the symbol definition that contains pins (usually ends with _1_1)
                                        for subitem in item[2:]:
                                            if isinstance(subitem, list) and subitem:
                                                if str(subitem[0]) == "symbol" and str(
                                                    subitem[1]
                                                ).endswith("_1_1"):
                                                    # Extract pins from this symbol definition
                                                    for pin_item in subitem[2:]:
                                                        if (
                                                            isinstance(pin_item, list)
                                                            and pin_item
                                                            and str(pin_item[0]) == "pin"
                                                        ):
                                                            pin_type = str(pin_item[1])
                                                            pin_name = None
                                                            pin_number = None
                                                            pin_position = None
                                                            pin_length = None
                                                            pin_orientation = None
                                                            pin_effects = {}

                                                            for pin_prop in pin_item[2:]:
                                                                if (
                                                                    isinstance(pin_prop, list)
                                                                    and pin_prop
                                                                ):
                                                                    if str(pin_prop[0]) == "name":
                                                                        pin_name = str(pin_prop[1])
                                                                    elif (
                                                                        str(pin_prop[0]) == "number"
                                                                    ):
                                                                        pin_number = str(
                                                                            pin_prop[1]
                                                                        )
                                                                    elif str(pin_prop[0]) == "at":
                                                                        # at has format (x y angle)
                                                                        pin_position = {
                                                                            "x": float(pin_prop[1]),
                                                                            "y": float(pin_prop[2]),
                                                                        }
                                                                        pin_orientation = (
                                                                            float(pin_prop[3])
                                                                            if len(pin_prop) > 3
                                                                            else None
                                                                        )
                                                                    elif (
                                                                        str(pin_prop[0]) == "length"
                                                                    ):
                                                                        pin_length = float(
                                                                            pin_prop[1]
                                                                        )
                                                                    elif (
                                                                        str(pin_prop[0])
                                                                        == "effects"
                                                                    ):
                                                                        for effect in pin_prop[1:]:
                                                                            if (
                                                                                isinstance(
                                                                                    effect, list
                                                                                )
                                                                                and effect
                                                                            ):
                                                                                pin_effects[
                                                                                    str(effect[0])
                                                                                ] = effect[1:]

                                                            if (
                                                                pin_name is not None
                                                                and pin_number is not None
                                                                and pin_position is not None
                                                                and pin_length is not None
                                                            ):
                                                                from kicad_lib_validator.models.base import (
                                                                    Position,
                                                                )
                                                                from kicad_lib_validator.models.symbol import (
                                                                    Pin,
                                                                )

                                                                pins.append(
                                                                    Pin(
                                                                        name=pin_name,
                                                                        number=pin_number,
                                                                        type=pin_type,
                                                                        position=Position(
                                                                            **pin_position
                                                                        ),
                                                                        length=pin_length,
                                                                        orientation=pin_orientation,
                                                                        effects=pin_effects,
                                                                    )
                                                                )
                                                elif str(subitem[0]) == "property":
                                                    prop_name = str(subitem[1])
                                                    prop_value = str(subitem[2])
                                                    properties[prop_name] = prop_value
                                        symbols.append(
                                            Symbol(
                                                name=symbol_name,
                                                library_name=full_library_name,
                                                properties=properties,
                                                categories=categories,
                                                pins=pins,
                                            )
                                        )
                                        logging.debug(
                                            f"Extracted symbol: {symbol_name} with properties: {properties} and pins: {pins}"
                                        )
            except ValueError as e:
                logging.error(f"Error resolving relative path for {file_path}: {e}")
                return symbols
    except Exception as e:
        logging.error(f"Error parsing symbol file {file_path}: {e}")
    logging.debug(f"Returning symbols from {file_path}: {symbols}")
    return symbols


def _find_symbols(library_root: Path, structure: LibraryStructure) -> List[Symbol]:
    """
    Find all symbol files in the library and parse them.
    """
    symbols: List[Symbol] = []
    if structure.library.directories and structure.library.directories.symbols:
        symbols_dir = library_root / structure.library.directories.symbols
        abs_symbols_dir = symbols_dir.resolve()
        logger.info(f"Searching for symbol files in: {abs_symbols_dir}")
        print(f"[DEBUG] Searching for symbol files in: {abs_symbols_dir}")
        if not symbols_dir.exists():
            logger.warning(f"Symbols directory not found: {abs_symbols_dir}")
            print(f"[DEBUG] Symbols directory not found: {abs_symbols_dir}")
            return symbols

        for file in symbols_dir.rglob("*.kicad_sym"):
            logger.info(f"Found symbol file: {file}")
            print(f"[DEBUG] Found symbol file: {file.resolve()}")
            symbols.extend(
                parse_symbol_file(file, structure.library.prefix, structure, library_root)
            )
    return symbols


def parse_footprint_file(
    file_path: Path, footprints_dir: Path, structure: Optional[LibraryStructure] = None
) -> Optional[Footprint]:
    """Parse a KiCad footprint file and extract footprint names and properties."""
    try:
        # Get relative path from footprints directory
        rel_path = file_path.resolve().relative_to(footprints_dir)

        # Extract categories from path
        # Example path: passive/capacitor_smd.pretty/C_0201_0603Metric.kicad_mod
        path_parts = list(rel_path.parts)
        # Remove .pretty from the directory name if present
        for i, part in enumerate(path_parts):
            if part.endswith(".pretty"):
                path_parts[i] = part[:-7]  # Remove .pretty suffix
        categories = path_parts[:-1]  # All parts except the filename

        # Build library_name using prefix and categories, like for symbols
        library_name = None
        if (
            structure is not None
            and hasattr(structure, "library")
            and hasattr(structure.library, "prefix")
        ):
            prefix = structure.library.prefix
            separator = "_"
            if (
                hasattr(structure.library, "naming")
                and structure.library.naming
                and hasattr(structure.library.naming, "footprints")
                and structure.library.naming.footprints
                and hasattr(structure.library.naming.footprints, "category_separator")
                and structure.library.naming.footprints.category_separator
            ):
                separator = structure.library.naming.footprints.category_separator
            # Capitalize categories if needed (to match symbol logic)
            library_name = prefix + separator.join(cat.capitalize() for cat in categories)
        else:
            # fallback
            library_name = "_".join(["Lib"] + [cat.capitalize() for cat in categories])

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Extract footprint name from file name
        footprint_name = file_path.stem

        # Parse the content to extract properties
        properties = {}
        tags = []
        pads = []
        layers = []

        # Import Pad model
        from kicad_lib_validator.models.footprint import Pad

        # Initialize required KiCad fields with empty values
        properties["Datasheet"] = ""
        properties["Description"] = ""

        # Extract properties and tags
        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("(property"):
                # Extract property name and value
                match = re.search(r'property\s+"([^"]+)"\s+"([^"]+)"', line)
                if match:
                    prop_name, prop_value = match.groups()
                    properties[prop_name] = prop_value
            elif line.startswith("(tags"):
                # Extract tags
                match = re.search(r'tags\s+"([^"]+)"', line)
                if match:
                    tags = match.group(1).split()
            elif line.startswith("(pad"):
                # Extract pad information
                pad_match = re.search(r'pad\s+"([^"]+)"\s+([^\s]+)', line)
                if pad_match:
                    pad_number = pad_match.group(1)
                    pad_type = pad_match.group(2)
                    # Extract shape, position, size, and layers
                    shape_match = re.search(r"shape\s+([^\s]+)", line)
                    shape = shape_match.group(1) if shape_match else "rect"
                    at_match = re.search(r"at\s+([\-\d.]+)\s+([\-\d.]+)(?:\s+([\-\d.]+))?", line)
                    if at_match:
                        x, y = float(at_match.group(1)), float(at_match.group(2))
                        rotation = float(at_match.group(3)) if at_match.group(3) else 0
                        at = [x, y, rotation]
                    else:
                        at = [0, 0, 0]
                    size_match = re.search(r"size\s+([\-\d.]+)\s+([\-\d.]+)", line)
                    if size_match:
                        size = [float(size_match.group(1)), float(size_match.group(2))]
                    else:
                        size = [0, 0]
                    layers_match = re.search(r"layers\s+([^\s]+)", line)
                    if layers_match:
                        pad_layers = layers_match.group(1).split()
                    else:
                        pad_layers = []
                    pad_obj = Pad(
                        number=pad_number,
                        type=pad_type,
                        shape=shape,
                        at=at,
                        size=size,
                        layers=pad_layers,
                    )
                    pads.append(pad_obj)

        # Create Footprint object
        footprint = Footprint(
            name=footprint_name,
            library_name=library_name,
            properties=properties,
            pads=pads,
            layers=layers,
            categories=categories,
            tags=tags,
        )

        logger.debug(f"Extracted footprint: {footprint}")
        return footprint

    except Exception as e:
        logger.error(f"Error parsing footprint file {file_path}: {str(e)}")
        return None


def _find_footprints(library_root: Path, structure: LibraryStructure) -> List[Footprint]:
    """
    Find all footprint files in the library and parse them.
    """
    footprints: List[Footprint] = []
    if structure.library.directories and structure.library.directories.footprints:
        footprints_dir = library_root / structure.library.directories.footprints
        abs_footprints_dir = footprints_dir.resolve()
        logger.info(f"Searching for footprint files in: {abs_footprints_dir}")
        print(f"[DEBUG] Searching for footprint files in: {abs_footprints_dir}")
        if not footprints_dir.exists():
            logger.warning(f"Footprints directory not found: {abs_footprints_dir}")
            print(f"[DEBUG] Footprints directory not found: {abs_footprints_dir}")
            return footprints

        for file in footprints_dir.rglob("*.kicad_mod"):
            logger.info(f"Found footprint file: {file}")
            print(f"[DEBUG] Found footprint file: {file.resolve()}")
            footprint = parse_footprint_file(file, abs_footprints_dir, structure)
            if footprint:
                footprints.append(footprint)
    return footprints


def _find_models_3d(library_root: Path, structure: LibraryStructure) -> List[Model3D]:
    models: List[Model3D] = []
    if not structure.library.directories or not structure.library.directories.models_3d:
        return models
    models_dir = library_root / structure.library.directories.models_3d
    if not models_dir.exists():
        return models
    # Case-insensitive search for .step and .wrl files
    model_files = [
        f for f in models_dir.rglob("*") if f.is_file() and f.suffix.lower() in [".step", ".wrl"]
    ]
    for file in model_files:
        # Get the relative path from the models_3d directory
        models_dir_abs = models_dir.resolve()
        rel_path = file.relative_to(models_dir_abs)
        category_path = str(rel_path.parent).replace("\\", "/")
        categories = category_path.split("/") if category_path else []

        # Set category and subcategory
        category = categories[0] if categories and categories[0] else None
        subcategory = categories[1] if len(categories) > 1 else None

        full_library_name = structure.library.prefix
        if (
            structure.library.naming
            and structure.library.naming.models_3d
            and structure.library.naming.models_3d.include_categories
            and structure.library.naming.models_3d.category_separator
        ):
            for cat in categories:
                if cat:
                    full_library_name += (
                        structure.library.naming.models_3d.category_separator + cat.capitalize()
                    )
        else:
            for category in categories:
                full_library_name += "_" + category.capitalize()
        models.append(
            Model3D(
                name=file.stem,
                format=file.suffix.lower().lstrip("."),
                units="mm",
                file_path=str(file),
                library_name=full_library_name,
                properties={},
                category=category,
                subcategory=subcategory,
            )
        )
    return models


def _find_documentation(library_root: Path, structure: LibraryStructure) -> List[Documentation]:
    docs: List[Documentation] = []
    if not structure.library.directories or not structure.library.directories.documentation:
        return docs
    docs_dir = library_root / structure.library.directories.documentation
    if not docs_dir.exists():
        return docs
    doc_files = list(docs_dir.rglob("*.pdf"))
    for file in doc_files:
        # Get the relative path from the documentation directory
        docs_dir_abs = docs_dir.resolve()
        rel_path = file.relative_to(docs_dir_abs)
        category_path = str(rel_path.parent).replace("\\", "/")
        categories = category_path.split("/") if category_path else []

        # Set category and subcategory
        category = categories[0] if categories and categories[0] else None
        subcategory = categories[1] if len(categories) > 1 else None

        full_library_name = structure.library.prefix
        if (
            structure.library.naming is not None
            and hasattr(structure.library.naming, "documentation")
            and structure.library.naming.documentation
            and getattr(structure.library.naming.documentation, "include_categories", False)
            and getattr(structure.library.naming.documentation, "category_separator", None)
        ):
            for cat in categories:
                if cat:
                    full_library_name += (
                        structure.library.naming.documentation.category_separator + cat.capitalize()
                    )
        else:
            for category in categories:
                full_library_name += "_" + category.capitalize()
        docs.append(
            Documentation(
                name=file.stem,
                format="pdf",
                file_path=str(file),
                library_name=full_library_name,
                properties={},
                category=category,
                subcategory=subcategory,
            )
        )
    return docs
