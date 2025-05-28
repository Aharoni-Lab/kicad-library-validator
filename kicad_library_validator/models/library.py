from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from .symbol import Symbol
from .footprint import Footprint
from .model3d import Model3D
from .documentation import Documentation
from .structure import LibraryStructure


class KiCadLibrary(BaseModel):
    """Main model representing a KiCad library."""
    structure: LibraryStructure
    symbols: List[Symbol] = Field(default_factory=list)
    footprints: List[Footprint] = Field(default_factory=list)
    models_3d: List[Model3D] = Field(default_factory=list)
    documentation: List[Documentation] = Field(default_factory=list)

    def get_entry_by_name(self, name: str) -> Optional[object]:
        """Get any entry by its name."""
        for entry in self.symbols + self.footprints + self.models_3d + self.documentation:
            if hasattr(entry, 'name') and entry.name == name:
                return entry
        return None

    def get_symbol_by_name(self, name: str) -> Optional[Symbol]:
        """Get a symbol by name."""
        for symbol in self.symbols:
            if symbol.name == name:
                return symbol
        return None

    def get_footprint_by_name(self, name: str) -> Optional[Footprint]:
        """Get a footprint by name."""
        for footprint in self.footprints:
            if footprint.name == name:
                return footprint
        return None

    def get_model_3d_by_name(self, name: str) -> Optional[Model3D]:
        """Get a 3D model by name."""
        for model in self.models_3d:
            if model.name == name:
                return model
        return None

    def get_documentation_by_name(self, name: str) -> Optional[Documentation]:
        """Get documentation by name."""
        for doc in self.documentation:
            if doc.name == name:
                return doc
        return None 