from typing import List, Dict, Optional
from pydantic import BaseModel, Field

from .base import Position, Size


class Pad(BaseModel):
    """Represents a pad in a footprint."""

    number: str
    type: str  # e.g., "thru_hole", "smd", etc.
    position: Position
    size: Size
    layers: List[str]
    drill: Optional[Dict] = None
    net: Optional[str] = None
    pad_type: Optional[str] = None
    roundrect_rratio: Optional[float] = None
    thermal_bridge_angle: Optional[int] = None


class Footprint(BaseModel):
    """Represents a KiCad footprint."""

    name: str
    library_name: str  # The name of the library this footprint belongs to
    properties: Dict[str, str] = Field(default_factory=dict)
    pads: List[Pad] = Field(default_factory=list)
    layers: List[str] = Field(default_factory=list)
    attr: Optional[Dict] = None  # Footprint attributes (through_hole, smd, etc.)
