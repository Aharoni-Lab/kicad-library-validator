# Library Structure File Guide

The structure file is a YAML document that defines the rules and organization for your KiCad library. The validator uses this file to check naming conventions, required properties, directory layout, and more.

## Main Sections
- **library:** General info, directory paths, and naming conventions.
- **symbols:** Rules for symbol categories, naming, and required properties.
- **footprints:** Rules for footprint categories, naming, required layers, and properties.
- **models_3d:** Rules for 3D model categories and naming.
- **documentation:** (Optional) Rules for documentation files.

## Example
```yaml
library:
  prefix: "MyLib"
  directories:
    symbols: "symbols"
    footprints: "footprints"
    models_3d: "3dmodels"
    documentation: "docs"
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
  passives:
    categories:
      resistors:
        naming:
          pattern: "^R[0-9]+$"
        required_properties:
          Reference:
            type: "string"
            pattern: "^R[0-9]+$"
```

## Customization
- **Add or remove categories** as needed for your library.
- **Adjust patterns** to match your naming conventions.
- **Specify required and optional properties** for each component type.

See the test structure file in `tests/test_kicad_lib/test_library_structure.yaml` for a full example. 