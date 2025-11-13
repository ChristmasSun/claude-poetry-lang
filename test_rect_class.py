#!/usr/bin/env python3
"""Test Rectangle class parsing."""

from lament.advanced import AdvancedLexer, AdvancedParser, AdvancedInterpreter

code = """
class Rectangle {
    sigh init(name, width, height) {
        this.name = name
        this.width = width
        this.height = height
    }
}

remember rect = new Rectangle("Box", 10, 20)
confess "Created rectangle"
"""

try:
    lexer = AdvancedLexer(code)
    tokens = lexer.tokenize()

    print("Tokens generated")

    parser = AdvancedParser(tokens)
    ast = parser.parse()

    print("Parsing successful")

    interp = AdvancedInterpreter()
    interp.execute(ast)

    print("Execution complete")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
