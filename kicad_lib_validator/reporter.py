"""
Library structure reporter for generating markdown reports.
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from kicad_lib_validator.models import Documentation, Footprint, KiCadLibrary, Model3D, Symbol
from kicad_lib_validator.parser.library_parser import (
    _find_documentation,
    _find_footprints,
    _find_models_3d,
    _find_symbols,
)
from kicad_lib_validator.validators.document_validator import validate_documentation
from kicad_lib_validator.validators.footprint_validator import validate_footprint
from kicad_lib_validator.validators.model3d_validator import validate_model3d
from kicad_lib_validator.validators.symbol_validator import validate_symbol

from .models.structure import LibraryStructure
from .utils.git_diff import get_changed_files


@dataclass
class FileStatus:
    """Status of a file in the library."""

    path: Path
    status: str  # 'new', 'modified', 'deleted', or 'unchanged'
    old_path: Optional[Path] = None  # For renamed files


@dataclass
class Issue:
    """Represents a validation issue."""

    type: str
    message: str
    severity: str  # 'error', 'warning', or 'success'


class LibraryReporter:
    """Generates markdown reports of the library structure."""

    def __init__(
        self, library_path: Path, structure: LibraryStructure, log_level: int = logging.INFO
    ):
        """
        Initialize the reporter.

        Args:
            library_path: Path to the library root
            structure: Parsed library structure
            log_level: Logging level
        """
        self.library_path = library_path
        self.structure = structure
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter("%(levelname)s: %(message)s")
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)

    def generate_report(
        self, output_path: Optional[Path] = None, compare_commit: Optional[str] = None
    ) -> str:
        """
        Generate a markdown report of the library structure.

        Args:
            output_path: Optional path to save the report
            compare_commit: Optional git commit to compare against

        Returns:
            The generated markdown report
        """
        self.logger.info("Generating library structure report")

        # Get changed files if comparing with a commit
        changed_files: Dict[str, FileStatus] = {}
        if compare_commit:
            changed_files = self._get_changed_files(compare_commit)

        # Generate report sections
        sections = [
            self._generate_header(),
            self._generate_directory_structure(changed_files),
            self._generate_symbols_section(changed_files),
            self._generate_footprints_section(changed_files),
            self._generate_3d_models_section(changed_files),
            self._generate_documentation_section(changed_files),
        ]

        # Combine sections
        report = "\n\n".join(sections)

        # Save report if output path is provided
        if output_path:
            output_path.write_text(report, encoding="utf-8")
            self.logger.info(f"Report saved to {output_path}")

        return report

    def generate_library_report(self, library: KiCadLibrary, output_path: Path) -> None:
        """
        Generate a markdown report with details about the parsed library.

        Args:
            library: The parsed KiCadLibrary instance
            output_path: Path to save the report to
        """
        self.logger.info("Generating detailed library report...")

        report = ["# KiCad Library Report\n"]

        # Symbols
        report.append("## Symbols\n")
        if library.symbol_libraries:
            for lib_name, symbol_lib in sorted(library.symbol_libraries.items()):
                report.append(f"### {lib_name}")
                if symbol_lib.symbols:
                    for symbol in symbol_lib.symbols:
                        report.append(f"- **{symbol.name}**")
                        if symbol.properties:
                            report.append("  - Properties:")
                            for key, value in symbol.properties.items():
                                report.append(f"    - {key}: {value}")
                else:
                    report.append("No symbols found in this library.\n")
        else:
            report.append("No symbol libraries found.\n")

        # Footprints
        report.append("\n## Footprints\n")
        if library.footprint_libraries:
            for lib_name, footprint_lib in sorted(library.footprint_libraries.items()):
                report.append(f"### {lib_name}")
                if footprint_lib.footprints:
                    for footprint in footprint_lib.footprints:
                        report.append(f"- **{footprint.name}**")
                        if footprint.properties:
                            report.append("  - Properties:")
                            for key, value in footprint.properties.items():
                                report.append(f"    - {key}: {value}")
                else:
                    report.append("No footprints found in this library.\n")
        else:
            report.append("No footprint libraries found.\n")

        # 3D Models
        report.append("\n## 3D Models\n")
        if library.model3d_libraries:
            for lib_name, model_lib in sorted(library.model3d_libraries.items()):
                report.append(f"### {lib_name}")
                if model_lib.models:
                    for model in model_lib.models:
                        report.append(f"- **{model.name}**")
                        if getattr(model, "properties", None):
                            report.append("  - Properties:")
                            for key, value in model.properties.items():
                                report.append(f"    - {key}: {value}")
                else:
                    report.append("No 3D models found in this library.\n")
        else:
            report.append("No 3D model libraries found.\n")

        # Documentation
        report.append("\n## Documentation\n")
        if library.documentation_libraries:
            for lib_name, doc_lib in sorted(library.documentation_libraries.items()):
                report.append(f"### {lib_name}")
                if doc_lib.docs:
                    for doc in doc_lib.docs:
                        report.append(f"- **{doc.name}**")
                        if getattr(doc, "properties", None):
                            report.append("  - Properties:")
                            for key, value in doc.properties.items():
                                report.append(f"    - {key}: {value}")
                else:
                    report.append("No documentation found in this library.\n")
        else:
            report.append("No documentation libraries found.\n")

        # Write report
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        self.logger.info(f"Detailed library report saved to {output_path}")

    def _generate_header(self) -> str:
        """Generate the report header."""
        return f"""# Library Structure Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Library Information
