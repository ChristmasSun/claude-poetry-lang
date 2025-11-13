#!/usr/bin/env python3
"""
Test script for modular Lament interpreter
"""

from lament.lexer import Lexer
from lament.parser import Parser
from lament.interpreter import LamentInterpreter
from lament.types import TimelineValue, Color

# Test program: Basic arithmetic and timeline features
test_code = """
remember x = 10
confess x
x = 20
confess x
x = 30
confess x@past(1)
confess x@origin
confess x@age
"""

print(f"{Color.CYAN}Testing modular Lament interpreter...{Color.RESET}\n")

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

print(f"\n{Color.BLUE}✓ Interpreter works{Color.RESET}")
print(f"\n{Color.CYAN}All modules working correctly!{Color.RESET}")
