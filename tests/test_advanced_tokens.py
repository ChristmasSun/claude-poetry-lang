#!/usr/bin/env python3
"""Test advanced lexer tokens."""

from lament.advanced import AdvancedLexer, AdvancedTokenType

code = """
class Point {
    sigh init(x) {
        this.x = x
    }
}
"""

lexer = AdvancedLexer(code)
tokens = lexer.tokenize()

print("Tokens:")
for token in tokens:
    print(f"  {token.type} ({token.type.name if hasattr(token.type, 'name') else token.type}) = {token.value}")
