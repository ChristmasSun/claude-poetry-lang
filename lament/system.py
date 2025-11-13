"""
Lament Language System Module
==============================

This module provides essential system-level features for the Lament programming language:
1. Async/Await - Cooperative multitasking with event loop
2. File I/O - File and directory operations
3. Testing Framework - Test blocks with assertions and colored output

These features integrate seamlessly with Lament's emotional syntax while providing
production-quality functionality for real-world applications.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import asyncio
import os
import sys
import pathlib
import time
from typing import Any, List, Dict, Callable, Optional
from dataclasses import dataclass
from lament.types import Color


# ============================================================================
# ASYNC/AWAIT SYSTEM
# ============================================================================

class LamentEventLoop:
    """
    Event loop for Lament's async/await system.

    Provides cooperative multitasking through coroutines, allowing multiple
    tasks to run concurrently without threading. The event loop manages
    task scheduling and execution.

    Features:
    - Task scheduling and execution
    - Cooperative yielding
    - Async function registration
    - Promise/future-like behavior
    """

    def __init__(self):
        """Initialize the event loop with empty task queue."""
        self.tasks = []
        self.current_task = None
        self.running = False

    def create_task(self, coro):
        """
        Create a new task from a coroutine.

        Args:
            coro: Coroutine or generator to wrap as a task

        Returns:
            Task wrapper that can be awaited
        """
        task = {
            'coro': coro,
            'status': 'pending',
            'result': None,
            'error': None
        }
        self.tasks.append(task)
        return task

    def run_until_complete(self, coro):
        """
        Run the event loop until the given coroutine completes.

        Args:
            coro: Main coroutine to execute

        Returns:
            Result of the coroutine execution
        """
        main_task = self.create_task(coro)
        self.running = True

        while self.running and any(t['status'] == 'pending' for t in self.tasks):
            for task in self.tasks:
                if task['status'] == 'pending':
                    self.current_task = task
                    try:
                        # Step the coroutine
                        result = next(task['coro'])

                        # If the result is a task, we're awaiting it
                        if isinstance(result, dict) and 'coro' in result:
                            # Check if the awaited task is complete
                            if result['status'] == 'complete':
                                # Resume with the result
                                task['coro'].send(result['result'])

                    except StopIteration as e:
                        # Coroutine completed
                        task['status'] = 'complete'
                        task['result'] = getattr(e, 'value', None)
                    except Exception as e:
                        # Coroutine failed
                        task['status'] = 'error'
                        task['error'] = e

        self.running = False
        return main_task['result']


# Global event loop instance
_event_loop = LamentEventLoop()


def async_function(func):
    """
    Decorator to mark a function as async.

    Wraps a regular function to return a generator that can be used
    with the event loop. This allows Lament's 'async sigh' syntax.

    Args:
        func: Function to make async

    Returns:
        Wrapped function that returns a generator
    """
    def wrapper(*args, **kwargs):
        def generator():
            result = func(*args, **kwargs)
            yield result
            return result
        return generator()
    wrapper.__is_async__ = True
    return wrapper


def await_task(task):
    """
    Await a task in the event loop.

    This is called by the 'await' expression in Lament code.
    It yields control back to the event loop until the task completes.

    Args:
        task: Task to await

    Returns:
        Result of the awaited task
    """
    # If it's a coroutine, create a task for it
    if hasattr(task, '__next__'):
        task_obj = _event_loop.create_task(task)
    else:
        task_obj = task

    # Yield to event loop
    while task_obj['status'] == 'pending':
        yield task_obj

    if task_obj['status'] == 'error':
        raise task_obj['error']

    return task_obj['result']


def sleep_async(seconds):
    """
    Async sleep function that yields control to the event loop.

    Args:
        seconds: Number of seconds to sleep

    Yields:
        Control back to event loop
    """
    start = time.time()
    while time.time() - start < seconds:
        yield None
    return None


# ============================================================================
# FILE I/O SYSTEM
# ============================================================================

class FileIOError(Exception):
    """Exception raised for file I/O errors in Lament."""
    pass


def read_file(path):
    """
    Read entire contents of a file.

    Args:
        path: Path to the file (string)

    Returns:
        String containing file contents

    Raises:
        FileIOError: If file cannot be read
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()
        with open(path_obj, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileIOError(f"File not found: {path}")
    except PermissionError:
        raise FileIOError(f"Permission denied: {path}")
    except IsADirectoryError:
        raise FileIOError(f"Path is a directory: {path}")
    except Exception as e:
        raise FileIOError(f"Error reading file {path}: {str(e)}")


def write_file(path, content):
    """
    Write content to a file, creating it if it doesn't exist.

    Args:
        path: Path to the file (string)
        content: Content to write (string)

    Returns:
        Number of bytes written

    Raises:
        FileIOError: If file cannot be written
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()
        # Create parent directories if they don't exist
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(path_obj, 'w', encoding='utf-8') as f:
            bytes_written = f.write(content)
        return bytes_written
    except PermissionError:
        raise FileIOError(f"Permission denied: {path}")
    except Exception as e:
        raise FileIOError(f"Error writing file {path}: {str(e)}")


def append_to_file(path, content):
    """
    Append content to a file.

    Args:
        path: Path to the file (string)
        content: Content to append (string)

    Returns:
        Number of bytes written

    Raises:
        FileIOError: If file cannot be written
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()
        # Create parent directories if they don't exist
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        with open(path_obj, 'a', encoding='utf-8') as f:
            bytes_written = f.write(content)
        return bytes_written
    except PermissionError:
        raise FileIOError(f"Permission denied: {path}")
    except Exception as e:
        raise FileIOError(f"Error appending to file {path}: {str(e)}")


def file_exists(path):
    """
    Check if a file exists.

    Args:
        path: Path to check (string)

    Returns:
        Boolean indicating if file exists
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()
        return path_obj.exists() and path_obj.is_file()
    except Exception:
        return False


def dir_exists(path):
    """
    Check if a directory exists.

    Args:
        path: Path to check (string)

    Returns:
        Boolean indicating if directory exists
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()
        return path_obj.exists() and path_obj.is_dir()
    except Exception:
        return False


def create_dir(path):
    """
    Create a directory (and parent directories if needed).

    Args:
        path: Path to create (string)

    Returns:
        True if successful

    Raises:
        FileIOError: If directory cannot be created
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()
        path_obj.mkdir(parents=True, exist_ok=True)
        return True
    except PermissionError:
        raise FileIOError(f"Permission denied: {path}")
    except Exception as e:
        raise FileIOError(f"Error creating directory {path}: {str(e)}")


def remove_file(path):
    """
    Remove a file.

    Args:
        path: Path to file (string)

    Returns:
        True if successful

    Raises:
        FileIOError: If file cannot be removed
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()
        path_obj.unlink()
        return True
    except FileNotFoundError:
        raise FileIOError(f"File not found: {path}")
    except PermissionError:
        raise FileIOError(f"Permission denied: {path}")
    except IsADirectoryError:
        raise FileIOError(f"Path is a directory: {path}")
    except Exception as e:
        raise FileIOError(f"Error removing file {path}: {str(e)}")


def remove_dir(path):
    """
    Remove an empty directory.

    Args:
        path: Path to directory (string)

    Returns:
        True if successful

    Raises:
        FileIOError: If directory cannot be removed
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()
        path_obj.rmdir()
        return True
    except FileNotFoundError:
        raise FileIOError(f"Directory not found: {path}")
    except PermissionError:
        raise FileIOError(f"Permission denied: {path}")
    except OSError as e:
        if "not empty" in str(e).lower():
            raise FileIOError(f"Directory not empty: {path}")
        raise FileIOError(f"Error removing directory {path}: {str(e)}")
    except Exception as e:
        raise FileIOError(f"Error removing directory {path}: {str(e)}")


def list_dir(path):
    """
    List contents of a directory.

    Args:
        path: Path to directory (string)

    Returns:
        List of filenames in the directory

    Raises:
        FileIOError: If directory cannot be listed
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()
        if not path_obj.is_dir():
            raise FileIOError(f"Not a directory: {path}")
        return [item.name for item in path_obj.iterdir()]
    except FileNotFoundError:
        raise FileIOError(f"Directory not found: {path}")
    except PermissionError:
        raise FileIOError(f"Permission denied: {path}")
    except Exception as e:
        raise FileIOError(f"Error listing directory {path}: {str(e)}")


def get_path_info(path):
    """
    Get information about a path.

    Args:
        path: Path to check (string)

    Returns:
        Dictionary with path information
    """
    try:
        path_obj = pathlib.Path(path).expanduser().resolve()

        if not path_obj.exists():
            return {'exists': False}

        stat = path_obj.stat()

        return {
            'exists': True,
            'is_file': path_obj.is_file(),
            'is_dir': path_obj.is_dir(),
            'size': stat.st_size,
            'modified': int(stat.st_mtime),
            'created': int(stat.st_ctime),
            'absolute_path': str(path_obj)
        }
    except Exception as e:
        return {'exists': False, 'error': str(e)}


def join_path(*parts):
    """
    Join path components.

    Args:
        *parts: Path components to join

    Returns:
        Joined path string
    """
    return str(pathlib.Path(*parts))


def get_parent_dir(path):
    """
    Get parent directory of a path.

    Args:
        path: Path string

    Returns:
        Parent directory path
    """
    return str(pathlib.Path(path).parent)


def get_filename(path):
    """
    Get filename from a path.

    Args:
        path: Path string

    Returns:
        Filename (last component of path)
    """
    return pathlib.Path(path).name


def get_extension(path):
    """
    Get file extension from a path.

    Args:
        path: Path string

    Returns:
        File extension (including dot)
    """
    return pathlib.Path(path).suffix


# ============================================================================
# TESTING FRAMEWORK
# ============================================================================

@dataclass
class TestResult:
    """
    Result of a single test execution.

    Attributes:
        name: Name of the test
        passed: Whether the test passed
        error: Error message if test failed
        duration: Test execution time in seconds
    """
    name: str
    passed: bool
    error: Optional[str] = None
    duration: float = 0.0


class TestRunner:
    """
    Test runner for Lament's testing framework.

    Manages test registration, execution, and result reporting.
    Provides colored output and detailed failure information.
    """

    def __init__(self):
        """Initialize test runner with empty test registry."""
        self.tests = []
        self.results = []

    def register_test(self, name, test_func):
        """
        Register a test function.

        Args:
            name: Name of the test
            test_func: Function to execute for this test
        """
        self.tests.append((name, test_func))

    def run_all(self):
        """
        Run all registered tests and collect results.

        Returns:
            Dictionary with summary statistics
        """
        self.results = []

        print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}  LAMENT TEST RUNNER{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}\n")

        for name, test_func in self.tests:
            result = self._run_test(name, test_func)
            self.results.append(result)

        return self._print_summary()

    def _run_test(self, name, test_func):
        """
        Run a single test.

        Args:
            name: Test name
            test_func: Test function

        Returns:
            TestResult object
        """
        print(f"{Color.BOLD}Running:{Color.RESET} {name}...", end=' ')
        sys.stdout.flush()

        start_time = time.time()

        try:
            test_func()
            duration = time.time() - start_time
            print(f"{Color.GREEN}{Color.BOLD}PASS{Color.RESET} ({duration:.3f}s)")
            return TestResult(name=name, passed=True, duration=duration)

        except AssertionError as e:
            duration = time.time() - start_time
            print(f"{Color.RED}{Color.BOLD}FAIL{Color.RESET} ({duration:.3f}s)")
            error_msg = str(e) if str(e) else "Assertion failed"
            print(f"  {Color.RED}Error: {error_msg}{Color.RESET}")
            return TestResult(name=name, passed=False, error=error_msg, duration=duration)

        except Exception as e:
            duration = time.time() - start_time
            print(f"{Color.RED}{Color.BOLD}ERROR{Color.RESET} ({duration:.3f}s)")
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"  {Color.RED}Error: {error_msg}{Color.RESET}")
            return TestResult(name=name, passed=False, error=error_msg, duration=duration)

    def _print_summary(self):
        """
        Print test execution summary.

        Returns:
            Dictionary with test statistics
        """
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed
        total_duration = sum(r.duration for r in self.results)

        print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}  TEST SUMMARY{Color.RESET}")
        print(f"{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}\n")

        print(f"  Total tests:  {Color.BOLD}{len(self.results)}{Color.RESET}")
        print(f"  Passed:       {Color.GREEN}{Color.BOLD}{passed}{Color.RESET}")
        print(f"  Failed:       {Color.RED}{Color.BOLD}{failed}{Color.RESET}")
        print(f"  Duration:     {Color.BOLD}{total_duration:.3f}s{Color.RESET}")

        if failed > 0:
            print(f"\n{Color.RED}{Color.BOLD}  FAILED TESTS:{Color.RESET}")
            for result in self.results:
                if not result.passed:
                    print(f"    {Color.RED}- {result.name}{Color.RESET}")
                    if result.error:
                        print(f"      {Color.YELLOW}{result.error}{Color.RESET}")

        print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}\n")

        return {
            'total': len(self.results),
            'passed': passed,
            'failed': failed,
            'duration': total_duration,
            'success': failed == 0
        }


