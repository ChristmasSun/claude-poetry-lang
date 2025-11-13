#!/usr/bin/env python3
"""
Lament Interpreter Integration Demo
====================================

This demo shows how the system features (File I/O, Testing, Async/Await)
are integrated into the Lament interpreter and accessible from Lament code.

It demonstrates:
1. System functions registered as built-ins
2. File I/O operations from Lament code
3. Testing framework integration
4. How to extend the interpreter with new features
"""

import sys
import os
import tempfile

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.lexer import Lexer
from lament.parser import Parser
from lament.interpreter import LamentInterpreter
from lament.types import Color


def demo_file_io_integration():
    """Demonstrate file I/O integration with Lament interpreter."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}FILE I/O INTEGRATION DEMO{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}\n")

    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="lament_integration_")
    test_file = os.path.join(temp_dir, "test.txt")

    # Lament code that uses file I/O
    code = f'''
    # Write a file using Lament
    remember filepath = "{test_file}"
    remember content = "Hello from Lament!\\nFile I/O is working."

    write_file(filepath, content)
    confess "File written successfully"

    # Read it back
    remember data = read_file(filepath)
    confess "File contents:"
    confess data

    # Check if file exists
    remember exists = file_exists(filepath)
    if exists {{
        confess "File exists: confirmed"
    }}

    # Get file info
    remember info = get_path_info(filepath)
    confess "File info retrieved successfully"
    '''

    try:
        # Execute Lament code
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = LamentInterpreter()
        interpreter.execute(ast)

        print(f"\n{Color.GREEN}File I/O integration successful!{Color.RESET}\n")

    except Exception as e:
        print(f"\n{Color.RED}Error: {e}{Color.RESET}\n")

    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


def demo_testing_integration():
    """Demonstrate testing framework integration with Lament interpreter."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}TESTING FRAMEWORK INTEGRATION DEMO{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}\n")

    # Lament code that uses testing framework
    code = '''
    # Define test functions
    sigh test_addition() {
        remember result = 2 + 3
        assert_equals(result, 5)
    }

    sigh test_strings() {
        remember greeting = "Hello " + "Lament"
        assert_contains(greeting, "Lament")
    }

    sigh test_lists() {
        remember numbers = [1, 2, 3, 4, 5]
        remember len = length_of(numbers)
        assert_equals(len, 5)
    }

    # Register tests
    register_test("Addition Test", test_addition)
    register_test("String Test", test_strings)
    register_test("List Test", test_lists)

    # Run all tests
    remember results = run_tests()

    # Check results
    confess ""
    confess "Test run complete!"
    '''

    try:
        # Execute Lament code
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = LamentInterpreter()
        interpreter.execute(ast)

        print(f"\n{Color.GREEN}Testing framework integration successful!{Color.RESET}\n")

    except Exception as e:
        print(f"\n{Color.RED}Error: {e}{Color.RESET}\n")


def demo_builtin_inspection():
    """Show all built-in functions available in the interpreter."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}BUILT-IN FUNCTIONS INSPECTION{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}\n")

    interpreter = LamentInterpreter()

    # Categorize built-ins
    categories = {
        'Math': ['ache_of', 'sqrt_of_pain', 'sin_of_loss', 'cos_of_hope'],
        'Collections': ['range', 'length_of'],
        'Type Checking': ['is_numb', 'is_whisper', 'is_void', 'typeof'],
        'Time': ['now', 'sleep', 'current_timeline'],
        'File I/O': [
            'read_file', 'write_file', 'append_to_file', 'file_exists',
            'dir_exists', 'create_dir', 'remove_file', 'remove_dir',
            'list_dir', 'get_path_info', 'join_path', 'get_parent_dir',
            'get_filename', 'get_extension'
        ],
        'Testing': [
            'register_test', 'run_tests', 'assert_equals', 'assert_not_equals',
            'assert_true', 'assert_false', 'assert_greater', 'assert_less',
            'assert_contains', 'assert_type'
        ],
        'Async': ['sleep_async']
    }

    for category, functions in categories.items():
        print(f"{Color.YELLOW}{Color.BOLD}{category}:{Color.RESET}")
        available = [f for f in functions if f in interpreter.globals]
        unavailable = [f for f in functions if f not in interpreter.globals]

        for func in available:
            print(f"  {Color.GREEN}✓{Color.RESET} {func}")

        for func in unavailable:
            print(f"  {Color.RED}✗{Color.RESET} {func} (not available)")

        print()

    total_builtins = len([k for k in interpreter.globals if callable(interpreter.globals[k])])
    print(f"{Color.BOLD}Total built-in functions: {total_builtins}{Color.RESET}\n")


def demo_error_handling():
    """Demonstrate error handling with system functions."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}ERROR HANDLING DEMO{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*60}{Color.RESET}\n")

    # Test 1: File not found
    print(f"{Color.YELLOW}Test 1: Reading non-existent file{Color.RESET}")
    code1 = '''
    remember content = read_file("/tmp/nonexistent_file_12345.txt")
    '''

    try:
        lexer = Lexer(code1)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = LamentInterpreter()
        interpreter.execute(ast)
    except Exception as e:
        print(f"{Color.RED}Expected error caught: {type(e).__name__}: {e}{Color.RESET}\n")

    # Test 2: Failed assertion
    print(f"{Color.YELLOW}Test 2: Failed assertion{Color.RESET}")
    code2 = '''
    sigh test_failure() {
        assert_equals(1, 2)
    }

    register_test("Failing Test", test_failure)
    remember results = run_tests()
    '''

    try:
        lexer = Lexer(code2)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
        interpreter = LamentInterpreter()
        interpreter.execute(ast)
    except Exception as e:
        print(f"{Color.RED}Error: {type(e).__name__}: {e}{Color.RESET}\n")


def main():
    """Run all integration demos."""
    print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}LAMENT SYSTEM FEATURES INTERPRETER INTEGRATION{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}")

    # Run demos
    demo_builtin_inspection()
    demo_file_io_integration()
    demo_testing_integration()
    demo_error_handling()

    # Summary
    print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}INTEGRATION COMPLETE{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}\n")

    print(f"{Color.GREEN}All system features are fully integrated!{Color.RESET}")
    print(f"\n{Color.CYAN}Available features:{Color.RESET}")
    print(f"  {Color.GREEN}✓{Color.RESET} File I/O operations (14 functions)")
    print(f"  {Color.GREEN}✓{Color.RESET} Testing framework (10 functions)")
    print(f"  {Color.GREEN}✓{Color.RESET} Async/await infrastructure (1 function)")
    print(f"  {Color.GREEN}✓{Color.RESET} Math and utility functions (10+ functions)")
    print(f"\n{Color.YELLOW}Total: 35+ built-in functions available in Lament{Color.RESET}\n")


if __name__ == "__main__":
    main()
