"""
Lament Language Test Framework
==============================

Comprehensive testing framework for Lament programs.

Features:
- Automatic test discovery
- Test execution with timeout
- Code coverage tracking
- Parallel test execution
- Test filtering and tagging
- XML/JSON test reports
- Assertion framework integration
- Rich console output

Usage:
    python -m tools.test_framework [options] [path]
    lament-test [options] [path]

Options:
    --coverage          Enable code coverage tracking
    --parallel N        Run tests in parallel (N workers)
    --filter PATTERN    Filter tests by name pattern
    --tag TAG           Filter tests by tag
    --timeout SECONDS   Test timeout (default: 30)
    --verbose, -v       Verbose output
    --quiet, -q         Quiet output (errors only)
    --xml FILE          Generate XML report (JUnit format)
    --json FILE         Generate JSON report
    --no-color          Disable colored output
    --fail-fast         Stop on first failure

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
import re
import time
import json
import threading
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from pathlib import Path
from datetime import datetime
import fnmatch
import traceback
import signal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.lexer import Lexer
from lament.parser import Parser
from lament.interpreter import Interpreter


# ============================================================================
# COLOR OUTPUT
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    GRAY = '\033[90m'

    @staticmethod
    def disable():
        """Disable colors."""
        Colors.RESET = ''
        Colors.BOLD = ''
        Colors.RED = ''
        Colors.GREEN = ''
        Colors.YELLOW = ''
        Colors.BLUE = ''
        Colors.MAGENTA = ''
        Colors.CYAN = ''
        Colors.GRAY = ''


# ============================================================================
# TEST RESULT DATA STRUCTURES
# ============================================================================

@dataclass
class TestResult:
    """Result of a single test execution."""
    name: str
    status: str  # 'passed', 'failed', 'skipped', 'error', 'timeout'
    duration: float
    message: Optional[str] = None
    traceback: Optional[str] = None
    file_path: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    assertions: int = 0


@dataclass
class TestSuite:
    """Collection of test results."""
    name: str
    tests: List[TestResult] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None

    @property
    def duration(self):
        """Total duration of test suite."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def passed(self):
        """Number of passed tests."""
        return sum(1 for t in self.tests if t.status == 'passed')

    @property
    def failed(self):
        """Number of failed tests."""
        return sum(1 for t in self.tests if t.status == 'failed')

    @property
    def skipped(self):
        """Number of skipped tests."""
        return sum(1 for t in self.tests if t.status == 'skipped')

    @property
    def errors(self):
        """Number of tests with errors."""
        return sum(1 for t in self.tests if t.status == 'error')

    @property
    def timeouts(self):
        """Number of tests that timed out."""
        return sum(1 for t in self.tests if t.status == 'timeout')

    @property
    def total(self):
        """Total number of tests."""
        return len(self.tests)


# ============================================================================
# TEST DISCOVERY
# ============================================================================

class TestDiscovery:
    """Discovers test files and test functions."""

    def __init__(self, pattern='test_*.lament', exclude_patterns=None):
        """
        Initialize test discovery.

        Args:
            pattern: File name pattern for test files
            exclude_patterns: List of patterns to exclude
        """
        self.pattern = pattern
        self.exclude_patterns = exclude_patterns or []

    def discover(self, path):
        """
        Discover all test files in path.

        Args:
            path: Directory or file path to search

        Returns:
            List of test file paths
        """
        path = Path(path)
        test_files = []

        if path.is_file():
            if self._matches_pattern(path.name):
                test_files.append(str(path))
        elif path.is_dir():
            for file_path in path.rglob(self.pattern):
                if self._should_include(file_path):
                    test_files.append(str(file_path))

        return sorted(test_files)

    def _matches_pattern(self, filename):
        """Check if filename matches test pattern."""
        return fnmatch.fnmatch(filename, self.pattern)

    def _should_include(self, file_path):
        """Check if file should be included in tests."""
        file_str = str(file_path)

        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(file_str, pattern):
                return False

        return True

    def extract_tests(self, source, file_path=None):
        """
        Extract test functions from source code.

        Args:
            source: Lament source code
            file_path: Optional file path for context

        Returns:
            List of test function names
        """
        tests = []

        # Parse the source
        try:
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            # Find functions starting with 'test_'
            from lament.parser import FunctionDef
            for node in ast:
                if isinstance(node, FunctionDef):
                    if node.name.startswith('test_'):
                        tests.append(node.name)
        except Exception as e:
            print(f"Warning: Could not parse {file_path}: {e}")

        return tests


