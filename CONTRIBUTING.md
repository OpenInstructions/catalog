# Contributing to OpenInstructions Catalog

Thank you for your interest in contributing! This guide will help you understand how to add or improve instructions in the catalog.

## Quick Start

1. **Fork**: Start by forking `https://github.com/OpenInstructions/catalog`
2. **Clone**: Clone your fork to your local machine
3. **Create/Edit**: Add or modify YAML files following our specification
4. **Test**: Run the build script locally to test your changes
5. **PR**: Submit a pull request with a clear description of your changes

## Guidelines

### General Requirements

- Follow the format defined in `SPEC.md`
- Include the required version fields:
  - `catalog_version`: Version of the catalog (e.g., "0.1.0")
  - `version`: Version of your specific instruction (e.g., "0.1.0")
- Keep instructions clear, detailed, and actionable
- Include examples to help LLMs understand expected outputs
- Use `snake_case` for field names and IDs
- Follow the directory structure as outlined below

### Understanding the Repository Structure

The repository uses a flat structure with version information embedded in the files themselves:

```
schemas/
└── web_app.yaml                 # Contains catalog_version: "0.1.0"
project_types/
├── web_app/
│   ├── react/
│   │   ├── setup.yaml           # Contains version: "0.1.0"
│   │   └── development.yaml     # Contains version: "0.1.0"
│   └── ci/
│       ├── javascript/
│       │   ├── github_actions.yaml  # Contains version: "0.1.0"
│       │   └── gitlab_ci.yaml       # Contains version: "0.1.0"
```

The build script generates a versioned directory structure with appropriate symlinks.

### Versioning Guidelines

#### Catalog Versions

- The `catalog_version` represents the version of the overall catalog structure
- Major catalog versions (e.g., `1.0.0`, `2.0.0`) indicate significant schema changes
- The current catalog version is `0.1.0`
- Set the `catalog_version` field in each YAML file to match the current catalog version

#### Instruction Versions

- The `version` field represents the version of the specific instruction file
- Follow semantic versioning principles:
  - Major version (`1.0.0`): Breaking changes to the instruction
  - Minor version (`0.1.0`): New features or significant improvements
  - Patch version (`0.0.1`): Bug fixes or minor clarifications
- To update an instruction:
  1. Edit the file directly
  2. Increment the `version` field appropriately
  3. Update any references to this file in schema files

### Working with the Build System

To test your changes locally:

1. **Set Up Python Environment**:
   ```bash
   # Create a virtual environment (recommended)
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Run the Build**:
   ```bash
   python scripts/build_catalog.py
   ```

3. **Check the Output**:
   The build output will be in the `./dist` directory. Verify that:
   - Your files appear in the correct locations
   - The catalog.json file includes your changes
   - The HTML index properly displays your instructions

   For backward compatibility, you can also run:
   ```bash
   npm run build
   ```
   which calls the same Python script.

### Common Contribution Tasks

#### Adding a New Project Type

1. Create a schema file in `schemas/<project_type>.yaml`
2. Define all phases and variants
3. Create directories for each variant under `project_types/<project_type>/`
4. Create instruction files for each phase

#### Adding a New Variant

1. Update the schema file to include the new variant
2. Create directories for the variant
3. Create instruction files for each affected phase

#### Improving an Existing Instruction

1. Identify the file to improve
2. Make your changes while maintaining the schema structure
3. Increment the `version` field
4. Update any references in schema files

### Best Practices

- **Be Specific**: Provide clear, actionable instructions
- **Include Examples**: Add input/output examples for complex tasks
- **Define Dependencies**: Clearly specify dependencies between tasks
- **Provide Context**: Explain why tasks are important, not just how to do them
- **Consider LLMs**: Structure your instructions to be easily understood by AI
- **Avoid Duplication**: If multiple variants share common instructions, consider using a shared implementation
- **Test Your Instructions**: Verify that your instructions can be followed successfully
- **Document Changes**: When submitting a PR, clearly explain what you changed and why

## Getting Started with a First Contribution

1. Browse the existing instructions to understand the format
2. Look for issues labeled "good first issue" 
3. Comment on an issue you'd like to work on
4. Ask questions in the GitHub Discussions if you need help

Thank you for contributing to OpenInstructions! 