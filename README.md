# KiCad Library Validator

A Python tool for validating KiCad component libraries, ensuring symbols, footprints, 3D models, and documentation conform to a defined structure and rules.

## Features

- Validates KiCad symbol, footprint, and 3D model libraries against a YAML structure definition
- Checks naming conventions, required properties, and directory structure
- Supports custom validation rules via a structure file
- Generates detailed validation and test reports
- Python 3.10+ supported

## Installation

```bash
pip install kicad-library-validator
```

## Usage

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

See the [docs/](docs/) directory for detailed documentation, structure file examples, and advanced usage.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 