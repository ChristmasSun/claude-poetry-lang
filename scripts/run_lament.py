#!/usr/bin/env python3
"""
Lament interpreter using modular structure
Entry point for running .lament files
"""

import sys
from lament.lexer import Lexer
from lament.parser import Parser
from lament.interpreter import LamentInterpreter
from lament.types import Color, bell


def main():
    """Entry point. The beginning of all confessions."""

    if len(sys.argv) != 2:
        print(f"\n{Color.CYAN}Usage: run_lament.py <filename.lament>{Color.RESET}", file=sys.stderr)
        print(f"{Color.YELLOW}(Every program is a confession. Give me a file to listen to.){Color.RESET}\n", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}💔 LAMENT ERROR 💔{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(f"{Color.CYAN}I searched for '{filename}' in all the directories,", file=sys.stderr)
        print(f"through all the folders of my heart—", file=sys.stderr)
        print(f"but it doesn't exist.{Color.RESET}", file=sys.stderr)
        print(f"\n{Color.YELLOW}(Perhaps it never did.){Color.RESET}", file=sys.stderr)
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(bell(1), end='', file=sys.stderr)
        sys.exit(1)

    try:
        # Lex
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()

        # Parse
        parser = Parser(tokens)
        ast = parser.parse()

        # Execute
        interpreter = LamentInterpreter()
        interpreter.execute(ast)

    except SyntaxError as e:
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}💔 LAMENT ERROR: SYNTAX 💔{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(f"{Color.CYAN}The grammar is broken. The syntax fractured.{Color.RESET}", file=sys.stderr)
        print(f"{Color.CYAN}I tried to understand, but the words make no sense.{Color.RESET}\n", file=sys.stderr)
        print(f"{Color.YELLOW}{str(e)}{Color.RESET}", file=sys.stderr)
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(bell(1), end='', file=sys.stderr)
        sys.exit(1)

    except Exception as e:
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}💔 LAMENT ERROR: UNKNOWN 💔{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(f"{Color.CYAN}Something went terribly wrong.{Color.RESET}", file=sys.stderr)
        print(f"{Color.CYAN}Reality itself has crashed.{Color.RESET}\n", file=sys.stderr)
        print(f"{Color.YELLOW}{str(e)}{Color.RESET}", file=sys.stderr)
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(bell(3), end='', file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
