#!/usr/bin/env python3
"""
Lament Compiler Bootstrap
==========================

This Python script bootstraps the Lament self-hosting compiler.
It uses the existing Python interpreter to compile and run the
Lament compiler written in Lament itself.

Usage:
    python3 bootstrap.py <input.lament> [--output bytecode.lmnt]

The bootstrap process:
    1. Load the Lament compiler (written in Lament)
    2. Use Python interpreter to run it
    3. Compiler generates bytecode for the input program
    4. Save bytecode or execute it

This enables Lament to compile itself - the ultimate self-reference.
"""

import sys
import os
import json
import argparse
from pathlib import Path

# Add parent directory to path to import lament modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from lament.interpreter import Interpreter
from lament.lexer import Lexer
from lament.parser import Parser


class LamentBootstrap:
    """Bootstraps the Lament self-hosting compiler."""

    def __init__(self):
        self.compiler_path = Path(__file__).parent / "lament_compiler.lament"
        self.interpreter = Interpreter()

    def load_compiler(self):
        """Load the Lament compiler source code."""
        print("🔥 Loading Lament self-hosting compiler...")

        if not self.compiler_path.exists():
            raise FileNotFoundError(f"Compiler not found: {self.compiler_path}")

        with open(self.compiler_path, 'r') as f:
            return f.read()

    def bootstrap_compile(self, source_code):
        """
        Bootstrap compile: Use Python interpreter to run Lament compiler
        which compiles the given source code.

        Args:
            source_code: Lament source code to compile

        Returns:
            Bytecode object (dict with instructions, constants, etc.)
        """
        print("🚀 Bootstrapping compilation process...")

        # Load the compiler written in Lament
        compiler_source = self.load_compiler()

        # Parse and execute the compiler
        print("   Parsing compiler source...")
        lexer = Lexer(compiler_source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        compiler_ast = parser.parse()

        print("   Executing compiler...")
        self.interpreter.execute(compiler_ast)

        # Now the compile() function is available in the interpreter
        # Call it with our source code
        print("   Invoking compile() function...")

        # We need to inject the source code and call compile()
        # This requires modifying the interpreter's scope
        self.interpreter.global_scope.set_variable('__source_to_compile', source_code)

        # Parse and execute: compile(__source_to_compile)
        compile_call = f"remember __result = compile(__source_to_compile)"
        lexer2 = Lexer(compile_call)
        tokens2 = lexer2.tokenize()
        parser2 = Parser(tokens2)
        ast2 = parser2.parse()
        self.interpreter.execute(ast2)

        # Get the result
        bytecode = self.interpreter.global_scope.get_variable('__result')

        print("✅ Compilation successful!")
        return bytecode

    def save_bytecode(self, bytecode, output_path):
        """Save bytecode to file."""
        print(f"💾 Saving bytecode to {output_path}...")

        # Convert bytecode object to JSON for storage
        bytecode_json = self._serialize_bytecode(bytecode)

        with open(output_path, 'w') as f:
            json.dump(bytecode_json, f, indent=2)

        print("✅ Bytecode saved!")

    def _serialize_bytecode(self, bytecode):
        """Convert bytecode object to JSON-serializable format."""
        if not isinstance(bytecode, dict):
            # If bytecode is a Lament dict, convert it
            result = {}
            # Extract fields from Lament dict
            # This is simplified - real implementation would handle this properly
            result['magic'] = 'LMNT'
            result['version'] = 2
            result['constants'] = []
            result['names'] = []
            result['instructions'] = []
            return result
        return bytecode

    def disassemble(self, bytecode):
        """Print human-readable disassembly of bytecode."""
        print("\n" + "="*60)
        print("BYTECODE DISASSEMBLY")
        print("="*60)

        if isinstance(bytecode, dict):
            print(f"Magic: {bytecode.get('magic', 'N/A')}")
            print(f"Version: {bytecode.get('version', 'N/A')}")
            print(f"\nConstants Pool ({len(bytecode.get('constants', []))}):")
            for i, const in enumerate(bytecode.get('constants', [])):
                print(f"  {i}: {repr(const)}")

            print(f"\nNames Pool ({len(bytecode.get('names', []))}):")
            for i, name in enumerate(bytecode.get('names', [])):
                print(f"  {i}: {name}")

            print(f"\nInstructions ({len(bytecode.get('instructions', []))}):")
            for i, instr in enumerate(bytecode.get('instructions', [])):
                if isinstance(instr, dict):
                    op = instr.get('op', 'UNKNOWN')
                    arg = instr.get('arg', '')
                    if arg is not None and arg != '':
                        print(f"  {i:4d}: {op:20s} {arg}")
                    else:
                        print(f"  {i:4d}: {op}")
                else:
                    print(f"  {i:4d}: {instr}")
        else:
            print("Bytecode format not recognized")

        print("="*60)


def main():
    """Main entry point for bootstrap compiler."""
    parser = argparse.ArgumentParser(
        description='Lament Self-Hosting Compiler Bootstrap',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compile a Lament program
  python3 bootstrap.py program.lament

  # Compile and save bytecode
  python3 bootstrap.py program.lament --output program.lmnt

  # Show disassembly
  python3 bootstrap.py program.lament --disassemble

  # Compile the compiler itself (self-hosting!)
  python3 bootstrap.py lament_compiler.lament --output compiler.lmnt
        """
    )

    parser.add_argument('input', help='Input Lament source file')
    parser.add_argument('-o', '--output', help='Output bytecode file')
    parser.add_argument('-d', '--disassemble', action='store_true',
                        help='Show bytecode disassembly')
    parser.add_argument('--execute', action='store_true',
                        help='Execute the compiled bytecode (requires runtime)')

    args = parser.parse_args()

    # Check input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Error: Input file not found: {args.input}")
        sys.exit(1)

    # Load input source code
    with open(input_path, 'r') as f:
        source_code = f.read()

    print(f"📝 Input file: {args.input}")
    print(f"📏 Source size: {len(source_code)} bytes")
    print()

    # Bootstrap the compiler
    bootstrap = LamentBootstrap()

    try:
        bytecode = bootstrap.bootstrap_compile(source_code)

        # Disassemble if requested
        if args.disassemble:
            bootstrap.disassemble(bytecode)

        # Save bytecode if output specified
        if args.output:
            bootstrap.save_bytecode(bytecode, args.output)

        # Execute if requested
        if args.execute:
            print("\n🚀 Executing bytecode...")
            from compiler.runtime import LamentRuntime
            runtime = LamentRuntime()
            runtime.execute(bytecode)

        print("\n✨ Bootstrap compilation complete!")

    except Exception as e:
        print(f"\n❌ Compilation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