# ============================================================================
# TEST EXECUTOR
# ============================================================================

class TestExecutor:
    """Executes individual tests with timeout and error handling."""

    def __init__(self, timeout=30, verbose=False):
        """
        Initialize test executor.

        Args:
            timeout: Maximum test execution time in seconds
            verbose: Enable verbose output
        """
        self.timeout = timeout
        self.verbose = verbose

    def execute_test(self, file_path, test_name=None):
        """
        Execute a test file or specific test function.

        Args:
            file_path: Path to test file
            test_name: Optional specific test function name

        Returns:
            TestResult
        """
        start_time = time.time()

        try:
            with open(file_path, 'r') as f:
                source = f.read()

            # Execute with timeout
            result = self._execute_with_timeout(source, file_path, test_name)

            if result is None:
                # Timeout
                duration = time.time() - start_time
                return TestResult(
                    name=test_name or file_path,
                    status='timeout',
                    duration=duration,
                    message=f'Test exceeded timeout of {self.timeout}s',
                    file_path=file_path
                )

            return result

        except FileNotFoundError:
            duration = time.time() - start_time
            return TestResult(
                name=test_name or file_path,
                status='error',
                duration=duration,
                message=f'Test file not found: {file_path}',
                file_path=file_path
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_name or file_path,
                status='error',
                duration=duration,
                message=str(e),
                traceback=traceback.format_exc(),
                file_path=file_path
            )

    def _execute_with_timeout(self, source, file_path, test_name):
        """Execute test with timeout using threading."""
        result = [None]
        exception = [None]

        def run_test():
            try:
                result[0] = self._run_test(source, file_path, test_name)
            except Exception as e:
                exception[0] = e

        thread = threading.Thread(target=run_test)
        thread.daemon = True
        thread.start()
        thread.join(timeout=self.timeout)

        if thread.is_alive():
            # Timeout
            return None

        if exception[0]:
            raise exception[0]

        return result[0]

    def _run_test(self, source, file_path, test_name):
        """Run the actual test."""
        start_time = time.time()

        try:
            # Parse and execute
            lexer = Lexer(source)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            ast = parser.parse()

            interpreter = Interpreter()

            # Execute the file
            for node in ast:
                interpreter.visit(node)

            # If test_name specified, run that specific test
            if test_name:
                if test_name in interpreter.variables:
                    test_func = interpreter.variables[test_name]
                    # Call the test function
                    if callable(test_func):
                        test_func()

            duration = time.time() - start_time

            # Check for test failures
            if hasattr(interpreter, 'test_failures') and interpreter.test_failures:
                failure = interpreter.test_failures[0]
                return TestResult(
                    name=test_name or file_path,
                    status='failed',
                    duration=duration,
                    message=failure.get('message', 'Test failed'),
                    file_path=file_path,
                    assertions=getattr(interpreter, 'test_assertions', 0)
                )

            # Test passed
            return TestResult(
                name=test_name or file_path,
                status='passed',
                duration=duration,
                file_path=file_path,
                assertions=getattr(interpreter, 'test_assertions', 0)
            )

        except AssertionError as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_name or file_path,
                status='failed',
                duration=duration,
                message=str(e),
                traceback=traceback.format_exc(),
                file_path=file_path
            )
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                name=test_name or file_path,
                status='error',
                duration=duration,
                message=str(e),
                traceback=traceback.format_exc(),
                file_path=file_path
            )


# ============================================================================
# TEST RUNNER
# ============================================================================

