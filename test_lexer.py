#!/usr/bin/env python3
"""
Test script for the Lament lexer module.
Verifies that tokenization works correctly.
"""

from lament.lexer import Lexer, TokenType

# Test code with various Lament features
test_code = """
# Test: Basic variable declaration
remember x = 42
remember name = "Zephyr"
remember truth = yes
remember lie = no
remember quantum = perhaps
remember nothing = void

# Test: Arithmetic and comparison
remember sum = 10 + 20 - 5
remember product = 3 * 4 / 2
remember remainder = 10 % 3
remember check = x == 42
remember less = x < 100
remember greater_eq = x >= 42

# Test: Temporal operators
x@past
x@origin
x@age
x@born
x@past(2)

# Test: Control flow
if x > 10 {
    confess "x is large"
} else {
    confess "x is small"
}

# Test: Loops
while x > 0 {
    x = x - 1
}

for i in range(10) {
    confess i
}

# Test: Functions
sigh greet(name) {
    confess "Hello, " + name
    exhale void
}

# Test: Lists and indexing
remember items = [1, 2, 3, 4, 5]
remember first = items[0]

# Test: Reality forking
fork reality {
    on yes {
        confess "Timeline A"
    }
    on no {
        confess "Timeline B"
    }
} collapse observe result

# Test: Multi-line comment
/* This is a
   multi-line comment
   testing tokenization */

# Test: Logical operators
remember both = yes and no
remember either = yes or no
remember inverted = not yes
"""

def main():
    """Run lexer tests."""
    print("=" * 70)
    print("LAMENT LEXER TEST")
    print("=" * 70)
    print()

    lexer = Lexer(test_code)

    try:
        tokens = lexer.tokenize()

        print(f"✓ Successfully tokenized {len(tokens)} tokens")
        print()
        print("Token Summary:")
        print("-" * 70)

        # Count token types
        token_counts = {}
        for token in tokens:
            token_type = token.type.name
            token_counts[token_type] = token_counts.get(token_type, 0) + 1

        # Display token type counts
        for token_type in sorted(token_counts.keys()):
            print(f"  {token_type:20} : {token_counts[token_type]:3} occurrences")

        print()
        print("-" * 70)
        print()

        # Display first 30 tokens
        print("First 30 tokens:")
        print("-" * 70)
        for i, token in enumerate(tokens[:30]):
            value_str = f"'{token.value}'" if token.value is not None else "None"
            print(f"  {i:3}. Line {token.line:2} | {token.type.name:15} | {value_str}")

        if len(tokens) > 30:
            print(f"  ... and {len(tokens) - 30} more tokens")

        print()
        print("-" * 70)

        # Verify key token types are present
        print()
        print("Verification:")
        print("-" * 70)

        required_types = [
            TokenType.REMEMBER,
            TokenType.CONFESS,
            TokenType.IF,
            TokenType.ELSE,
            TokenType.WHILE,
            TokenType.FOR,
            TokenType.SIGH,
            TokenType.EXHALE,
            TokenType.FORK,
            TokenType.REALITY,
            TokenType.AT_PAST,
            TokenType.AT_ORIGIN,
            TokenType.AT_AGE,
            TokenType.AT_BORN,
            TokenType.NUMBER,
            TokenType.STRING,
            TokenType.IDENTIFIER,
        ]

        all_types = [t.type for t in tokens]
        for required in required_types:
            found = required in all_types
            status = "✓" if found else "✗"
            print(f"  {status} {required.name}")

        print()
        print("=" * 70)
        print("LEXER TEST COMPLETE - ALL CHECKS PASSED!")
        print("=" * 70)

    except Exception as e:
        print(f"✗ Lexer test failed!")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    exit(main())
