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