- **Name**: {self.structure.library.prefix}
- **Description**: {self.structure.library.description}
- **Maintainer**: {self.structure.library.maintainer}
- **License**: {self.structure.library.license}
- **Website**: {self.structure.library.website}
- **Repository**: {self.structure.library.repository}
"""

    def _generate_directory_structure(self, changed_files: Dict[str, FileStatus]) -> str:
        """Generate the directory structure section."""
        sections = ["## Directory Structure"]

        # Get directory structure from model
        if not self.structure.library.directories:
            sections.append("No directory information available.")
            return "\n".join(sections)
        directories = self.structure.library.directories.model_dump()

        for dir_type, dir_name in directories.items():
            dir_path = self.library_path / dir_name
            if dir_path.exists():
                sections.append(f"### {dir_type.title()}")
                sections.append(f"Path: `{dir_name}`")

                # List subdirectories
                if dir_path.is_dir():
                    subdirs = [d for d in dir_path.iterdir() if d.is_dir()]
                    if subdirs:
                        sections.append("\nSubdirectories:")
                        for subdir in sorted(subdirs):
                            sections.append(f"- `{subdir.name}`")
                sections.append("")

        return "\n".join(sections)

    def _format_validation_results(self, results: Dict[str, List[str]]) -> str:
        """Format validation results as markdown."""
        lines = []
        if results.get("successes"):
            lines.append("  - ✅ **Passing Validations:**")
            for msg in results["successes"]:
                lines.append(f"    - {msg}")
        if results.get("warnings"):
            lines.append("  - ⚠️ **Warnings:**")
            for msg in results["warnings"]:
                lines.append(f"    - {msg}")
        if results.get("errors"):
            lines.append("  - ❌ **Errors:**")
            for msg in results["errors"]:
                lines.append(f"    - {msg}")
        return "\n".join(lines)

    def _group_by_category(self, items: List[Any]) -> Dict[str, Any]:
        """Group items by their full category path."""
        grouped: Dict[str, Any] = {}
        for item in items:
            # Get categories list, defaulting to ["Uncategorized"] if None
            categories = item.categories or ["Uncategorized"]

            # Start at the root of our grouped dict
            current = grouped

            # Traverse the category path
            for i, category in enumerate(categories):
                if i == len(categories) - 1:
                    # Last category - store the item
                    if category not in current:
                        current[category] = []
                    current[category].append(item)
                else:
                    # Not the last category - create/use subgroup
                    if category not in current:
                        current[category] = {}
                    current = current[category]

        return grouped

    def _format_category_section(self, items: Dict[str, Any], indent: int = 0) -> List[str]:
        """Format a category section with proper indentation."""
        lines = []
        for name, content in sorted(items.items()):
            if isinstance(content, list):
                # This is a leaf node with items
                lines.append(f"{'#' * (indent + 4)} {name}")
                for item in sorted(content, key=lambda x: x.name):
                    lines.append(f"- **{item.name}**")
                    # Validate using the full category path
                    if item.categories:
                        results = self._validate_item(item)
                        lines.append(self._format_validation_results(results))
            else:
                # This is a subgroup
                lines.append(f"{'#' * (indent + 3)} {name}")
                lines.extend(self._format_category_section(content, indent + 1))
        return lines

    def _validate_item(self, item: Any) -> Dict[str, List[str]]:
        """Validate an item based on its type."""

        def to_dict(result: Any) -> Dict[str, List[str]]:
            if (
                hasattr(result, "errors")
                and hasattr(result, "warnings")
                and hasattr(result, "successes")
            ):
                return {
                    "errors": list(getattr(result, "errors", [])),
                    "warnings": list(getattr(result, "warnings", [])),
                    "successes": list(getattr(result, "successes", [])),
                }
            # Fallback: ensure all keys are present and are lists of str
            return {
                "errors": list(result.get("errors", [])),
                "warnings": list(result.get("warnings", [])),
                "successes": list(result.get("successes", [])),
            }

        if isinstance(item, Symbol):
            return to_dict(validate_symbol(item, self.structure))
        elif isinstance(item, Footprint):
            return to_dict(validate_footprint(item, self.structure))
        elif isinstance(item, Model3D):
            return to_dict(validate_model3d(item, self.structure))
        elif isinstance(item, Documentation):
            return to_dict(validate_documentation(item, self.structure))
        return {"errors": ["Unknown item type"], "warnings": [], "successes": []}

    def _generate_symbols_section(self, changed_files: Dict[str, FileStatus]) -> str:
        """Generate the symbols section with validation results."""
        sections = ["## Symbols"]

        # Get symbols directory
        if not self.structure.library.directories or not self.structure.library.directories.symbols:
            return "\n".join(sections + ["No symbols directory found.", ""])
        symbols_dir = self.library_path / self.structure.library.directories.symbols
        if not symbols_dir.exists():
            return "\n".join(sections + ["No symbols directory found.", ""])

        # List symbol files
        symbol_files = list(symbols_dir.rglob("*.kicad_sym"))
        if not symbol_files:
            return "\n".join(sections + ["No symbol files found.", ""])

        sections.append("### Symbol Files")
        for file in sorted(symbol_files):
            rel_path = file.relative_to(self.library_path)
            status = self._get_file_status(str(rel_path), changed_files)
            sections.append(f"- {status} `{rel_path}`")

        # Parse and validate symbols
        all_symbols = _find_symbols(self.library_path, self.structure)
        if all_symbols:
            sections.append("\n### Symbol Validation Results")
            grouped_symbols = self._group_by_category(all_symbols)
            sections.extend(self._format_category_section(grouped_symbols))
        else:
            sections.append("No symbols found to validate.")

        return "\n".join(sections + [""])

    def _generate_footprints_section(self, changed_files: Dict[str, FileStatus]) -> str:
        """Generate the footprints section with validation results."""
        sections = ["## Footprints"]

        if (
            not self.structure.library.directories
            or not self.structure.library.directories.footprints
        ):
            return "\n".join(sections + ["No footprints directory found.", ""])
        footprints_dir = self.library_path / self.structure.library.directories.footprints
        if not footprints_dir.exists():
            return "\n".join(sections + ["No footprints directory found.", ""])

        footprint_files = list(footprints_dir.rglob("*.kicad_mod"))
        if not footprint_files:
            return "\n".join(sections + ["No footprint files found.", ""])

        sections.append("### Footprint Files")
        for file in sorted(footprint_files):
            rel_path = file.relative_to(self.library_path)
            status = self._get_file_status(str(rel_path), changed_files)
            sections.append(f"- {status} `{rel_path}`")

        all_footprints = _find_footprints(self.library_path, self.structure)
        if all_footprints:
            sections.append("\n### Footprint Validation Results")
            grouped_footprints = self._group_by_category(all_footprints)
            sections.extend(self._format_category_section(grouped_footprints))
        else:
            sections.append("No footprints found to validate.")

        return "\n".join(sections + [""])

    def _generate_3d_models_section(self, changed_files: Dict[str, FileStatus]) -> str:
        """Generate the 3D models section with validation results."""
        sections = ["## 3D Models"]

        if (
            not self.structure.library.directories
            or not self.structure.library.directories.models_3d
        ):
            return "\n".join(sections + ["No 3D models directory found.", ""])
        models_dir = self.library_path / self.structure.library.directories.models_3d
        if not models_dir.exists():
            return "\n".join(sections + ["No 3D models directory found.", ""])

        model_files = list(models_dir.rglob("*.step"))
        if not model_files:
            return "\n".join(sections + ["No 3D model files found.", ""])

        sections.append("### 3D Model Files")
        for file in sorted(model_files):
            rel_path = file.relative_to(self.library_path)
            status = self._get_file_status(str(rel_path), changed_files)
            sections.append(f"- {status} `{rel_path}`")

        all_models = _find_models_3d(self.library_path, self.structure)
        if all_models:
            sections.append("\n### 3D Model Validation Results")
            grouped_models = self._group_by_category(all_models)
            sections.extend(self._format_category_section(grouped_models))
        else:
            sections.append("No 3D models found to validate.")

        return "\n".join(sections + [""])

    def _generate_documentation_section(self, changed_files: Dict[str, FileStatus]) -> str:
        """Generate the documentation section with validation results."""
        sections = ["## Documentation"]

        if (
            not self.structure.library.directories
            or not self.structure.library.directories.documentation
        ):
            return "\n".join(sections + ["No documentation directory found.", ""])
        docs_dir = self.library_path / self.structure.library.directories.documentation
        if not docs_dir.exists():
            return "\n".join(sections + ["No documentation directory found.", ""])

        doc_files = list(docs_dir.rglob("*.pdf"))
        if not doc_files:
            return "\n".join(sections + ["No documentation files found.", ""])

        sections.append("### Documentation Files")
        for file in sorted(doc_files):
            rel_path = file.relative_to(self.library_path)
            status = self._get_file_status(str(rel_path), changed_files)
            sections.append(f"- {status} `{rel_path}`")

        all_docs = _find_documentation(self.library_path, self.structure)
        if all_docs:
            sections.append("\n### Documentation Validation Results")
            grouped_docs = self._group_by_category(all_docs)
            sections.extend(self._format_category_section(grouped_docs))
        else:
            sections.append("No documentation found to validate.")

        return "\n".join(sections + [""])

    def _get_changed_files(self, compare_commit: str) -> Dict[str, FileStatus]:
        """Get changed files compared to a specific commit."""
        changed_files = {}
        for file_path, status in get_changed_files(self.library_path, compare_commit).items():
            changed_files[str(file_path)] = FileStatus(path=Path(file_path), status=status)
        return changed_files

    def _get_file_status(self, file_path: str, changed_files: Dict[str, FileStatus]) -> str:
        """Get the markdown status marker for a file."""
        if not changed_files:
            return ""
        status = changed_files.get(file_path, "unchanged")
        if isinstance(status, FileStatus):
            status_key = status.status
        else:
            status_key = str(status)
        markers = {"new": "🆕", "modified": "📝", "deleted": "🗑️", "unchanged": ""}
        return markers.get(status_key, "")

    def _group_issues_by_type(self, issues: List[Issue]) -> Dict[str, List[Issue]]:
        """Group issues by their type."""
        grouped: Dict[str, List[Issue]] = {}
        for issue in issues:
            if issue.type not in grouped:
                grouped[issue.type] = []
            grouped[issue.type].append(issue)
        return grouped