# Global test runner instance
_test_runner = TestRunner()


def register_test(name, test_func):
    """
    Register a test with the global test runner.

    Args:
        name: Test name
        test_func: Test function to execute
    """
    _test_runner.register_test(name, test_func)


def run_tests():
    """
    Run all registered tests.

    Returns:
        Test summary dictionary
    """
    return _test_runner.run_all()


def assert_equals(actual, expected, message=None):
    """
    Assert that two values are equal.

    Args:
        actual: Actual value
        expected: Expected value
        message: Optional custom error message

    Raises:
        AssertionError: If values are not equal
    """
    if actual != expected:
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"Expected {expected}, but got {actual}")


def assert_not_equals(actual, expected, message=None):
    """
    Assert that two values are not equal.

    Args:
        actual: Actual value
        expected: Value that should not match
        message: Optional custom error message

    Raises:
        AssertionError: If values are equal
    """
    if actual == expected:
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"Expected not {expected}, but got {actual}")


def assert_true(value, message=None):
    """
    Assert that a value is truthy.

    Args:
        value: Value to check
        message: Optional custom error message

    Raises:
        AssertionError: If value is not truthy
    """
    if not value:
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"Expected truthy value, but got {value}")


def assert_false(value, message=None):
    """
    Assert that a value is falsy.

    Args:
        value: Value to check
        message: Optional custom error message

    Raises:
        AssertionError: If value is not falsy
    """
    if value:
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"Expected falsy value, but got {value}")


