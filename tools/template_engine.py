#!/usr/bin/env python3
"""
Lament Template Engine - Creating from Templates, Mourning Manual Boilerplate

A powerful template engine for generating project files and structures.
Supports variable substitution, conditional blocks, loops, and file generation.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import os
import re
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import textwrap


# ============================================================================
# TEMPLATE SYNTAX
# ============================================================================
# Variables: {{variable_name}}
# Conditionals: {{#if condition}}...{{/if}}
# Else: {{#if condition}}...{{#else}}...{{/if}}
# Loops: {{#each items}}{{this}}{{/each}}
# Comments: {{! This is a comment }}
# Includes: {{> partial_name}}
# ============================================================================


@dataclass
class TemplateContext:
    """Context for template rendering with variables and helpers."""
    variables: Dict[str, Any] = field(default_factory=dict)
    helpers: Dict[str, Callable] = field(default_factory=dict)
    partials: Dict[str, str] = field(default_factory=dict)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a variable from context, supporting dot notation."""
        parts = key.split('.')
        value = self.variables

        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return default

            if value is None:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """Set a variable in context."""
        self.variables[key] = value

    def register_helper(self, name: str, func: Callable) -> None:
        """Register a template helper function."""
        self.helpers[name] = func

    def register_partial(self, name: str, template: str) -> None:
        """Register a partial template."""
        self.partials[name] = template

    def copy(self) -> 'TemplateContext':
        """Create a copy of this context."""
        return TemplateContext(
            variables=self.variables.copy(),
            helpers=self.helpers.copy(),
            partials=self.partials.copy()
        )


class TemplateParser:
    """Parser for template syntax."""

    # Regex patterns
    VARIABLE_PATTERN = re.compile(r'\{\{([^#/>!][^}]*)\}\}')
    COMMENT_PATTERN = re.compile(r'\{\{!.*?\}\}', re.DOTALL)
    IF_PATTERN = re.compile(r'\{\{#if\s+([^}]+)\}\}(.*?)(?:\{\{#else\}\}(.*?))?\{\{/if\}\}', re.DOTALL)
    EACH_PATTERN = re.compile(r'\{\{#each\s+([^}]+)\}\}(.*?)\{\{/each\}\}', re.DOTALL)
    PARTIAL_PATTERN = re.compile(r'\{\{>\s*([^}]+)\}\}')

    def __init__(self):
        """Initialize parser."""
        pass

    def parse(self, template: str, context: TemplateContext) -> str:
        """Parse and render a template."""
        # Remove comments first
        result = self.COMMENT_PATTERN.sub('', template)

        # Process partials
        result = self._process_partials(result, context)

        # Process conditionals
        result = self._process_conditionals(result, context)

        # Process loops
        result = self._process_loops(result, context)

        # Process variables
        result = self._process_variables(result, context)

        return result

    def _process_partials(self, template: str, context: TemplateContext) -> str:
        """Process partial includes."""
        def replace_partial(match):
            partial_name = match.group(1).strip()
            if partial_name in context.partials:
                return context.partials[partial_name]
            return f"{{{{> {partial_name} NOT FOUND}}}}"

        return self.PARTIAL_PATTERN.sub(replace_partial, template)

    def _process_conditionals(self, template: str, context: TemplateContext) -> str:
        """Process if/else conditionals."""
        def replace_conditional(match):
            condition = match.group(1).strip()
            if_block = match.group(2)
            else_block = match.group(3) or ""

            # Evaluate condition
            if self._evaluate_condition(condition, context):
                return self.parse(if_block, context)
            else:
                return self.parse(else_block, context)

        # Process nested conditionals from inside out
        max_iterations = 100
        iteration = 0
        while self.IF_PATTERN.search(template) and iteration < max_iterations:
            template = self.IF_PATTERN.sub(replace_conditional, template)
            iteration += 1

        return template

    def _process_loops(self, template: str, context: TemplateContext) -> str:
        """Process each loops."""
        def replace_loop(match):
            items_expr = match.group(1).strip()
            loop_body = match.group(2)

            # Get items from context
            items = context.get(items_expr, [])
            if not isinstance(items, (list, tuple)):
                items = [items]

            # Render loop body for each item
            results = []
            for i, item in enumerate(items):
                # Create loop context
                loop_context = context.copy()
                loop_context.set('this', item)
                loop_context.set('index', i)
                loop_context.set('first', i == 0)
                loop_context.set('last', i == len(items) - 1)

                # If item is a dict, add its keys to context
                if isinstance(item, dict):
                    for key, value in item.items():
                        loop_context.set(key, value)

                results.append(self.parse(loop_body, loop_context))

            return ''.join(results)

        # Process nested loops from inside out
        max_iterations = 100
        iteration = 0
        while self.EACH_PATTERN.search(template) and iteration < max_iterations:
            template = self.EACH_PATTERN.sub(replace_loop, template)
            iteration += 1

        return template

    def _process_variables(self, template: str, context: TemplateContext) -> str:
        """Process variable substitutions."""
        def replace_variable(match):
            var_expr = match.group(1).strip()

            # Check for helper function call
            if '(' in var_expr:
                return self._call_helper(var_expr, context)

            # Simple variable lookup
            value = context.get(var_expr, '')
            return str(value) if value is not None else ''

        return self.VARIABLE_PATTERN.sub(replace_variable, template)

    def _evaluate_condition(self, condition: str, context: TemplateContext) -> bool:
        """Evaluate a conditional expression."""
        # Handle negation
        if condition.startswith('!'):
            return not self._evaluate_condition(condition[1:].strip(), context)

        # Handle comparison operators
        for op in ['==', '!=', '>', '<', '>=', '<=']:
            if op in condition:
                left, right = condition.split(op, 1)
                left_val = self._get_value(left.strip(), context)
                right_val = self._get_value(right.strip(), context)

                if op == '==':
                    return left_val == right_val
                elif op == '!=':
                    return left_val != right_val
                elif op == '>':
                    return left_val > right_val
                elif op == '<':
                    return left_val < right_val
                elif op == '>=':
                    return left_val >= right_val
                elif op == '<=':
                    return left_val <= right_val

        # Simple truthiness check
        value = context.get(condition)
        return bool(value)

    def _get_value(self, expr: str, context: TemplateContext) -> Any:
        """Get value from expression (variable or literal)."""
        expr = expr.strip()

        # String literal
        if (expr.startswith('"') and expr.endswith('"')) or \
           (expr.startswith("'") and expr.endswith("'")):
            return expr[1:-1]

        # Number literal
        try:
            if '.' in expr:
                return float(expr)
            return int(expr)
        except ValueError:
            pass

        # Boolean literal
        if expr.lower() == 'true':
            return True
        if expr.lower() == 'false':
            return False

        # Variable
        return context.get(expr)

    def _call_helper(self, expr: str, context: TemplateContext) -> str:
        """Call a helper function."""
        # Parse function call: helper_name(arg1, arg2, ...)
        match = re.match(r'(\w+)\((.*?)\)', expr)
        if not match:
            return expr

        helper_name = match.group(1)
        args_str = match.group(2)

        if helper_name not in context.helpers:
            return f"[HELPER {helper_name} NOT FOUND]"

        # Parse arguments
        args = []
        if args_str.strip():
            for arg in args_str.split(','):
                args.append(self._get_value(arg.strip(), context))

        # Call helper
        try:
            result = context.helpers[helper_name](*args)
            return str(result) if result is not None else ''
        except Exception as e:
            return f"[HELPER ERROR: {e}]"


