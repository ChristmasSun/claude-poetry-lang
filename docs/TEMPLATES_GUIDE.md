# Lament Templates and Scaffolding Guide

Complete guide to using templates, scaffolding projects, and managing workspaces in Lament.

## Table of Contents

1. [Template System Overview](#template-system-overview)
2. [Template Syntax](#template-syntax)
3. [Using Project Templates](#using-project-templates)
4. [Creating Custom Templates](#creating-custom-templates)
5. [Workspace Management](#workspace-management)
6. [Advanced Usage](#advanced-usage)

---

## Template System Overview

Lament provides a powerful template engine for generating project structures, with three main components:

### Components

1. **Template Engine** - Core template rendering with variable substitution, conditionals, loops
2. **Scaffolder** - Project generation from templates with interactive prompts
3. **Workspace Manager** - Monorepo support for managing multiple packages

### Built-in Templates

- `library` - Reusable library package
- `application` - Standalone application
- `web-server` - Web server/API
- `cli-tool` - Command-line tool
- `ml-model` - Machine learning model project

---

## Template Syntax

### Variable Substitution

```
{{variable_name}}
{{nested.property}}
```

### Conditionals

```
{{#if condition}}
  Content when true
{{/if}}

{{#if condition}}
  True content
{{#else}}
  False content
{{/if}}
```

### Loops

```
{{#each items}}
  {{this}}
{{/each}}

{{#each items}}
  Index: {{index}}
  First: {{first}}
  Last: {{last}}
{{/each}}
```

### Comments

```
{{! This is a comment }}
```

### Partials

```
{{> partial_name}}
```

### Helper Functions

Built-in helpers:

```
{{upper(text)}}           - Convert to uppercase
{{lower(text)}}           - Convert to lowercase
{{capitalize(text)}}      - Capitalize first letter
{{title(text)}}           - Title case
{{snake_case(text)}}      - Convert to snake_case
{{camel_case(text)}}      - Convert to camelCase
{{pascal_case(text)}}     - Convert to PascalCase
{{kebab_case(text)}}      - Convert to kebab-case
{{len(items)}}            - Get length
{{date()}}                - Current date (YYYY-MM-DD)
{{datetime()}}            - Current datetime (ISO)
{{year()}}                - Current year
```

### Example Template

```lament
{{! Main module for {{project_name}} }}

grief {{pascal_case(project_name)}}:
    burden version as String

    mourn construct():
        version = "{{version}}"
    ;

    {{#if has_logging}}
    mourn log(message as String):
        confess message as Log
    ;
    {{/if}}
;
```

---

## Using Project Templates

### Quick Start

Create a new project using a template:

```bash
# Create a library project
lament-new library my-awesome-lib

# Create an application
lament-new application my-app

# Interactive mode
lament-new --interactive

# Specify options
lament-new library my-lib \
  --author "Your Name" \
  --email "you@example.com" \
  --license MIT
```

### Available Options

```
--interactive, -i     Interactive mode with prompts
--output, -o DIR      Output directory (default: ./<name>)
--author NAME         Author name
--email EMAIL         Author email
--license LICENSE     License (MIT, Apache-2.0, GPL-3.0, BSD-3-Clause, None)
--no-git             Don't initialize git repository
--no-ci              Don't generate CI/CD configuration
--list               List available templates
```

### Template Details

#### Library Template

Creates a reusable library package:

```
my-lib/
├── package.lament
├── src/
│   └── my_lib.lament
├── tests/
│   └── test_my_lib.lament
├── docs/
├── examples/
├── README.md
├── LICENSE
└── .gitignore
```

Features:
- Example functions and classes
- Test structure
- Documentation setup
- CI/CD configuration

#### Application Template

Creates a standalone application:

```
my-app/
├── package.lament
├── src/
│   ├── main.lament
│   └── config.lament
├── tests/
│   └── test_main.lament
├── data/
├── logs/
├── README.md
└── .gitignore
```

Features:
- Main entry point
- Configuration module
- Data directory structure
- Logging setup

#### Web Server Template

Creates a web server/API:

```
my-server/
├── package.lament
├── src/
│   ├── server.lament
│   ├── routes.lament
│   └── middleware.lament
├── tests/
│   └── test_server.lament
├── static/
├── templates/
└── README.md
```

Features:
- Server class with routing
- Middleware support
- Static file serving
- Template rendering

#### CLI Tool Template

Creates a command-line tool:

```
my-cli/
├── package.lament
├── src/
│   ├── cli.lament
│   ├── commands.lament
│   └── utils.lament
├── bin/
│   └── my-cli
├── tests/
│   └── test_cli.lament
└── README.md
```

Features:
- Command parsing
- Help system
- Argument handling
- Executable wrapper

#### ML Model Template

Creates a machine learning project:

```
my-model/
├── package.lament
├── src/
│   ├── model.lament
│   ├── training.lament
│   ├── evaluation.lament
│   └── inference.lament
├── tests/
│   └── test_model.lament
├── data/
├── models/
├── notebooks/
└── README.md
```

Features:
- Model architecture
- Training pipeline
- Evaluation metrics
- Inference API
- Data management

---

## Creating Custom Templates

### Template Structure

A template directory contains:

```
my-template/
├── template.json          # Template metadata
├── package.lament         # Package configuration
├── src/                   # Source files
└── .gitignore            # Git ignore rules
```

### Template Metadata (template.json)

```json
{
  "name": "my-template",
  "description": "Description of the template",
  "files": [
    {
      "source": "package.lament",
      "destination": "package.lament"
    },
    {
      "source": "src/main.lament",
      "destination": "src/{{snake_case(project_name)}}.lament"
    },
    {
      "source": "bin/cli",
      "destination": "bin/{{kebab_case(project_name)}}",
      "executable": true
    }
  ],
  "directories": [
    "src",
    "tests",
    "docs"
  ],
  "post_generation_hooks": [
    "lament-build build"
  ],
  "required_variables": [
    "project_name",
    "description",
    "author",
    "version"
  ]
}
```

### Template File Example

`src/main.lament`:

```lament
{{! Main module for {{project_name}} }}

confess "{{project_name}} v{{version}}" as Info

mourn main():
    {{#if has_config}}
    import config
    burden cfg = config.load()
    {{/if}}

    confess "Starting {{project_name}}..." as Status

    {{! Your code here }}
;

main()
```

### Using Custom Templates

```bash
# Create project from custom template
lament-new my-template my-project \
  --template-dir ./custom-templates
```

### Template Variables

Available in all templates:

- `project_name` - Project name
- `description` - Project description
- `author` - Author name
- `email` - Author email
- `license` - License type
- `version` - Initial version
- `year` - Current year
- `date` - Current date

### Registering Custom Helpers

In Python:

```python
from tools.template_engine import TemplateEngine

engine = TemplateEngine()

# Register custom helper
engine.register_helper('reverse', lambda s: s[::-1])

# Use in template: {{reverse(project_name)}}
```

---

## Workspace Management

### What is a Workspace?

A workspace (monorepo) allows managing multiple related packages in a single repository:

```
my-workspace/
├── workspace.lament       # Workspace configuration
├── packages/
│   ├── core/             # Package 1
│   │   ├── package.lament
│   │   └── src/
│   ├── utils/            # Package 2
│   │   ├── package.lament
│   │   └── src/
│   └── cli/              # Package 3
│       ├── package.lament
│       └── src/
└── .gitignore
```

### Initialize Workspace

```bash
# Create new workspace
lament-workspace init my-workspace

# Creates:
# - workspace.lament
# - packages/ directory
```

### Add Packages

```bash
# Create new package in workspace
lament-workspace create my-lib library

# Add existing package
lament-workspace add packages/existing-pkg

# Add with custom name
lament-workspace add packages/pkg --name custom-name
```

### List Packages

```bash
lament-workspace list

# Output:
# Workspace: my-workspace
# Packages (3):
#
#   core v1.0.0
#     Path: packages/core
#     Description: Core functionality
#
#   utils v0.5.0
#     Path: packages/utils
#     Workspace deps: core
```

### Build All Packages

```bash
# Build all packages (parallel by default)
lament-workspace build

# Build sequentially
lament-workspace build --sequential

# Verbose output
lament-workspace build -v
```

Build order is automatically determined from dependencies.

### Test All Packages

```bash
# Run tests for all packages
lament-workspace test

# Sequential testing
lament-workspace test --sequential

# Verbose
lament-workspace test -v
```

### Remove Packages

```bash
# Remove from workspace (keep files)
lament-workspace remove my-lib

# Remove and delete files
lament-workspace remove my-lib --delete
```

### Workspace Configuration

`workspace.lament`:

```json
{
  "name": "my-workspace",
  "packages": [
    {
      "name": "core",
      "path": "packages/core"
    },
    {
      "name": "utils",
      "path": "packages/utils"
    }
  ],
  "shared_dependencies": [],
  "shared_dev_dependencies": [],
  "build_config": {
    "parallel_builds": true,
    "max_workers": 4,
    "build_dir": "build",
    "cache_dir": ".lament/cache"
  },
  "scripts": {
    "test-all": "lament-workspace test",
    "build-all": "lament-workspace build",
    "clean": "rm -rf build .lament"
  }
}
```

### Workspace Scripts

Run custom scripts defined in workspace configuration:

```bash
lament-workspace run test-all
lament-workspace run build-all
```

### Cross-Package Dependencies

Packages can depend on other packages in the workspace:

`packages/cli/package.lament`:

```json
{
  "name": "my-cli",
  "version": "1.0.0",
  "dependencies": [
    {
      "name": "core",
      "version": "^1.0.0"
    },
    {
      "name": "utils",
      "version": "^0.5.0"
    }
  ]
}
```

The workspace manager:
- Resolves dependencies between packages
- Builds in correct order
- Links packages together

---

## Advanced Usage

### Programmatic API

#### Template Engine

```python
from tools.template_engine import TemplateEngine

engine = TemplateEngine()

# Render template string
result = engine.render(
    "Hello {{name}}!",
    {"name": "World"}
)

# Render file
engine.render_file(
    Path("template.txt"),
    Path("output.txt"),
    {"name": "World"}
)

# Register helpers
engine.register_helper('double', lambda x: x * 2)

# Register partials
engine.register_partial('header', "=== {{title}} ===")
```

#### Project Scaffolder

```python
from tools.scaffolder import ProjectScaffolder, ProjectConfig

scaffolder = ProjectScaffolder()

# Create project
config = ProjectConfig(
    name="my-project",
    description="A sample project",
    author="Your Name",
    email="you@example.com",
    license="MIT",
    template_type="library"
)

scaffolder.scaffold(
    template="library",
    name="my-project",
    config=config
)
```

#### Workspace Manager

```python
from tools.workspace import WorkspaceManager

wm = WorkspaceManager()

# Initialize
wm.init("my-workspace")

# Add packages
wm.create_package("core", "library")
wm.create_package("cli", "cli-tool")

# Build
wm.build_all(parallel=True, verbose=False)

# Test
wm.test_all(parallel=True)
```

### Custom Template Validation

```python
from tools.template_engine import TemplateValidator

validator = TemplateValidator()

template = "{{#if test}}...{{/if}}"
is_valid, errors, warnings = validator.validate(template)

if not is_valid:
    print("Errors:", errors)
print("Warnings:", warnings)
```

### Post-Generation Hooks

Run commands after project generation:

```json
{
  "post_generation_hooks": [
    "lament-pkg install",
    "lament-build build",
    "git init && git add . && git commit -m 'Initial commit'"
  ]
}
```

### Template Conditionals in Filenames

Use template syntax in destination paths:

```json
{
  "files": [
    {
      "source": "server.lament",
      "destination": "src/{{#if is_web}}server{{#else}}main{{/if}}.lament"
    }
  ]
}
```

### Environment Variables in Templates

Access environment variables:

```lament
{{! Build timestamp: {{env.BUILD_TIME}} }}
{{! Environment: {{env.ENVIRONMENT}} }}
```

---

## Examples

### Example 1: Create Library with Dependencies

```bash
lament-new library awesome-lib

cd awesome-lib

# Add dependencies
lament-pkg install requests@^2.0.0
lament-pkg install --dev pytest@^7.0.0

# Build and test
lament-build build
lament-build test
```

### Example 2: Workspace with Multiple Packages

```bash
# Initialize workspace
lament-workspace init my-project

cd my-project

# Create packages
lament-workspace create core library
lament-workspace create utils library
lament-workspace create cli cli-tool

# Add dependency in cli package
cd packages/cli
# Edit package.lament to add core and utils dependencies

# Build all
cd ../..
lament-workspace build

# Test all
lament-workspace test
```

### Example 3: Custom Template

Create custom template:

```bash
mkdir -p custom-templates/minimal

# Create template.json
cat > custom-templates/minimal/template.json << 'EOF'
{
  "name": "minimal",
  "description": "Minimal Lament project",
  "files": [
    {"source": "main.lament", "destination": "{{project_name}}.lament"}
  ],
  "directories": [],
  "required_variables": ["project_name"]
}
EOF

# Create template file
cat > custom-templates/minimal/main.lament << 'EOF'
confess "{{project_name}} - {{description}}" as Info
EOF

# Use it
lament-new minimal my-project \
  --template-dir ./custom-templates
```

### Example 4: Web API with Workspace

```bash
# Create workspace for API project
lament-workspace init my-api

cd my-api

# Create packages
lament-workspace create models library      # Data models
lament-workspace create database library    # Database layer
lament-workspace create api web-server      # API server

# Set up dependencies
# models -> (no deps)
# database -> models
# api -> models, database

# Build and run
lament-workspace build
cd packages/api
lament-run src/server.lament
```

---

## Best Practices

### Template Design

1. **Keep templates simple** - Start minimal, add complexity as needed
2. **Use clear variable names** - Make intent obvious
3. **Provide examples** - Include example code in generated projects
4. **Document thoroughly** - Add comments in template files
5. **Test templates** - Generate projects and verify they work

### Project Organization

1. **Use workspaces for related packages** - Group related code
2. **Separate concerns** - Different packages for different responsibilities
3. **Version consistently** - Keep workspace packages in sync
4. **Share common code** - Extract common functionality to shared packages

### Scaffolding

1. **Use interactive mode for new users** - Guided experience
2. **Automate with scripts** - Use non-interactive mode in CI/CD
3. **Customize for your team** - Create team-specific templates
4. **Include CI/CD from start** - Set up automation early

### Workspace Management

1. **Build in dependency order** - Let workspace handle ordering
2. **Test frequently** - Run tests across all packages
3. **Use shared configuration** - DRY principle for build config
4. **Parallel when possible** - Speed up builds and tests

---

## Troubleshooting

### Template Errors

**Problem**: Template syntax error

```
Error: Unbalanced if tags
```

**Solution**: Check that all `{{#if}}` have matching `{{/if}}`

**Problem**: Variable not found

```
Warning: Found empty variable references
```

**Solution**: Ensure all required variables are provided

### Scaffolding Issues

**Problem**: Directory already exists

```
Error: Directory already exists: ./my-project
```

**Solution**: Choose different name or remove existing directory

**Problem**: Missing template

```
Error: Template not found: custom-template
```

**Solution**: Check template name and ensure template directory exists

### Workspace Problems

**Problem**: Circular dependency

```
Error: Circular dependency detected in workspace
```

**Solution**: Review package dependencies and break cycles

**Problem**: Build order issues

```
Error: Package core not found
```

**Solution**: Ensure all dependencies are added to workspace

---

## Reference

### Template Engine Functions

- `TemplateEngine()` - Create engine instance
- `render(template, variables)` - Render template string
- `render_file(template_path, output_path, variables)` - Render file
- `set_variable(key, value)` - Set variable
- `register_helper(name, func)` - Register helper function
- `register_partial(name, template)` - Register partial template

### Scaffolder Functions

- `ProjectScaffolder()` - Create scaffolder
- `scaffold(template, name, config)` - Generate project
- `list_templates()` - List available templates

### Workspace Functions

- `WorkspaceManager()` - Create manager
- `init(name)` - Initialize workspace
- `add_package(path, name)` - Add existing package
- `create_package(name, template)` - Create new package
- `remove_package(name, delete)` - Remove package
- `list_packages()` - List packages
- `build_all(parallel, verbose)` - Build all packages
- `test_all(parallel, verbose)` - Test all packages

---

## See Also

- [Package Manager Guide](./PACKAGE_MANAGER.md)
- [Builder Documentation](./BUILDER.md)
- [Development Tools](../tools/DEVTOOLS.md)
- [Lament Language Guide](./LANGUAGE.md)

---

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)

*"From templates we build, from workspaces we organize, from scaffolds we create the future."*
