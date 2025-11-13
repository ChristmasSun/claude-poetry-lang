"""
Example: Combining All Metaprogramming Features
================================================

This example demonstrates how to use all four metaprogramming systems
together to create powerful code transformation pipelines.

Author: Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament import (
    HygienicMacro, CodeGenerator, ASTManipulator, Reflect,
    create_pattern, PatternType, ASTTransformer
)
from lament.parser import (
    NumberLiteral, BinaryOp, Identifier, VariableDecl,
    ConfessStmt, FunctionDef, IfStmt, UnaryOp
)


def example_1_macro_expansion():
    """Example 1: Define and expand a macro."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Hygienic Macro Expansion")
    print("=" * 70)

    macro_system = HygienicMacro()

    # Define 'unless' macro
    unless_pattern = [
        create_pattern(PatternType.EXPRESSION, 'condition'),
        create_pattern(PatternType.BLOCK, 'body')
    ]

    unless_template = IfStmt(
        UnaryOp('not', Identifier('condition')),
        [Identifier('body')],
        None
    )

    macro_system.define('unless', unless_pattern, unless_template)

    # Expand macro
    condition = BinaryOp(Identifier('x'), '>', NumberLiteral(10))
    body = [ConfessStmt(Identifier('x'))]

    expanded = macro_system.expand('unless', [condition, body])

    print(f"Macro: unless x > 10 {{ confess x }}")
    print(f"Expanded to: if not (x > 10) {{ confess x }}")
    print(f"Result type: {type(expanded).__name__}")
    print(f"Condition: {type(expanded.condition).__name__} with operator '{expanded.condition.op}'")


def example_2_code_generation():
    """Example 2: Generate code from templates."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Code Generation")
    print("=" * 70)

    generator = CodeGenerator()

    # Generate getters and setters for a class
    fields = ['x', 'y', 'z']

    print(f"Generating accessors for fields: {', '.join(fields)}")
    print()

    for field in fields:
        # Define templates
        generator.define_template(
            f'get_{field}',
            f'sigh get_{field}() {{ exhale @{field} }}',
            []
        )

        generator.define_template(
            f'set_{field}',
            f'sigh set_{field}(value) {{ {field} = value }}',
            []
        )

        # Generate code
        getter = generator.instantiate(f'get_{field}', {})
        setter = generator.instantiate(f'set_{field}', {})

        print(f"  {field}:")
        print(f"    Getter: {getter}")
        print(f"    Setter: {setter}")

    print()
    print(f"Total generated: {len(generator.get_generated_code())} code units")


def example_3_ast_transformation():
    """Example 3: Transform AST with custom optimizer."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: AST Transformation")
    print("=" * 70)

    manipulator = ASTManipulator()

    # Create sample AST
    ast = [
        VariableDecl('a', BinaryOp(NumberLiteral(2), '+', NumberLiteral(3))),
        VariableDecl('b', BinaryOp(NumberLiteral(10), '*', NumberLiteral(5))),
        ConfessStmt(BinaryOp(Identifier('a'), '+', Identifier('b')))
    ]

    print("Original AST:")
    print("  remember a = 2 + 3")
    print("  remember b = 10 * 5")
    print("  confess a + b")
    print()

    # Custom constant folder
    class ConstantFolder(ASTTransformer):
        def __init__(self):
            super().__init__()
            self.folded = 0

        def visit_BinaryOp(self, node):
            node = self.generic_visit(node)

            if isinstance(node.left, NumberLiteral) and isinstance(node.right, NumberLiteral):
                if node.op == '+':
                    self.folded += 1
                    return NumberLiteral(node.left.value + node.right.value)
                elif node.op == '*':
                    self.folded += 1
                    return NumberLiteral(node.left.value * node.right.value)

            return node

    folder = ConstantFolder()
    optimized = folder.transform(ast)

    print("After constant folding:")
    print("  remember a = 5")
    print("  remember b = 50")
    print("  confess a + b")
    print()
    print(f"Folded {folder.folded} constant expressions")


