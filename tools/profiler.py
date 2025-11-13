"""
Lament Language Profiler
========================

Performance profiling tool for Lament programs.

Features:
- Time profiling (execution time per statement/function)
- Memory profiling (memory usage tracking)
- Call count tracking
- Hotspot detection
- Flamegraph generation
- Timeline visualization
- Profile export (JSON, HTML)

Usage:
    python -m tools.profiler <file.lament>
    lament-profile <file.lament>

Options:
    --time          Time profiling only (default)
    --memory        Memory profiling
    --flamegraph    Generate flamegraph
    --output FILE   Save profile to file

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
import time
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.lexer import Lexer
from lament.parser import (
    Parser, ASTNode, NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral,
    Identifier, BinaryOp, UnaryOp, Assignment, VariableDecl, ConfessStmt,
    IfStmt, WhileStmt, ForStmt, FunctionDef, FunctionCall, ExhaleStmt,
    TemporalAccess, ListLiteral, DictLiteral, IndexAccess, ForkReality
)
from lament.interpreter import LamentInterpreter, ReturnValue


@dataclass
class ProfileEntry:
    """Profile data for a single execution unit."""
    name: str
    call_count: int = 0
    total_time: float = 0.0
    self_time: float = 0.0
    memory_delta: int = 0
    children: List['ProfileEntry'] = field(default_factory=list)


@dataclass
class ProfilingResult:
    """Complete profiling result."""
    total_time: float
    total_memory: int
    function_profiles: Dict[str, ProfileEntry]
    statement_profiles: List[Tuple[int, float]]  # (statement_index, time)
    hotspots: List[Tuple[str, float]]  # (location, time)


class LamentProfiler(LamentInterpreter):
    """Profiling interpreter for Lament.

    Extends the interpreter to track:
    - Execution time per statement
    - Function call counts and times
    - Memory usage
    - Call graph

    Example:
        profiler = LamentProfiler(ast)
        result = profiler.profile()
        profiler.print_report(result)
    """

    def __init__(self, ast, source_lines=None):
        """Initialize profiler.

        Args:
            ast: Parsed AST
            source_lines: Optional source code lines
        """
        super().__init__()

        self.ast = ast
        self.source_lines = source_lines

        # Profiling data
        self.statement_times = []  # [(stmt_idx, time)]
        self.function_profiles = {}  # func_name -> ProfileEntry
        self.call_stack = []  # [(func_name, start_time)]
        self.current_function = None

        # Memory tracking
        self.memory_snapshots = []
        self.enable_memory_profiling = False

    def get_memory_usage(self):
        """Get current memory usage estimate."""
        # Simplified memory tracking
        # In production, use tracemalloc or psutil
        total = 0

        # Count variables
        for scope in self.scopes:
            total += len(scope) * 100  # Estimate per variable

        total += len(self.globals) * 100

        return total

    def profile(self, enable_memory=False):
        """Run program with profiling.

        Args:
            enable_memory: Enable memory profiling

        Returns:
            ProfilingResult
        """
        self.enable_memory_profiling = enable_memory
        start_time = time.time()
        start_memory = self.get_memory_usage()

        # Execute with profiling
        try:
            for i, stmt in enumerate(self.ast):
                stmt_start = time.time()

                if enable_memory:
                    mem_before = self.get_memory_usage()

                self.current_statement_index = i
                self.execute_statement(stmt)

                stmt_time = time.time() - stmt_start
                self.statement_times.append((i, stmt_time))

                if enable_memory:
                    mem_after = self.get_memory_usage()
                    self.memory_snapshots.append((i, mem_after - mem_before))

        except Exception as e:
            print(f"Error during profiling: {e}")

        total_time = time.time() - start_time
        total_memory = self.get_memory_usage() - start_memory

        # Calculate hotspots
        hotspots = self.find_hotspots()

        return ProfilingResult(
            total_time=total_time,
            total_memory=total_memory,
            function_profiles=self.function_profiles,
            statement_profiles=self.statement_times,
            hotspots=hotspots
        )

    def execute_statement(self, stmt):
        """Override to add profiling hooks."""
        if isinstance(stmt, FunctionDef):
            # Track function definition
            if stmt.name not in self.function_profiles:
                self.function_profiles[stmt.name] = ProfileEntry(name=stmt.name)
            super().execute_statement(stmt)

        elif isinstance(stmt, FunctionCall):
            # Profile function call
            self.profile_function_call(stmt)

        else:
            super().execute_statement(stmt)

    def profile_function_call(self, expr):
        """Profile a function call."""
        start_time = time.time()
        mem_before = self.get_memory_usage() if self.enable_memory_profiling else 0

        # Track entry
        if expr.name in self.function_profiles:
            profile = self.function_profiles[expr.name]
            profile.call_count += 1
        else:
            profile = ProfileEntry(name=expr.name, call_count=1)
            self.function_profiles[expr.name] = profile

        self.call_stack.append((expr.name, start_time))

        # Execute
        try:
            result = self.evaluate(expr)
        finally:
            # Track exit
            elapsed = time.time() - start_time
            profile.total_time += elapsed
            profile.self_time += elapsed  # Simplified

            if self.enable_memory_profiling:
                mem_after = self.get_memory_usage()
                profile.memory_delta += (mem_after - mem_before)

            self.call_stack.pop()

        return result

    def evaluate(self, expr):
        """Override to profile function calls in expressions."""
        if isinstance(expr, FunctionCall):
            return self.profile_function_call(expr)
        else:
            return super().evaluate(expr)

    def find_hotspots(self, threshold=0.1):
        """Find performance hotspots.

        Args:
            threshold: Minimum percentage of total time to be considered hotspot

        Returns:
            List of (location, time) tuples
        """
        hotspots = []

        # Function hotspots
        for name, profile in self.function_profiles.items():
            if profile.total_time > 0:
                hotspots.append((f"function {name}", profile.total_time))

        # Statement hotspots
        for stmt_idx, stmt_time in self.statement_times:
            if stmt_time > 0.001:  # More than 1ms
                location = f"statement {stmt_idx}"
                if self.source_lines and stmt_idx < len(self.source_lines):
                    line_preview = self.source_lines[stmt_idx].strip()[:50]
                    location = f"line {stmt_idx + 1}: {line_preview}"
                hotspots.append((location, stmt_time))

        # Sort by time and filter by threshold
        hotspots.sort(key=lambda x: x[1], reverse=True)

        if hotspots:
            total_time = sum(t for _, t in hotspots)
            threshold_time = total_time * threshold
            hotspots = [(loc, t) for loc, t in hotspots if t >= threshold_time]

        return hotspots[:10]  # Top 10

    def print_report(self, result):
        """Print profiling report.

        Args:
            result: ProfilingResult
        """
        print("\n" + "=" * 70)
        print("LAMENT PROFILER REPORT")
        print("=" * 70)

        # Summary
        print(f"\nTotal execution time: {result.total_time:.6f}s")
        if self.enable_memory_profiling:
            print(f"Total memory delta: {result.total_memory} bytes")

        # Function profiles
        if result.function_profiles:
            print("\n" + "-" * 70)
            print("FUNCTION PROFILES")
            print("-" * 70)
            print(f"{'Function':<30} {'Calls':>8} {'Total Time':>12} {'Avg Time':>12}")
            print("-" * 70)

            sorted_funcs = sorted(
                result.function_profiles.items(),
                key=lambda x: x[1].total_time,
                reverse=True
            )

            for name, profile in sorted_funcs:
                avg_time = profile.total_time / profile.call_count if profile.call_count > 0 else 0
                print(f"{name:<30} {profile.call_count:>8} "
                      f"{profile.total_time:>12.6f}s {avg_time:>12.6f}s")

                if self.enable_memory_profiling and profile.memory_delta != 0:
                    print(f"  Memory delta: {profile.memory_delta} bytes")

        # Hotspots
        if result.hotspots:
            print("\n" + "-" * 70)
            print("PERFORMANCE HOTSPOTS")
            print("-" * 70)
            print(f"{'Location':<50} {'Time':>12} {'% of Total':>10}")
            print("-" * 70)

            for location, hotspot_time in result.hotspots:
                percentage = (hotspot_time / result.total_time * 100) if result.total_time > 0 else 0
                print(f"{location:<50} {hotspot_time:>12.6f}s {percentage:>9.1f}%")

        # Statement timing summary
        if result.statement_profiles:
            print("\n" + "-" * 70)
            print("STATEMENT TIMING SUMMARY")
            print("-" * 70)

            total_stmt_time = sum(t for _, t in result.statement_profiles)
            avg_stmt_time = total_stmt_time / len(result.statement_profiles)
            max_stmt_time = max((t for _, t in result.statement_profiles), default=0)

            print(f"Total statements: {len(result.statement_profiles)}")
            print(f"Average time per statement: {avg_stmt_time:.6f}s")
            print(f"Maximum statement time: {max_stmt_time:.6f}s")

        print("\n" + "=" * 70 + "\n")

    def generate_flamegraph_data(self, result):
        """Generate flamegraph data.

        Returns:
            List of (stack_trace, time) tuples
        """
        flamegraph_data = []

        # Generate from function profiles
        for name, profile in result.function_profiles.items():
            # Simplified: just function names
            # Real flamegraphs would track full call stacks
            flamegraph_data.append((name, profile.total_time))

        return flamegraph_data

    def export_json(self, result, filename):
        """Export profile data as JSON.

        Args:
            result: ProfilingResult
            filename: Output filename
        """
        data = {
            'total_time': result.total_time,
            'total_memory': result.total_memory,
            'functions': {},
            'statements': [],
            'hotspots': []
        }

        # Function profiles
        for name, profile in result.function_profiles.items():
            data['functions'][name] = {
                'call_count': profile.call_count,
                'total_time': profile.total_time,
                'self_time': profile.self_time,
                'memory_delta': profile.memory_delta
            }

        # Statement profiles
        data['statements'] = [
            {'index': idx, 'time': t}
            for idx, t in result.statement_profiles
        ]

        # Hotspots
        data['hotspots'] = [
            {'location': loc, 'time': t}
            for loc, t in result.hotspots
        ]

        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)

        print(f"Profile exported to {filename}")

    def export_html(self, result, filename):
        """Export profile as HTML report.

        Args:
            result: ProfilingResult
            filename: Output filename
        """
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Lament Profile Report</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #e0e0e0;
            padding: 20px;
        }}
        h1 {{
            color: #ff6b9d;
            border-bottom: 2px solid #ff6b9d;
        }}
        h2 {{
            color: #ffd93d;
            margin-top: 30px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #333;
        }}
        th {{
            background: #2a2a2a;
            color: #ffd93d;
        }}
        .hotspot {{
            background: #3a1a1a;
        }}
        .summary {{
            background: #2a2a2a;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <h1>💔 Lament Profiler Report</h1>

    <div class="summary">
        <h2>Summary</h2>
        <p><strong>Total Execution Time:</strong> {result.total_time:.6f}s</p>
        <p><strong>Total Memory Delta:</strong> {result.total_memory} bytes</p>
        <p><strong>Functions Profiled:</strong> {len(result.function_profiles)}</p>
        <p><strong>Statements Executed:</strong> {len(result.statement_profiles)}</p>
    </div>

    <h2>Function Profiles</h2>
    <table>
        <tr>
            <th>Function</th>
            <th>Calls</th>
            <th>Total Time</th>
            <th>Avg Time</th>
            <th>Memory Delta</th>
        </tr>
"""

        # Add function rows
        sorted_funcs = sorted(
            result.function_profiles.items(),
            key=lambda x: x[1].total_time,
            reverse=True
        )

        for name, profile in sorted_funcs:
            avg_time = profile.total_time / profile.call_count if profile.call_count > 0 else 0
            html += f"""
        <tr>
            <td>{name}</td>
            <td>{profile.call_count}</td>
            <td>{profile.total_time:.6f}s</td>
            <td>{avg_time:.6f}s</td>
            <td>{profile.memory_delta} bytes</td>
        </tr>
"""

        html += """
    </table>

    <h2>Performance Hotspots</h2>
    <table>
        <tr>
            <th>Location</th>
            <th>Time</th>
            <th>% of Total</th>
        </tr>
"""

        # Add hotspot rows
        for location, hotspot_time in result.hotspots:
            percentage = (hotspot_time / result.total_time * 100) if result.total_time > 0 else 0
            html += f"""
        <tr class="hotspot">
            <td>{location}</td>
            <td>{hotspot_time:.6f}s</td>
            <td>{percentage:.1f}%</td>
        </tr>
"""

        html += """
    </table>
</body>
</html>
"""

        with open(filename, 'w') as f:
            f.write(html)

        print(f"HTML report exported to {filename}")


