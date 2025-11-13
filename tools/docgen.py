"""
Lament Language Documentation Generator
=======================================

Automatic documentation generator for Lament programs.

Features:
- Extract docstrings from functions
- Generate HTML documentation
- Cross-reference links
- Symbol index
- Type annotations (where available)
- Example code extraction
- Markdown support

Usage:
    python -m tools.docgen <file.lament>
    lament-doc <file.lament>

Options:
    --output DIR    Output directory (default: ./docs)
    --format FORMAT Output format: html, markdown, pdf (default: html)
    --title TITLE   Documentation title
    --auto          Auto-generate docs from all modules
    --serve         Start live documentation server
    --port PORT     Server port (default: 8000)
    --watch         Watch for file changes and regenerate
    --deps          Generate module dependency graph
    --search        Generate search index

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
import re
import json
import http.server
import socketserver
import threading
import time
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import fnmatch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.lexer import Lexer
from lament.parser import (
    Parser, ASTNode, FunctionDef, VariableDecl
)


@dataclass
class FunctionDoc:
    """Documentation for a function."""
    name: str
    params: List[str]
    docstring: Optional[str] = None
    examples: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    source: Optional[str] = None


@dataclass
class VariableDoc:
    """Documentation for a variable."""
    name: str
    initial_value: str
    docstring: Optional[str] = None
    is_temporal: bool = True


@dataclass
class ModuleDoc:
    """Documentation for entire module."""
    title: str
    description: Optional[str] = None
    functions: List[FunctionDoc] = field(default_factory=list)
    variables: List[VariableDoc] = field(default_factory=list)
    source_file: Optional[str] = None
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)


@dataclass
class ProjectDoc:
    """Documentation for entire project."""
    title: str
    modules: Dict[str, ModuleDoc] = field(default_factory=dict)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)


class DocGenerator:
    """Documentation generator for Lament code.

    Extracts documentation from:
    - Comments before functions/variables
    - Inline comments
    - Docstrings (multi-line comments)
    - Example code

    Generates:
    - HTML documentation
    - Markdown documentation
    - Symbol index
    - Cross-references

    Example:
        generator = DocGenerator()
        docs = generator.extract_docs(ast, source)
        generator.generate_html(docs, output_dir)
    """

    def __init__(self):
        self.cross_references = {}  # symbol -> locations

    def extract_docs(self, ast, source, source_file=None):
        """Extract documentation from AST and source.

        Args:
            ast: Parsed AST
            source: Original source code
            source_file: Optional source filename

        Returns:
            ModuleDoc
        """
        source_lines = source.split('\n')

        # Extract module-level docstring
        module_doc = self.extract_module_docstring(source)

        # Extract function and variable docs
        functions = []
        variables = []

        for i, stmt in enumerate(ast):
            if isinstance(stmt, FunctionDef):
                func_doc = self.extract_function_doc(stmt, source_lines, i)
                functions.append(func_doc)

            elif isinstance(stmt, VariableDecl):
                var_doc = self.extract_variable_doc(stmt, source_lines, i)
                variables.append(var_doc)

        return ModuleDoc(
            title=self.extract_title(source) or "Lament Documentation",
            description=module_doc,
            functions=functions,
            variables=variables,
            source_file=source_file
        )

    def extract_module_docstring(self, source):
        """Extract module-level docstring from source."""
        # Look for comment block at start of file
        lines = source.split('\n')
        docstring_lines = []

        in_docstring = False
        for line in lines:
            stripped = line.strip()

            # Multi-line comment start
            if stripped.startswith('/*'):
                in_docstring = True
                content = stripped[2:].strip()
                if content and not content.startswith('*'):
                    docstring_lines.append(content)
                continue

            # Multi-line comment end
            if in_docstring and '*/' in stripped:
                content = stripped.replace('*/', '').strip()
                if content and not content.startswith('*'):
                    docstring_lines.append(content)
                break

            # Inside multi-line comment
            if in_docstring:
                content = stripped.lstrip('*').strip()
                if content:
                    docstring_lines.append(content)
                continue

            # Single-line comment
            if stripped.startswith('#'):
                docstring_lines.append(stripped[1:].strip())
            elif stripped and not stripped.startswith('#'):
                # Hit non-comment code
                break

        return '\n'.join(docstring_lines) if docstring_lines else None

    def extract_title(self, source):
        """Extract title from source comments."""
        lines = source.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            if line.strip().startswith('# ') and len(line.strip()) < 100:
                return line.strip()[2:].strip()
        return None

    def extract_function_doc(self, func_def, source_lines, stmt_index):
        """Extract documentation for a function.

        Args:
            func_def: FunctionDef AST node
            source_lines: Source code lines
            stmt_index: Statement index in AST

        Returns:
            FunctionDoc
        """
        # Look for comments before function
        docstring = self.find_preceding_comment(source_lines, stmt_index)

        # Extract examples from docstring
        examples = self.extract_examples(docstring) if docstring else []

        # Extract return info
        returns = self.extract_returns(docstring) if docstring else None

        # Get source code
        source = self.extract_function_source(func_def, source_lines)

        return FunctionDoc(
            name=func_def.name,
            params=func_def.params,
            docstring=docstring,
            examples=examples,
            returns=returns,
            source=source
        )

    def extract_variable_doc(self, var_decl, source_lines, stmt_index):
        """Extract documentation for a variable."""
        docstring = self.find_preceding_comment(source_lines, stmt_index)

        return VariableDoc(
            name=var_decl.name,
            initial_value=self.format_value(var_decl.value),
            docstring=docstring,
            is_temporal=True
        )

    def find_preceding_comment(self, source_lines, stmt_index):
        """Find comment immediately before a statement."""
        comment_lines = []

        # Look backwards for comments
        for i in range(stmt_index - 1, -1, -1):
            if i >= len(source_lines):
                continue

            line = source_lines[i].strip()

            if not line:
                continue

            if line.startswith('#'):
                comment_lines.insert(0, line[1:].strip())
            elif line.startswith('/*'):
                # Multi-line comment
                in_comment = True
                j = i
                while j < len(source_lines) and in_comment:
                    comment_line = source_lines[j].strip()
                    if '*/' in comment_line:
                        in_comment = False
                    content = comment_line.replace('/*', '').replace('*/', '').lstrip('*').strip()
                    if content:
                        comment_lines.insert(0, content)
                    j += 1
                break
            else:
                # Hit non-comment
                break

        return '\n'.join(comment_lines) if comment_lines else None

    def extract_examples(self, docstring):
        """Extract example code from docstring."""
        if not docstring:
            return []

        examples = []
        in_example = False
        example_lines = []

        for line in docstring.split('\n'):
            if 'Example:' in line or 'example:' in line:
                in_example = True
                continue

            if in_example:
                if line.strip() and not line.startswith(' '):
                    # End of example
                    if example_lines:
                        examples.append('\n'.join(example_lines))
                    in_example = False
                    example_lines = []
                else:
                    example_lines.append(line)

        if example_lines:
            examples.append('\n'.join(example_lines))

        return examples

    def extract_returns(self, docstring):
        """Extract return information from docstring."""
        if not docstring:
            return None

        for line in docstring.split('\n'):
            if 'Returns:' in line or 'returns:' in line:
                return line.split(':', 1)[1].strip()

        return None

    def extract_function_source(self, func_def, source_lines):
        """Extract function source code."""
        # This is approximate - would need line tracking in AST
        # For now, return a simplified version
        params = ', '.join(func_def.params)
        return f"sigh {func_def.name}({params}) {{\n  ...\n}}"

    def format_value(self, value_node):
        """Format AST value node as string."""
        from lament.parser import NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral

        if isinstance(value_node, NumberLiteral):
            return str(value_node.value)
        elif isinstance(value_node, StringLiteral):
            return f'"{value_node.value}"'
        elif isinstance(value_node, BoolLiteral):
            return value_node.value
        elif isinstance(value_node, VoidLiteral):
            return 'void'
        else:
            return '...'

    def generate_html(self, docs, output_dir):
        """Generate HTML documentation.

        Args:
            docs: ModuleDoc
            output_dir: Output directory
        """
        os.makedirs(output_dir, exist_ok=True)

        # Generate main page
        html = self.render_html_template(docs)

        output_file = os.path.join(output_dir, 'index.html')
        with open(output_file, 'w') as f:
            f.write(html)

        # Generate CSS
        css = self.generate_css()
        css_file = os.path.join(output_dir, 'style.css')
        with open(css_file, 'w') as f:
            f.write(css)

        print(f"Documentation generated in {output_dir}")
        print(f"Open {output_file} in your browser")

    def render_html_template(self, docs):
        """Render HTML documentation template."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{docs.title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>💔 {docs.title}</h1>
            <p class="subtitle">Lament Language Documentation</p>
        </header>

        <nav>
            <h2>Navigation</h2>
            <ul>
                <li><a href="#overview">Overview</a></li>
                <li><a href="#functions">Functions</a></li>
                <li><a href="#variables">Variables</a></li>
            </ul>
        </nav>

        <main>