class TemplateValidator:
    """Validates template syntax and structure."""

    def __init__(self):
        """Initialize validator."""
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate(self, template: str) -> Tuple[bool, List[str], List[str]]:
        """
        Validate template syntax.
        Returns (is_valid, errors, warnings).
        """
        self.errors = []
        self.warnings = []

        # Check for balanced tags
        self._check_balanced_tags(template, 'if')
        self._check_balanced_tags(template, 'each')

        # Check for undefined variables (warning only)
        self._check_variable_usage(template)

        # Check for syntax errors
        self._check_syntax_errors(template)

        return len(self.errors) == 0, self.errors, self.warnings

    def _check_balanced_tags(self, template: str, tag: str) -> None:
        """Check if opening and closing tags are balanced."""
        open_pattern = re.compile(rf'\{{\{{#{tag}\s+[^}}]+\}}\}}')
        close_pattern = re.compile(rf'\{{\{{/{tag}\}}\}}')

        open_count = len(open_pattern.findall(template))
        close_count = len(close_pattern.findall(template))

        if open_count != close_count:
            self.errors.append(
                f"Unbalanced {tag} tags: {open_count} opening, {close_count} closing"
            )

    def _check_variable_usage(self, template: str) -> None:
        """Check for potential undefined variables."""
        # This is a basic check - just warns about empty variable references
        empty_vars = re.findall(r'\{\{\s*\}\}', template)
        if empty_vars:
            self.warnings.append(f"Found {len(empty_vars)} empty variable references")

    def _check_syntax_errors(self, template: str) -> None:
        """Check for common syntax errors."""
        # Unclosed tags
        unclosed = re.findall(r'\{\{[^}]*$', template)
        if unclosed:
            self.errors.append("Found unclosed template tags")

        # Invalid tag syntax
        invalid_tags = re.findall(r'\{\{[#/][^\w]', template)
        if invalid_tags:
            self.errors.append("Found invalid tag syntax")


