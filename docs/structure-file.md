# Library Structure File Guide

The structure file is a YAML document that defines the rules and organization for your KiCad library. The validator uses this file to check naming conventions, required properties, directory layout, and more.

## Basic Structure

```yaml
version: "1.0"
description: "KiCad library for [Lab Name]"

library:
  prefix: "LabLib"
  description: "KiCad library for [Lab Name]"
  maintainer: "Lab Maintainer <maintainer@example.com>"
  license: "MIT"
  website: "https://github.com/[org]/[repo]"
  repository: "https://github.com/[org]/[repo].git"
  directories:
    symbols: "symbols"
    footprints: "footprints"
    models_3d: "3dmodels"
    documentation: "docs"
    tables: "tables"
  naming:
    symbols:
      prefix: true
      separator: "_"
      case: "upper"
      include_categories: true
      category_separator: "_"
    footprints:
      prefix: true
      separator: "_"
      case: "upper"
      include_categories: true
      category_separator: "_"
    models_3d:
      prefix: false
      separator: "_"
      case: "lower"
      include_categories: false
      category_separator: "_"
```

## Component Organization

The structure file uses a hierarchical organization with `subgroups` and `entries`:

### Subgroups
- Used to create nested categories (e.g., manufacturer, series, type)
- Can contain other subgroups or entries
- Must have a description
- Example:
```yaml
symbols:
  passives:  # Top-level group
    description: "Passive components"
    subgroups:
      resistors:  # Nested group
        description: "Resistors"
        subgroups:
          smd:  # Further nesting
            description: "SMD Resistors"
```

### Entries
- Define the actual component rules and requirements
- Must be under a subgroup
- Can contain naming rules, required properties, and other constraints
- Example:
```yaml
symbols:
  passives:
    subgroups:
      resistors:
        entries:
          standard:
            description: "Standard resistors"
            naming:
              pattern: "^R[0-9]+$"
              description_pattern: "^[0-9.]+[kM]?[Ω]? Resistor$"
```

## Available Rules and Constraints

### Naming Rules
```yaml
naming:
  pattern: "^[A-Z0-9-]+$"  # Regex pattern for component names
  description_pattern: "^[A-Z0-9-]+ Component$"  # Regex pattern for descriptions
```

### Property Rules
```yaml
required_properties:
  Reference:
    type: "string"  # string, number, boolean, url, email
    pattern: "^R[0-9]+$"  # Optional regex pattern
    description: "Component reference designator"
  Validated:
    type: "string"
    pattern: "^(Yes|No)$"  # For boolean-like properties
    description: "Whether the component has been validated"
```

### Pin Rules (for Symbols)
```yaml
pins:
  min_count: 2
  max_count: 2
  required_types:
    - "passive"
    - "power"
    - "input"
    - "output"
  naming:
    pattern: "^[12]$"
    description_pattern: "^Pin [12]$"
```

### Layer Rules (for Footprints)
```yaml
required_layers:
  - "F.Cu"
  - "B.Cu"
  - "F.SilkS"
  - "B.SilkS"
  - "F.Mask"
  - "B.Mask"
  - "F.Paste"
  - "B.Paste"
  - "F.CrtYd"
  - "B.CrtYd"
  - "*.Cu"
```

### Pad Rules (for Footprints)
```yaml
required_pads:
  min_count: 2
  max_count: 2
  required_types:
    - "smd"
    - "thru_hole"
  naming:
    pattern: "^[12]$"
    description_pattern: "^Pad [12]$"
```

## Property Types and Patterns

### String Properties
- Use regex patterns to validate format
- Example: `pattern: "^[A-Z0-9-]+$"`

### Boolean Properties
- Use string type with specific pattern
- Example: `pattern: "^(Yes|No)$"`

### URL Properties
- Use string type with URL pattern
- Example: `pattern: "^https?://.+$"`

### Number Properties
- Use string type with number pattern
- Example: `pattern: "^[0-9.]+[kM]?[Ω]?$"`

## Best Practices

1. **Organization**
   - Use meaningful group names
   - Keep hierarchy depth reasonable (3-4 levels max)
   - Use consistent naming across groups

2. **Validation Rules**
   - Make patterns specific but not overly restrictive
   - Include clear descriptions for all properties
   - Use consistent patterns across similar components

3. **Documentation**
   - Add descriptions to all groups and entries
   - Document any special requirements or exceptions
   - Keep property descriptions clear and concise

4. **Maintenance**
   - Review and update patterns as needed
   - Keep property requirements up to date
   - Document any changes to the structure

See the template in `templates/library/structure.yaml` for a full example. 