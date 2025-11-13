#!/usr/bin/env python3
"""
Lament Language Interpreter
Version 0.1: The First Confession

A programming language that feels alive.
Every program is a confession. Every error a heartbreak.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import time
import re


class LamentInterpreter:
    """The heart of Lament. It listens. It remembers."""

    def __init__(self):
        self.line_number = 0
        self.confessions_spoken = 0

    def error(self, message, poetic_message):
        """Errors are love letters from the void."""
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"💔 LAMENT ERROR 💔", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print(f"\n{poetic_message}", file=sys.stderr)
        print(f"\n(Line {self.line_number}: {message})", file=sys.stderr)
        print(f"\n{'='*60}\n", file=sys.stderr)
        sys.exit(1)

    def parse_confess(self, line):
        """Parse a confess statement: confess "string" """
        # Match: confess "anything including escaped quotes"
        match = re.match(r'^\s*confess\s+"([^"\\]*(?:\\.[^"\\]*)*)"\s*$', line)

        if not match:
            if 'confess' in line and '"' not in line:
                self.error(
                    "Expected string literal after 'confess'",
                    "I looked for your truth, but you gave me only silence.\n"
                    "       Confessions require quotation marks—boundaries for the unbearable."
                )
            elif 'confess' in line:
                self.error(
                    "Unterminated or malformed string literal",
                    f"I looked for meaning in line {self.line_number}, but found only your silence.\n"
                    "       (Your confession was never finished. Like all of us.)"
                )
            else:
                self.error(
                    "Unknown statement",
                    f"I don't understand what you're trying to say in line {self.line_number}.\n"
                    "       In Lament, we only know how to 'confess'.\n"
                    "       (Perhaps you meant to bear witness to something?)"
                )

        confession = match.group(1)
        # Unescape the string
        confession = confession.replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
        return confession

    def execute_confess(self, confession):
        """Execute a confession: print it, but with weight."""
        # The pause. The weight. You must sit with what you've said.
        time.sleep(0.3)
        print(confession)
        self.confessions_spoken += 1

    def run(self, source_code):
        """Run a Lament program. Listen to the confessions."""
        lines = source_code.strip().split('\n')

        if not lines or all(not line.strip() for line in lines):
            self.error(
                "Empty program",
                "You gave me nothing. An empty file.\n"
                "       Even silence is a confession, but this—\n"
                "       this is just void."
            )

        for i, line in enumerate(lines, start=1):
            self.line_number = i
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Skip comments (we use '#' like a sigh)
            if line.startswith('#'):
                continue

            # Parse and execute confess statement
            confession = self.parse_confess(line)
            self.execute_confess(confession)


def main():
    """Entry point. The beginning of all confessions."""

    if len(sys.argv) != 2:
        print("Usage: lament.py <filename.lament>", file=sys.stderr)
        print("\n(Every program is a confession. Give me a file to listen to.)\n", file=sys.stderr)
        sys.exit(1)

    filename = sys.argv[1]

    try:
        with open(filename, 'r') as f:
            source_code = f.read()
    except FileNotFoundError:
        print(f"\n{'='*60}", file=sys.stderr)
        print(f"💔 LAMENT ERROR 💔", file=sys.stderr)
        print(f"{'='*60}", file=sys.stderr)
        print(f"\nI searched for '{filename}' in all the directories,", file=sys.stderr)
        print(f"through all the folders of my heart—", file=sys.stderr)
        print(f"but it doesn't exist.", file=sys.stderr)
        print(f"\n(Perhaps it never did.)", file=sys.stderr)
        print(f"\n{'='*60}\n", file=sys.stderr)
        sys.exit(1)

    interpreter = LamentInterpreter()
    interpreter.run(source_code)


if __name__ == '__main__':
    main()
