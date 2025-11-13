#!/usr/bin/env python3
"""
Comprehensive integration test for Lament bytecode compiler and VM.
Demonstrates the full workflow: source code -> lexer -> parser -> AST -> bytecode -> VM execution.
"""

from lament import (
    # Lexer and parser
    Lexer, Parser,
    # Bytecode compiler and VM
    BytecodeCompiler, BytecodeVM, Bytecode, BytecodeInstruction
)


def demonstrate_bytecode_workflow():
    """Complete demonstration of the bytecode compilation pipeline."""

    print("=" * 70)
    print("LAMENT BYTECODE COMPILER & VM - INTEGRATION TEST")
    print("=" * 70)

    # Example Lament program
    source_code = """
remember x = 42
remember y = 10
remember z = x + y * 2

if z > 50 {
    confess "z is greater than 50"
    confess z
} else {
    confess "z is not greater than 50"
}

remember counter = 0
while counter < 3 {
    confess counter
    counter = counter + 1
}

confess "Program complete!"
"""

    print("\n--- SOURCE CODE ---")
    print(source_code)

    # Step 1: Lexical Analysis
    print("\n--- STEP 1: LEXICAL ANALYSIS ---")
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    print(f"✓ Generated {len(tokens)} tokens")

    # Step 2: Parsing (AST Construction)
    print("\n--- STEP 2: PARSING ---")
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"✓ Generated {len(ast)} AST nodes")

    # Step 3: Bytecode Compilation
    print("\n--- STEP 3: BYTECODE COMPILATION ---")
    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    print(f"✓ Compiled to bytecode:")
    print(f"  - {len(bytecode.instructions)} instructions")
    print(f"  - {len(bytecode.constants)} constants: {bytecode.constants[:10]}{'...' if len(bytecode.constants) > 10 else ''}")
    print(f"  - {len(bytecode.names)} names: {bytecode.names}")

    # Step 4: Disassembly (for debugging)
    print("\n--- STEP 4: BYTECODE DISASSEMBLY ---")
    print(bytecode.disassemble())

    # Step 5: VM Execution
    print("\n--- STEP 5: VM EXECUTION ---")
    print("Output:")
    print("-" * 40)
    vm = BytecodeVM()
    result = vm.execute(bytecode)
    print("-" * 40)

    # Step 6: Execution Statistics
    print("\n--- STEP 6: EXECUTION STATISTICS ---")
    stats = vm.get_stats()
    print(f"Instructions executed: {stats['instructions_executed']}")
    print(f"Max stack depth: {stats['max_stack_depth']}")
    print(f"Variables allocated: {stats['variables_allocated']}")
    print(f"Final stack size: {stats['final_stack_size']}")

    print("\nFinal variable state:")
    for name, value in sorted(vm.variables.items()):
        print(f"  {name} = {value}")

    print("\n" + "=" * 70)
    print("INTEGRATION TEST COMPLETE ✓")
    print("=" * 70)


def performance_comparison():
    """Compare bytecode execution performance characteristics."""

    print("\n\n" + "=" * 70)
    print("PERFORMANCE ANALYSIS")
    print("=" * 70)

    # Test program: compute factorial using loop
    source = """
remember n = 10
remember result = 1
remember i = 1

while i <= n {
    result = result * i
    i = i + 1
}

confess result
"""

    print("\n--- Test Program: Factorial of 10 ---")
    print(source)

    # Compile
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    compiler = BytecodeCompiler()
    bytecode = compiler.compile(ast)

    print(f"\nBytecode size: {len(bytecode.instructions)} instructions")

    # Execute
    vm = BytecodeVM()
    result = vm.execute(bytecode)

    stats = vm.get_stats()
    print(f"\nExecution statistics:")
    print(f"  Instructions executed: {stats['instructions_executed']}")
    print(f"  Max stack depth: {stats['max_stack_depth']}")
    print(f"  Computed factorial(10) = {vm.variables['result']}")

    # Verify correctness
    import math
    expected = math.factorial(10)
    assert vm.variables['result'] == expected, f"Expected {expected}, got {vm.variables['result']}"
    print(f"  ✓ Result verified correct!")

    print("\n" + "=" * 70)


def showcase_all_opcodes():
    """Showcase various bytecode instructions."""

    print("\n\n" + "=" * 70)
    print("BYTECODE INSTRUCTION SET SHOWCASE")
    print("=" * 70)

    print(f"\nTotal opcodes defined: {len(list(BytecodeInstruction))}")
    print("\nInstruction categories:")

    categories = {
        "Stack manipulation": ["LOAD_CONST", "LOAD_VAR", "STORE_VAR", "POP_TOP", "DUP_TOP"],
        "Arithmetic": ["BINARY_ADD", "BINARY_SUB", "BINARY_MUL", "BINARY_DIV", "BINARY_MOD", "UNARY_NEG"],
        "Comparison": ["COMPARE_EQ", "COMPARE_NE", "COMPARE_LT", "COMPARE_GT", "COMPARE_LE", "COMPARE_GE"],
        "Logical": ["LOGICAL_AND", "LOGICAL_OR", "LOGICAL_NOT"],
        "Control flow": ["JUMP", "JUMP_IF_FALSE", "JUMP_IF_TRUE"],
        "Functions": ["CALL_FUNC", "RETURN", "MAKE_FUNC"],
        "Collections": ["BUILD_LIST", "BUILD_DICT", "INDEX_GET", "INDEX_SET"],
        "Temporal": ["LOAD_PAST", "LOAD_ORIGIN", "LOAD_AGE", "LOAD_BORN"],
        "I/O": ["PRINT"],
        "Control": ["HALT", "NOP"]
    }

    for category, opcodes in categories.items():
        print(f"\n{category}:")
        for opcode_name in opcodes:
            try:
                opcode = BytecodeInstruction[opcode_name]
                print(f"  ✓ {opcode_name}")
            except KeyError:
                print(f"  ✗ {opcode_name} (not found)")

    print("\n" + "=" * 70)


if __name__ == "__main__":
    demonstrate_bytecode_workflow()
    performance_comparison()
    showcase_all_opcodes()

    print("\n\n🎉 All integration tests completed successfully! 🎉\n")
