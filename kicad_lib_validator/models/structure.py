import re
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field, HttpUrl, field_validator


class LibraryDirectories(BaseModel):
    """Directory structure configuration."""

    symbols: str = "symbols"
    footprints: str = "footprints"
    models_3d: Optional[str] = "3dmodels"
    documentation: Optional[str] = "docs"
    tables: Optional[str] = "tables"  # Directory for library-specific table files

    @field_validator("symbols", "footprints", "models_3d", "documentation", "tables")
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

    symbols: Optional[NamingConvention] = Field(default_factory=lambda: NamingConvention())
    footprints: Optional[NamingConvention] = Field(default_factory=lambda: NamingConvention())
    models_3d: Optional[NamingConvention] = Field(default_factory=lambda: NamingConvention())


class LibraryInfo(BaseModel):
    """Library metadata and configuration."""

    prefix: str
    env_prefix: Optional[str] = None  # Environment variable prefix (no dots allowed)
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
        if not re.match(r"^[A-Za-z0-9.]+$", v):
            raise ValueError("Library prefix must contain only alphanumeric characters and periods")
        return v

    @field_validator("env_prefix")
    @classmethod
    def validate_env_prefix(cls, v: Optional[str], info: Any) -> Optional[str]:
        """Validate environment variable prefix."""
        if v is None:
            # If not provided, use the display prefix but remove dots
            prefix = info.data.get("prefix", "")
            if isinstance(prefix, str):
                return prefix.replace(".", "")
            return ""
        if not re.match(r"^[A-Za-z0-9]+$", v):
            raise ValueError(
                "Environment prefix must contain only alphanumeric characters (no dots)"
            )
        return v

    @field_validator("maintainer")
    @classmethod
    def validate_maintainer(cls, v: Optional[str]) -> Optional[str]:
        """Validate maintainer email format if provided."""
        if v is not None and not re.match(r"^[^<]+ <[^>]+>$", v):
            raise ValueError("Maintainer must be in format 'Name <email@example.com>'")
        return v


class PropertyDefinition(BaseModel):
    """Definition of a property with its requirements."""

    description: Optional[str] = None
    required: bool = True
    pattern: Optional[str] = None
    ki_field_name: Optional[str] = (
        None  # Maps to KiCad's internal field name (e.g., "ki_keywords" for "Keywords")
    )

    @field_validator("pattern")
    @classmethod
    def validate_pattern(cls, v: Optional[str]) -> Optional[str]:
        """Validate pattern if provided."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid pattern: {e}")
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


class ComponentEntry(BaseModel):
    """Definition of a component entry with its rules and requirements."""

    naming: Optional[ComponentNaming] = None
    required_properties: Optional[Dict[str, PropertyDefinition]] = None
    pins: Optional[PinRequirements] = None
    required_layers: Optional[List[str]] = None
    required_pads: Optional[PinRequirements] = None
    reference_prefix: Optional[str] = (
        None  # Expected prefix for Reference field (e.g., "R" for resistors)
    )
    reference_pattern: Optional[str] = (
        None  # Expected pattern for Reference field (e.g., "REF**" for footprints)
    )

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

    @field_validator("reference_prefix")
    @classmethod
    def validate_reference_prefix(cls, v: Optional[str]) -> Optional[str]:
        """Validate reference prefix if provided."""
        if v is not None:
            if not re.match(r"^[A-Za-z0-9]+$", v):
                raise ValueError("Reference prefix must contain only alphanumeric characters")
        return v

    @field_validator("reference_pattern")
    @classmethod
    def validate_reference_pattern(cls, v: Optional[str]) -> Optional[str]:
        """Validate reference pattern if provided."""
        if v is not None:
            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"Invalid reference pattern: {e}")
        return v


class ComponentGroup(BaseModel):
    """A group of components that can contain either entries or subgroups."""

    entries: Optional[Dict[str, ComponentEntry]] = None
    subgroups: Optional[Dict[str, "ComponentGroup"]] = None

    @field_validator("entries", "subgroups")
    @classmethod
    def validate_not_both_empty(cls, v: Optional[Dict], info: Any) -> Optional[Dict]:
        """Validate that at least one of entries or subgroups is provided."""
        if (
            v is None
            and info.data.get("subgroups" if info.field_name == "entries" else "entries") is None
        ):
            raise ValueError("Component group must have either entries or subgroups")
        return v


class LibraryStructure(BaseModel):
    """Complete library structure definition."""

    version: str = "1.0"
    description: Optional[str] = ""
    library: LibraryInfo
    symbols: Optional[Dict[str, ComponentGroup]] = Field(default_factory=lambda: {})
    footprints: Optional[Dict[str, ComponentGroup]] = Field(default_factory=lambda: {})
    models_3d: Optional[Dict[str, ComponentGroup]] = Field(default_factory=lambda: {})
    documentation: Optional[Dict[str, ComponentGroup]] = Field(default_factory=lambda: {})

    @field_validator("version")
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        if not re.match(r"^\d+\.\d+$", v):
            raise ValueError("Version must be in format 'major.minor'")
        return v