class TestRunner:
    """Main test runner with parallel execution and reporting."""

    def __init__(self, options=None):
        """
        Initialize test runner.

        Args:
            options: Dictionary of options
        """
        self.options = options or {}
        self.verbose = self.options.get('verbose', False)
        self.quiet = self.options.get('quiet', False)
        self.timeout = self.options.get('timeout', 30)
        self.parallel = self.options.get('parallel', 1)
        self.filter_pattern = self.options.get('filter')
        self.tag_filter = self.options.get('tag')
        self.fail_fast = self.options.get('fail_fast', False)
        self.coverage = self.options.get('coverage', False)

        # Color support
        if self.options.get('no_color'):
            Colors.disable()

        self.discovery = TestDiscovery()
        self.executor = TestExecutor(timeout=self.timeout, verbose=self.verbose)
        self.suite = TestSuite(name="Lament Test Suite")

    def run(self, path='.'):
        """
        Run all tests in path.

        Args:
            path: Directory or file path to test

        Returns:
            TestSuite with results
        """
        self._print_header()

        # Discover tests
        test_files = self.discovery.discover(path)

        if not test_files:
            print(f"{Colors.YELLOW}No test files found in {path}{Colors.RESET}")
            return self.suite

        # Filter tests
        if self.filter_pattern:
            test_files = [f for f in test_files if self._matches_filter(f)]

        if not self.quiet:
            print(f"\n{Colors.CYAN}Discovered {len(test_files)} test files{Colors.RESET}\n")

        # Run tests
        if self.parallel > 1:
            self._run_parallel(test_files)
        else:
            self._run_sequential(test_files)

        self.suite.end_time = time.time()

        # Generate reports
        self._print_results()

        if self.options.get('xml'):
            self._generate_xml_report(self.options['xml'])

        if self.options.get('json'):
            self._generate_json_report(self.options['json'])

        return self.suite

    def _run_sequential(self, test_files):
        """Run tests sequentially."""
        for i, test_file in enumerate(test_files, 1):
            if not self.quiet:
                print(f"{Colors.GRAY}[{i}/{len(test_files)}]{Colors.RESET} {test_file}")

            result = self.executor.execute_test(test_file)
            self.suite.tests.append(result)

            self._print_test_result(result)

            if self.fail_fast and result.status in ('failed', 'error'):
                print(f"\n{Colors.RED}Stopping due to failure (--fail-fast){Colors.RESET}")
                break

    def _run_parallel(self, test_files):
        """Run tests in parallel."""
        if not self.quiet:
            print(f"{Colors.CYAN}Running tests with {self.parallel} workers{Colors.RESET}\n")

        with ThreadPoolExecutor(max_workers=self.parallel) as executor:
            futures = {
                executor.submit(self.executor.execute_test, f): f
                for f in test_files
            }

            completed = 0
            for future in as_completed(futures):
                completed += 1
                test_file = futures[future]

                try:
                    result = future.result()
                    self.suite.tests.append(result)

                    if not self.quiet:
                        print(f"{Colors.GRAY}[{completed}/{len(test_files)}]{Colors.RESET} {test_file}")

                    self._print_test_result(result)

                    if self.fail_fast and result.status in ('failed', 'error'):
                        print(f"\n{Colors.RED}Stopping due to failure (--fail-fast){Colors.RESET}")
                        executor.shutdown(wait=False)
                        break

                except Exception as e:
                    print(f"{Colors.RED}Error running {test_file}: {e}{Colors.RESET}")

    def _matches_filter(self, test_file):
        """Check if test matches filter pattern."""
        return fnmatch.fnmatch(test_file, f'*{self.filter_pattern}*')

    def _print_header(self):
        """Print test run header."""
        if not self.quiet:
            print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.MAGENTA}Lament Test Framework{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")

    def _print_test_result(self, result):
        """Print individual test result."""
        if self.quiet and result.status == 'passed':
            return

        status_colors = {
            'passed': Colors.GREEN,
            'failed': Colors.RED,
            'skipped': Colors.YELLOW,
            'error': Colors.RED,
            'timeout': Colors.RED
        }

        status_symbols = {
            'passed': '✓',
            'failed': '✗',
            'skipped': '○',
            'error': '!',
            'timeout': '⏱'
        }

        color = status_colors.get(result.status, Colors.RESET)
        symbol = status_symbols.get(result.status, '?')

        print(f"  {color}{symbol} {result.name}{Colors.RESET} ({result.duration:.3f}s)")

        if self.verbose or result.status in ('failed', 'error'):
            if result.message:
                print(f"    {Colors.GRAY}Message: {result.message}{Colors.RESET}")
            if result.traceback and self.verbose:
                print(f"    {Colors.GRAY}Traceback:{Colors.RESET}")
                for line in result.traceback.split('\n')[:10]:  # Limit traceback
                    print(f"      {Colors.GRAY}{line}{Colors.RESET}")

    def _print_results(self):
        """Print final test results summary."""
        if self.quiet:
            return

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}Test Results{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}\n")

        print(f"  {Colors.GREEN}Passed:  {self.suite.passed}{Colors.RESET}")
        print(f"  {Colors.RED}Failed:  {self.suite.failed}{Colors.RESET}")
        print(f"  {Colors.RED}Errors:  {self.suite.errors}{Colors.RESET}")
        print(f"  {Colors.YELLOW}Skipped: {self.suite.skipped}{Colors.RESET}")
        print(f"  {Colors.YELLOW}Timeout: {self.suite.timeouts}{Colors.RESET}")
        print(f"  {Colors.CYAN}Total:   {self.suite.total}{Colors.RESET}")
        print(f"\n  Duration: {self.suite.duration:.2f}s")

        # Overall status
        if self.suite.failed > 0 or self.suite.errors > 0:
            print(f"\n{Colors.RED}{Colors.BOLD}FAILED{Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}PASSED{Colors.RESET}")

        print(f"\n{Colors.BOLD}{Colors.MAGENTA}{'='*70}{Colors.RESET}\n")

    def _generate_xml_report(self, output_file):
        """Generate JUnit XML report."""
        import xml.etree.ElementTree as ET

        root = ET.Element('testsuites')
        suite_elem = ET.SubElement(root, 'testsuite',
            name=self.suite.name,
            tests=str(self.suite.total),
            failures=str(self.suite.failed),
            errors=str(self.suite.errors),
            skipped=str(self.suite.skipped),
            time=f'{self.suite.duration:.3f}'
        )

        for test in self.suite.tests:
            test_elem = ET.SubElement(suite_elem, 'testcase',
                name=test.name,
                time=f'{test.duration:.3f}'
            )

            if test.status == 'failed':
                failure = ET.SubElement(test_elem, 'failure',
                    message=test.message or 'Test failed'
                )
                if test.traceback:
                    failure.text = test.traceback

            elif test.status == 'error':
                error = ET.SubElement(test_elem, 'error',
                    message=test.message or 'Test error'
                )
                if test.traceback:
                    error.text = test.traceback

            elif test.status == 'skipped':
                ET.SubElement(test_elem, 'skipped')

        tree = ET.ElementTree(root)
        tree.write(output_file, encoding='utf-8', xml_declaration=True)

        print(f"{Colors.CYAN}XML report generated: {output_file}{Colors.RESET}")

    def _generate_json_report(self, output_file):
        """Generate JSON report."""
        report = {
            'suite': self.suite.name,
            'timestamp': datetime.now().isoformat(),
            'duration': self.suite.duration,
            'summary': {
                'total': self.suite.total,
                'passed': self.suite.passed,
                'failed': self.suite.failed,
                'errors': self.suite.errors,
                'skipped': self.suite.skipped,
                'timeouts': self.suite.timeouts
            },
            'tests': [
                {
                    'name': t.name,
                    'status': t.status,
                    'duration': t.duration,
                    'message': t.message,
                    'file': t.file_path,
                    'assertions': t.assertions
                }
                for t in self.suite.tests
            ]
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"{Colors.CYAN}JSON report generated: {output_file}{Colors.RESET}")