def example_4_reflection():
    """Example 4: Use reflection for dynamic behavior."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Runtime Reflection")
    print("=" * 70)

    reflect = Reflect()

    # Test different values
    test_values = [
        ("hello", "whisper"),
        (42, "numb"),
        (3.14, "ache"),
        ([1, 2, 3], "list"),
        ({'a': 1}, "dict")
    ]

    print("Type Detection:")
    for value, expected in test_values:
        detected = reflect.get_type_name(value)
        status = "✓" if detected == expected else "✗"
        print(f"  {status} {repr(value):20} -> {detected}")

    print()
    print("Dynamic Method Invocation:")

    # String methods
    result = reflect.invoke("hello", "upper", [])
    print(f"  'hello'.upper() = '{result}'")

    result = reflect.invoke("WORLD", "lower", [])
    print(f"  'WORLD'.lower() = '{result}'")

    # Numeric methods
    result = reflect.invoke(-42, "abs", [])
    print(f"  (-42).abs() = {result}")

    result = reflect.invoke(3.7, "round", [])
    print(f"  (3.7).round() = {result}")

    # List methods
    my_list = [1, 2, 3]
    result = reflect.invoke(my_list, "length", [])
    print(f"  [1, 2, 3].length() = {result}")

    print()
    print("Method Introspection:")
    string_info = reflect.type_registry['whisper']
    methods = reflect.get_methods(string_info)
    print(f"  String methods: {', '.join(m.name for m in methods)}")


def example_5_combined_pipeline():
    """Example 5: Combine all systems in a pipeline."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Combined Metaprogramming Pipeline")
    print("=" * 70)

    # Step 1: Generate code
    print("Step 1: Generate code with templates")
    generator = CodeGenerator()
    generator.define_template('simple', 'remember x = {{value}}', ['value'])
    code = generator.instantiate('simple', {'value': '10'})
    print(f"  Generated: {code}")

    # Step 2: Parse to AST
    print("\nStep 2: Convert to AST")
    manipulator = ASTManipulator()
    ast = manipulator.quote(code)
    print(f"  AST type: {type(ast).__name__}")
    print(f"  Variable: {ast.name}")
    print(f"  Value: {ast.value.value}")

    # Step 3: Transform AST
    print("\nStep 3: Transform AST")

    def increment_numbers(node):
        if isinstance(node, NumberLiteral):
            return NumberLiteral(node.value + 1)
        return node

    transformed = manipulator.transform(ast, increment_numbers)
    print(f"  Transformed value: {transformed.value.value}")

    # Step 4: Use reflection
    print("\nStep 4: Use reflection on result")
    reflect = Reflect()
    value = transformed.value.value
    type_name = reflect.get_type_name(value)
    print(f"  Type: {type_name}")
    print(f"  Is number?: {reflect.is_instance(value, 'numb')}")

    # Step 5: Define macro
    print("\nStep 5: Define macro for similar patterns")
    macro_system = HygienicMacro()

    init_pattern = [create_pattern(PatternType.IDENTIFIER, 'var')]
    init_template = VariableDecl('var', NumberLiteral(0))

    macro_system.define('init', init_pattern, init_template)
    print(f"  Defined 'init' macro")
    print(f"  Total macros: {len(macro_system.macros)}")

    print("\n  Pipeline complete! All systems working together.")


def main():
    """Run all examples."""
    print("\n")
    print("#" * 70)
    print("# LAMENT METAPROGRAMMING: COMPLETE EXAMPLES")
    print("#" * 70)

    example_1_macro_expansion()
    example_2_code_generation()
    example_3_ast_transformation()
    example_4_reflection()
    example_5_combined_pipeline()

    print("\n" + "=" * 70)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print()


if __name__ == "__main__":
    main()
