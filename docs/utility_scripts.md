# Utility Scripts

This document describes the utility scripts included in the KiCad Library Validator package.

## Library Structure Creator

The `create_library_structure.py` script creates a directory structure for a KiCad library based on a YAML configuration file.

### Usage

```bash
python -m kicad_lib_validator.utils.create_library_structure /path/to/structure.yaml
```

### YAML Structure Example

```yaml
version: "1.0"
description: "KiCad library for [Lab Name]"
library:
  prefix: "LabLib"
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
```

### Options

- `--dry-run`: Show what would be created without making changes
- `--verbose`: Enable verbose logging

## KiCad Table Updater

The `update_kicad_tables.py` script generates KiCad library tables (sym-lib-table and fp-lib-table) based on a YAML configuration file.

### Usage

```bash
python -m kicad_lib_validator.utils.update_kicad_tables /path/to/structure.yaml [--output-dir /path/to/output]
```

### Features

- Generates both symbol and footprint library tables
- Uses environment variable-style paths (e.g., `${MYLIB_DIR}`) for portability
- Preserves existing library entries
- Supports custom output directory

### Options

- `--dry-run`: Show what would be done without making changes
- `--verbose`: Enable verbose logging
- `--output-dir`: Specify a custom output directory for the tables (defaults to KiCad config directory)

### Example Output

Symbol library table:
```
(sym_lib_table
  (lib (name "LabLib_Passive_Capacitor_Murata_GRM")
    (type "KiCad")
    (uri "${LABLIB_DIR}/symbols/Passive/Capacitor/Murata/GRM/GRM188R71C104KA01.kicad_sym")
    (options "")
    (descr "Symbol library for LabLib_Passive_Capacitor_Murata_GRM")
  )
)
```

Footprint library table:
```
(fp_lib_table
  (lib (name "LabLib_Capacitor_SMD_Murata_GRM")
    (type "KiCad")
    (uri "${LABLIB_DIR}/footprints/Capacitor/SMD/Murata/GRM/GRM188R71C104KA01.pretty")
    (options "")
    (descr "Footprint library for LabLib_Capacitor_SMD_Murata_GRM")
  )
)
```

### Environment Variables

The script uses environment variables for library paths. For example, if your library prefix is "LabLib", you'll need to set:

```bash
# Windows
set LABLIB_DIR=C:\path\to\your\library

# Unix/Linux/MacOS
export LABLIB_DIR=/path/to/your/library
```

This makes the library tables portable across different systems and installations.

## Library Report Generator

The `generate_report.py` script generates a validation report for a KiCad library based on its structure definition.

### Usage

```bash
python -m kicad_lib_validator.utils.generate_report /path/to/library [--structure-file /path/to/structure.yaml] [--output-path /path/to/report.md]
```

### Features

- Generates a comprehensive markdown report of the library structure
- Validates library components against the structure definition
- Shows library information, directory structure, and component details
- Supports custom structure file and output path

### Options

- `--structure-file`: Path to the structure YAML file (defaults to library_dir/structure.yaml)
- `--output-path`: Path where to save the report (defaults to library_dir/library_report.md)
- `--verbose`: Show the generated report in the console

### Example Output

```markdown
# Library Structure Report

Generated: 2024-03-14 15:30:45

## Library Information
- **Name**: LabLib
- **Description**: Example library
- **Maintainer**: Lab Maintainer <maintainer@example.com>
- **License**: MIT
- **Website**: https://github.com/[org]/[repo]

## Directory Structure
### Symbols
Path: `symbols`
Subdirectories:
- `Passive/Capacitor/Murata/GRM`

### Footprints
Path: `footprints`
Subdirectories:
- `Capacitor/SMD/Murata/GRM`

## Symbols
### Symbol Files
- `symbols/Passive/Capacitor/Murata/GRM/GRM188R71C104KA01.kicad_sym`

## Footprints
### Footprint Files
- `footprints/Capacitor/SMD/Murata/GRM/GRM188R71C104KA01.pretty`