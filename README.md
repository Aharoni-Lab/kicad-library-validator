# KiCad Library Validator

A Python tool for validating KiCad component libraries, ensuring symbols, footprints, 3D models, and documentation conform to a defined structure and rules.

## Features

- Validates KiCad symbol, footprint, and 3D model libraries against a YAML structure definition
- Supports deeply nested component organization with subgroups and entries
- Enforces naming conventions, required properties, and directory structure
- Validates component-specific requirements (pins, layers, pads)
- Generates detailed validation and test reports
- Creates library directory structures from YAML configuration
- Generates KiCad library tables (sym-lib-table and fp-lib-table)
- Python 3.10+ supported

## Installation

```bash
pip install kicad-library-validator
```

## Usage

### Library Validation

Validate a library:
```bash
kicad-library-validator --library-path /path/to/your/library --structure-file /path/to/structure.yaml
```

Or use the Python API:
```python
from kicad_lib_validator.validator import KiCadLibraryValidator

validator = KiCadLibraryValidator(library_path, structure_file)
result = validator.validate()
print(result.errors)
```

### Utility Scripts

The package includes utility scripts for common tasks:

1. **Library Structure Creator**: Creates a directory structure for a KiCad library based on a YAML configuration
   ```bash
   python -m kicad_lib_validator.utils.create_library_structure /path/to/structure.yaml
   ```

2. **KiCad Table Updater**: Generates KiCad library tables (sym-lib-table and fp-lib-table)
   ```bash
   python -m kicad_lib_validator.utils.update_kicad_tables /path/to/structure.yaml [--output-dir /path/to/output]
   ```

3. **Library Report Generator**: Generates a comprehensive markdown report of your library structure
   ```bash
   python -m kicad_lib_validator.utils.generate_report /path/to/library [--structure-file /path/to/structure.yaml]
   ```

For detailed documentation on these utilities, see [Utility Scripts](docs/utility_scripts.md).

## Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kicad-library-validator.git
   cd kicad-library-validator
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Unix or MacOS:
   source .venv/bin/activate
   ```
3. Install development dependencies:
   ```bash
   pip install -e ".[dev,test]"
   ```
4. Run tests and type checks:
   ```bash
   python -m pytest
   mypy kicad_lib_validator --exclude site-packages
   ```

## Documentation

See the [docs/](docs/) directory for detailed documentation:
- [Overview](docs/overview.md) - High-level overview of the validator
- [Structure File Guide](docs/structure-file.md) - Detailed guide to the YAML structure definition
- [Utility Scripts](docs/utility_scripts.md) - Documentation for utility scripts
- [Advanced Usage](docs/advanced-usage.md) - Advanced usage patterns and tips

## License

This project is licensed under the MIT License - see the LICENSE file for details. 