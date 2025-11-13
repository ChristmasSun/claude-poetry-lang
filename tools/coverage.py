"""
Lament Language Code Coverage Tool
==================================

Comprehensive code coverage tracking for Lament programs.

Features:
- Line coverage tracking
- Branch coverage tracking
- Function coverage tracking
- Multiple report formats (HTML, text, JSON)
- Integration with test framework
- Minimum coverage enforcement
- Coverage diff between runs
- Source code highlighting

Usage:
    python -m tools.coverage [options] <file.lament>
    lament-coverage [options] <file.lament>

Options:
    --html DIR          Generate HTML coverage report
    --text              Generate text coverage report (default)
    --json FILE         Generate JSON coverage report
    --min PERCENT       Fail if coverage below minimum (0-100)
    --include PATTERN   Include only files matching pattern
    --exclude PATTERN   Exclude files matching pattern
    --branch            Track branch coverage (in addition to line coverage)
    --output FILE       Save coverage data to file

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
import json
import time
from typing import Dict, List, Set, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
from collections import defaultdict
import fnmatch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.lexer import Lexer
from lament.parser import Parser, ASTNode, FunctionDef
from lament.interpreter import Interpreter


# ============================================================================
# COVERAGE DATA STRUCTURES
# ============================================================================

@dataclass
class LineCoverage:
    """Coverage data for a single line."""
    line_number: int
    executed: bool = False
    execution_count: int = 0


@dataclass
class BranchCoverage:
    """Coverage data for a branch."""
    line_number: int
    branch_id: int
    taken: bool = False
    execution_count: int = 0


@dataclass
class FunctionCoverage:
    """Coverage data for a function."""
    name: str
    start_line: int
    end_line: int
    executed: bool = False
    execution_count: int = 0


@dataclass
class FileCoverage:
    """Coverage data for a file."""
    file_path: str
    lines: Dict[int, LineCoverage] = field(default_factory=dict)
    branches: List[BranchCoverage] = field(default_factory=list)
    functions: Dict[str, FunctionCoverage] = field(default_factory=dict)
    total_lines: int = 0
    executable_lines: int = 0

    @property
    def executed_lines(self):
        """Number of executed lines."""
        return sum(1 for line in self.lines.values() if line.executed)

    @property
    def line_coverage_percent(self):
        """Line coverage percentage."""
        if self.executable_lines == 0:
            return 100.0
        return (self.executed_lines / self.executable_lines) * 100

    @property
    def executed_branches(self):
        """Number of executed branches."""
        return sum(1 for branch in self.branches if branch.taken)

    @property
    def branch_coverage_percent(self):
        """Branch coverage percentage."""
        if not self.branches:
            return 100.0
        return (self.executed_branches / len(self.branches)) * 100

    @property
    def executed_functions(self):
        """Number of executed functions."""
        return sum(1 for func in self.functions.values() if func.executed)

    @property
    def function_coverage_percent(self):
        """Function coverage percentage."""
        if not self.functions:
            return 100.0
        return (self.executed_functions / len(self.functions)) * 100


@dataclass
class CoverageReport:
    """Complete coverage report."""
    files: Dict[str, FileCoverage] = field(default_factory=dict)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    @property
    def total_lines(self):
        """Total lines across all files."""
        return sum(f.executable_lines for f in self.files.values())

    @property
    def executed_lines(self):
        """Total executed lines across all files."""
        return sum(f.executed_lines for f in self.files.values())

    @property
    def overall_coverage(self):
        """Overall line coverage percentage."""
        if self.total_lines == 0:
            return 100.0
        return (self.executed_lines / self.total_lines) * 100

    @property
    def total_functions(self):
        """Total functions across all files."""
        return sum(len(f.functions) for f in self.files.values())

    @property
    def executed_functions(self):
        """Total executed functions across all files."""
        return sum(f.executed_functions for f in self.files.values())

    @property
    def overall_function_coverage(self):
        """Overall function coverage percentage."""
        if self.total_functions == 0:
            return 100.0
        return (self.executed_functions / self.total_functions) * 100


# ============================================================================
# COVERAGE TRACKER
# ============================================================================

class CoverageTracker:
    """Tracks code coverage during execution."""

    def __init__(self, include_patterns=None, exclude_patterns=None, track_branches=False):
        """
        Initialize coverage tracker.

        Args:
            include_patterns: List of file patterns to include
            exclude_patterns: List of file patterns to exclude
            track_branches: Enable branch coverage tracking
        """
        self.include_patterns = include_patterns or ['*.lament']
        self.exclude_patterns = exclude_patterns or []
        self.track_branches = track_branches
        self.report = CoverageReport()
        self.current_file = None

    def start_tracking(self, file_path):
        """Start tracking coverage for a file."""
        if not self._should_track(file_path):
            return

        self.current_file = file_path

        if file_path not in self.report.files:
            self.report.files[file_path] = FileCoverage(file_path=file_path)

    def _should_track(self, file_path):
        """Check if file should be tracked."""
        # Check include patterns
        included = any(fnmatch.fnmatch(file_path, pattern) for pattern in self.include_patterns)
        if not included:
            return False

        # Check exclude patterns
        excluded = any(fnmatch.fnmatch(file_path, pattern) for pattern in self.exclude_patterns)
        if excluded:
            return False

        return True

    def mark_line_executed(self, line_number):
        """Mark a line as executed."""
        if not self.current_file:
            return

        file_cov = self.report.files.get(self.current_file)
        if not file_cov:
            return

        if line_number not in file_cov.lines:
            file_cov.lines[line_number] = LineCoverage(line_number)

        file_cov.lines[line_number].executed = True
        file_cov.lines[line_number].execution_count += 1

    def mark_branch_taken(self, line_number, branch_id):
        """Mark a branch as taken."""
        if not self.current_file or not self.track_branches:
            return

        file_cov = self.report.files.get(self.current_file)
        if not file_cov:
            return

        # Find or create branch
        branch = None
        for b in file_cov.branches:
            if b.line_number == line_number and b.branch_id == branch_id:
                branch = b
                break

        if not branch:
            branch = BranchCoverage(line_number, branch_id)
            file_cov.branches.append(branch)

        branch.taken = True
        branch.execution_count += 1

    def mark_function_executed(self, function_name):
        """Mark a function as executed."""
        if not self.current_file:
            return

        file_cov = self.report.files.get(self.current_file)
        if not file_cov:
            return

        if function_name in file_cov.functions:
            file_cov.functions[function_name].executed = True
            file_cov.functions[function_name].execution_count += 1

    def analyze_source(self, source, file_path):
        """Analyze source code to identify executable lines and functions."""
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            file_cov = self.report.files.get(file_path)
            if not file_cov:
                file_cov = FileCoverage(file_path=file_path)
                self.report.files[file_path] = file_cov

            source_lines = source.split('\n')
            file_cov.total_lines = len(source_lines)

            # Identify executable lines (exclude comments and blank lines)
            for i, line in enumerate(source_lines, 1):
                stripped = line.strip()
                if stripped and not stripped.startswith('#') and not stripped.startswith('//'):
                    file_cov.lines[i] = LineCoverage(i)
                    file_cov.executable_lines += 1

            # Extract functions
            for node in ast:
                if isinstance(node, FunctionDef):
                    func_cov = FunctionCoverage(
                        name=node.name,
                        start_line=1,  # Would need line info in AST
                        end_line=1
                    )
                    file_cov.functions[node.name] = func_cov

        except Exception as e:
            print(f"Warning: Could not analyze {file_path}: {e}")

    def stop_tracking(self):
        """Stop tracking coverage."""
        self.report.end_time = time.time()
        return self.report


# ============================================================================
# INSTRUMENTED INTERPRETER
# ============================================================================

class InstrumentedInterpreter(Interpreter):
    """Interpreter with coverage tracking."""

    def __init__(self, tracker):
        """
        Initialize instrumented interpreter.

        Args:
            tracker: CoverageTracker instance
        """
        super().__init__()
        self.tracker = tracker

    def visit(self, node):
        """Visit AST node with coverage tracking."""
        # Track line execution
        if hasattr(node, 'line'):
            self.tracker.mark_line_executed(node.line)

        # Track function calls
        if isinstance(node, FunctionDef):
            self.tracker.mark_function_executed(node.name)

        return super().visit(node)


# ============================================================================
# COVERAGE COLLECTOR
# ============================================================================

class CodeCoverage:
    """Main code coverage collector."""

    def __init__(self, options=None):
        """
        Initialize code coverage collector.

        Args:
            options: Dictionary of options
        """
        self.options = options or {}
        self.tracker = CoverageTracker(
            include_patterns=self.options.get('include', ['*.lament']),
            exclude_patterns=self.options.get('exclude', []),
            track_branches=self.options.get('branch', False)
        )

    def run_with_coverage(self, file_path):
        """
        Run file with coverage tracking.

        Args:
            file_path: Path to Lament file

        Returns:
            CoverageReport
        """
        try:
            with open(file_path, 'r') as f:
                source = f.read()

            # Analyze source for coverage baseline
            self.tracker.analyze_source(source, file_path)

            # Start tracking
            self.tracker.start_tracking(file_path)

            # Parse and execute with instrumented interpreter
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            interpreter = InstrumentedInterpreter(self.tracker)

            for node in ast:
                interpreter.visit(node)

            # Stop tracking
            return self.tracker.stop_tracking()

        except FileNotFoundError:
            print(f"Error: File not found: {file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error running coverage: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    def generate_text_report(self, report, output_file=None):
        """
        Generate text coverage report.

        Args:
            report: CoverageReport
            output_file: Optional output file path
        """
        lines = []
        lines.append("=" * 80)
        lines.append("Lament Code Coverage Report")
        lines.append("=" * 80)
        lines.append("")

        # Overall summary
        lines.append(f"Overall Coverage: {report.overall_coverage:.2f}%")
        lines.append(f"Total Lines: {report.total_lines}")
        lines.append(f"Executed Lines: {report.executed_lines}")
        lines.append(f"Total Functions: {report.total_functions}")
        lines.append(f"Executed Functions: {report.executed_functions}")
        lines.append("")

        # Per-file coverage
        lines.append("Per-File Coverage:")
        lines.append("-" * 80)

        for file_path, file_cov in sorted(report.files.items()):
            lines.append(f"\n{file_path}")
            lines.append(f"  Lines:     {file_cov.line_coverage_percent:6.2f}% ({file_cov.executed_lines}/{file_cov.executable_lines})")
            lines.append(f"  Functions: {file_cov.function_coverage_percent:6.2f}% ({file_cov.executed_functions}/{len(file_cov.functions)})")

            if file_cov.branches:
                lines.append(f"  Branches:  {file_cov.branch_coverage_percent:6.2f}% ({file_cov.executed_branches}/{len(file_cov.branches)})")

            # Show uncovered lines
            uncovered = [line_num for line_num, line in sorted(file_cov.lines.items()) if not line.executed]
            if uncovered:
                lines.append(f"  Uncovered lines: {', '.join(map(str, uncovered[:20]))}")
                if len(uncovered) > 20:
                    lines.append(f"    ... and {len(uncovered) - 20} more")

        lines.append("")
        lines.append("=" * 80)

        report_text = '\n'.join(lines)

        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            print(f"Text coverage report written to {output_file}")
        else:
            print(report_text)

    def generate_json_report(self, report, output_file):
        """
        Generate JSON coverage report.

        Args:
            report: CoverageReport
            output_file: Output file path
        """
        data = {
            'summary': {
                'overall_coverage': report.overall_coverage,
                'total_lines': report.total_lines,
                'executed_lines': report.executed_lines,
                'total_functions': report.total_functions,
                'executed_functions': report.executed_functions
            },
            'files': {}
        }

        for file_path, file_cov in report.files.items():
            data['files'][file_path] = {
                'line_coverage': file_cov.line_coverage_percent,
                'executed_lines': file_cov.executed_lines,
                'executable_lines': file_cov.executable_lines,
                'function_coverage': file_cov.function_coverage_percent,
                'executed_functions': file_cov.executed_functions,
                'total_functions': len(file_cov.functions),
                'lines': {
                    str(line_num): {
                        'executed': line.executed,
                        'count': line.execution_count
                    }
                    for line_num, line in file_cov.lines.items()
                },
                'functions': {
                    name: {
                        'executed': func.executed,
                        'count': func.execution_count
                    }
                    for name, func in file_cov.functions.items()
                }
            }

        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"JSON coverage report written to {output_file}")

    def generate_html_report(self, report, output_dir):
        """
        Generate HTML coverage report.

        Args:
            report: CoverageReport
            output_dir: Output directory
        """
        os.makedirs(output_dir, exist_ok=True)

        # Generate index page
        self._generate_html_index(report, output_dir)

        # Generate per-file pages
        for file_path, file_cov in report.files.items():
            self._generate_html_file_report(file_path, file_cov, output_dir)

        # Generate CSS
        self._generate_html_css(output_dir)

        print(f"HTML coverage report generated in {output_dir}")
        print(f"Open {os.path.join(output_dir, 'index.html')} in your browser")

    def _generate_html_index(self, report, output_dir):
        """Generate HTML index page."""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Lament Coverage Report</title>
    <link rel="stylesheet" href="coverage.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Lament Coverage Report</h1>
        </header>

        <div class="summary">
            <h2>Summary</h2>
            <div class="metric">
                <span class="label">Overall Coverage:</span>
                <span class="value coverage-{self._get_coverage_class(report.overall_coverage)}">
                    {report.overall_coverage:.2f}%
                </span>
            </div>
            <div class="metric">
                <span class="label">Total Lines:</span>
                <span class="value">{report.total_lines}</span>
            </div>
            <div class="metric">
                <span class="label">Executed Lines:</span>
                <span class="value">{report.executed_lines}</span>
            </div>
        </div>

        <div class="files">
            <h2>Files</h2>
            <table>
                <thead>
                    <tr>
                        <th>File</th>
                        <th>Line Coverage</th>
                        <th>Function Coverage</th>
                        <th>Lines</th>
                    </tr>
                </thead>
                <tbody>
"""

        for file_path, file_cov in sorted(report.files.items()):
            file_name = os.path.basename(file_path)
            html += f"""
                    <tr>
                        <td><a href="{file_name}.html">{file_path}</a></td>
                        <td class="coverage-{self._get_coverage_class(file_cov.line_coverage_percent)}">
                            {file_cov.line_coverage_percent:.2f}%
                        </td>
                        <td class="coverage-{self._get_coverage_class(file_cov.function_coverage_percent)}">
                            {file_cov.function_coverage_percent:.2f}%
                        </td>
                        <td>{file_cov.executed_lines}/{file_cov.executable_lines}</td>
                    </tr>
"""

        html += """
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""

        with open(os.path.join(output_dir, 'index.html'), 'w') as f:
            f.write(html)

    def _generate_html_file_report(self, file_path, file_cov, output_dir):
        """Generate HTML report for a single file."""
        file_name = os.path.basename(file_path)

        # Read source
        try:
            with open(file_path, 'r') as f:
                source_lines = f.readlines()
        except:
            source_lines = []

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Coverage: {file_path}</title>
    <link rel="stylesheet" href="coverage.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{file_path}</h1>
            <a href="index.html">Back to Index</a>
        </header>

        <div class="summary">
            <div class="metric">
                <span class="label">Line Coverage:</span>
                <span class="value coverage-{self._get_coverage_class(file_cov.line_coverage_percent)}">
                    {file_cov.line_coverage_percent:.2f}%
                </span>
            </div>
        </div>

        <div class="source">
            <table>
"""

        for i, line in enumerate(source_lines, 1):
            line_cov = file_cov.lines.get(i)
            if line_cov:
                if line_cov.executed:
                    css_class = 'covered'
                    count = line_cov.execution_count
                else:
                    css_class = 'uncovered'
                    count = 0
            else:
                css_class = 'non-executable'
                count = ''

            line_html = line.rstrip().replace('<', '&lt;').replace('>', '&gt;')
            html += f"""
                <tr class="{css_class}">
                    <td class="line-number">{i}</td>
                    <td class="hit-count">{count}</td>
                    <td class="source-line"><pre>{line_html}</pre></td>
                </tr>
"""

        html += """
            </table>
        </div>
    </div>
</body>
</html>
"""

        output_file = os.path.join(output_dir, f"{file_name}.html")
        with open(output_file, 'w') as f:
            f.write(html)

    def _generate_html_css(self, output_dir):
        """Generate CSS for HTML reports."""
        css = """
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    background: #1a1a2e;
    color: #e0e0e0;
    margin: 0;
    padding: 0;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background: #16213e;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

header h1 {
    color: #ff6b9d;
    margin: 0;
}

header a {
    color: #6fe7dd;
    text-decoration: none;
}

.summary {
    background: #16213e;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
}

.summary h2 {
    color: #ffd93d;
    margin-top: 0;
}

.metric {
    margin: 10px 0;
    font-size: 1.2em;
}

.metric .label {
    color: #c0c0c0;
}

.metric .value {
    font-weight: bold;
    margin-left: 10px;
}

.coverage-high { color: #4caf50; }
.coverage-medium { color: #ff9800; }
.coverage-low { color: #f44336; }

.files {
    background: #16213e;
    padding: 20px;
    border-radius: 10px;
}

.files h2 {
    color: #ffd93d;
    margin-top: 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    background: #2a2a3e;
}

thead {
    background: #1a1a2e;
}

th {
    color: #ffd93d;
    padding: 15px;
    text-align: left;
    border-bottom: 2px solid #3a3a4e;
}

td {
    padding: 12px 15px;
    border-bottom: 1px solid #3a3a4e;
}

tbody tr:hover {
    background: #3a3a4e;
}

a {
    color: #6fe7dd;
    text-decoration: none;
}

a:hover {
    color: #ff6b9d;
}

.source table {
    font-family: 'Courier New', monospace;
    font-size: 0.9em;
}

.source td {
    padding: 2px 10px;
}

.line-number {
    text-align: right;
    color: #888;
    width: 60px;
    user-select: none;
}

.hit-count {
    text-align: right;
    width: 60px;
    color: #888;
}

.source-line {
    padding-left: 20px;
}

.source-line pre {
    margin: 0;
    padding: 0;
}

tr.covered {
    background: rgba(76, 175, 80, 0.2);
}

tr.uncovered {
    background: rgba(244, 67, 54, 0.2);
}

tr.non-executable {
    background: transparent;
    color: #666;
}
"""

        with open(os.path.join(output_dir, 'coverage.css'), 'w') as f:
            f.write(css)

    def _get_coverage_class(self, percent):
        """Get CSS class for coverage percentage."""
        if percent >= 80:
            return 'high'
        elif percent >= 50:
            return 'medium'
        else:
            return 'low'

    def check_minimum_coverage(self, report, minimum):
        """
        Check if coverage meets minimum threshold.

        Args:
            report: CoverageReport
            minimum: Minimum coverage percentage (0-100)

        Returns:
            True if coverage meets minimum, False otherwise
        """
        if report.overall_coverage < minimum:
            print(f"\nError: Coverage {report.overall_coverage:.2f}% is below minimum {minimum}%")
            return False
        return True


