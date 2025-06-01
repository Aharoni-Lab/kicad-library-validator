"""
Footprint model for KiCad libraries.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from .base import Position, Size


class Pad(BaseModel):
    """Represents a pad in a KiCad footprint."""

    number: str
    type: str
    shape: str
    at: List[float] = Field(default_factory=lambda: [0, 0, 0])
    size: List[float] = Field(default_factory=lambda: [0, 0])
    layers: List[str] = Field(default_factory=list)


class Footprint(BaseModel):
    """Represents a KiCad footprint.

    Required KiCad fields:
    - Reference: Component reference designator (must be REF**)
    - Value: Component value or part number
    - Datasheet: Link to component datasheet
    - Description: Component description
    - Tags: Keywords for the footprint (defined in the tags field)
    """

    name: str
    library_name: str  # The name of the library this footprint belongs to
    properties: Dict[str, str] = Field(default_factory=dict)
    pads: List[Pad] = Field(default_factory=list)
    layers: List[str] = Field(default_factory=list)
    attr: Optional[Dict] = None  # Footprint attributes (through_hole, smd, etc.)
    categories: Optional[List[str]] = None  # Nested categories for structure lookup
    tags: List[str] = Field(default_factory=list)  # Keywords for the footprint