"""

        # Overview section
        if docs.description:
            html += f"""
            <section id="overview">
                <h2>Overview</h2>
                <div class="description">
                    {self.format_markdown(docs.description)}
                </div>
            </section>
"""

        # Functions section
        if docs.functions:
            html += """
            <section id="functions">
                <h2>Functions</h2>
"""

            for func in docs.functions:
                params = ', '.join(func.params)
                html += f"""
                <div class="function">
                    <h3 id="func-{func.name}">
                        <code>{func.name}({params})</code>
                    </h3>
"""

                if func.docstring:
                    html += f"""
                    <div class="docstring">
                        {self.format_markdown(func.docstring)}
                    </div>
"""

                if func.params:
                    html += """
                    <h4>Parameters</h4>
                    <ul class="params">
"""
                    for param in func.params:
                        html += f"                        <li><code>{param}</code></li>\n"
                    html += """
                    </ul>
"""

                if func.returns:
                    html += f"""
                    <h4>Returns</h4>
                    <p>{func.returns}</p>
"""

                if func.examples:
                    html += """
                    <h4>Examples</h4>
"""
                    for example in func.examples:
                        html += f"""
                    <pre><code class="lament">{example}</code></pre>
"""

                if func.source:
                    html += f"""
                    <details>
                        <summary>Source Code</summary>
                        <pre><code class="lament">{func.source}</code></pre>
                    </details>