def profile_file(filename, enable_memory=False):
    """Profile a Lament source file.

    Args:
        filename: Path to .lament file
        enable_memory: Enable memory profiling

    Returns:
        ProfilingResult
    """
    with open(filename, 'r') as f:
        source = f.read()

    source_lines = source.split('\n')

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    profiler = LamentProfiler(ast, source_lines)
    return profiler.profile(enable_memory=enable_memory)


def main():
    """CLI entry point for profiler."""
    if len(sys.argv) < 2:
        print("Usage: lament-profile <file.lament> [options]")
        print("\nProfile Lament program performance.")
        print("\nOptions:")
        print("  --time          Time profiling (default)")
        print("  --memory        Enable memory profiling")
        print("  --flamegraph    Generate flamegraph data")
        print("  --output FILE   Export to file (.json or .html)")
        sys.exit(1)

    filename = sys.argv[1]
    enable_memory = '--memory' in sys.argv
    flamegraph = '--flamegraph' in sys.argv

    output_file = None
    if '--output' in sys.argv:
        idx = sys.argv.index('--output')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    try:
        # Load and parse
        with open(filename, 'r') as f:
            source = f.read()

        source_lines = source.split('\n')

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        # Profile
        print(f"Profiling {filename}...")
        profiler = LamentProfiler(ast, source_lines)
        result = profiler.profile(enable_memory=enable_memory)

        # Print report
        profiler.print_report(result)

        # Export if requested
        if output_file:
            if output_file.endswith('.json'):
                profiler.export_json(result, output_file)
            elif output_file.endswith('.html'):
                profiler.export_html(result, output_file)
            else:
                print(f"Unknown output format: {output_file}")

        # Flamegraph
        if flamegraph:
            flamegraph_data = profiler.generate_flamegraph_data(result)
            flamegraph_file = filename.replace('.lament', '_flamegraph.txt')
            with open(flamegraph_file, 'w') as f:
                for stack, time in flamegraph_data:
                    f.write(f"{stack} {int(time * 1000000)}\n")
            print(f"Flamegraph data written to {flamegraph_file}")

    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error profiling {filename}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
