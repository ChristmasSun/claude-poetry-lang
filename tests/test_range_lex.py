#!/usr/bin/env python3
"""Test range lexing."""

from lament.advanced import AdvancedLexer

code = """
case 0..59 => { confess "test" }
"""

lexer = AdvancedLexer(code)
tokens = lexer.tokenize()

print("Tokens:")
for token in tokens:
    if token.type.name != 'EOF':
        print(f"  {token.type} ({token.type.name}) = {repr(token.value)}")
