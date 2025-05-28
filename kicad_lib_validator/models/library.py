from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .symbol import Symbol
from .footprint import Footprint
from .model3d import Model3D
from .documentation import Documentation
from .structure import LibraryStructure


class SymbolLibrary(BaseModel):
    """Represents a category of symbols (e.g., Test_Passives_Capacitors)."""

    name: str  # The full library name (e.g., Test_Passives_Capacitors)
    symbols: List[Symbol] = Field(default_factory=list)

    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to this library."""
        self.symbols.append(symbol)


class FootprintLibrary(BaseModel):
    """Represents a category of footprints."""

    name: str
    footprints: List[Footprint] = Field(default_factory=list)

    def add_footprint(self, footprint: Footprint) -> None:
        """Add a footprint to this library."""
        self.footprints.append(footprint)


class Model3DLibrary(BaseModel):
    """Represents a category of 3D models."""

    name: str
    models: List[Model3D] = Field(default_factory=list)

    def add_model(self, model: Model3D) -> None:
        """Add a 3D model to this library."""
        self.models.append(model)


class DocumentationLibrary(BaseModel):
    """Represents a category of documentation."""

    name: str
    docs: List[Documentation] = Field(default_factory=list)

    def add_doc(self, doc: Documentation) -> None:
        """Add documentation to this library."""
        self.docs.append(doc)


class KiCadLibrary(BaseModel):
    """Main model representing a KiCad library."""

    structure: LibraryStructure
    symbol_libraries: Dict[str, SymbolLibrary] = Field(default_factory=dict)
    footprint_libraries: Dict[str, FootprintLibrary] = Field(default_factory=dict)
    model3d_libraries: Dict[str, Model3DLibrary] = Field(default_factory=dict)
    documentation_libraries: Dict[str, DocumentationLibrary] = Field(default_factory=dict)

    def add_symbol(self, symbol: Symbol) -> None:
        """Add a symbol to the appropriate library."""
        if symbol.library_name not in self.symbol_libraries:
            self.symbol_libraries[symbol.library_name] = SymbolLibrary(name=symbol.library_name)
        self.symbol_libraries[symbol.library_name].add_symbol(symbol)

    def add_footprint(self, footprint: Footprint) -> None:
        """Add a footprint to the appropriate library."""
        if footprint.library_name not in self.footprint_libraries:
            self.footprint_libraries[footprint.library_name] = FootprintLibrary(
                name=footprint.library_name
            )
        self.footprint_libraries[footprint.library_name].add_footprint(footprint)

    def add_model3d(self, model: Model3D) -> None:
        """Add a 3D model to the appropriate library."""
        if model.library_name not in self.model3d_libraries:
            self.model3d_libraries[model.library_name] = Model3DLibrary(name=model.library_name)
        self.model3d_libraries[model.library_name].add_model(model)

    def add_documentation(self, doc: Documentation) -> None:
        """Add documentation to the appropriate library."""
        if doc.library_name not in self.documentation_libraries:
            self.documentation_libraries[doc.library_name] = DocumentationLibrary(
                name=doc.library_name
            )
        self.documentation_libraries[doc.library_name].add_doc(doc)

    def get_symbol_by_name(self, name: str) -> Optional[Symbol]:
        """Get a symbol by name across all libraries."""
        for library in self.symbol_libraries.values():
            for symbol in library.symbols:
                if symbol.name == name:
                    return symbol
        return None

    def get_footprint_by_name(self, name: str) -> Optional[Footprint]:
        """Get a footprint by name across all libraries."""
        for library in self.footprint_libraries.values():
            for footprint in library.footprints:
                if footprint.name == name:
                    return footprint
        return None

    def get_model3d_by_name(self, name: str) -> Optional[Model3D]:
        """Get a 3D model by name across all libraries."""
        for library in self.model3d_libraries.values():
            for model in library.models:
                if model.name == name:
                    return model
        return None

    def get_documentation_by_name(self, name: str) -> Optional[Documentation]:
        """Get documentation by name across all libraries."""
        for library in self.documentation_libraries.values():
            for doc in library.docs:
                if doc.name == name:
                    return doc
        return None
