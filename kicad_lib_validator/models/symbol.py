from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from .base import Position


class Pin(BaseModel):
    """Represents a pin in a symbol."""

    name: str
    number: str
    type: str  # e.g., "input", "output", "bidirectional", etc.
    position: Position
    length: float
    orientation: Optional[float] = None
    effects: Dict = Field(default_factory=dict)


class Symbol(BaseModel):
    """Represents a KiCad symbol."""

    name: str
    library_name: str  # The name of the library this symbol belongs to
    properties: Dict[str, str] = Field(default_factory=dict)
    pins: List[Pin] = Field(default_factory=list)
    units: int = 1
    is_power: bool = False
    is_graphic: bool = False
    is_mechanical: bool = False
