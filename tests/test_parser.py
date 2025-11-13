#!/usr/bin/env python3
"""
Test script for the modular Lament parser.
"""

from lament.lexer import Lexer
from lament.parser import Parser

# Test source code
test_code = """
# Variable declaration and confess
remember x = 42
confess x

# Arithmetic
remember y = x + 10
confess y

# String
remember msg = "Hello, Lament!"
confess msg

# Function definition
sigh add(a, b) {
    exhale a + b
}

# Function call
remember result = add(5, 7)
confess result

# Control flow
if result > 10 {
    confess "Result is greater than 10"
} else {
    confess "Result is 10 or less"
}

# Loop
for i in range(1, 5) {
    confess i
}

# Temporal operators
remember counter = 0
counter = 1
counter = 2
counter = 3
confess counter@past
confess counter@origin
confess counter@age
"""

def test_parser():
    """Test the parser with sample code."""
    print("Testing Lament Parser...")
    print("=" * 60)

    try:
        # Lex
        print("Step 1: Lexing...")
        lexer = Lexer(test_code)
        tokens = lexer.tokenize()
        print(f"  ✓ Generated {len(tokens)} tokens")

        # Parse
        print("\nStep 2: Parsing...")
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"  ✓ Generated AST with {len(ast)} statements")

        # Display AST structure
        print("\nStep 3: AST Structure:")
        print("-" * 60)
        for i, node in enumerate(ast[:10], 1):  # Show first 10 nodes
            print(f"{i:2}. {node.__class__.__name__}: {str(node)[:70]}")
        if len(ast) > 10:
            print(f"    ... and {len(ast) - 10} more statements")

        print("\n" + "=" * 60)
        print("✓ Parser test PASSED!")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Parser test FAILED!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_parser()
    exit(0 if success else 1)
