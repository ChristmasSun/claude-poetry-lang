#!/usr/bin/env python3
"""
Test script for Lament bytecode compiler and VM.
"""

import sys
from lament.lexer import Lexer
from lament.parser import Parser
from lament.bytecode import BytecodeCompiler, BytecodeVM

def test_basic_arithmetic():
    """Test basic arithmetic operations."""
    print("\n=== Test: Basic Arithmetic ===")

    source = """
remember a = 10
remember b = 20
remember c = a + b
confess c
"""

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    print(f"Compiled: {bytecode}")
    print(f"Constants: {bytecode.constants}")
    print(f"Names: {bytecode.names}")
    print(f"\nDisassembly:")
    print(bytecode.disassemble())

    print(f"\nExecuting...")
    vm = BytecodeVM()
    result = vm.execute(bytecode)

    print(f"\nStats: {vm.get_stats()}")
    print(f"Variables: {vm.variables}")
    print("✓ Test passed")


def test_complex_expression():
    """Test complex expression with multiple operations."""
    print("\n=== Test: Complex Expression ===")

    source = """
remember x = 5
remember y = 3
remember z = (x * y) + (x - y)
confess z
"""

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    print(f"\nDisassembly:")
    print(bytecode.disassemble())

    vm = BytecodeVM()
    result = vm.execute(bytecode)

    expected = (5 * 3) + (5 - 3)  # Should be 17
    assert vm.variables['z'] == expected, f"Expected {expected}, got {vm.variables['z']}"
    print(f"Result: {vm.variables['z']}")
    print("✓ Test passed")


def test_conditionals():
    """Test if-else statements."""
    print("\n=== Test: Conditionals ===")

    source = """
remember x = 10
if x > 5 {
    confess "x is greater than 5"
} else {
    confess "x is not greater than 5"
}
"""

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    print(f"\nDisassembly:")
    print(bytecode.disassemble())

    vm = BytecodeVM()
    result = vm.execute(bytecode)

    print("✓ Test passed")


def test_while_loop():
    """Test while loop."""
    print("\n=== Test: While Loop ===")

    source = """
remember counter = 0
while counter < 5 {
    confess counter
    counter = counter + 1
}
confess "Done"
"""

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    print(f"\nDisassembly:")
    print(bytecode.disassemble())

    vm = BytecodeVM()
    result = vm.execute(bytecode)

    assert vm.variables['counter'] == 5
    print(f"\nFinal counter: {vm.variables['counter']}")
    print("✓ Test passed")


def test_comparison_operators():
    """Test comparison operators."""
    print("\n=== Test: Comparison Operators ===")

    source = """
remember a = 10
remember b = 20
remember eq = a == 10
remember ne = a != b
remember lt = a < b
remember gt = a > b
remember le = a <= 10
remember ge = a >= 10
confess eq
confess ne
confess lt
confess gt
confess le
confess ge
"""

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    vm = BytecodeVM()
    result = vm.execute(bytecode)

    assert vm.variables['eq'] == True
    assert vm.variables['ne'] == True
    assert vm.variables['lt'] == True
    assert vm.variables['gt'] == False
    assert vm.variables['le'] == True
    assert vm.variables['ge'] == True

    print(f"\nVariables: {vm.variables}")
    print("✓ Test passed")


def test_logical_operators():
    """Test logical operators."""
    print("\n=== Test: Logical Operators ===")

    source = """
remember a = yes
remember b = no
remember and_result = a and b
remember or_result = a or b
confess and_result
confess or_result
"""

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    vm = BytecodeVM()
    result = vm.execute(bytecode)

    print(f"\nVariables: {vm.variables}")
    assert vm.variables['and_result'] == False
    assert vm.variables['or_result'] == True
    print("✓ Test passed")


def test_list_operations():
    """Test list creation."""
    print("\n=== Test: List Operations ===")

    source = """
remember mylist = [1, 2, 3, 4, 5]
confess mylist
"""

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    print(f"\nDisassembly:")
    print(bytecode.disassemble())

    vm = BytecodeVM()
    result = vm.execute(bytecode)

    print(f"\nVariables: {vm.variables}")
    assert vm.variables['mylist'] == [1, 2, 3, 4, 5]
    print("✓ Test passed")


def test_unary_operators():
    """Test unary operators."""
    print("\n=== Test: Unary Operators ===")

    source = """
remember x = 10
remember neg_x = -x
remember flag = yes
remember not_flag = not flag
confess neg_x
confess not_flag
"""

    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    vm = BytecodeVM()
    result = vm.execute(bytecode)

    print(f"\nVariables: {vm.variables}")
    assert vm.variables['neg_x'] == -10
    assert vm.variables['not_flag'] == False
    print("✓ Test passed")


def main():
    """Run all tests."""
    print("=" * 60)
    print("LAMENT BYTECODE COMPILER & VM TEST SUITE")
    print("=" * 60)

    try:
        test_basic_arithmetic()
        test_complex_expression()
        test_conditionals()
        test_while_loop()
        test_comparison_operators()
        test_logical_operators()
        test_list_operations()
        test_unary_operators()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED ✓")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