"""

                html += """
                </div>
"""

            html += """
            </section>
"""

        # Variables section
        if docs.variables:
            html += """
            <section id="variables">
                <h2>Variables</h2>
                <table class="variables">
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Initial Value</th>
                            <th>Description</th>
                        </tr>
                    </thead>
                    <tbody>
"""

            for var in docs.variables:
                description = var.docstring or "(no description)"
                html += f"""
                        <tr>
                            <td><code>{var.name}</code></td>
                            <td><code>{var.initial_value}</code></td>
                            <td>{description}</td>
                        </tr>
"""

            html += """
                    </tbody>
                </table>
            </section>
"""

        # Footer
        html += f"""
        </main>

        <footer>
            <p>Generated by Lament Documentation Generator</p>
            <p>Generated on {now}</p>
        </footer>
    </div>
</body>
</html>
"""

        return html

    def generate_css(self):
        """Generate CSS stylesheet."""
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Georgia', serif;
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: #e0e0e0;
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    padding: 40px 0;
    border-bottom: 2px solid #ff6b9d;
}

header h1 {
    font-size: 3em;
    color: #ff6b9d;
    margin-bottom: 10px;
}

.subtitle {
    color: #ffd93d;
    font-style: italic;
}

nav {
    background: #2a2a3e;
    padding: 20px;
    border-radius: 10px;
    margin: 20px 0;
}

nav h2 {
    color: #ffd93d;
    margin-bottom: 15px;
}

nav ul {
    list-style: none;
}

nav li {
    margin: 10px 0;
}

nav a {
    color: #e0e0e0;
    text-decoration: none;
    transition: color 0.3s;
}

nav a:hover {
    color: #ff6b9d;
}

main {
    padding: 20px 0;
}

section {
    margin: 40px 0;
}

section h2 {
    color: #ffd93d;
    font-size: 2em;
    margin-bottom: 20px;
    border-bottom: 2px solid #ffd93d;
    padding-bottom: 10px;
}

.function {
    background: #2a2a3e;
    padding: 25px;
    border-radius: 10px;
    margin: 20px 0;
    border-left: 4px solid #ff6b9d;
}

.function h3 {
    color: #ff6b9d;
    margin-bottom: 15px;
}

.function h4 {
    color: #ffd93d;
    margin-top: 20px;
    margin-bottom: 10px;
}

.docstring {
    color: #c0c0c0;
    margin: 15px 0;
}

.params {
    list-style: none;
    margin-left: 20px;
}

.params li {
    margin: 5px 0;
}

code {
    background: #1a1a2e;
    padding: 2px 6px;
    border-radius: 3px;
    color: #6fe7dd;
    font-family: 'Courier New', monospace;
}

pre {
    background: #1a1a2e;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    margin: 15px 0;
}

pre code {
    background: none;
    padding: 0;
}

details {
    margin-top: 15px;
}

summary {
    cursor: pointer;
    color: #ffd93d;
    padding: 10px;
    background: #1a1a2e;
    border-radius: 5px;
}

summary:hover {
    background: #2a2a3e;
}

.variables {
    width: 100%;
    border-collapse: collapse;
    background: #2a2a3e;
    border-radius: 10px;
    overflow: hidden;
}

.variables th {
    background: #1a1a2e;
    color: #ffd93d;
    padding: 15px;
    text-align: left;
}

.variables td {
    padding: 15px;
    border-top: 1px solid #3a3a4e;
}

footer {
    text-align: center;
    padding: 40px 0;
    color: #888;
    border-top: 1px solid #3a3a4e;
    margin-top: 60px;
}
"""

    def format_markdown(self, text):
        """Convert simple markdown to HTML."""
        if not text:
            return ""

        # Convert to paragraphs
        paragraphs = text.split('\n\n')
        html_parts = []

        for para in paragraphs:
            # Bold
            para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)
            # Italic
            para = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)
            # Code
            para = re.sub(r'`(.+?)`', r'<code>\1</code>', para)

            html_parts.append(f'<p>{para}</p>')

        return '\n'.join(html_parts)

    def generate_markdown(self, docs, output_file):
        """Generate Markdown documentation.

        Args:
            docs: ModuleDoc
            output_file: Output file path
        """
        md = f"# {docs.title}\n\n"

        if docs.description:
            md += f"{docs.description}\n\n"

        # Functions
        if docs.functions:
            md += "## Functions\n\n"

            for func in docs.functions:
                params = ', '.join(func.params)
                md += f"### `{func.name}({params})`\n\n"

                if func.docstring:
                    md += f"{func.docstring}\n\n"

                if func.params:
                    md += "**Parameters:**\n\n"
                    for param in func.params:
                        md += f"- `{param}`\n"
                    md += "\n"

                if func.returns:
                    md += f"**Returns:** {func.returns}\n\n"

                if func.examples:
                    md += "**Examples:**\n\n"
                    for example in func.examples:
                        md += f"```lament\n{example}\n```\n\n"

        # Variables
        if docs.variables:
            md += "## Variables\n\n"

            for var in docs.variables:
                md += f"### `{var.name}`\n\n"
                md += f"Initial value: `{var.initial_value}`\n\n"
                if var.docstring:
                    md += f"{var.docstring}\n\n"

        with open(output_file, 'w') as f:
            f.write(md)

        print(f"Markdown documentation generated: {output_file}")

    def generate_project_docs(self, project_path, output_dir, options=None):
        """
        Generate documentation for entire project.

        Args:
            project_path: Path to project directory
            output_dir: Output directory
            options: Optional generation options
        """
        options = options or {}
        project_path = Path(project_path)

        # Discover all Lament files
        lament_files = list(project_path.rglob('*.lament'))

        if not lament_files:
            print(f"No Lament files found in {project_path}")
            return

        print(f"Generating documentation for {len(lament_files)} files...")

        # Generate docs for each module
        project_doc = ProjectDoc(title=options.get('title', 'Project Documentation'))

        for file_path in lament_files:
            try:
                with open(file_path, 'r') as f:
                    source = f.read()

                lexer = Lexer(source)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()

                module_doc = self.extract_docs(ast, source, str(file_path))
                module_name = file_path.relative_to(project_path).as_posix()
                project_doc.modules[module_name] = module_doc

                # Extract imports for dependency graph
                imports = self.extract_imports(source)
                if imports:
                    project_doc.dependencies[module_name] = imports

                print(f"  Processed: {module_name}")

            except Exception as e:
                print(f"  Warning: Could not process {file_path}: {e}")

        # Generate outputs
        os.makedirs(output_dir, exist_ok=True)

        # Generate HTML overview
        self.generate_project_html(project_doc, output_dir)

        # Generate individual module pages
        for module_name, module_doc in project_doc.modules.items():
            module_output = os.path.join(output_dir, f"{module_name.replace('/', '_')}.html")
            self.generate_html(module_doc, output_dir)

        # Generate dependency graph if requested
        if options.get('deps'):
            self.generate_dependency_graph(project_doc, output_dir)

        # Generate search index if requested
        if options.get('search'):
            self.generate_search_index(project_doc, output_dir)

        print(f"\nProject documentation generated in {output_dir}")

    def extract_imports(self, source):
        """Extract import statements from source."""
        imports = []
        for line in source.split('\n'):
            line = line.strip()
            if line.startswith('import ') or line.startswith('use '):
                # Extract module name
                parts = line.split()
                if len(parts) >= 2:
                    imports.append(parts[1].strip('"\''))
        return imports

    def generate_project_html(self, project_doc, output_dir):
        """Generate HTML overview page for project."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{project_doc.title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{project_doc.title}</h1>
            <p class="subtitle">Lament Language Documentation</p>
        </header>

        <nav>
            <h2>Modules</h2>
            <ul>
"""

        for module_name in sorted(project_doc.modules.keys()):
            safe_name = module_name.replace('/', '_')
            html += f'                <li><a href="{safe_name}.html">{module_name}</a></li>\n'

        html += """
            </ul>
        </nav>

        <main>
            <section id="overview">
                <h2>Project Overview</h2>
                <p>Total Modules: {}</p>
            </section>
        </main>

        <footer>
            <p>Generated by Lament Documentation Generator</p>
            <p>Generated on {}</p>
        </footer>
    </div>
</body>
</html>
""".format(len(project_doc.modules), now)

        with open(os.path.join(output_dir, 'index.html'), 'w') as f:
            f.write(html)

    def generate_dependency_graph(self, project_doc, output_dir):
        """Generate module dependency graph."""
        # Generate DOT format for graphviz
        dot = "digraph Dependencies {\n"
        dot += "  node [shape=box, style=filled, fillcolor=lightblue];\n"
        dot += "  rankdir=LR;\n\n"

        for module, deps in project_doc.dependencies.items():
            safe_module = module.replace('/', '_').replace('.', '_')
            for dep in deps:
                safe_dep = dep.replace('/', '_').replace('.', '_')
                dot += f'  "{safe_module}" -> "{safe_dep}";\n'

        dot += "}\n"

        dot_file = os.path.join(output_dir, 'dependencies.dot')
        with open(dot_file, 'w') as f:
            f.write(dot)

        print(f"Dependency graph saved to {dot_file}")
        print("Use 'dot -Tpng dependencies.dot -o dependencies.png' to generate image")

        # Also generate JSON format
        json_file = os.path.join(output_dir, 'dependencies.json')
        with open(json_file, 'w') as f:
            json.dump(project_doc.dependencies, f, indent=2)

        print(f"Dependency data saved to {json_file}")

    def generate_search_index(self, project_doc, output_dir):
        """Generate search index for documentation."""
        index = {
            'modules': [],
            'functions': [],
            'variables': []
        }

        for module_name, module_doc in project_doc.modules.items():
            # Index module
            index['modules'].append({
                'name': module_name,
                'title': module_doc.title,
                'description': module_doc.description,
                'url': f"{module_name.replace('/', '_')}.html"
            })

            # Index functions
            for func in module_doc.functions:
                index['functions'].append({
                    'name': func.name,
                    'module': module_name,
                    'params': func.params,
                    'docstring': func.docstring,
                    'url': f"{module_name.replace('/', '_')}.html#func-{func.name}"
                })

            # Index variables
            for var in module_doc.variables:
                index['variables'].append({
                    'name': var.name,
                    'module': module_name,
                    'docstring': var.docstring,
                    'url': f"{module_name.replace('/', '_')}.html#var-{var.name}"
                })

        # Save index
        index_file = os.path.join(output_dir, 'search_index.json')
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)

        print(f"Search index generated: {index_file}")

        # Generate search HTML interface
        self.generate_search_html(output_dir)

    def generate_search_html(self, output_dir):
        """Generate search interface HTML."""
        html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Documentation Search</title>
    <link rel="stylesheet" href="style.css">
    <style>
        .search-container {
            padding: 20px;
            background: #2a2a3e;
            border-radius: 10px;
            margin: 20px 0;
        }
        #search-box {
            width: 100%;
            padding: 15px;
            font-size: 1.2em;
            background: #1a1a2e;
            border: 2px solid #ff6b9d;
            color: #e0e0e0;
            border-radius: 5px;
        }
        .search-results {
            margin-top: 20px;
        }
        .result-item {
            background: #2a2a3e;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #ffd93d;
        }
        .result-type {
            color: #6fe7dd;
            font-size: 0.9em;
            text-transform: uppercase;
        }
        .result-name {
            color: #ff6b9d;
            font-size: 1.2em;
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Documentation Search</h1>
            <a href="index.html">Back to Index</a>
        </header>

        <div class="search-container">
            <input type="text" id="search-box" placeholder="Search for functions, variables, modules...">
        </div>

        <div class="search-results" id="results"></div>
    </div>

    <script>
        let searchIndex = null;

        // Load search index
        fetch('search_index.json')
            .then(response => response.json())
            .then(data => {
                searchIndex = data;
            });

        // Search function
        function search(query) {
            if (!searchIndex || !query) {
                document.getElementById('results').innerHTML = '';
                return;
            }

            query = query.toLowerCase();
            const results = [];

            // Search functions
            searchIndex.functions.forEach(func => {
                if (func.name.toLowerCase().includes(query)) {
                    results.push({
                        type: 'function',
                        name: func.name,
                        module: func.module,
                        description: func.docstring,
                        url: func.url
                    });
                }
            });

            // Search variables
            searchIndex.variables.forEach(variable => {
                if (variable.name.toLowerCase().includes(query)) {
                    results.push({
                        type: 'variable',
                        name: variable.name,
                        module: variable.module,
                        description: variable.docstring,
                        url: variable.url
                    });
                }
            });

            // Search modules
            searchIndex.modules.forEach(module => {
                if (module.name.toLowerCase().includes(query) ||
                    (module.title && module.title.toLowerCase().includes(query))) {
                    results.push({
                        type: 'module',
                        name: module.name,
                        description: module.description,
                        url: module.url
                    });
                }
            });

            displayResults(results);
        }

        function displayResults(results) {
            const container = document.getElementById('results');

            if (results.length === 0) {
                container.innerHTML = '<p>No results found</p>';
                return;
            }

            let html = '<h2>Results (' + results.length + ')</h2>';

            results.forEach(result => {
                html += '<div class="result-item">';
                html += '<div class="result-type">' + result.type + '</div>';
                html += '<div class="result-name"><a href="' + result.url + '">' + result.name + '</a></div>';
                if (result.module) {
                    html += '<div>Module: ' + result.module + '</div>';
                }
                if (result.description) {
                    html += '<div>' + result.description.substring(0, 200) + '...</div>';
                }
                html += '</div>';
            });

            container.innerHTML = html;
        }

        // Attach search event
        document.getElementById('search-box').addEventListener('input', function(e) {
            search(e.target.value);
        });
    </script>
</body>
</html>
"""

        with open(os.path.join(output_dir, 'search.html'), 'w') as f:
            f.write(html)

        print(f"Search interface generated: {os.path.join(output_dir, 'search.html')}")

    def generate_pdf(self, docs, output_file):
        """
        Generate PDF documentation (requires wkhtmltopdf or similar).

        Args:
            docs: ModuleDoc
            output_file: Output PDF file path
        """
        try:
            # Generate HTML first
            import tempfile
            with tempfile.TemporaryDirectory() as tmpdir:
                self.generate_html(docs, tmpdir)
                html_file = os.path.join(tmpdir, 'index.html')

                # Try to use wkhtmltopdf
                import subprocess
                result = subprocess.run(
                    ['wkhtmltopdf', html_file, output_file],
                    capture_output=True,
                    text=True
                )

                if result.returncode == 0:
                    print(f"PDF documentation generated: {output_file}")
                else:
                    print(f"Error generating PDF: {result.stderr}")
                    print("Note: wkhtmltopdf must be installed for PDF generation")

        except FileNotFoundError:
            print("Error: wkhtmltopdf not found. Please install it for PDF generation.")
        except Exception as e:
            print(f"Error generating PDF: {e}")


class DocServer:
    """Live documentation server with auto-reload."""

    def __init__(self, doc_dir, port=8000):
        """
        Initialize documentation server.

        Args:
            doc_dir: Documentation directory
            port: Server port
        """
        self.doc_dir = doc_dir
        self.port = port
        self.server = None
        self.thread = None

    def start(self):
        """Start the documentation server."""
        class Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=self.doc_dir, **kwargs)

            def log_message(self, format, *args):
                # Suppress default logging
                pass

        self.server = socketserver.TCPServer(("", self.port), Handler)

        def serve():
            print(f"\nDocumentation server running at http://localhost:{self.port}")
            print("Press Ctrl+C to stop\n")
            self.server.serve_forever()

        self.thread = threading.Thread(target=serve, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the documentation server."""
        if self.server:
            self.server.shutdown()
            print("Documentation server stopped")


class DocWatcher:
    """Watches for file changes and regenerates documentation."""

    def __init__(self, source_path, output_dir, generator, options=None):
        """
        Initialize documentation watcher.

        Args:
            source_path: Path to watch
            output_dir: Output directory
            generator: DocGenerator instance
            options: Generation options
        """
        self.source_path = Path(source_path)
        self.output_dir = output_dir
        self.generator = generator
        self.options = options or {}
        self.last_mtime = {}
        self.running = False

    def start(self):
        """Start watching for changes."""
        self.running = True
        print(f"Watching {self.source_path} for changes...")

        try:
            while self.running:
                changed = self.check_changes()
                if changed:
                    print(f"\nDetected changes, regenerating documentation...")
                    self.regenerate()

                time.sleep(1)  # Check every second

        except KeyboardInterrupt:
            print("\nStopping watcher...")
            self.running = False

    def check_changes(self):
        """Check if any files have changed."""
        changed = False

        for file_path in self.source_path.rglob('*.lament'):
            mtime = file_path.stat().st_mtime
            if str(file_path) not in self.last_mtime:
                self.last_mtime[str(file_path)] = mtime
            elif mtime > self.last_mtime[str(file_path)]:
                self.last_mtime[str(file_path)] = mtime
                changed = True

        return changed

    def regenerate(self):
        """Regenerate documentation."""
        try:
            if self.source_path.is_file():
                with open(self.source_path, 'r') as f:
                    source = f.read()

                lexer = Lexer(source)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                ast = parser.parse()

                docs = self.generator.extract_docs(ast, source, str(self.source_path))
                self.generator.generate_html(docs, self.output_dir)
            else:
                self.generator.generate_project_docs(
                    self.source_path,
                    self.output_dir,
                    self.options
                )

            print("Documentation updated!")

        except Exception as e:
            print(f"Error regenerating documentation: {e}")


def main():
    """CLI entry point for documentation generator."""
    if len(sys.argv) < 2:
        print("Usage: lament-doc <file.lament> [options]")
        print("\nGenerate documentation for Lament programs.")
        print("\nOptions:")
        print("  --output DIR    Output directory (default: ./docs)")
        print("  --format FORMAT Output format: html, markdown, pdf (default: html)")
        print("  --title TITLE   Documentation title")
        print("  --auto          Auto-generate docs from all modules")
        print("  --serve         Start live documentation server")
        print("  --port PORT     Server port (default: 8000)")
        print("  --watch         Watch for file changes and regenerate")
        print("  --deps          Generate module dependency graph")
        print("  --search        Generate search index")
        sys.exit(1)

    filename = sys.argv[1]

    output_dir = './docs'
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]

    output_format = 'html'
    if '--format' in sys.argv:
        idx = sys.argv.index('--format')
        if idx + 1 < len(sys.argv):
            output_format = sys.argv[idx + 1]

    title = None
    if '--title' in sys.argv:
        idx = sys.argv.index('--title')
        if idx + 1 < len(sys.argv):
            title = sys.argv[idx + 1]

    port = 8000
    if '--port' in sys.argv:
        idx = sys.argv.index('--port')
        if idx + 1 < len(sys.argv):
            port = int(sys.argv[idx + 1])

    auto_mode = '--auto' in sys.argv
    serve = '--serve' in sys.argv
    watch = '--watch' in sys.argv
    deps = '--deps' in sys.argv
    search = '--search' in sys.argv

    options = {
        'title': title,
        'deps': deps,
        'search': search
    }

    try:
        generator = DocGenerator()

        if auto_mode:
            # Auto-generate docs for entire project
            generator.generate_project_docs(filename, output_dir, options)
        else:
            # Generate docs for single file
            with open(filename, 'r') as f:
                source = f.read()

            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            docs = generator.extract_docs(ast, source, filename)

            if title:
                docs.title = title

            if output_format == 'html':
                generator.generate_html(docs, output_dir)
            elif output_format == 'markdown':
                md_file = os.path.join(output_dir, 'README.md')
                os.makedirs(output_dir, exist_ok=True)
                generator.generate_markdown(docs, md_file)
            elif output_format == 'pdf':
                pdf_file = os.path.join(output_dir, 'documentation.pdf')
                os.makedirs(output_dir, exist_ok=True)
                generator.generate_pdf(docs, pdf_file)
            else:
                print(f"Unknown format: {output_format}")
                sys.exit(1)

        # Start server if requested
        if serve:
            server = DocServer(output_dir, port)
            server.start()

            if watch:
                # Watch for changes
                watcher = DocWatcher(filename, output_dir, generator, options)
                watcher.start()
            else:
                # Just keep server running
                try:
                    while True:
                        time.sleep(1)
                except KeyboardInterrupt:
                    server.stop()

        elif watch:
            # Watch without server
            watcher = DocWatcher(filename, output_dir, generator, options)
            watcher.start()

    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating documentation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
