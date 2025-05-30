"""
Parser for the actual KiCad library contents, using the structure definition.
"""

import logging
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
                                        for prop in item[2:]:
                                            if (
                                                isinstance(prop, list)
                                                and prop
                                                and str(prop[0]) == "property"
                                            ):
                                                prop_name = str(prop[1])
                                                prop_value = str(prop[2])
                                                properties[prop_name] = prop_value
                                        symbols.append(
                                            Symbol(
                                                name=symbol_name,
                                                library_name=full_library_name,
                                                properties=properties,
                                                categories=categories,
                                            )
                                        )
                                        logging.debug(
                                            f"Extracted symbol: {symbol_name} with properties: {properties}"
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
    file_path: Path, library_name: str, structure: LibraryStructure, library_root: Path
) -> List[Footprint]:
    """Parse a KiCad footprint file and extract footprint names and properties."""
    logging.debug(f"Parsing footprint file: {file_path}")
    footprints: List[Footprint] = []
    try:
        if structure.library.directories and structure.library.directories.footprints:
            footprints_dir = (library_root / structure.library.directories.footprints).resolve()
            rel_path = file_path.relative_to(footprints_dir)
            categories = str(rel_path.parent).replace("\\", "/").split("/")
            category = categories[0] if len(categories) > 0 and categories[0] else None
            subcategory = categories[1] if len(categories) > 1 else None
            full_library_name = library_name
            if (
                structure.library.naming
                and structure.library.naming.footprints
                and structure.library.naming.footprints.include_categories
            ):
                for cat in categories:
                    if cat and structure.library.naming.footprints.category_separator:
                        full_library_name += (
                            structure.library.naming.footprints.category_separator
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
                    # Accept both (footprint ...) and (kicad_module ...)
                    if str(data[0]) in ("footprint", "kicad_module"):
                        footprint_name = str(data[1])
                        properties = {}
                        layers = []
                        for prop in data[2:]:
                            if isinstance(prop, list) and prop:
                                if str(prop[0]) == "property":
                                    prop_name = str(prop[1])
                                    prop_value = str(prop[2])
                                    properties[prop_name] = prop_value
                                elif str(prop[0]) == "layer":
                                    layers.append(str(prop[1]))
                        footprints.append(
                            Footprint(
                                name=footprint_name,
                                library_name=full_library_name,
                                properties=properties,
                                layers=layers,
                                category=category,
                                subcategory=subcategory,
                            )
                        )
                        logging.debug(
                            f"Extracted footprint: {footprint_name} with properties: {properties}"
                        )
    except Exception as e:
        logging.error(f"Error parsing footprint file {file_path}: {e}")
    logging.debug(f"Returning footprints from {file_path}: {footprints}")
    print(f"[DEBUG] Returning footprints from {file_path}: {footprints}")
    return footprints


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
            footprints.extend(
                parse_footprint_file(file, structure.library.prefix, structure, library_root)
            )
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
