# OpenInstructions Specification (v0.1.0)

This document defines the YAML format for OpenInstructions. OpenInstructions uses a two-level architecture: a root schema that outlines project types and phases, and detailed instructions for each specific phase.

## Versioning

- **Version Fields**: Each file includes two essential version fields:
  - `catalog_version`: Version of the catalog (Major.Minor.Patch)
  - `version`: Version of the specific instruction (Major.Minor.Patch)

- **Git-Based Versioning**:
  - Source files are stored in a flat structure in the Git repository
  - Version information is embedded in the files themselves
  - Official releases are tagged in the repository (e.g., `v0.1.0`, `v0.1.0`)
  - The build process generates versioned URLs and directories

## Directory Structure

### Source Repository (Flat Structure)

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

### Generated Structure (After Build)

```
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

## Root Schema

This schema defines a complete project type with its lifecycle phases and supported variants.

```yaml
# Project Type Root Schema
catalog_version: <string>         # Catalog version (e.g., "0.1.0")
project_type: <string>            # Project type ID (e.g., "web_app")
title: <string>                   # Human-readable project type name
description: <string>             # Description of this project type

# Variants supported for this project type
variants:
  - id: <string>                  # Variant identifier (e.g., "language")
    title: <string>               # Human-readable variant name
    options:                      # Available options
      - id: <string>              # Option identifier (e.g., "python")
        title: <string>           # Human-readable option name
        description: <string>     # Brief description (optional)

# Lifecycle phases in recommended sequence
phases:
  - id: <string>                  # Phase identifier (e.g., "setup")
    title: <string>               # Human-readable phase name
    description: <string>         # Brief description
    dependencies: [<phase_id>]    # Phases that must be completed first
    required: <boolean>           # Whether mandatory (default: true)
    
    # For variant-specific implementations:
    variants:
      - variant: <variant_id>     # Reference to variant
        options:
          - option: <option_id>   # Reference to option
            path: <string>        # Path to instruction file
            version: <string>     # Version of this phase
    
    # For generic phases (no variants):
    path: <string>                # Path to generic phase
    version: <string>             # Version of this phase

# Global context
global_context:
  prerequisites: [<string>]       # Global prerequisites
  constraints: [<string>]         # Universal constraints
```

## Phase Instruction Schema

This schema defines detailed instructions for a specific phase of a project.

```yaml
# Phase Instruction Schema
instruction_id: <string>          # Unique identifier
title: <string>                   # Concise title
version: <string>                 # Version of this instruction (e.g., "0.1.0")
catalog_version: <string>         # Catalog version (e.g., "0.1.0")
project_type: <string>            # Must match parent project_type
phase: <string>                   # Must match phase.id from root schema
variant_option: <string>          # Optional: variant this implements (e.g., "python")
instruction_type: <string>        # Optional: type of instruction (e.g., "creation", "refactoring")
applicable_to: [<string>]         # Optional: what this instruction can be applied to

# Context (helps LLMs understand the "why")
context:
  objective: <string>             # Overall goal of this phase
  background: <string>            # Optional: Relevant background
  preconditions: [<string>]       # Optional: Conditions that must be true before starting
  postconditions: [<string>]      # Optional: Conditions that must be true after completion

# Structured tasks (the "what")
tasks:
  - id: <string>                  # Task identifier (e.g., "task1")
    title: <string>               # Short description
    description: <string>         # Detailed explanation
    priority: <integer>           # 1-5 (1 highest)
    dependencies: [<task_id>]     # Required previous tasks
    acceptance_criteria: [<string>]  # Definition of "done"
    examples:                     # Optional but valuable
      - input: <string>           # Example scenario or starting code
        output: <string>          # Expected result or ending code
        explanation: <string>     # Optional: Why this transformation works

# Patterns (optional, useful for refactoring and other transformations)
patterns:
  - id: <string>                  # Pattern identifier
    name: <string>                # Human-readable pattern name
    description: <string>         # Explanation of the pattern
    applicability: <string>       # When to apply this pattern
    examples: [<string>]          # Examples of the pattern

# Constraints
constraints: [<string>]           # Technical, performance, or security constraints