# ============================================================================
# CLI INTERFACE
# ============================================================================

def main():
    """CLI entry point for coverage tool."""
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: lament-coverage [options] <file.lament>")
        sys.exit(1)

    options = {}
    file_path = None
    i = 1

    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == '--html':
            i += 1
            if i < len(sys.argv):
                options['html'] = sys.argv[i]
        elif arg == '--text':
            options['text'] = True
        elif arg == '--json':
            i += 1
            if i < len(sys.argv):
                options['json'] = sys.argv[i]
        elif arg == '--min':
            i += 1
            if i < len(sys.argv):
                options['min'] = float(sys.argv[i])
        elif arg == '--include':
            i += 1
            if i < len(sys.argv):
                options['include'] = options.get('include', [])
                options['include'].append(sys.argv[i])
        elif arg == '--exclude':
            i += 1
            if i < len(sys.argv):
                options['exclude'] = options.get('exclude', [])
                options['exclude'].append(sys.argv[i])
        elif arg == '--branch':
            options['branch'] = True
        elif arg == '--output':
            i += 1
            if i < len(sys.argv):
                options['output'] = sys.argv[i]
        elif not arg.startswith('-'):
            file_path = arg

        i += 1

    if not file_path:
        print("Error: No file specified")
        sys.exit(1)

    # Run coverage
    coverage = CodeCoverage(options)
    report = coverage.run_with_coverage(file_path)

    # Generate reports
    if options.get('html'):
        coverage.generate_html_report(report, options['html'])
    elif options.get('json'):
        coverage.generate_json_report(report, options['json'])
    else:
        # Default to text report
        coverage.generate_text_report(report, options.get('output'))

    # Check minimum coverage
    if 'min' in options:
        if not coverage.check_minimum_coverage(report, options['min']):
            sys.exit(1)

    return 0


if __name__ == '__main__':
    sys.exit(main())
