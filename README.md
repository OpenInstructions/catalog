# OpenInstructions Catalog

Welcome to the **OpenInstructions Catalog**, a public collection of phase-based instructions for Large Language Models (LLMs) and developers to create and refactor development projects. Hosted as raw YAML files on GitHub, this catalog powers project initialization and refactoring, with a CLI tool that integrates with OpenRouter to execute instructions.

## Project Attribution and Name Protection

**OpenInstructions** is an open-source initiative by Ilia Lirtsman and Gosha Dozoretz. The 'OpenInstructions' name and branding are reserved for this project and its officially authorized derivatives. Unauthorized use of the name for other projects or purposes is not permitted without explicit permission from the founders.

## Features

- **Structured**: Clearly defined phases with dependency tracking
- **Modular**: Support for multiple variants (frontend frameworks, programming languages, CI platforms)
- **Multi-dimensional**: Select different options for each variant dimension (e.g., React + GitHub Actions)
- **Versioned**: Git-based versioning with build-time directory structure 
- **Compatible**: Works with any LLM capable of following structured instructions

## Why OpenInstructions?

- **Structured**: Detailed instructions split by project phase (setup, development, etc.)
- **Versioned**: Git-based versioning with semantic versioning for instructions
- **AI-Ready**: Optimized for LLMs with clear task definitions and examples
- **Community-Driven**: Open to contributions for continuous improvement
- **Modular**: Support for multiple variants with shared components where appropriate

## Getting Started

1. Browse instructions by project type at [openinstructions.org](https://openinstructions.org):
   - [Web Application Schema](https://openinstructions.org/catalog/v1/schemas/web_app.yaml) - Complete web app lifecycle
   - **React Instructions**:
     - [Latest React setup](https://openinstructions.org/catalog/v1/project_types/web_app/react/latest/setup.yaml)
     - [Specific React setup (v0.1.0)](https://openinstructions.org/catalog/v1/project_types/web_app/react/v0.1.0/setup.yaml)
   - **CI Instructions**:
     - [GitHub Actions CI](https://openinstructions.org/catalog/v1/project_types/web_app/ci/javascript/latest/github_actions.yaml)
     - [GitLab CI](https://openinstructions.org/catalog/v1/project_types/web_app/ci/javascript/latest/gitlab_ci.yaml)

2. Access via direct URLs:
   - Latest catalog: `https://openinstructions.org/catalog/latest/...`
   - Latest instruction: `https://openinstructions.org/catalog/v1/project_types/web_app/react/latest/setup.yaml`
   - Specific version: `https://openinstructions.org/catalog/v1/project_types/web_app/react/v0.1.0/setup.yaml`
   - GitHub tag: `https://raw.githubusercontent.com/OpenInstructions/catalog/v0.1.0/project_types/web_app/react/setup.yaml`

3. Integrate with your CLI or application:

```python
import yaml
import requests

# Access the latest schema via the web
schema_url = "https://openinstructions.org/catalog/latest/schemas/web_app.yaml"
schema = yaml.safe_load(requests.get(schema_url).text)

# Determine variants for your project
frontend_framework = "react"  # or "vue", "angular"
ci_platform = "github_actions"  # or "gitlab_ci"

# Get the phases for the selected variants
phases = []
for phase in schema['phases']:
    phase_info = {
        'id': phase['id'],
        'title': phase['title'],
        'description': phase['description']
    }
    
    # Handle variant-specific phases
    if 'variants' in phase:
        for variant_group in phase['variants']:
            # Handle frontend framework variants
            if variant_group['variant'] == 'frontend_framework':
                for option in variant_group['options']:
                    if option['option'] == frontend_framework:
                        phase_info['path'] = option['path']
                        phase_info['version'] = option['version']
            
            # Handle CI platform variants
            elif variant_group['variant'] == 'ci_platform':
                for option in variant_group['options']:
                    if option['option'] == ci_platform:
                        phase_info['path'] = option['path']
                        phase_info['version'] = option['version']
    
    # Handle generic phases
    elif 'path' in phase:
        phase_info['path'] = phase['path']
        phase_info['version'] = phase['version']
    
    phases.append(phase_info)

# Now you can fetch each phase's instructions
for phase in phases:
    if 'path' in phase:
        instruction_url = f"https://openinstructions.org/catalog/latest/{phase['path']}"
        instruction = yaml.safe_load(requests.get(instruction_url).text)
        # Process the instruction...
```

## Repository Structure

The repository uses a flat structure with version information embedded in the files:

```
# Source repository
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

The build process generates a versioned directory structure for web access:

```
# Generated structure (after build)
catalog/
├── latest/ -> v1/              # Symlink to latest catalog version
├── v1/                         # Catalog version 1.x
│   ├── schemas/
│   │   └── web_app.yaml        # Root schema with variants and phases
│   ├── project_types/
│   │   ├── web_app/
│   │   │   ├── react/
│   │   │   │   ├── latest/ -> v0.1.0/  # Symlink to latest version
│   │   │   │   └── v0.1.0/             # Instruction version
│   │   │   │       └── setup.yaml
```

## Version Support

The catalog uses Git-based versioning with a build process that generates versioned directories:

1. **Source Versioning**: Version information is stored directly in files:
   ```yaml
   catalog_version: "0.1.0"  # Catalog version
   version: "0.1.0"          # Instruction version
   ```

2. **Git Tags**: Official releases use Git tags (e.g., `v0.1.0`):
   ```
   git tag v0.1.0
   git push origin v0.1.0
   ```

3. **Generated Structure**: The build script automatically creates:
   - Catalog version directories (`v1/`)
   - Instruction version directories (`v0.1.0/`)
   - "Latest" symlinks at both levels

4. **URL Access**: Multiple access patterns for flexibility:
   - Latest: `https://openinstructions.org/catalog/latest/...`
   - Specific: `https://openinstructions.org/catalog/v1/project_types/web_app/react/v0.1.0/setup.yaml`
   - Git tag: `https://raw.githubusercontent.com/OpenInstructions/catalog/v0.1.0/project_types/web_app/react/setup.yaml`

## Key Design Features

- **Multi-Variant Support**: Instructions can vary by multiple dimensions
- **Task Dependencies**: Clear dependencies between phases and between tasks
- **Detailed Context**: Each instruction includes objectives and background
- **Phased Approach**: Complex projects broken into manageable phases
- **Git-Based Versioning**: Simple source structure that builds to versioned outputs
- **LLM-Optimized**: Structured to be easy for LLMs to understand and implement

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md) for details on how to add new instructions or improve existing ones.

## Development

1. **Local Setup**:
   ```bash
   git clone https://github.com/OpenInstructions/catalog.git
   cd catalog
   # Set up a Python virtual environment (recommended)
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Build Locally**:
   ```bash
   python scripts/build_catalog.py
   ```

3. **Test**:
   The build output will be in the `./dist` directory.

## License

This project is licensed under the terms of the MIT license. While the code is MIT-licensed, the 'OpenInstructions' name and branding are reserved for this project.

## Get Involved:
- Star this repo
- Join [Discussions](https://github.com/OpenInstructions/catalog/discussions)
- Open issues for features or bugs
- Submit PRs to improve instructions 