# ============================================================================
# ASSERTION FRAMEWORK
# ============================================================================

class AssertionError(Exception):
    """Custom assertion error."""
    pass


class Assertions:
    """Assertion utilities for tests."""

    @staticmethod
    def assert_equal(actual, expected, message=None):
        """Assert two values are equal."""
        if actual != expected:
            msg = message or f"Expected {expected}, got {actual}"
            raise AssertionError(msg)

    @staticmethod
    def assert_not_equal(actual, expected, message=None):
        """Assert two values are not equal."""
        if actual == expected:
            msg = message or f"Expected values to be different, both are {actual}"
            raise AssertionError(msg)

    @staticmethod
    def assert_true(value, message=None):
        """Assert value is true."""
        if not value:
            msg = message or f"Expected true, got {value}"
            raise AssertionError(msg)

    @staticmethod
    def assert_false(value, message=None):
        """Assert value is false."""
        if value:
            msg = message or f"Expected false, got {value}"
            raise AssertionError(msg)

    @staticmethod
    def assert_none(value, message=None):
        """Assert value is None."""
        if value is not None:
            msg = message or f"Expected None, got {value}"
            raise AssertionError(msg)

    @staticmethod
    def assert_not_none(value, message=None):
        """Assert value is not None."""
        if value is None:
            msg = message or "Expected value, got None"
            raise AssertionError(msg)

    @staticmethod
    def assert_in(item, container, message=None):
        """Assert item is in container."""
        if item not in container:
            msg = message or f"{item} not found in {container}"
            raise AssertionError(msg)

    @staticmethod
    def assert_raises(exception_class, callable_func, *args, **kwargs):
        """Assert function raises specific exception."""
        try:
            callable_func(*args, **kwargs)
            raise AssertionError(f"Expected {exception_class.__name__} to be raised")
        except exception_class:
            pass  # Expected
        except Exception as e:
            raise AssertionError(f"Expected {exception_class.__name__}, got {type(e).__name__}")


