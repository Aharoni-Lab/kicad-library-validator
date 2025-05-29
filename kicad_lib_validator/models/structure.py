import re
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, field_validator


class LibraryDirectories(BaseModel):
    """Directory structure configuration."""

    symbols: str = "symbols"
    footprints: str = "footprints"
    models_3d: Optional[str] = "3dmodels"
    documentation: Optional[str] = "docs"

    @field_validator("symbols", "footprints", "models_3d", "documentation")
    @classmethod
    def validate_directory_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate directory names are valid."""
        if v is not None and not re.match(r"^[a-zA-Z0-9_-]+$", v):
            raise ValueError(f"Directory name '{v}' contains invalid characters")
        return v


class NamingConvention(BaseModel):
    """Naming convention configuration."""

    prefix: Optional[bool] = True
    separator: Optional[str] = "_"
    case: Optional[Literal["upper", "lower", "mixed"]] = "upper"
    include_categories: Optional[bool] = False
    category_separator: Optional[str] = "_"

    @field_validator("separator")
    @classmethod
    def validate_separator(cls, v: Optional[str]) -> Optional[str]:
        """Validate separator is a single character."""
        if v is not None and len(v) != 1:
            raise ValueError("Separator must be a single character")
        return v


class LibraryNaming(BaseModel):
    """Naming conventions for different library elements."""

    symbols: Optional[NamingConvention] = Field(default_factory=NamingConvention)
    footprints: Optional[NamingConvention] = Field(default_factory=NamingConvention)
    models_3d: Optional[NamingConvention] = Field(default_factory=NamingConvention)


class LibraryInfo(BaseModel):
    """Library metadata and configuration."""

    prefix: str
    description: Optional[str] = ""
    maintainer: Optional[str] = None
    license: Optional[str] = None
    website: Optional[HttpUrl] = None
    repository: Optional[HttpUrl] = None
    directories: Optional[LibraryDirectories] = Field(default_factory=LibraryDirectories)
    naming: Optional[LibraryNaming] = Field(default_factory=LibraryNaming)

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v: str) -> str:
        """Validate library prefix."""
        if not re.match(r"^[A-Za-z0-9]+$", v):
            raise ValueError("Library prefix must contain only alphanumeric characters")
        return v

    @field_validator("maintainer")
    @classmethod
    def validate_maintainer(cls, v: Optional[str]) -> Optional[str]:
        """Validate maintainer email format if provided."""
        if v is not None and not re.match(r"^[^<]+ <[^>]+>$", v):
            raise ValueError("Maintainer must be in format 'Name <email@example.com>'")
        return v


class PropertyDefinition(BaseModel):
    """Definition of a property in a component."""

    type: str
    pattern: Optional[str] = None
    optional: Optional[bool] = False
    description: Optional[str] = None

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate property type."""
        valid_types = {"string", "number", "boolean", "url", "email"}
        if v.lower() not in valid_types:
            raise ValueError(f"Property type must be one of: {', '.join(valid_types)}")
        return v.lower()

    @field_validator("pattern")
    @classmethod
    def validate_pattern(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Validate regex pattern if provided."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v


class PinNaming(BaseModel):
    """Naming rules for pins."""

    pattern: Optional[str] = None
    description_pattern: Optional[str] = None

    @field_validator("pattern", "description_pattern")
    @classmethod
    def validate_patterns(cls, v: Optional[str]) -> Optional[str]:
        """Validate regex patterns if provided."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v


class PinRequirements(BaseModel):
    """Requirements for pins in a component."""

    min_count: Optional[int] = 0
    max_count: Optional[int] = None
    required_types: Optional[List[str]] = None
    naming: Optional[PinNaming] = None

    @field_validator("min_count")
    @classmethod
    def validate_min_count(cls, v: Optional[int]) -> Optional[int]:
        """Validate minimum pin count if provided."""
        if v is not None and v < 0:
            raise ValueError("Minimum pin count cannot be negative")
        return v

    @field_validator("max_count")
    @classmethod
    def validate_max_count(cls, v: Optional[int], info: Any) -> Optional[int]:
        """Validate maximum pin count if provided."""
        if v is not None:
            min_count = info.data.get("min_count", 0)
            if v < min_count:
                raise ValueError("Maximum pin count cannot be less than minimum count")
        return v

    @field_validator("required_types")
    @classmethod
    def validate_required_types(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate required pin types if provided."""
        if v is not None:
            valid_types = {
                "input",
                "output",
                "bidirectional",
                "tri_state",
                "passive",
                "power",
                "unspecified",
            }
            invalid_types = [t for t in v if t.lower() not in valid_types]
            if invalid_types:
                raise ValueError(f"Invalid pin types: {', '.join(invalid_types)}")
            return [t.lower() for t in v]
        return v


class ComponentNaming(BaseModel):
    """Naming rules for a component."""

    pattern: Optional[str] = None
    description_pattern: Optional[str] = None

    @field_validator("pattern", "description_pattern")
    @classmethod
    def validate_patterns(cls, v: Optional[str]) -> Optional[str]:
        """Validate regex patterns if provided."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {e}")
        return v


class ComponentCategory(BaseModel):
    """Definition of a component category."""

    description: Optional[str] = ""
    prefix: Optional[str] = None
    naming: Optional[ComponentNaming] = None
    required_properties: Optional[Dict[str, PropertyDefinition]] = None
    pins: Optional[PinRequirements] = None
    required_layers: Optional[List[str]] = None
    required_pads: Optional[PinRequirements] = None

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v: Optional[str]) -> Optional[str]:
        """Validate component prefix if provided."""
        if v is not None and not re.match(r"^[A-Za-z0-9]+$", v):
            raise ValueError("Component prefix must contain only alphanumeric characters")
        return v

    @field_validator("required_layers")
    @classmethod
    def validate_layers(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate required layers if provided."""
        if v is not None:
            valid_layers = {
                "F.Cu",
                "B.Cu",
                "F.SilkS",
                "B.SilkS",
                "F.Mask",
                "B.Mask",
                "F.Paste",
                "B.Paste",
                "F.CrtYd",
                "B.CrtYd",
                "*.Cu",
            }
            invalid_layers = [l for l in v if l not in valid_layers]
            if invalid_layers:
                raise ValueError(f"Invalid layers: {', '.join(invalid_layers)}")
        return v


class ComponentType(BaseModel):
    """Definition of a component type (e.g., passive, active)."""

    description: Optional[str] = ""
    prefix: Optional[str] = None
    categories: Optional[Dict[str, ComponentCategory]] = Field(default_factory=dict)
    naming: Optional[ComponentNaming] = None
    required_properties: Optional[Dict[str, PropertyDefinition]] = None

    @field_validator("prefix")
    @classmethod
    def validate_prefix(cls, v: Optional[str]) -> Optional[str]:
        """Validate component type prefix if provided."""
        if v is not None and not re.match(r"^[A-Za-z0-9]+$", v):
            raise ValueError("Component type prefix must contain only alphanumeric characters")
        return v


class LibraryStructure(BaseModel):
    """Complete library structure definition."""

    version: str = "1.0"
    description: Optional[str] = ""
    library: LibraryInfo
    symbols: Optional[Dict[str, ComponentType]] = Field(default_factory=dict)
    footprints: Optional[Dict[str, ComponentType]] = Field(default_factory=dict)
    models_3d: Optional[Dict[str, ComponentType]] = Field(default_factory=dict)
    documentation: Optional[Dict[str, ComponentType]] = Field(default_factory=dict)

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        if not re.match(r"^\d+\.\d+$", v):
            raise ValueError("Version must be in format 'major.minor'")
        return v
