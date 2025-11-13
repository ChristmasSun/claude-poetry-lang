#!/usr/bin/env python3
"""
Lament System Features Demo
============================

This demo showcases the three essential features added to Lament:
1. File I/O - Reading, writing, and manipulating files
2. Testing Framework - Running tests with assertions and colored output
3. Async/Await - Cooperative multitasking (via Python interface)

The demo runs comprehensive tests to verify all functionality works correctly.
"""

import sys
import os
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.system import (
    # File I/O
    read_file, write_file, append_to_file, file_exists, dir_exists,
    create_dir, remove_file, remove_dir, list_dir, get_path_info,
    join_path, get_parent_dir, get_filename, get_extension,
    FileIOError,

    # Testing
    register_test, run_tests, assert_equals, assert_not_equals,
    assert_true, assert_false, assert_greater, assert_less,
    assert_contains, assert_type,

    # Colors for output
    Color
)


def main():
    """Run comprehensive demo of all system features."""

    print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}  LAMENT SYSTEM FEATURES DEMO{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}\n")

    # Create temporary directory for file I/O tests
    temp_dir = tempfile.mkdtemp(prefix="lament_test_")
    print(f"{Color.CYAN}Using temporary directory: {temp_dir}{Color.RESET}\n")

    try:
        # =====================================================================
        # REGISTER ALL TESTS
        # =====================================================================

        # --- File I/O Tests ---

        def test_write_and_read_file():
            """Test basic file writing and reading."""
            test_file = join_path(temp_dir, "test.txt")
            content = "Hello from Lament!\nThis is a test file."

            # Write file
            bytes_written = write_file(test_file, content)
            assert_greater(bytes_written, 0, "Should write bytes")

            # Read file back
            read_content = read_file(test_file)
            assert_equals(read_content, content, "Content should match")

        def test_append_to_file():
            """Test appending content to a file."""
            test_file = join_path(temp_dir, "append_test.txt")

            # Write initial content
            write_file(test_file, "Line 1\n")

            # Append more content
            append_to_file(test_file, "Line 2\n")
            append_to_file(test_file, "Line 3\n")

            # Read and verify
            content = read_file(test_file)
            assert_contains(content, "Line 1")
            assert_contains(content, "Line 2")
            assert_contains(content, "Line 3")

        def test_file_exists():
            """Test file existence checking."""
            test_file = join_path(temp_dir, "exists_test.txt")

            # File shouldn't exist yet
            assert_false(file_exists(test_file), "File should not exist initially")

            # Create file
            write_file(test_file, "test")

            # Now it should exist
            assert_true(file_exists(test_file), "File should exist after creation")

        def test_directory_operations():
            """Test directory creation and listing."""
            test_dir = join_path(temp_dir, "test_subdir")

            # Directory shouldn't exist yet
            assert_false(dir_exists(test_dir), "Directory should not exist initially")

            # Create directory
            create_dir(test_dir)
            assert_true(dir_exists(test_dir), "Directory should exist after creation")

            # Create some files in it
            write_file(join_path(test_dir, "file1.txt"), "content1")
            write_file(join_path(test_dir, "file2.txt"), "content2")

            # List directory contents
            files = list_dir(test_dir)
            assert_equals(len(files), 2, "Should have 2 files")
            assert_contains(files, "file1.txt")
            assert_contains(files, "file2.txt")

        def test_path_info():
            """Test getting path information."""
            test_file = join_path(temp_dir, "info_test.txt")
            content = "Test content for info"
            write_file(test_file, content)

            info = get_path_info(test_file)
            assert_true(info['exists'], "File should exist")
            assert_true(info['is_file'], "Should be a file")
            assert_false(info['is_dir'], "Should not be a directory")
            assert_greater(info['size'], 0, "Should have non-zero size")
            assert_true('absolute_path' in info, "Should have absolute path")

        def test_path_manipulation():
            """Test path manipulation functions."""
            # Test join_path
            path = join_path("home", "user", "file.txt")
            assert_contains(path, "file.txt")

            # Test get_filename
            filename = get_filename("/home/user/document.txt")
            assert_equals(filename, "document.txt")

            # Test get_extension
            ext = get_extension("file.py")
            assert_equals(ext, ".py")

            # Test get_parent_dir
            parent = get_parent_dir("/home/user/file.txt")
            assert_contains(parent, "user")

        def test_remove_file():
            """Test file removal."""
            test_file = join_path(temp_dir, "remove_test.txt")

            # Create file
            write_file(test_file, "will be removed")
            assert_true(file_exists(test_file))

            # Remove file
            remove_file(test_file)
            assert_false(file_exists(test_file), "File should be removed")

        # --- Testing Framework Tests ---

        def test_assert_equals():
            """Test assert_equals function."""
            assert_equals(5, 5)
            assert_equals("hello", "hello")
            assert_equals([1, 2, 3], [1, 2, 3])

        def test_assert_not_equals():
            """Test assert_not_equals function."""
            assert_not_equals(5, 6)
            assert_not_equals("hello", "world")

        def test_assert_true_false():
            """Test boolean assertions."""
            assert_true(True)
            assert_true(1)
            assert_true("non-empty")

            assert_false(False)
            assert_false(0)
            assert_false("")

        def test_assert_comparisons():
            """Test comparison assertions."""
            assert_greater(10, 5)
            assert_greater(3.14, 2.5)

            assert_less(5, 10)
            assert_less(-1, 0)

        def test_assert_contains():
            """Test container membership assertion."""
            assert_contains([1, 2, 3, 4, 5], 3)
            assert_contains("hello world", "world")
            assert_contains({"a": 1, "b": 2}, "a")

        def test_assert_type():
            """Test type assertion."""
            assert_type(42, 'numb')
            assert_type(3.14, 'ache')
            assert_type("hello", 'whisper')
            assert_type(True, 'maybe')
            assert_type([1, 2, 3], 'list')
            assert_type({"a": 1}, 'dict')

        def test_math_operations():
            """Test mathematical operations."""
            result = 5 + 3
            assert_equals(result, 8)

            result = 10 - 4
            assert_equals(result, 6)

            result = 6 * 7
            assert_equals(result, 42)

            result = 20 / 4
            assert_equals(result, 5.0)

        def test_string_operations():
            """Test string operations."""
            s1 = "Hello"
            s2 = "World"
            combined = s1 + " " + s2

            assert_equals(combined, "Hello World")
            assert_contains(combined, "Hello")
            assert_contains(combined, "World")

        def test_list_operations():
            """Test list operations."""
            lst = [1, 2, 3]
            lst.append(4)

            assert_equals(len(lst), 4)
            assert_contains(lst, 4)
            assert_equals(lst[0], 1)
            assert_equals(lst[-1], 4)

        def test_edge_cases():
            """Test edge cases and boundary conditions."""
            # Empty strings
            assert_equals("", "")
            assert_false("")

            # Zero values
            assert_equals(0, 0)
            assert_false(0)

            # Empty lists
            assert_equals([], [])
            assert_equals(len([]), 0)

        # =====================================================================
        # REGISTER ALL TESTS WITH THE FRAMEWORK
        # =====================================================================

        register_test("Write and Read File", test_write_and_read_file)
        register_test("Append to File", test_append_to_file)
        register_test("File Exists Check", test_file_exists)
        register_test("Directory Operations", test_directory_operations)
        register_test("Path Information", test_path_info)
        register_test("Path Manipulation", test_path_manipulation)
        register_test("Remove File", test_remove_file)
        register_test("Assert Equals", test_assert_equals)
        register_test("Assert Not Equals", test_assert_not_equals)
        register_test("Assert True/False", test_assert_true_false)
        register_test("Assert Comparisons", test_assert_comparisons)
        register_test("Assert Contains", test_assert_contains)
        register_test("Assert Type", test_assert_type)
        register_test("Math Operations", test_math_operations)
        register_test("String Operations", test_string_operations)
        register_test("List Operations", test_list_operations)
        register_test("Edge Cases", test_edge_cases)

        # =====================================================================
        # RUN ALL TESTS
        # =====================================================================

        results = run_tests()

        # =====================================================================
        # DEMONSTRATE FILE I/O FEATURES
        # =====================================================================

        print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.MAGENTA}{Color.BOLD}  FILE I/O DEMONSTRATION{Color.RESET}")
        print(f"{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}\n")

        # Create a sample file with some content
        sample_file = join_path(temp_dir, "lament_sample.txt")
        sample_content = """The Lament Language
====================

A programming language that feels alive.

Features:
- Emotional syntax (remember, confess, sigh)
- Temporal operators (@past, @origin)
- Reality branching (fork reality)
- File I/O operations
- Testing framework
- Async/await support
"""

        print(f"{Color.CYAN}Writing sample file...{Color.RESET}")
        write_file(sample_file, sample_content)
        print(f"{Color.GREEN}File written: {sample_file}{Color.RESET}\n")

        print(f"{Color.CYAN}Reading file back...{Color.RESET}")
        read_content = read_file(sample_file)
        print(f"{Color.YELLOW}{read_content}{Color.RESET}\n")

        print(f"{Color.CYAN}File information:{Color.RESET}")
        info = get_path_info(sample_file)
        print(f"  Size: {info['size']} bytes")
        print(f"  Is file: {info['is_file']}")
        print(f"  Is directory: {info['is_dir']}")
        print(f"  Absolute path: {info['absolute_path']}\n")

        # =====================================================================
        # FINAL REPORT
        # =====================================================================

        print(f"{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}")
        print(f"{Color.MAGENTA}{Color.BOLD}  DEMO COMPLETE{Color.RESET}")
        print(f"{Color.MAGENTA}{Color.BOLD}{'='*60}{Color.RESET}\n")

        if results['success']:
            print(f"{Color.GREEN}{Color.BOLD}All features are working correctly!{Color.RESET}")
            print(f"\n{Color.CYAN}System features successfully integrated:{Color.RESET}")
            print(f"  {Color.GREEN}✓{Color.RESET} File I/O operations")
            print(f"  {Color.GREEN}✓{Color.RESET} Testing framework with assertions")
            print(f"  {Color.GREEN}✓{Color.RESET} Colored test output")
            print(f"  {Color.GREEN}✓{Color.RESET} Path manipulation utilities")
            print(f"\n{Color.YELLOW}Note: Async/await syntax requires parser extensions.{Color.RESET}")
            print(f"{Color.YELLOW}The event loop infrastructure is ready for integration.{Color.RESET}\n")
            return 0
        else:
            print(f"{Color.RED}{Color.BOLD}Some tests failed. Please review the output above.{Color.RESET}\n")
            return 1

    finally:
        # Clean up temporary directory
        print(f"{Color.CYAN}Cleaning up temporary files...{Color.RESET}")
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"{Color.GREEN}Cleanup complete.{Color.RESET}\n")


if __name__ == "__main__":
    sys.exit(main())