class TemplateEngine:
    """Main template engine for rendering templates."""

    def __init__(self):
        """Initialize template engine."""
        self.parser = TemplateParser()
        self.validator = TemplateValidator()
        self.context = TemplateContext()
        self._register_default_helpers()

    def _register_default_helpers(self) -> None:
        """Register default helper functions."""
        self.context.register_helper('upper', lambda s: str(s).upper())
        self.context.register_helper('lower', lambda s: str(s).lower())
        self.context.register_helper('capitalize', lambda s: str(s).capitalize())
        self.context.register_helper('title', lambda s: str(s).title())
        self.context.register_helper('len', lambda s: len(s) if s else 0)
        self.context.register_helper('date', lambda: datetime.now().strftime('%Y-%m-%d'))
        self.context.register_helper('datetime', lambda: datetime.now().isoformat())
        self.context.register_helper('year', lambda: datetime.now().year)

        # String helpers
        self.context.register_helper('snake_case', self._snake_case)
        self.context.register_helper('camel_case', self._camel_case)
        self.context.register_helper('pascal_case', self._pascal_case)
        self.context.register_helper('kebab_case', self._kebab_case)

    def _snake_case(self, s: str) -> str:
        """Convert to snake_case."""
        s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', s)
        s = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', s)
        s = s.replace('-', '_').replace(' ', '_')
        return s.lower()

    def _camel_case(self, s: str) -> str:
        """Convert to camelCase."""
        words = re.split(r'[-_\s]+', s)
        return words[0].lower() + ''.join(w.capitalize() for w in words[1:])

    def _pascal_case(self, s: str) -> str:
        """Convert to PascalCase."""
        words = re.split(r'[-_\s]+', s)
        return ''.join(w.capitalize() for w in words)

    def _kebab_case(self, s: str) -> str:
        """Convert to kebab-case."""
        s = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1-\2', s)
        s = re.sub(r'([a-z\d])([A-Z])', r'\1-\2', s)
        s = s.replace('_', '-').replace(' ', '-')
        return s.lower()

    def render(self, template: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """
        Render a template with variables.

        Args:
            template: Template string
            variables: Variables to use in rendering

        Returns:
            Rendered template string
        """
        # Update context with variables
        if variables:
            for key, value in variables.items():
                self.context.set(key, value)

        # Validate template
        is_valid, errors, warnings = self.validator.validate(template)
        if not is_valid:
            raise ValueError(f"Template validation failed: {', '.join(errors)}")

        # Render template
        return self.parser.parse(template, self.context)

    def render_file(self, template_path: Path, output_path: Path,
                   variables: Optional[Dict[str, Any]] = None) -> None:
        """
        Render a template file to an output file.

        Args:
            template_path: Path to template file
            output_path: Path to output file
            variables: Variables to use in rendering
        """
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()

        rendered = self.render(template, variables)

        # Create parent directory if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered)

    def set_variable(self, key: str, value: Any) -> None:
        """Set a template variable."""
        self.context.set(key, value)

    def set_variables(self, variables: Dict[str, Any]) -> None:
        """Set multiple template variables."""
        for key, value in variables.items():
            self.context.set(key, value)

    def register_helper(self, name: str, func: Callable) -> None:
        """Register a custom helper function."""
        self.context.register_helper(name, func)

    def register_partial(self, name: str, template: str) -> None:
        """Register a partial template."""
        self.context.register_partial(name, template)

    def register_partial_file(self, name: str, template_path: Path) -> None:
        """Register a partial from a file."""
        with open(template_path, 'r', encoding='utf-8') as f:
            template = f.read()
        self.register_partial(name, template)


@dataclass
class FileTemplate:
    """Represents a file to be generated from a template."""
    source: str  # Source template path (relative to template dir)
    destination: str  # Destination path (relative to project root, may contain template vars)
    executable: bool = False

    def resolve_destination(self, variables: Dict[str, Any]) -> str:
        """Resolve template variables in destination path."""
        engine = TemplateEngine()
        engine.set_variables(variables)
        return engine.render(self.destination)


@dataclass
class DirectoryTemplate:
    """Represents a directory structure template."""
    name: str
    description: str
    files: List[FileTemplate] = field(default_factory=list)
    directories: List[str] = field(default_factory=list)
    post_generation_hooks: List[str] = field(default_factory=list)
    required_variables: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'description': self.description,
            'files': [
                {
                    'source': f.source,
                    'destination': f.destination,
                    'executable': f.executable
                }
                for f in self.files
            ],
            'directories': self.directories,
            'post_generation_hooks': self.post_generation_hooks,
            'required_variables': self.required_variables
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'DirectoryTemplate':
        """Create from dictionary."""
        files = [
            FileTemplate(
                source=f['source'],
                destination=f['destination'],
                executable=f.get('executable', False)
            )
            for f in data.get('files', [])
        ]

        return DirectoryTemplate(
            name=data['name'],
            description=data['description'],
            files=files,
            directories=data.get('directories', []),
            post_generation_hooks=data.get('post_generation_hooks', []),
            required_variables=data.get('required_variables', [])
        )


class ProjectGenerator:
    """Generates project structures from templates."""

    def __init__(self, template_dir: Path):
        """
        Initialize generator.

        Args:
            template_dir: Directory containing templates
        """
        self.template_dir = template_dir
        self.engine = TemplateEngine()

    def load_template(self, template_name: str) -> DirectoryTemplate:
        """
        Load a directory template.

        Args:
            template_name: Name of template to load

        Returns:
            Loaded directory template
        """
        template_path = self.template_dir / template_name
        if not template_path.exists():
            raise ValueError(f"Template not found: {template_name}")

        # Load template metadata
        meta_path = template_path / "template.json"
        if not meta_path.exists():
            raise ValueError(f"Template metadata not found: {meta_path}")

        with open(meta_path, 'r') as f:
            data = json.load(f)

        return DirectoryTemplate.from_dict(data)

    def generate(self, template_name: str, output_dir: Path,
                variables: Dict[str, Any]) -> None:
        """
        Generate a project from a template.

        Args:
            template_name: Name of template to use
            output_dir: Directory to generate project in
            variables: Variables for template rendering
        """
        # Load template
        template = self.load_template(template_name)

        # Validate required variables
        missing = [v for v in template.required_variables if v not in variables]
        if missing:
            raise ValueError(f"Missing required variables: {', '.join(missing)}")

        # Set variables in engine
        self.engine.set_variables(variables)

        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create directories
        for directory in template.directories:
            dir_path = output_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)

        # Generate files
        template_base = self.template_dir / template_name
        for file_template in template.files:
            source_path = template_base / file_template.source

            # Resolve destination path
            dest_rel = file_template.resolve_destination(variables)
            dest_path = output_dir / dest_rel

            # Create parent directory
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Render file
            if source_path.suffix in ['.lament', '.py', '.md', '.json', '.txt', '.sh', '.yml', '.yaml']:
                # Text file - render template
                self.engine.render_file(source_path, dest_path, variables)
            else:
                # Binary file - copy as-is
                shutil.copy2(source_path, dest_path)

            # Set executable if needed
            if file_template.executable:
                os.chmod(dest_path, 0o755)

        print(f"Generated project from template '{template_name}' at {output_dir}")

        # Run post-generation hooks
        self._run_hooks(template.post_generation_hooks, output_dir, variables)

    def _run_hooks(self, hooks: List[str], output_dir: Path,
                  variables: Dict[str, Any]) -> None:
        """Run post-generation hooks."""
        for hook in hooks:
            print(f"Running hook: {hook}")
            # Render hook command with variables
            command = self.engine.render(hook, variables)

            # Execute hook
            import subprocess
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=output_dir,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    print(f"Hook failed: {result.stderr}")
                else:
                    print(f"Hook succeeded: {result.stdout}")
            except Exception as e:
                print(f"Hook error: {e}")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def render_template_string(template: str, variables: Dict[str, Any]) -> str:
    """
    Convenience function to render a template string.

    Args:
        template: Template string
        variables: Variables for rendering

    Returns:
        Rendered string
    """
    engine = TemplateEngine()
    return engine.render(template, variables)


