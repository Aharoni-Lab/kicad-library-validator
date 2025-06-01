#!/usr/bin/env python3
"""Script to set up the development environment."""

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


def main() -> None:
    """Set up the development environment."""
    # Ensure we're in the project root
    project_root = Path(__file__).parent.parent
    if not (project_root / "pyproject.toml").exists():
        print("Error: Must run from project root directory")
        sys.exit(1)

    # Create virtual environment
    print("Creating virtual environment...")
    if not run_command([sys.executable, "-m", "venv", ".venv"]):
        sys.exit(1)

    # Determine pip path
    if sys.platform == "win32":
        pip_path = project_root / ".venv" / "Scripts" / "pip"
    else:
        pip_path = project_root / ".venv" / "bin" / "pip"

    # Upgrade pip
    print("Upgrading pip...")
    if not run_command([str(pip_path), "install", "--upgrade", "pip"]):
        sys.exit(1)

    # Install development dependencies
    print("Installing development dependencies...")
    if not run_command([str(pip_path), "install", "-e", ".[dev]"]):
        sys.exit(1)

    print("\nDevelopment environment setup complete!")
    print("\nTo activate the virtual environment:")
    if sys.platform == "win32":
        print("    .venv\\Scripts\\activate")
    else:
        print("    source .venv/bin/activate")


if __name__ == "__main__":
    main() 