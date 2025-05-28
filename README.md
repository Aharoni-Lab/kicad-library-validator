# KiCad Library Validator

A Python package for validating KiCad component libraries. This tool ensures the integrity and correctness of KiCad symbols, footprints, and 3D models.

## Features

- Validates KiCad symbol libraries.
- Validates KiCad footprint libraries.
- Validates 3D models and datasheets.
- Generates validation reports.

## Installation

```bash
pip install kicad-library-validator
```

## Usage

```bash
kicad-library-validator --library-path /path/to/your/library
```

## Development

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kicad-library-validator.git
   cd kicad-library-validator
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # On Windows
   source .venv/bin/activate  # On Unix or MacOS
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Run tests:
   ```bash
   python scripts/run_tests.py
   ```

## License

This project is licensed under the MIT License - see the LICENSE file for details. 