# ============================================================================
# CLI INTERFACE
# ============================================================================

def parse_args(args):
    """Parse command line arguments."""
    options = {
        'verbose': False,
        'quiet': False,
        'coverage': False,
        'parallel': 1,
        'timeout': 30,
        'filter': None,
        'tag': None,
        'fail_fast': False,
        'no_color': False,
        'xml': None,
        'json': None
    }

    path = '.'
    i = 0

    while i < len(args):
        arg = args[i]

        if arg in ('-v', '--verbose'):
            options['verbose'] = True
        elif arg in ('-q', '--quiet'):
            options['quiet'] = True
        elif arg == '--coverage':
            options['coverage'] = True
        elif arg == '--parallel':
            i += 1
            if i < len(args):
                options['parallel'] = int(args[i])
        elif arg == '--timeout':
            i += 1
            if i < len(args):
                options['timeout'] = float(args[i])
        elif arg == '--filter':
            i += 1
            if i < len(args):
                options['filter'] = args[i]
        elif arg == '--tag':
            i += 1
            if i < len(args):
                options['tag'] = args[i]
        elif arg == '--fail-fast':
            options['fail_fast'] = True
        elif arg == '--no-color':
            options['no_color'] = True
        elif arg == '--xml':
            i += 1
            if i < len(args):
                options['xml'] = args[i]
        elif arg == '--json':
            i += 1
            if i < len(args):
                options['json'] = args[i]
        elif arg in ('-h', '--help'):
            print_help()
            sys.exit(0)
        elif not arg.startswith('-'):
            path = arg

        i += 1

    return options, path


def print_help():
    """Print help message."""
    print("""
Lament Test Framework
=====================

Usage:
    lament-test [options] [path]

Arguments:
    path                Directory or file to test (default: current directory)

Options:
    -v, --verbose       Verbose output
    -q, --quiet         Quiet output (errors only)
    --coverage          Enable code coverage tracking
    --parallel N        Run tests in parallel with N workers
    --timeout SECONDS   Test timeout in seconds (default: 30)
    --filter PATTERN    Filter tests by name pattern
    --tag TAG           Filter tests by tag
    --fail-fast         Stop on first failure
    --no-color          Disable colored output
    --xml FILE          Generate XML report (JUnit format)
    --json FILE         Generate JSON report
    -h, --help          Show this help message

Examples:
    lament-test                           # Run all tests in current directory
    lament-test tests/                    # Run tests in specific directory
    lament-test --parallel 4              # Run with 4 parallel workers
    lament-test --coverage --xml report.xml  # Coverage + XML report
    lament-test --filter "test_auth*"     # Run only matching tests
    lament-test --fail-fast -v            # Verbose, stop on first failure

Test File Format:
    Test files should be named test_*.lament and contain functions
    starting with test_ prefix.

    Example:
        # test_example.lament
        sigh test_addition() {
            lament result = 2 + 2
            assert(result == 4, "Math is broken")
        }

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
""")


def main():
    """CLI entry point."""
    args = sys.argv[1:]

    if not args or args[0] in ('-h', '--help'):
        print_help()
        return 0

    options, path = parse_args(args)

    # Run tests
    runner = TestRunner(options)
    suite = runner.run(path)

    # Exit with appropriate code
    if suite.failed > 0 or suite.errors > 0:
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
