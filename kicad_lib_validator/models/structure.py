from typing import Dict, List, Optional, Literal, Any
import re
from pydantic import BaseModel, Field, HttpUrl, field_validator


class LibraryDirectories(BaseModel):
    """Directory structure configuration."""
    symbols: str = "symbols"
    footprints: str = "footprints"
    models_3d: str = "3dmodels"
    documentation: str = "docs"

    @field_validator('symbols', 'footprints', 'models_3d', 'documentation')
    @classmethod
    def validate_directory_name(cls, v: str) -> str:
        """Validate directory names are valid."""
        if not re.match(r'^[a-zA-Z0-9_-]+$', v):
            raise ValueError(f"Directory name '{v}' contains invalid characters")
        return v


class NamingConvention(BaseModel):
    """Naming convention configuration."""
    prefix: bool = True
    separator: str = "_"
    case: Literal["upper", "lower", "mixed"] = "upper"
    include_categories: bool = False
    category_separator: str = "_"

    @field_validator('separator')
    @classmethod
    def validate_separator(cls, v: str) -> str:
        """Validate separator is a single character."""
        if len(v) != 1:
            raise ValueError("Separator must be a single character")
        return v


class LibraryNaming(BaseModel):
    """Naming conventions for different library elements."""
    symbols: NamingConvention
    footprints: NamingConvention
    models_3d: NamingConvention


class LibraryInfo(BaseModel):
    """Library metadata and configuration."""
    prefix: str
    description: str
    maintainer: str
    license: str
    website: Optional[HttpUrl] = None
    repository: Optional[HttpUrl] = None
    directories: LibraryDirectories = Field(default_factory=LibraryDirectories)
    naming: LibraryNaming

    @field_validator('prefix')
    @classmethod
    def validate_prefix(cls, v: str) -> str:
        """Validate library prefix."""
        if not re.match(r'^[A-Za-z0-9]+$', v):
            raise ValueError("Library prefix must contain only alphanumeric characters")
        return v

    @field_validator('maintainer')
    @classmethod
    def validate_maintainer(cls, v: str) -> str:
        """Validate maintainer email format."""
        if not re.match(r'^[^<]+ <[^>]+>$', v):
            raise ValueError("Maintainer must be in format 'Name <email@example.com>'")
        return v


class PropertyDefinition(BaseModel):
    """Definition of a property in a component."""
    type: str
    pattern: Optional[str] = None
    optional: bool = False
    description: Optional[str] = None

    @field_validator('type')
    @classmethod
    def validate_type(cls, v: str) -> str:
        """Validate property type."""
        valid_types = {'string', 'number', 'boolean', 'url', 'email'}
        if v.lower() not in valid_types:
            raise ValueError(f"Property type must be one of: {', '.join(valid_types)}")
        return v.lower()

    @field_validator('pattern')
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
    pattern: str
    description_pattern: str

    @field_validator('pattern', 'description_pattern')
    @classmethod
    def validate_patterns(cls, v: str) -> str:
        """Validate regex patterns."""
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v


class PinRequirements(BaseModel):
    """Requirements for pins in a component."""
    min_count: int
    max_count: Optional[int] = None
    required_types: List[str]
    naming: Optional[PinNaming] = None

    @field_validator('min_count')
    @classmethod
    def validate_min_count(cls, v: int) -> int:
        """Validate minimum pin count."""
        if v < 0:
            raise ValueError("Minimum pin count cannot be negative")
        return v

    @field_validator('max_count')
    @classmethod
    def validate_max_count(cls, v: Optional[int], info: Any) -> Optional[int]:
        """Validate maximum pin count."""
        if v is not None:
            min_count = info.data.get('min_count', 0)
            if v < min_count:
                raise ValueError("Maximum pin count cannot be less than minimum count")
        return v

    @field_validator('required_types')
    @classmethod
    def validate_required_types(cls, v: List[str]) -> List[str]:
        """Validate required pin types."""
        valid_types = {'input', 'output', 'bidirectional', 'tri_state', 'passive', 'power', 'unspecified'}
        invalid_types = [t for t in v if t.lower() not in valid_types]
        if invalid_types:
            raise ValueError(f"Invalid pin types: {', '.join(invalid_types)}")
        return [t.lower() for t in v]


