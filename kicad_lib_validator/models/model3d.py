from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Model3D(BaseModel):
    """Represents a 3D model in the library."""

    name: str
    library_name: str  # The name of the library this model belongs to
    format: str  # e.g., "step", "wrl", etc.
    units: str  # e.g., "mm", "inch"
    file_path: str
    properties: Dict[str, str] = Field(default_factory=dict)
    rotation: Optional[Dict[str, float]] = None  # x, y, z rotation in degrees
    offset: Optional[Dict[str, float]] = None  # x, y, z offset
    scale: Optional[Dict[str, float]] = None  # x, y, z scale factors
    footprint_filters: List[str] = Field(default_factory=list)  # List of compatible footprint names