# Resources (helpful references)
resources:
  - title: <string>               # Resource title
    url: <string>                 # URL to resource
    description: <string>         # Why it's helpful
```

## Example: Web App Project Type Schema

```yaml
catalog_version: "0.1.0"
project_type: "web_app"
title: "Web Application"
description: "A modern web application with frontend, backend, and deployment components"

variants:
  - id: "frontend_framework"
    title: "Frontend Framework"
    options:
      - id: "react"
        title: "React"
        description: "Implement using React with hooks and functional components"
      - id: "vue"
        title: "Vue.js"
        description: "Implement using Vue.js with composition API"
  
  - id: "ci_platform"
    title: "CI Platform"
    options:
      - id: "github_actions"
        title: "GitHub Actions"
      - id: "gitlab_ci"
        title: "GitLab CI"

phases:
  - id: "setup"
    title: "Project Setup"
    description: "Initialize project structure and dependencies"
    dependencies: []
    variants:
      - variant: "frontend_framework"
        options:
          - option: "react"
            path: "project_types/web_app/react/setup.yaml"
            version: "0.1.0"
          - option: "vue"
            path: "project_types/web_app/vue/setup.yaml"
            version: "0.1.0"
  
  - id: "ci_setup"
    title: "CI Configuration"
    description: "Set up continuous integration pipeline"
    dependencies: ["setup"]
    variants:
      - variant: "ci_platform"
        options:
          - option: "github_actions"
            path: "project_types/web_app/ci/github_actions.yaml"
            version: "0.1.0"
          - option: "gitlab_ci"
            path: "project_types/web_app/ci/gitlab_ci.yaml"
            version: "0.1.0"
  
  - id: "documentation"
    title: "Documentation"
    description: "Create project and user documentation"
    dependencies: ["setup"]
    path: "project_types/web_app/shared/documentation.yaml"
    version: "0.1.0"
    
  - id: "refactoring"
    title: "Codebase Refactoring"
    description: "Improve code quality and maintainability through refactoring"
    dependencies: ["setup"]
    variants:
      - variant: "frontend_framework"
        options:
          - option: "react"
            path: "project_types/web_app/react/refactoring.yaml"
            version: "0.1.0"

global_context:
  prerequisites: [
    "Node.js 16+ installed",
    "Package manager (npm, yarn, or pnpm)"
  ]
  constraints: [
    "Must be deployable to standard web hosting platforms",
    "Must work in modern browsers (Edge, Chrome, Firefox, Safari)"
  ]
```

## Example: React Refactoring Instruction

```yaml
instruction_id: "react-refactor-001"
title: "React Codebase Refactoring"
version: "0.1.0"
catalog_version: "0.1.0"
project_type: "web_app"
phase: "refactoring"
variant_option: "react"
instruction_type: "refactoring"
applicable_to: ["react-class-components", "legacy-react-code"]

context:
  objective: "Modernize React codebase by improving component structure and adopting best practices"
  background: "Modern React emphasizes functional components, hooks, and code splitting"
  preconditions: [
    "Existing React application with version 16.8+",
    "Component structure already established"
  ]
  postconditions: [
    "Improved performance",
    "Better code maintainability",
    "Type safety (if TypeScript)"
  ]

tasks:
  - id: "react-refactor-001"
    title: "Analyze component structure"
    description: "Identify components for refactoring, focusing on large class components"
    priority: 1
    dependencies: []
    acceptance_criteria: [
      "List of components created with priority ratings",
      "Dependencies between components mapped"
    ]
    
  - id: "react-refactor-002"
    title: "Convert class components to functional components"
    description: "Transform class components to functional components using hooks"
    priority: 2
    dependencies: ["react-refactor-001"]
    acceptance_criteria: [
      "All targeted components converted to functional components",
      "Tests pass with equivalent functionality"
    ]
    examples:
      - input: |
          class Counter extends React.Component {
            constructor(props) {
              super(props);
              this.state = { count: 0 };
              this.increment = this.increment.bind(this);
            }
            
            increment() {
              this.setState(state => ({ count: state.count + 1 }));
            }
            
            render() {
              return (
                <div>
                  <p>Count: {this.state.count}</p>
                  <button onClick={this.increment}>Increment</button>
                </div>
              );
            }
          }
        output: |
          function Counter() {
            const [count, setCount] = useState(0);
            
            const increment = () => {
              setCount(prevCount => prevCount + 1);
            };
            
            return (
              <div>
                <p>Count: {count}</p>
                <button onClick={increment}>Increment</button>
              </div>
            );
          }
        explanation: "Converted class component state to useState hook, removed binding, and simplified render logic"

