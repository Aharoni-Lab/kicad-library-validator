"""
Git diff utilities for tracking library changes.
"""
from pathlib import Path
from typing import Dict, Optional
import subprocess
import logging


def get_changed_files(
    library_path: Path,
    compare_commit: str,
    log_level: int = logging.INFO
) -> Dict[Path, str]:
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
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    changed_files = {}
    
    try:
        # Get list of changed files
        result = subprocess.run(
            ['git', 'diff', '--name-status', compare_commit],
            cwd=library_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse output
        for line in result.stdout.splitlines():
            status, file_path = line.split(maxsplit=1)
            file_path = library_path / file_path
            
            # Map git status to our status
            if status == 'A':
                changed_files[file_path] = 'new'
            elif status == 'M':
                changed_files[file_path] = 'modified'
            elif status == 'D':
                changed_files[file_path] = 'deleted'
            elif status == 'R':
                # Renamed files have format: R100 old_path new_path
                _, old_path, new_path = line.split(maxsplit=2)
                changed_files[library_path / new_path] = 'modified'
                changed_files[library_path / old_path] = 'deleted'
        
        logger.info(f"Found {len(changed_files)} changed files")
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to get git diff: {e}")
        logger.error(f"Git error output: {e.stderr}")
        raise
    
    return changed_files 