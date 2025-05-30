#!/usr/bin/env python3
"""Script to run tests with various tools."""

import subprocess
import sys
from pathlib import Path
from typing import List


def run_command(command: List[str]) -> bool:
    """Run a command and return True if successful."""
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command {' '.join(command)}:")
        print(e.stderr)
        return False


def main():
    """Run tests with various tools."""
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    if not (project_root / "pyproject.toml").exists():
        print("Error: Must run from project root directory")
        sys.exit(1)

    # Determine Python path
    if sys.platform == "win32":
        python_path = project_root / ".venv" / "Scripts" / "python"
    else:
        python_path = project_root / ".venv" / "bin" / "python"

    # Run tests
    print("Running tests...")
    if not run_command([str(python_path), "-m", "pytest"]):
        sys.exit(1)

    # Run type checking
    print("\nRunning type checking...")
    if not run_command([str(python_path), "-m", "mypy", "kicad_lib_validator"]):
        sys.exit(1)

    # Run linting
    print("\nRunning linting...")
    if not run_command([str(python_path), "-m", "ruff", "check", "kicad_lib_validator"]):
        sys.exit(1)

    print("\nAll checks passed!")


if __name__ == "__main__":
    main() 