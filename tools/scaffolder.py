#!/usr/bin/env python3
"""
Lament Project Scaffolder - Building Structure from Despair

A comprehensive project scaffolding system for quickly creating new Lament projects
from built-in or custom templates.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Import template engine
from tools.template_engine import TemplateEngine, ProjectGenerator, DirectoryTemplate, FileTemplate


# ============================================================================
# LICENSE TEMPLATES
# ============================================================================

LICENSES = {
    'MIT': '''MIT License

Copyright (c) {{year}} {{author}}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
''',

    'Apache-2.0': '''Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/

Copyright {{year}} {{author}}

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
''',

    'GPL-3.0': '''GNU GENERAL PUBLIC LICENSE
Version 3, 29 June 2007

Copyright (C) {{year}} {{author}}

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
''',

    'BSD-3-Clause': '''BSD 3-Clause License

Copyright (c) {{year}}, {{author}}

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
}


# ============================================================================
# CI/CD TEMPLATES
# ============================================================================

GITHUB_ACTIONS_CI = '''name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install Lament
      run: |
        pip install -r requirements.txt

    - name: Run tests
      run: |
        lament-build test

    - name: Run linter
      run: |
        lament-lint src/

  build:
    runs-on: ubuntu-latest
    needs: test

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Build project
      run: |
        lament-build build

    - name: Upload artifacts
      uses: actions/upload-artifact@v3
      with:
        name: {{project_name}}-build
        path: build/
'''


# ============================================================================
# PROJECT CONFIGURATION
# ============================================================================

@dataclass
class ProjectConfig:
    """Configuration for a new project."""
    name: str
    description: str
    author: str
    email: str
    license: str
    version: str = "0.1.0"
    python_version: str = "3.10"
    use_git: bool = True
    use_ci: bool = True
    template_type: str = "library"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for template rendering."""
        return {
            'project_name': self.name,
            'description': self.description,
            'author': self.author,
            'email': self.email,
            'license': self.license,
            'version': self.version,
            'python_version': self.python_version,
            'year': datetime.now().year,
            'date': datetime.now().strftime('%Y-%m-%d'),
        }


# ============================================================================
# INTERACTIVE PROMPTS
# ============================================================================