def assert_greater(actual, expected, message=None):
    """
    Assert that actual is greater than expected.

    Args:
        actual: Actual value
        expected: Value to compare against
        message: Optional custom error message

    Raises:
        AssertionError: If actual is not greater than expected
    """
    if not actual > expected:
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"Expected {actual} > {expected}")


def assert_less(actual, expected, message=None):
    """
    Assert that actual is less than expected.

    Args:
        actual: Actual value
        expected: Value to compare against
        message: Optional custom error message

    Raises:
        AssertionError: If actual is not less than expected
    """
    if not actual < expected:
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"Expected {actual} < {expected}")


def assert_contains(container, item, message=None):
    """
    Assert that a container contains an item.

    Args:
        container: Container to check
        item: Item to look for
        message: Optional custom error message

    Raises:
        AssertionError: If item is not in container
    """
    if item not in container:
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"Expected {container} to contain {item}")


def assert_type(value, expected_type_name, message=None):
    """
    Assert that a value has the expected type.

    Args:
        value: Value to check
        expected_type_name: Expected type name (e.g., 'numb', 'whisper')
        message: Optional custom error message

    Raises:
        AssertionError: If type doesn't match
    """
    type_map = {
        'numb': int,
        'ache': float,
        'whisper': str,
        'maybe': bool,
        'void': type(None),
        'list': list,
        'dict': dict
    }

    expected_type = type_map.get(expected_type_name)
    if expected_type is None:
        raise AssertionError(f"Unknown type: {expected_type_name}")

    if not isinstance(value, expected_type):
        if message:
            raise AssertionError(message)
        else:
            raise AssertionError(f"Expected type {expected_type_name}, but got {type(value).__name__}")