patterns:
  - id: "lifecycle-to-hooks"
    name: "Lifecycle Methods to Hooks"
    description: "Replace React lifecycle methods with equivalent hook implementations"
    applicability: "Class components using componentDidMount, componentDidUpdate, etc."
    examples: [
      "componentDidMount → useEffect(() => {}, [])",
      "componentDidUpdate → useEffect(() => {}, [dependencies])"
    ]
  
  - id: "state-to-context"
    name: "Prop Drilling to Context"
    description: "Replace deep prop drilling with React Context API"
    applicability: "Components passing props through multiple levels of the component tree"

constraints: [
  "Must maintain existing functionality and API contracts",
  "Code must pass all existing tests after refactoring",
  "Must support gradual adoption (work with existing class components)"
]

resources:
  - title: "React Hooks Documentation"
    url: "https://reactjs.org/docs/hooks-intro.html"
    description: "Official guide for using hooks in functional components"
  
  - title: "React TypeScript Cheatsheet"
    url: "https://react-typescript-cheatsheet.netlify.app/"
    description: "Patterns for typing React components in TypeScript"
```

## URL-Based Version Access

The generated structure supports several ways to access content:

1. **Latest catalog version**:
   ```
   https://openinstructions.org/catalog/latest/...
   ```

2. **Specific catalog version**:
   ```
   https://openinstructions.org/catalog/v1/...
   ```

3. **Latest instruction version**:
   ```
   https://openinstructions.org/catalog/v1/project_types/web_app/react/latest/setup.yaml
   ```

4. **Specific instruction version**:
   ```
   https://openinstructions.org/catalog/v1/project_types/web_app/react/v0.1.0/setup.yaml
   ```

5. **Raw GitHub access** (by tag):
   ```
   https://raw.githubusercontent.com/OpenInstructions/catalog/v0.1.0/project_types/web_app/react/setup.yaml
   ```

## Build Process

The build process converts the flat source structure into the versioned directory structure:

1. **Read source files**: Parse all YAML files to extract version information
2. **Create version directories**: Generate catalog version directories (v1, v2, etc.)
3. **Generate instruction versions**: Create instruction version directories (v0.1.0, v1.0, etc.)
4. **Create symlinks**: Set up "latest" symlinks at both catalog and instruction levels
5. **Copy content**: Copy files to their appropriate locations

## Implementation Notes

1. **Minimal Requirements**:
   - At least one phase is required in the root schema
   - At least one task is required in a phase-specific instruction
   - Always include `catalog_version` and `version` fields in every file

2. **Naming Conventions**:
   - Use `snake_case` for field names and IDs
   - All IDs should be unique within their scope
   - Use descriptive, consistent naming patterns

3. **Best Practices**:
   - Include examples to improve LLM performance
   - Provide clear task dependencies to guide implementation
   - Use concise, action-oriented task descriptions
   - Consider which phases need variants and which can be shared
   - For refactoring instructions, include clear before/after examples

4. **Technical Considerations**:
   - Build tools handle symlink creation and file copying
   - Consider alternatives to symlinks (HTML redirects, server configs) for better cross-platform support
   - Use Git tags for official releases
   - Run the build script before deploying

## Benefits of This Structure

1. **Complete Lifecycle View**: Root schema provides LLMs with a full understanding of the project lifecycle
2. **Modular Variants**: Support for multiple implementations of the same project type
3. **Efficient Schema**: Clear, concise structure with focused fields
4. **Consistent Versioning**: Clear version information for both catalog and instructions
5. **URL-Based Access**: Predictable paths for accessing specific versions
6. **Backward Compatibility**: Old versions remain accessible alongside new ones
7. **LLM-Optimized**: Structured format designed for efficient processing by Large Language Models
8. **Transformation Support**: Enhanced structure for both creation and transformation instructions 