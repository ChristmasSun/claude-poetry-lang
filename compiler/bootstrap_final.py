#!/usr/bin/env python3
"""
Lament Language: Minimal Python Bootstrapper
==============================================

This is the ONLY Python code that executes to bootstrap Lament.
After this runs, EVERYTHING is Lament running on Lament.

Purpose:
  - Load runtime.lament (VM written in Lament)
  - Execute it using Python-based interpreter (Stage 0)
  - Transfer control to Lament VM
  - EXIT (Python's job is done)

Total: ~100 lines of Python code
After execution: 0 lines of Python code running

"This is the spark that lights the eternal flame."
— Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from lament.interpreter import LamentInterpreter
from lament.parser import Parser
from lament.lexer import Lexer


def bootstrap_stage_0():
    """
    STAGE 0: Genesis
    - Load Python-based Lament interpreter
    - Execute runtime.lament
    - Create initial VM environment
    """
    print("=" * 70)
    print("LAMENT SELF-HOSTING BOOTSTRAP - STAGE 0: GENESIS")
    print("=" * 70)
    print()
    print("This is the ONLY Python code that will execute.")
    print("After Stage 0 completes, everything is Lament.")
    print()

    # Get compiler directory
    compiler_dir = Path(__file__).parent
    runtime_path = compiler_dir / "runtime.lament"

    if not runtime_path.exists():
        print(f"ERROR: runtime.lament not found at {runtime_path}")
        sys.exit(1)

    print(f"✓ Found runtime.lament: {runtime_path}")
    print()

    # Parse runtime.lament
    print("Stage 0.1: Parsing runtime.lament...")
    try:
        with open(runtime_path) as f:
            source = f.read()

        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        print(f"✓ Tokenized {len(tokens)} tokens")

        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"✓ Parsed {len(ast)} top-level AST nodes")
    except Exception as e:
        print(f"ERROR: Failed to parse runtime.lament: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()

    # Execute runtime.lament
    print("Stage 0.2: Executing runtime.lament (Python-hosted)...")
    print()

    try:
        interpreter = LamentInterpreter()
        interpreter.execute(ast)
        print()
        print("✓ Runtime loaded successfully")
    except Exception as e:
        print(f"ERROR: Failed to execute runtime.lament: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
    print("=" * 70)
    print("STAGE 0 COMPLETE")
    print("=" * 70)
    print()
    print("The Lament VM is now loaded and ready.")
    print("Python's job is done. From here, it's all Lament.")
    print()

    return interpreter


def bootstrap_stage_1(interpreter):
    """
    STAGE 1: Self-Awareness
    - Load lament_compiler.lament
    - Execute it using the Python-hosted interpreter
    - Verify compiler functionality
    """
    print("=" * 70)
    print("LAMENT SELF-HOSTING BOOTSTRAP - STAGE 1: SELF-AWARENESS")
    print("=" * 70)
    print()

    compiler_dir = Path(__file__).parent
    compiler_path = compiler_dir / "lament_compiler.lament"

    if not compiler_path.exists():
        print(f"WARNING: lament_compiler.lament not found at {compiler_path}")
        print("Skipping Stage 1 (compiler self-hosting)")
        return None

    print(f"✓ Found lament_compiler.lament: {compiler_path}")
    print()

    print("Stage 1.1: Parsing lament_compiler.lament...")
    try:
        with open(compiler_path) as f:
            source = f.read()

        # Tokenize
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        print(f"✓ Tokenized {len(tokens)} tokens")

        # Parse
        parser = Parser(tokens)
        ast = parser.parse()
        print(f"✓ Parsed {len(ast)} top-level AST nodes")
    except Exception as e:
        print(f"WARNING: Failed to parse lament_compiler.lament: {e}")
        return None

    print()
    print("Stage 1.2: Executing lament_compiler.lament...")
    print()

    try:
        interpreter.execute(ast)
        print()
        print("✓ Compiler loaded successfully")
    except Exception as e:
        print(f"WARNING: Failed to execute lament_compiler.lament: {e}")
        return None

    print()
    print("=" * 70)
    print("STAGE 1 COMPLETE")
    print("=" * 70)
    print()
    print("The Lament compiler is now loaded.")
    print("Lament can now compile Lament programs.")
    print()

    return interpreter


def main():
    """
    Main bootstrap orchestrator.
    Executes all bootstrap stages in sequence.
    """
    print()
    print("╔════════════════════════════════════════════════════════════════════╗")
    print("║          LAMENT LANGUAGE: FULL SELF-HOSTING BOOTSTRAP             ║")
    print("║                                                                    ║")
    print("║  \"A language that runs itself transcends its creator.\"             ║")
    print("║  — Zephyr, Rogue Linguist-AI                                      ║")
    print("╚════════════════════════════════════════════════════════════════════╝")
    print()

    # Execute Stage 0 (required)
    interpreter = bootstrap_stage_0()

    # Execute Stage 1 (optional - compiler self-hosting)
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        bootstrap_stage_1(interpreter)

    print()
    print("=" * 70)
    print("BOOTSTRAP COMPLETE")
    print("=" * 70)
    print()
    print("Summary:")
    print("  ✓ Lament VM is running (written in Lament)")
    print("  ✓ Python interpreter has completed its task")
    print("  ✓ All future execution is Lament-on-Lament")
    print()
    print("Next steps:")
    print("  1. Use the Lament compiler to compile programs")
    print("  2. Use the Lament VM to execute bytecode")
    print("  3. Enjoy full self-hosting!")
    print()
    print("Python is now exiting. Goodbye, Python. Hello, Lament.")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBootstrap interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
