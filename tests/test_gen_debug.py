#!/usr/bin/env python3
"""Test generators with full debug."""

from lament.advanced import AdvancedLexer, AdvancedParser, AdvancedInterpreter
import sys

code = """
sigh count_up(n) {
    remember i = 0
    while i < n {
        yield i
        i = i + 1
    }
}

confess "Counting to 5:"
remember counter = count_up(5)
for num in counter {
    confess num
}
"""

try:
    lexer = AdvancedLexer(code)
    tokens = lexer.tokenize()
    print("Lexing OK")

    parser = AdvancedParser(tokens)
    ast = parser.parse()
    print("Parsing OK")

    interpreter = AdvancedInterpreter()
    interpreter.execute(ast)
    print("Execution OK")

except SystemExit:
    print("SystemExit caught")
    pass
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
