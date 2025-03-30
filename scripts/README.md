# OpenInstructions Catalog Build System

This directory contains scripts for building and validating the OpenInstructions catalog.

## Build Process

The main build script (`build_catalog.py`) performs the following tasks:

1. Collects all YAML files from the `project_types/` directory
2. Validates each file for required fields and structure
3. Builds a catalog index in JSON format
4. Copies all valid files to the `dist/` directory
5. Generates a simple HTML index page for browsing the catalog

## Requirements

The build system requires Python 3.8+ and the following dependencies:
- PyYAML (for YAML processing)
- jsonschema (for schema validation)

Install dependencies with:
```bash
pip install -r requirements.txt
```

## Running the Build

To build the catalog locally, run:
```bash
python scripts/build_catalog.py
```

This will create a `dist/` directory containing all processed files and the catalog index.

## Adding Custom Validation

To add more detailed validation rules, modify the `validate_yaml_file()` function in `build_catalog.py`. 
You can add schema-based validation using the jsonschema library by defining schema files in the `schemas/` directory. 