from pathlib import Path
from kicad_library_validator.parser.structure_parser import parse_library_structure
from kicad_library_validator.parser.library_parser import parse_library
from kicad_library_validator.reporter import LibraryReporter


def main():
    test_data_dir = Path("tests/test_kicad_lib").resolve()
    structure_file = (test_data_dir / "test_library_structure.yaml").resolve()

    # Parse structure and library
    structure = parse_library_structure(structure_file)
    library = parse_library(test_data_dir, structure)

    # Generate report
    reporter = LibraryReporter(test_data_dir, structure)
    output_path = Path("test_library_report.md").resolve()
    reporter.generate_library_report(library, output_path)

    print(f"Report generated at {output_path}")
    print("\n--- Markdown Output ---\n")
    print(output_path.read_text(encoding='utf-8'))


if __name__ == "__main__":
    main() 