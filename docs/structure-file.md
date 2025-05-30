# Library Structure File Guide

The structure file is a YAML document that defines the rules and organization for your KiCad library. The validator uses this file to check naming conventions, required properties, directory layout, and more.

## Main Sections
- **library:** General info, directory paths, and naming conventions.
- **symbols:** Deeply nested rules for symbol categories, subgroups, entries, naming, and required properties.
- **footprints:** Deeply nested rules for footprint categories, subgroups, entries, naming, required layers, pads, and properties.
- **models_3d:** Deeply nested rules for 3D model categories, subgroups, entries, and naming.
- **documentation:** Top-level categories (e.g., passives, actives), each with their own documentation categories and required properties.

## Example
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

symbols:
  Passive:
    subgroups:
      Capacitor:
        subgroups:
          Murata:
            subgroups:
              GRM:
                entries:
                  GRM188R71C104KA01:
                    naming:
                      pattern: "^[A-Z0-9-]+$"
                      description_pattern: "^[A-Z0-9-]+ Capacitor$"
                    required_properties:
                      Reference:
                        type: "string"
                        pattern: "^C[0-9]+$"
                        description: "Component reference designator"
                      Value:
                        type: "string"
                        pattern: "^[0-9.]+[pPnNuUmMkK]?F$"
                        description: "Capacitance value"
                      Voltage:
                        type: "string"
                        pattern: "^[0-9.]+V$"
                        description: "Voltage rating"
                      Validated:
                        type: "boolean"
                        description: "Whether the component has been validated"
                    pins:
                      min_count: 2
                      max_count: 2
                      required_types:
                        - "passive"

footprints:
  Capacitor:
    subgroups:
      SMD:
        subgroups:
          Murata:
            subgroups:
              GRM:
                entries:
                  GRM188R71C104KA01:
                    naming:
                      pattern: "^[A-Z0-9-]+$"
                      description_pattern: "^[A-Z0-9-]+ Capacitor$"
                    required_layers:
                      - "F.Cu"
                      - "B.Cu"
                      - "F.SilkS"
                    required_pads:
                      min_count: 2
                      required_types:
                        - "smd"
                      naming:
                        pattern: "^[12]$"
                        description_pattern: "^Pad [12]$"
                    required_properties:
                      Reference:
                        type: "string"
                        pattern: "^C[0-9]+$"
                        description: "Component reference designator"
                      Validated:
                        type: "boolean"
                        description: "Whether the component has been validated"

models_3d:
  Capacitor:
    subgroups:
      SMD:
        subgroups:
          Murata:
            subgroups:
              GRM:
                entries:
                  GRM188R71C104KA01:
                    naming:
                      pattern: "^[A-Z0-9-]+$"
                      description_pattern: "^[A-Z0-9-]+ Capacitor$"
                    required_properties:
                      Description:
                        type: "string"
                        pattern: "^[A-Z0-9-]+ Capacitor$"
                        description: "Component description"
                      Validated:
                        type: "boolean"
                        description: "Whether the component has been validated"

documentation:
  passives:
    description: "Passive components"
    categories:
      datasheets:
        description: "Component datasheets"
        required_properties:
          title:
            type: "string"
          url:
            type: "string"
            pattern: "^https?://.+$"

## Understanding Subgroups and Entries
- **subgroups:** Used to create nested categories (e.g., manufacturer, series, type).
- **entries:** The actual component definitions, each with its own naming and property rules.
- You can nest as many levels of `subgroups` as needed for your organization.
- Each `entry` can define its own `naming`, `required_properties`, and other requirements (like `pins` for symbols, `required_layers` for footprints).

## Customization
- **Add or remove subgroups/entries** as needed for your library.
- **Adjust patterns** to match your naming conventions.
- **Specify required and optional properties** for each component type.
- **Use the `documentation` section** to define rules for datasheets and other docs, organized by top-level categories.

See the template in `templates/library/structure.yaml` for a full example. 