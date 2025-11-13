#!/usr/bin/env python3
"""
Test synesthetic error messages
"""

from lament.lexer import Lexer
from lament.parser import Parser
from lament.interpreter import LamentInterpreter
from lament.types import Color

# Test program: Undefined variable (should trigger error)
test_code = """
confess undefined_variable
"""

print(f"{Color.CYAN}Testing synesthetic error handling...{Color.RESET}\n")
print(f"{Color.YELLOW}(This should produce a beautiful error message){Color.RESET}\n")

# Lex
lexer = Lexer(test_code)
tokens = lexer.tokenize()

# Parse
parser = Parser(tokens)
ast = parser.parse()

# Execute (will error)
interpreter = LamentInterpreter()
interpreter.execute(ast)