class ComponentNaming(BaseModel):
    """Naming rules for a component."""
    pattern: str
    description_pattern: str

    @field_validator('pattern', 'description_pattern')
    @classmethod
    def validate_patterns(cls, v: str) -> str:
        """Validate regex patterns."""
        try:
            re.compile(v)
        except re.error as e:
            raise ValueError(f"Invalid regex pattern: {e}")
        return v


class ComponentCategory(BaseModel):
    """Definition of a component category."""
    description: str
    prefix: Optional[str] = None
    naming: ComponentNaming
    required_properties: Dict[str, PropertyDefinition]
    pins: Optional[PinRequirements] = None
    required_layers: Optional[List[str]] = None
    required_pads: Optional[PinRequirements] = None

    @field_validator('prefix')
    @classmethod
    def validate_prefix(cls, v: Optional[str]) -> Optional[str]:
        """Validate component prefix."""
        if v is not None and not re.match(r'^[A-Za-z0-9]+$', v):
            raise ValueError("Component prefix must contain only alphanumeric characters")
        return v

    @field_validator('required_layers')
    @classmethod
    def validate_layers(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate required layers."""
        if v is not None:
            valid_layers = {
                'F.Cu', 'B.Cu', 'F.SilkS', 'B.SilkS', 'F.Mask', 'B.Mask',
                'F.Paste', 'B.Paste', 'F.CrtYd', 'B.CrtYd', '*.Cu'
            }
            invalid_layers = [l for l in v if l not in valid_layers]
            if invalid_layers:
                raise ValueError(f"Invalid layers: {', '.join(invalid_layers)}")
        return v


class ComponentType(BaseModel):
    """Definition of a component type (e.g., passive, active)."""
    description: str
    prefix: Optional[str] = None
    categories: Dict[str, ComponentCategory]

    @field_validator('prefix')
    @classmethod
    def validate_prefix(cls, v: Optional[str]) -> Optional[str]:
        """Validate component type prefix."""
        if v is not None and not re.match(r'^[A-Za-z0-9]+$', v):
            raise ValueError("Component type prefix must contain only alphanumeric characters")
        return v


class LibraryStructure(BaseModel):
    """Complete library structure definition."""
    version: str
    description: str
    library: LibraryInfo
    symbols: Dict[str, ComponentType]
    footprints: Dict[str, ComponentType]

    @field_validator('version')
    @classmethod
    def validate_version(cls, v: str) -> str:
        """Validate version format."""
        if not re.match(r'^\d+\.\d+(\.\d+)?$', v):
            raise ValueError("Version must be in format 'X.Y' or 'X.Y.Z'")
        return v

    def validate_component_name(self, name: str, component_type: str, category: str) -> bool:
        """
        Validate that the category exists for the given component type and that the component name matches the category's naming pattern.
        Supports dot-separated paths like 'passives.resistors'.
        """
        if component_type not in ['symbols', 'footprints']:
            raise ValueError("Component type must be 'symbols' or 'footprints'")
        components = getattr(self, component_type)
        path = category.split(".")
        if len(path) == 2:
            type_key, cat_key = path
            type_def = components.get(type_key)
            if type_def and cat_key in type_def.categories:
                cat_def = type_def.categories[cat_key]
                return bool(re.match(cat_def.naming.pattern, name))
        return False

    def validate_property(self, name: str, value: str, component_type: str, category: str) -> bool:
        """
        Validate a property value against its definition.
        If the property is in required_properties, it must exist in the test input to pass.
        If the property is not in required_properties, it is allowed to pass.
        """
        if component_type not in ['symbols', 'footprints']:
            raise ValueError("Component type must be 'symbols' or 'footprints'")
        components = getattr(self, component_type)
        path = category.split(".")
        if len(path) == 2:
            type_key, cat_key = path
            type_def = components.get(type_key)
            if type_def and cat_key in type_def.categories:
                cat_def = type_def.categories[cat_key]
                if name in cat_def.required_properties:
                    prop_def = cat_def.required_properties[name]
                    if prop_def.pattern and not re.match(prop_def.pattern, value):
                        return False
                return True
        return False 