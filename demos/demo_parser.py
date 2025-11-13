#!/usr/bin/env python3
"""
Demonstration of the modular Lament parser.
Shows how the parser can be used to parse Lament code into an AST.
"""

from lament import Lexer, Parser
from lament import (
    NumberLiteral, StringLiteral, BinaryOp, Identifier,
    VariableDecl, ConfessStmt, FunctionDef, IfStmt
)

def pretty_print_ast(node, indent=0):
    """Pretty print an AST node."""
    prefix = "  " * indent
    if isinstance(node, NumberLiteral):
        return f"{prefix}Number({node.value})"
    elif isinstance(node, StringLiteral):
        return f"{prefix}String(\"{node.value}\")"
    elif isinstance(node, Identifier):
        return f"{prefix}Var({node.name})"
    elif isinstance(node, BinaryOp):
        result = f"{prefix}BinaryOp({node.op}):\n"
        result += pretty_print_ast(node.left, indent + 1) + "\n"
        result += pretty_print_ast(node.right, indent + 1)
        return result
    elif isinstance(node, VariableDecl):
        result = f"{prefix}VariableDecl({node.name}):\n"
        result += pretty_print_ast(node.value, indent + 1)
        return result
    elif isinstance(node, ConfessStmt):
        result = f"{prefix}Confess:\n"
        result += pretty_print_ast(node.value, indent + 1)
        return result
    elif isinstance(node, FunctionDef):
        params = ", ".join(node.params)
        result = f"{prefix}FunctionDef({node.name}({params})):\n"
        for stmt in node.body:
            result += pretty_print_ast(stmt, indent + 1) + "\n"
        return result.rstrip()
    elif isinstance(node, IfStmt):
        result = f"{prefix}If:\n"
        result += f"{prefix}  Condition:\n"
        result += pretty_print_ast(node.condition, indent + 2) + "\n"
        result += f"{prefix}  Then:\n"
        for stmt in node.then_block:
            result += pretty_print_ast(stmt, indent + 2) + "\n"
        if node.else_block:
            result += f"{prefix}  Else:\n"
            for stmt in node.else_block:
                result += pretty_print_ast(stmt, indent + 2) + "\n"
        return result.rstrip()
    else:
        return f"{prefix}{node.__class__.__name__}(...)"

def demo():
    """Run parser demonstration."""
    print("=" * 70)
    print(" " * 20 + "LAMENT PARSER DEMO")
    print("=" * 70)

    # Sample Lament code
    code = """
    # A simple Lament program
    remember greeting = "Hello, Lament!"
    confess greeting

    # Fibonacci function
    sigh fibonacci(n) {
        if n <= 1 {
            exhale n
        } else {
            exhale fibonacci(n - 1) + fibonacci(n - 2)
        }
    }

    # Calculate fibonacci
    remember fib_10 = fibonacci(10)
    confess fib_10
    """

    print("\nSource Code:")
    print("-" * 70)
    print(code)

    # Lex
    print("\n" + "=" * 70)
    print("STEP 1: Lexical Analysis (Tokenization)")
    print("=" * 70)
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    print(f"Generated {len(tokens)} tokens")
    print("\nFirst 10 tokens:")
    for i, token in enumerate(tokens[:10], 1):
        print(f"  {i:2}. {token.type.name:15} = {repr(token.value):20} (line {token.line})")
    print(f"  ... and {len(tokens) - 10} more tokens")

    # Parse
    print("\n" + "=" * 70)
    print("STEP 2: Parsing (AST Generation)")
    print("=" * 70)
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"Generated AST with {len(ast)} top-level statements\n")

    # Display AST
    print("Abstract Syntax Tree:")
    print("-" * 70)
    for i, node in enumerate(ast, 1):
        print(f"\nStatement {i}:")
        print(pretty_print_ast(node))

    print("\n" + "=" * 70)
    print("✓ Parser successfully converted Lament code into AST!")
    print("=" * 70)
    print("\nThe AST can now be:")
    print("  • Executed by an interpreter")
    print("  • Analyzed for optimization")
    print("  • Type-checked")
    print("  • Compiled to bytecode")
    print("  • Transformed to other languages")
    print("=" * 70)

if __name__ == "__main__":
    demo()
