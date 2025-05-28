from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Documentation(BaseModel):
    """Represents documentation in the library."""

    name: str
    library_name: str  # The name of the library this documentation belongs to
    format: str  # e.g., "pdf", "html", etc.
    file_path: str
    properties: Dict[str, str] = Field(default_factory=dict)
    related_symbols: List[str] = Field(default_factory=list)  # List of related symbol names
    related_footprints: List[str] = Field(default_factory=list)  # List of related footprint names
    language: Optional[str] = None  # e.g., "en", "de", etc.
    version: Optional[str] = None
    last_updated: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
