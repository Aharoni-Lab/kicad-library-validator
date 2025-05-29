# KiCad Library Validator Templates

This directory contains templates and documentation for incorporating the KiCad Library Validator into your KiCad library repository.

## Contents

- `github/` - GitHub-specific templates and workflows
  - `workflows/` - GitHub Actions workflow templates
  - `pr_template.md` - Pull request template
  - `issue_template.md` - Issue template
- `library/` - Library structure templates
  - `structure.yaml` - Example library structure definition
  - `README.md` - Library README template
  - `CONTRIBUTING.md` - Contribution guidelines template
  - `.gitignore` - Git ignore rules for KiCad libraries
- `docs/` - Documentation templates
  - `validation_rules.md` - Validation rules documentation template
  - `library_usage.md` - Library usage documentation template

## Usage

1. Copy the relevant templates to your library repository
2. Customize the templates to match your library's needs
3. Follow the setup instructions in each template

## Setup Instructions

### GitHub Actions Setup

1. Copy the contents of `github/workflows/` to `.github/workflows/` in your repository
2. Copy `github/pr_template.md` to `.github/pull_request_template.md`
3. Copy `github/issue_template.md` to `.github/issue_template.md`
4. Update the workflow files with your specific requirements

### Library Structure Setup

1. Copy `library/structure.yaml` to your repository root
2. Copy `library/.gitignore` to your repository root
3. Customize the structure definition to match your library's organization
4. Copy and customize `library/README.md` and `library/CONTRIBUTING.md`

### Documentation Setup

1. Copy the contents of `docs/` to your repository's documentation directory
2. Customize the documentation to match your library's rules and usage

## Customization

Each template includes comments and placeholders to help you customize it for your specific needs. Make sure to:

1. Update all placeholder values
2. Review and adjust validation rules
3. Customize documentation to match your library's requirements
4. Update GitHub workflow configurations as needed 