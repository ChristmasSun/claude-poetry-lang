#!/usr/bin/env python3
"""
Advanced test for modular Lament interpreter - functions and built-ins
"""

from lament.lexer import Lexer
from lament.parser import Parser
from lament.interpreter import LamentInterpreter
from lament.types import Color

# Test program: Functions and built-ins
test_code = """
# Test function definition and calls
sigh add(a, b) {
    exhale a + b
}

remember result = add(5, 3)
confess result

# Test built-in functions
remember numbers = [1, 2, 3, 4, 5]
confess length_of(numbers)

# Test timeline features with function
remember counter = 0
counter = 1
counter = 2
counter = 3
confess counter@origin
confess counter@age
"""

print(f"{Color.CYAN}Testing advanced Lament features...{Color.RESET}\n")

try:
    # Lex
    lexer = Lexer(test_code)
    tokens = lexer.tokenize()
    print(f"{Color.BLUE}✓ Lexer works{Color.RESET}")

    # Parse
    parser = Parser(tokens)
    ast = parser.parse()
    print(f"{Color.BLUE}✓ Parser works{Color.RESET}")

    # Execute
    print(f"\n{Color.CYAN}Program output:{Color.RESET}")
    interpreter = LamentInterpreter()
    interpreter.execute(ast)

    print(f"\n{Color.BLUE}✓ All advanced features work!{Color.RESET}")

except Exception as e:
    print(f"\n{Color.RED}✗ Error: {e}{Color.RESET}")
    raise
