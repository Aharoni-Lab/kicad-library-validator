# Advanced Usage

## Custom Validation
- You can extend or modify the structure YAML file to enforce organization-specific rules.
- Add new categories, subcategories, or properties as needed.
- Use regular expressions in patterns to enforce naming conventions.

## Continuous Integration (CI)
- Integrate the validator into your CI pipeline to automatically check library submissions.
- Example (GitHub Actions):
  ```yaml
  - name: Run KiCad Library Validator
    run: |
      kicad-library-validator --library-path ./my-library --structure-file ./structure.yaml
  ```
- Fail the build if validation errors are found.

## Troubleshooting
- **Validation errors:** Review the error messages and compare your library files to the structure file requirements.
- **Type errors:** Run `mypy` to check for type issues in the codebase.
- **Test failures:** Run `pytest` for detailed test output.
- **3D model/file not found:** Ensure file extensions and directory names match the structure file and are case-correct, especially on Linux.

## Contributing
- See the `CONTRIBUTING.md` file (if present) for guidelines.
- Open issues or pull requests for bugs, features, or questions. 