# ============================================================================
# INTEGRATION WITH LAMENT INTERPRETER
# ============================================================================

def register_system_builtins(interpreter):
    """
    Register all system functions with a Lament interpreter.

    This function should be called during interpreter initialization to
    add all async, file I/O, and testing functions to the global scope.

    Args:
        interpreter: LamentInterpreter instance
    """
    # File I/O functions
    interpreter.globals['read_file'] = read_file
    interpreter.globals['write_file'] = write_file
    interpreter.globals['append_to_file'] = append_to_file
    interpreter.globals['file_exists'] = file_exists
    interpreter.globals['dir_exists'] = dir_exists
    interpreter.globals['create_dir'] = create_dir
    interpreter.globals['remove_file'] = remove_file
    interpreter.globals['remove_dir'] = remove_dir
    interpreter.globals['list_dir'] = list_dir
    interpreter.globals['get_path_info'] = get_path_info
    interpreter.globals['join_path'] = join_path
    interpreter.globals['get_parent_dir'] = get_parent_dir
    interpreter.globals['get_filename'] = get_filename
    interpreter.globals['get_extension'] = get_extension

    # Testing functions
    interpreter.globals['register_test'] = register_test
    interpreter.globals['run_tests'] = run_tests
    interpreter.globals['assert_equals'] = assert_equals
    interpreter.globals['assert_not_equals'] = assert_not_equals
    interpreter.globals['assert_true'] = assert_true
    interpreter.globals['assert_false'] = assert_false
    interpreter.globals['assert_greater'] = assert_greater
    interpreter.globals['assert_less'] = assert_less
    interpreter.globals['assert_contains'] = assert_contains
    interpreter.globals['assert_type'] = assert_type

    # Async functions (simplified for now - full async/await needs parser support)
    interpreter.globals['sleep_async'] = sleep_async


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Async/Await
    'LamentEventLoop',
    'async_function',
    'await_task',
    'sleep_async',

    # File I/O
    'FileIOError',
    'read_file',
    'write_file',
    'append_to_file',
    'file_exists',
    'dir_exists',
    'create_dir',
    'remove_file',
    'remove_dir',
    'list_dir',
    'get_path_info',
    'join_path',
    'get_parent_dir',
    'get_filename',
    'get_extension',

    # Testing
    'TestResult',
    'TestRunner',
    'register_test',
    'run_tests',
    'assert_equals',
    'assert_not_equals',
    'assert_true',
    'assert_false',
    'assert_greater',
    'assert_less',
    'assert_contains',
    'assert_type',

    # Integration
    'register_system_builtins',
]