def render_template_file(template_path: Path, output_path: Path,
                         variables: Dict[str, Any]) -> None:
    """
    Convenience function to render a template file.

    Args:
        template_path: Path to template file
        output_path: Path to output file
        variables: Variables for rendering
    """
    engine = TemplateEngine()
    engine.render_file(template_path, output_path, variables)


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Example template
    template = """
# {{project_name}}

{{! This is a comment }}
Description: {{description}}

## Features

{{#if has_features}}
{{#each features}}
- {{this}}
{{/each}}
{{/if}}

{{#if !has_features}}
No features yet.
{{/if}}

## Author

{{author}} ({{year}})

## License

{{upper(license)}}
"""

    # Render example
    engine = TemplateEngine()
    result = engine.render(template, {
        'project_name': 'My Awesome Project',
        'description': 'A project that does amazing things',
        'has_features': True,
        'features': ['Fast', 'Reliable', 'Easy to use'],
        'author': 'Zephyr',
        'license': 'mit'
    })

    print(result)
    print("\n" + "=" * 80 + "\n")

    # Validation example
    invalid_template = "{{#if test}}unclosed"
    validator = TemplateValidator()
    is_valid, errors, warnings = validator.validate(invalid_template)
    print(f"Valid: {is_valid}")
    print(f"Errors: {errors}")
    print(f"Warnings: {warnings}")