class InteractivePrompter:
    """Interactive command-line prompts for project configuration."""

    def __init__(self):
        """Initialize prompter."""
        pass

    def prompt_string(self, message: str, default: str = "") -> str:
        """Prompt for a string value."""
        if default:
            prompt = f"{message} [{default}]: "
        else:
            prompt = f"{message}: "

        value = input(prompt).strip()
        return value if value else default

    def prompt_bool(self, message: str, default: bool = True) -> bool:
        """Prompt for a boolean value."""
        default_str = "Y/n" if default else "y/N"
        prompt = f"{message} [{default_str}]: "

        value = input(prompt).strip().lower()
        if not value:
            return default
        return value in ['y', 'yes', 'true', '1']

    def prompt_choice(self, message: str, choices: List[str], default: Optional[str] = None) -> str:
        """Prompt for a choice from a list."""
        print(f"\n{message}")
        for i, choice in enumerate(choices, 1):
            marker = " (default)" if choice == default else ""
            print(f"  {i}. {choice}{marker}")

        while True:
            prompt = "Choose [1-{}]: ".format(len(choices))
            if default:
                prompt = f"Choose [1-{len(choices)}] or press Enter for default: "

            value = input(prompt).strip()

            if not value and default:
                return default

            try:
                index = int(value) - 1
                if 0 <= index < len(choices):
                    return choices[index]
            except ValueError:
                pass

            print("Invalid choice. Please try again.")

    def prompt_config(self) -> ProjectConfig:
        """Interactively prompt for project configuration."""
        print("=" * 60)
        print("Lament Project Scaffolder - Interactive Mode")
        print("=" * 60)
        print()

        # Project name
        name = self.prompt_string("Project name")
        while not name:
            print("Project name is required.")
            name = self.prompt_string("Project name")

        # Description
        description = self.prompt_string(
            "Project description",
            f"A Lament {name} project"
        )

        # Author
        author = self.prompt_string("Author name", self._get_git_config("user.name"))

        # Email
        email = self.prompt_string("Author email", self._get_git_config("user.email"))

        # Template type
        template_type = self.prompt_choice(
            "Project template",
            ["library", "application", "web-server", "cli-tool", "ml-model"],
            default="library"
        )

        # License
        license = self.prompt_choice(
            "License",
            ["MIT", "Apache-2.0", "GPL-3.0", "BSD-3-Clause", "None"],
            default="MIT"
        )

        # Version
        version = self.prompt_string("Initial version", "0.1.0")

        # Git
        use_git = self.prompt_bool("Initialize git repository?", True)

        # CI/CD
        use_ci = self.prompt_bool("Set up CI/CD (GitHub Actions)?", True)

        print()
        return ProjectConfig(
            name=name,
            description=description,
            author=author,
            email=email,
            license=license,
            version=version,
            use_git=use_git,
            use_ci=use_ci,
            template_type=template_type
        )

    def _get_git_config(self, key: str) -> str:
        """Get git config value."""
        try:
            result = subprocess.run(
                ['git', 'config', '--get', key],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except Exception:
            return ""


# ============================================================================
# PROJECT SCAFFOLDER
# ============================================================================

class ProjectScaffolder:
    """Main project scaffolding system."""

    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialize scaffolder.

        Args:
            template_dir: Directory containing templates (defaults to bundled templates)
        """
        if template_dir is None:
            # Use bundled templates
            current_file = Path(__file__).resolve()
            self.template_dir = current_file.parent.parent / "templates"
        else:
            self.template_dir = template_dir

        self.engine = TemplateEngine()
        self.generator = ProjectGenerator(self.template_dir)
        self.prompter = InteractivePrompter()

    def scaffold(self, template: str, name: str, output_dir: Optional[Path] = None,
                config: Optional[ProjectConfig] = None, interactive: bool = False) -> None:
        """
        Scaffold a new project.

        Args:
            template: Template type to use
            name: Project name
            output_dir: Output directory (defaults to ./<name>)
            config: Project configuration (prompts if not provided)
            interactive: Use interactive mode
        """
        # Determine output directory
        if output_dir is None:
            output_dir = Path.cwd() / name

        # Get configuration
        if interactive:
            config = self.prompter.prompt_config()
            name = config.name
            output_dir = Path.cwd() / name
        elif config is None:
            # Create default config
            config = ProjectConfig(
                name=name,
                description=f"A Lament {template} project",
                author="",
                email="",
                license="MIT",
                template_type=template
            )

        # Check if directory exists
        if output_dir.exists():
            print(f"Error: Directory already exists: {output_dir}")
            return

        print(f"\nScaffolding new {template} project: {name}")
        print(f"Output directory: {output_dir}")
        print()

        # Generate from template
        try:
            self.generator.generate(template, output_dir, config.to_dict())
        except ValueError as e:
            print(f"Error: {e}")
            return

        # Generate additional files
        self._generate_readme(output_dir, config)
        if config.license != "None":
            self._generate_license(output_dir, config)
        if config.use_ci:
            self._generate_ci_config(output_dir, config)

        # Initialize git
        if config.use_git:
            self._init_git(output_dir, config)

        print()
        print("=" * 60)
        print(f"Project '{name}' created successfully!")
        print("=" * 60)
        print()
        print("Next steps:")
        print(f"  cd {name}")
        print("  lament-pkg install        # Install dependencies")
        print("  lament-build test         # Run tests")
        print("  lament-build build        # Build project")
        print()

    def _generate_readme(self, output_dir: Path, config: ProjectConfig) -> None:
        """Generate README.md file."""
        template = f'''# {config.name}

{config.description}

## Installation

```bash
# Install dependencies
lament-pkg install

# Build project
lament-build build
```

## Usage

'''

        if config.template_type == "library":
            template += '''```lament
import {config.name}

# Use library here
```
'''
        elif config.template_type == "cli-tool":
            template += f'''```bash
# Run CLI tool
{config.name} --help
```
'''
        elif config.template_type == "web-server":
            template += '''```bash
# Start server
lament-run src/main.lament
```
'''
        elif config.template_type == "application":
            template += '''```bash
# Run application
lament-run src/main.lament
```
'''

        template += f'''
## Development

```bash
# Run tests
lament-build test

# Run linter
lament-lint src/

# Format code
lament-fmt src/
```

## License

{config.license}

## Author

{config.author}
'''

        readme_path = output_dir / "README.md"
        rendered = self.engine.render(template, config.to_dict())
        with open(readme_path, 'w') as f:
            f.write(rendered)

        print(f"Generated README.md")

    def _generate_license(self, output_dir: Path, config: ProjectConfig) -> None:
        """Generate LICENSE file."""
        if config.license not in LICENSES:
            print(f"Warning: Unknown license {config.license}, skipping LICENSE file")
            return

        license_path = output_dir / "LICENSE"
        template = LICENSES[config.license]
        rendered = self.engine.render(template, config.to_dict())

        with open(license_path, 'w') as f:
            f.write(rendered)

        print(f"Generated LICENSE ({config.license})")

    def _generate_ci_config(self, output_dir: Path, config: ProjectConfig) -> None:
        """Generate CI/CD configuration."""
        workflows_dir = output_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        ci_path = workflows_dir / "ci.yml"
        rendered = self.engine.render(GITHUB_ACTIONS_CI, config.to_dict())

        with open(ci_path, 'w') as f:
            f.write(rendered)

        print(f"Generated CI/CD config (.github/workflows/ci.yml)")

    def _init_git(self, output_dir: Path, config: ProjectConfig) -> None:
        """Initialize git repository."""
        try:
            # Initialize repo
            subprocess.run(['git', 'init'], cwd=output_dir, check=True, capture_output=True)

            # Create .gitignore
            gitignore_content = '''# Lament
.lament/
*.lament.pyc
__pycache__/
build/
dist/

# Python
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
'''
            gitignore_path = output_dir / ".gitignore"
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)

            # Initial commit
            subprocess.run(['git', 'add', '.'], cwd=output_dir, check=True, capture_output=True)
            subprocess.run(
                ['git', 'commit', '-m', 'Initial commit from lament-new'],
                cwd=output_dir,
                check=True,
                capture_output=True
            )

            print("Initialized git repository")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to initialize git: {e}")
        except FileNotFoundError:
            print("Warning: git not found, skipping repository initialization")

    def list_templates(self) -> List[str]:
        """List available templates."""
        templates = []

        if not self.template_dir.exists():
            return templates

        for item in self.template_dir.iterdir():
            if item.is_dir() and (item / "template.json").exists():
                templates.append(item.name)

        return sorted(templates)


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Project Scaffolder - Building Structure from Despair",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-new library my-lib                    Create library project
  lament-new application my-app --interactive  Create with interactive prompts
  lament-new web-server api-server             Create web server project
  lament-new cli-tool my-cli                   Create CLI tool project
  lament-new ml-model my-model                 Create ML model project
  lament-new --list                            List available templates
        """
    )

    parser.add_argument('--version', action='version', version='lament-new 1.0.0')

    parser.add_argument(
        'template',
        nargs='?',
        help='Template type (library, application, web-server, cli-tool, ml-model)'
    )

    parser.add_argument(
        'name',
        nargs='?',
        help='Project name'
    )

    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Interactive mode with prompts'
    )

    parser.add_argument(
        '-o', '--output',
        type=Path,
        help='Output directory (default: ./<name>)'
    )

    parser.add_argument(
        '--author',
        help='Author name'
    )

    parser.add_argument(
        '--email',
        help='Author email'
    )

    parser.add_argument(
        '--license',
        choices=['MIT', 'Apache-2.0', 'GPL-3.0', 'BSD-3-Clause', 'None'],
        default='MIT',
        help='License (default: MIT)'
    )

    parser.add_argument(
        '--no-git',
        action='store_true',
        help='Do not initialize git repository'
    )

    parser.add_argument(
        '--no-ci',
        action='store_true',
        help='Do not generate CI/CD configuration'
    )

    parser.add_argument(
        '--list',
        action='store_true',
        help='List available templates'
    )

    args = parser.parse_args()

    # Create scaffolder
    scaffolder = ProjectScaffolder()

    # List templates
    if args.list:
        templates = scaffolder.list_templates()
        print("Available templates:")
        for template in templates:
            print(f"  - {template}")
        return

    # Validate arguments
    if not args.interactive and (not args.template or not args.name):
        parser.error("template and name are required (or use --interactive)")
        return

    # Create configuration
    if args.interactive:
        config = None  # Will be prompted
        template = None
        name = None
    else:
        config = ProjectConfig(
            name=args.name,
            description=f"A Lament {args.template} project",
            author=args.author or "",
            email=args.email or "",
            license=args.license,
            use_git=not args.no_git,
            use_ci=not args.no_ci,
            template_type=args.template
        )
        template = args.template
        name = args.name

    # Scaffold project
    scaffolder.scaffold(
        template=template,
        name=name,
        output_dir=args.output,
        config=config,
        interactive=args.interactive
    )


if __name__ == '__main__':
    main()
