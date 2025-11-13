#!/usr/bin/env python3
"""
Demo: Using the modular Lament interpreter
Shows both programmatic and string-based execution
"""

from lament.types import Color, TimelineValue, LamentType
from lament.lexer import Lexer
from lament.parser import Parser
from lament.interpreter import LamentInterpreter

print(f"{Color.CYAN}{Color.BOLD}=== Modular Lament Demo ==={Color.RESET}\n")

# Demo 1: Programmatic access to types
print(f"{Color.MAGENTA}1. Type System:{Color.RESET}")
val = TimelineValue(current=10)
val.assign(20)
val.assign(30)
print(f"   Current: {val.current}")
print(f"   Past(1): {val.get_past(1)}")
print(f"   Origin: {val.get_origin()}")
print(f"   Age: {val.get_age()}")

# Demo 2: Execute Lament code
print(f"\n{Color.MAGENTA}2. Execute Lament Code:{Color.RESET}")
code = """
remember greeting = "Hello, modular world!"
confess greeting

sigh square(n) {
    exhale n * n
}

confess square(7)
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()
interpreter = LamentInterpreter()
print(f"   Output:")
interpreter.execute(ast)

# Demo 3: Access interpreter internals
print(f"\n{Color.MAGENTA}3. Interpreter Introspection:{Color.RESET}")
print(f"   Built-in functions: {len(interpreter.globals)}")
print(f"   Available: {', '.join(list(interpreter.globals.keys())[:5])}...")
print(f"   Current timeline: {interpreter.current_timeline}")

print(f"\n{Color.CYAN}{Color.BOLD}=== Demo Complete ==={Color.RESET}")
