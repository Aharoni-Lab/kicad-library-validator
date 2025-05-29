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
library:
  prefix: "MyLib"
  directories:
    symbols: "symbols"
    footprints: "footprints"
    models: "3dmodels"
    docs: "docs"
  naming:
    symbols:
      include_categories: true
      category_separator: "_"
    footprints:
      include_categories: true
      category_separator: "_"
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
  (lib (name "MyLib_Actives_Ics")
    (type "KiCad")
    (uri "${MYLIB_DIR}/symbols/actives/ics/ics.kicad_sym")
    (options "")
    (descr "Symbol library for MyLib_Actives_Ics")
  )
)
```

Footprint library table:
```
(fp_lib_table
  (lib (name "MyLib_Smd_Capacitors")
    (type "KiCad")
    (uri "${MYLIB_DIR}/footprints/smd/capacitors.pretty")
    (options "")
    (descr "Footprint library for MyLib_Smd_Capacitors")
  )
)
```

### Environment Variables

The script uses environment variables for library paths. For example, if your library prefix is "MyLib", you'll need to set:

```bash
# Windows
set MYLIB_DIR=C:\path\to\your\library

# Unix/Linux/MacOS
export MYLIB_DIR=/path/to/your/library
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
- **Name**: MyLib
- **Description**: Example library
- **Maintainer**: John Doe <john@example.com>
- **License**: MIT
- **Website**: https://example.com/library

## Directory Structure
### Symbols
Path: `symbols`
Subdirectories:
- `actives`
- `passives`

### Footprints
Path: `footprints`
Subdirectories:
- `smd`

## Symbols
### Symbol Files
- `symbols/actives/ics/ics.kicad_sym`
- `symbols/passives/capacitors/capacitors.kicad_sym`

## Footprints
### Footprint Files
- `footprints/smd/capacitors/capacitors.pretty`
- `footprints/smd/resistors/resistors.pretty`
``` 