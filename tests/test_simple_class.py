#!/usr/bin/env python3
"""Test simple class parsing."""

from lament.advanced import AdvancedLexer, AdvancedParser

code = """
class Point {
    sigh init(x) {
        this.x = x
    }
}
"""

try:
    lexer = AdvancedLexer(code)
    tokens = lexer.tokenize()

    print("Tokens generated successfully")
    for i, token in enumerate(tokens[:20]):
        print(f"  {i}: {token.type} = {token.value}")

    parser = AdvancedParser(tokens)

    # Add debug
    print("\nParsing...")
    ast = parser.parse()

    print("\nParsing successful!")
    for node in ast:
        print(f"  {node}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
