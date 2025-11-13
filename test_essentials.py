#!/usr/bin/env python3
"""
Test runner for Lament Essential Features Demo

This script runs the comprehensive demo that tests:
1. Module System (import/export)
2. Exception Handling (attempt/catch/finally)
3. String Interpolation (template strings with ${})

Usage:
    python test_essentials.py
"""

import sys
import os

# Add lament to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lament.essentials import (
    EssentialLexer,
    EssentialParser,
    EssentialInterpreter,
    ModuleLoader,
    LamentException
)


def run_demo():
    """Run the essential features demonstration."""
    print("=" * 70)
    print("LAMENT LANGUAGE - ESSENTIAL FEATURES TEST")
    print("=" * 70)
    print()

    # Path to demo file
    demo_file = os.path.join(os.path.dirname(__file__), "demo_essentials.lament")

    if not os.path.exists(demo_file):
        print(f"Error: Demo file not found at {demo_file}")
        sys.exit(1)

    # Read demo source code
    with open(demo_file, 'r') as f:
        source = f.read()

    try:
        # Initialize module loader with current directory
        module_loader = ModuleLoader(search_paths=[os.path.dirname(__file__)])

        # Tokenize
        print("Tokenizing...")
        lexer = EssentialLexer(source)
        tokens = lexer.tokenize()
        print(f"✓ Generated {len(tokens)} tokens")
        print()

        # Parse
        print("Parsing...")
        parser = EssentialParser(tokens)
        ast = parser.parse()
        print(f"✓ Generated AST with {len(ast)} top-level statements")
        print()

        # Execute
        print("Executing demo...")
        print("=" * 70)
        print()

        interpreter = EssentialInterpreter(module_loader=module_loader)
        interpreter.current_file = demo_file
        interpreter.execute(ast)

        print()
        print("=" * 70)
        print("✓ Demo completed successfully!")
        print("=" * 70)

    except LamentException as e:
        print()
        print("=" * 70)
        print("Lament Exception:")
        print(str(e))
        print("=" * 70)
        sys.exit(1)

    except SyntaxError as e:
        print()
        print("=" * 70)
        print(f"Syntax Error: {e}")
        print("=" * 70)
        sys.exit(1)

    except Exception as e:
        print()
        print("=" * 70)
        print(f"Unexpected Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    run_demo()
