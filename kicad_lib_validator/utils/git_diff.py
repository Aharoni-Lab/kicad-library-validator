"""
Git diff utilities for tracking library changes.
"""

import logging
import subprocess
from pathlib import Path
from typing import Dict, Optional


def get_changed_files(
    library_path: Path, compare_commit: str, log_level: int = logging.INFO
) -> Dict[str, str]:
    """
    Get files that have changed since a specific commit.

    Args:
        library_path: Path to the library root
        compare_commit: Git commit to compare against
        log_level: Logging level

    Returns:
        Dictionary mapping file paths to their status ('new', 'modified', or 'deleted')
    """
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    changed_files: Dict[str, str] = {}

    try:
        # Get list of changed files
        result = subprocess.run(
            ["git", "diff", "--name-status", compare_commit],
            cwd=library_path,
            capture_output=True,
            text=True,
            check=True,
        )

        # Parse output
        for line in result.stdout.splitlines():
            status, *file_path = line.split("\t")
            if file_path:
                file_str = file_path[-1]
                changed_files[file_str] = status

        logger.info(f"Found {len(changed_files)} changed files")

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get git diff: {e}")
        logger.error(f"Git error output: {e.stderr}")
        raise

    return changed_files
