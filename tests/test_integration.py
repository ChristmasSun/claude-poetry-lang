#!/usr/bin/env python3
"""
Integration test for the modular Lament parser.
Tests that the parser can be used with the original interpreter.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lament import Lexer, Parser
from lament import (
    VariableDecl, ConfessStmt, Assignment, IfStmt, WhileStmt, ForStmt,
    FunctionDef, FunctionCall, ExhaleStmt, TemporalAccess,
    NumberLiteral, StringLiteral, BinaryOp, Identifier
)

def test_basic_parsing():
    """Test basic parsing operations."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Parsing")
    print("=" * 60)

    code = """
    remember x = 42
    confess x
    """

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    assert len(ast) == 2
    assert isinstance(ast[0], VariableDecl)
    assert ast[0].name == 'x'
    assert isinstance(ast[0].value, NumberLiteral)
    assert ast[0].value.value == 42

    assert isinstance(ast[1], ConfessStmt)
    assert isinstance(ast[1].value, Identifier)
    assert ast[1].value.name == 'x'

    print("✓ Basic parsing works correctly")
    return True

def test_expressions():
    """Test expression parsing."""
    print("\n" + "=" * 60)
    print("TEST 2: Expression Parsing")
    print("=" * 60)

    code = """
    remember result = (10 + 20) * 2 - 5
    """

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    assert len(ast) == 1
    assert isinstance(ast[0], VariableDecl)
    assert isinstance(ast[0].value, BinaryOp)  # Should be subtraction at top level

    print("✓ Expression parsing works correctly")
    return True

def test_control_flow():
    """Test control flow parsing."""
    print("\n" + "=" * 60)
    print("TEST 3: Control Flow Parsing")
    print("=" * 60)

    code = """
    if yes {
        confess "true branch"
    } else {
        confess "false branch"
    }

    while no {
        confess "never executes"
    }

    for i in range(5) {
        confess i
    }
    """

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    assert len(ast) == 3
    assert isinstance(ast[0], IfStmt)
    assert isinstance(ast[1], WhileStmt)
    assert isinstance(ast[2], ForStmt)

    print("✓ Control flow parsing works correctly")
    return True

def test_functions():
    """Test function parsing."""
    print("\n" + "=" * 60)
    print("TEST 4: Function Parsing")
    print("=" * 60)

    code = """
    sigh add(a, b) {
        exhale a + b
    }

    remember result = add(5, 7)
    """

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    assert len(ast) == 2
    assert isinstance(ast[0], FunctionDef)
    assert ast[0].name == 'add'
    assert len(ast[0].params) == 2
    assert ast[0].params[0] == 'a'
    assert ast[0].params[1] == 'b'
    assert len(ast[0].body) == 1
    assert isinstance(ast[0].body[0], ExhaleStmt)

    assert isinstance(ast[1], VariableDecl)
    assert isinstance(ast[1].value, FunctionCall)
    assert ast[1].value.name == 'add'

    print("✓ Function parsing works correctly")
    return True

def test_temporal_operators():
    """Test temporal operator parsing."""
    print("\n" + "=" * 60)
    print("TEST 5: Temporal Operator Parsing")
    print("=" * 60)

    code = """
    remember x = 0
    x = 1
    x = 2
    confess x@past
    confess x@origin
    confess x@age
    """

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    assert len(ast) == 6
    assert isinstance(ast[0], VariableDecl)
    assert isinstance(ast[1], Assignment)
    assert isinstance(ast[2], Assignment)

    # Check temporal accesses
    assert isinstance(ast[3], ConfessStmt)
    assert isinstance(ast[3].value, TemporalAccess)
    assert ast[3].value.operator == 'past'

    assert isinstance(ast[4], ConfessStmt)
    assert isinstance(ast[4].value, TemporalAccess)
    assert ast[4].value.operator == 'origin'

    assert isinstance(ast[5], ConfessStmt)
    assert isinstance(ast[5].value, TemporalAccess)
    assert ast[5].value.operator == 'age'

    print("✓ Temporal operator parsing works correctly")
    return True

def test_complex_program():
    """Test a complex program with multiple features."""
    print("\n" + "=" * 60)
    print("TEST 6: Complex Program Parsing")
    print("=" * 60)

    code = """
    # Fibonacci function
    sigh fib(n) {
        if n <= 1 {
            exhale n
        } else {
            exhale fib(n - 1) + fib(n - 2)
        }
    }

    # Calculate fibonacci numbers
    for i in range(0, 10) {
        remember result = fib(i)
        confess result
    }
    """

    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    assert len(ast) == 2
    assert isinstance(ast[0], FunctionDef)
    assert ast[0].name == 'fib'
    assert isinstance(ast[1], ForStmt)

    print("✓ Complex program parsing works correctly")
    return True

def run_all_tests():
    """Run all integration tests."""
    print("\n" + "=" * 70)
    print(" " * 15 + "LAMENT PARSER INTEGRATION TESTS")
    print("=" * 70)

    tests = [
        test_basic_parsing,
        test_expressions,
        test_control_flow,
        test_functions,
        test_temporal_operators,
        test_complex_program,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"✗ Test failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ Test error: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 70)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 70)

    if failed == 0:
        print("\n🎉 All tests passed! Parser is working correctly.")
        return True
    else:
        print(f"\n❌ {failed} test(s) failed.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
