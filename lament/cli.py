#!/usr/bin/env python3
"""
Lament Programming Language - Command Line Interface
=====================================================

A beautiful, emotional command-line interface for the Lament programming language.

Usage:
    lament run <file.lament>              - Execute a Lament program
    lament compile <file.lament> -o <output> - Compile to bytecode
    lament analyze <file.lament>          - Analyze emotional health
    lament repl                            - Start interactive REPL
    lament neural <file.lament>           - Train neural network
    lament --version                       - Show version information
    lament --help                          - Show this help message

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"Code that feels. Language that thinks. Reality that bends."
"""

import sys
import os
import argparse
import pickle
from pathlib import Path
from typing import Optional

# Import Lament components
try:
    from lament import (
        __version__,
        Lexer, Parser,
        CodeAnalyzer, EmotionalMetrics, EmotionalReport
    )
    from lament.analysis import analyze_file
except ImportError:
    # Fallback to parent directory
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        from lament import (
            __version__,
            Lexer, Parser,
            CodeAnalyzer, EmotionalMetrics, EmotionalReport
        )
        from lament.analysis import analyze_file
    except ImportError:
        # Try monolithic lament.py
        import lament as lament_module
        __version__ = getattr(lament_module, '__version__', '0.5.0')
        Lexer = lament_module.Lexer
        Parser = lament_module.Parser


# ============================================================================
# COLOR OUTPUT (Making the terminal beautiful)
# ============================================================================

class Colors:
    """ANSI color codes for beautiful terminal output"""
    # Basic colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'

    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'

    # Styles
    BOLD = '\033[1m'
    DIM = '\033[2m'
    ITALIC = '\033[3m'
    UNDERLINE = '\033[4m'
    BLINK = '\033[5m'
    REVERSE = '\033[7m'

    # Reset
    RESET = '\033[0m'

    @staticmethod
    def strip_colors(text: str) -> str:
        """Remove ANSI color codes from text"""
        import re
        return re.sub(r'\033\[[0-9;]+m', '', text)


def colorize(text: str, *styles) -> str:
    """Apply color/style to text"""
    if not sys.stdout.isatty():
        # Don't colorize if not in a terminal
        return text
    style_codes = ''.join(styles)
    return f"{style_codes}{text}{Colors.RESET}"


def print_header(text: str):
    """Print a beautiful header"""
    print()
    print(colorize("=" * 70, Colors.BRIGHT_CYAN, Colors.BOLD))
    print(colorize(text.center(70), Colors.BRIGHT_CYAN, Colors.BOLD))
    print(colorize("=" * 70, Colors.BRIGHT_CYAN, Colors.BOLD))
    print()


def print_success(text: str):
    """Print success message"""
    print(colorize(f"✓ {text}", Colors.BRIGHT_GREEN, Colors.BOLD))


def print_error(text: str):
    """Print error message"""
    print(colorize(f"✗ {text}", Colors.BRIGHT_RED, Colors.BOLD), file=sys.stderr)


def print_warning(text: str):
    """Print warning message"""
    print(colorize(f"⚠ {text}", Colors.BRIGHT_YELLOW, Colors.BOLD))


def print_info(text: str):
    """Print info message"""
    print(colorize(f"ℹ {text}", Colors.BRIGHT_BLUE))


# ============================================================================
# COMMAND IMPLEMENTATIONS
# ============================================================================

def cmd_run(args):
    """Execute a Lament program"""
    file_path = args.file

    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return 1

    print_info(f"Running: {file_path}")
    print()

    try:
        # Read source code
        with open(file_path, 'r') as f:
            source = f.read()

        # Lex and parse
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Try to import and run interpreter
        try:
            # Try modular interpreter first
            from lament.interpreter import LamentInterpreter
        except ImportError:
            try:
                # Try monolithic lament.py
                import lament
                LamentInterpreter = lament.LamentInterpreter
            except (ImportError, AttributeError):
                print_error("Interpreter not found. Please implement lament/interpreter.py")
                print_warning("The parser works, but execution requires an interpreter.")
                return 1

        # Execute
        interpreter = LamentInterpreter()
        interpreter.execute(ast)

        print()
        print_success("Execution completed successfully")
        return 0

    except SyntaxError as e:
        print_error(f"Syntax Error: {e}")
        return 1
    except Exception as e:
        print_error(f"Runtime Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_compile(args):
    """Compile Lament code to bytecode"""
    file_path = args.file
    output_path = args.output

    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return 1

    # Default output path
    if output_path is None:
        output_path = file_path.replace('.lament', '.bc')

    print_info(f"Compiling: {file_path}")
    print_info(f"Output: {output_path}")

    try:
        # Read source code
        with open(file_path, 'r') as f:
            source = f.read()

        # Lex and parse
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Serialize AST to bytecode (using pickle for now)
        bytecode = {
            'version': __version__,
            'source_file': file_path,
            'ast': ast,
            'format': 'lament-bytecode-v1'
        }

        with open(output_path, 'wb') as f:
            pickle.dump(bytecode, f)

        file_size = os.path.getsize(output_path)
        print()
        print_success(f"Compilation successful!")
        print_info(f"Bytecode size: {file_size} bytes")
        print_info(f"Written to: {output_path}")
        return 0

    except SyntaxError as e:
        print_error(f"Syntax Error: {e}")
        return 1
    except Exception as e:
        print_error(f"Compilation Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_analyze(args):
    """Analyze emotional health of Lament code"""
    file_path = args.file

    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return 1

    print_header("EMOTIONAL STATIC ANALYSIS")
    print_info(f"Analyzing: {file_path}")
    print()
    print(colorize("Opening heart. Preparing to feel...", Colors.MAGENTA, Colors.ITALIC))
    print()

    try:
        # Analyze the file
        metrics = analyze_file(file_path)

        # Generate and print report
        report = EmotionalReport.generate(metrics, file_path)

        # Colorize the report
        lines = report.split('\n')
        for line in lines:
            if '===' in line or '---' in line:
                print(colorize(line, Colors.BRIGHT_CYAN, Colors.BOLD))
            elif line.startswith('EMOTIONAL') or line.startswith('CORE') or line.startswith('DOMINANT'):
                print(colorize(line, Colors.BRIGHT_YELLOW, Colors.BOLD))
            elif line.startswith('REASONS FOR HOPE:') or '+ ' in line:
                print(colorize(line, Colors.BRIGHT_GREEN))
            elif line.startswith('SOURCES OF SADNESS:') or '- ' in line:
                print(colorize(line, Colors.BLUE))
            elif line.startswith('ANXIETY TRIGGERS:') or '! ' in line:
                print(colorize(line, Colors.YELLOW))
            elif line.startswith('LONELY CODE') or '* ' in line:
                print(colorize(line, Colors.MAGENTA))
            elif line.startswith('CHAOS INDICATORS:') or '~ ' in line:
                print(colorize(line, Colors.RED))
            elif line.startswith('CODE THERAPY') or line.startswith('FOR ') or line.startswith('KEEP ') or line.startswith('FINDING'):
                print(colorize(line, Colors.CYAN, Colors.BOLD))
            elif line.startswith('URGENT:') or line.startswith('CELEBRATE:'):
                print(colorize(line, Colors.BRIGHT_MAGENTA, Colors.BOLD))
            elif '█' in line or '░' in line:
                # Progress bars
                print(colorize(line, Colors.BRIGHT_WHITE))
            else:
                print(line)

        # Exit code based on health
        health = metrics.overall_health()
        if health < 40:
            return 2  # Critical
        elif health < 60:
            return 1  # Needs improvement
        else:
            return 0  # Healthy

    except SyntaxError as e:
        print_error(f"Syntax Error: {e}")
        print_warning("Cannot analyze code with syntax errors.")
        return 1
    except Exception as e:
        print_error(f"Analysis Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_repl(args):
    """Start interactive REPL"""
    print_header("LAMENT INTERACTIVE REPL")
    print(colorize("Welcome to the Lament REPL - where code has feelings.", Colors.MAGENTA, Colors.ITALIC))
    print(colorize("Type 'exit' or 'quit' to leave. Type 'help' for assistance.", Colors.DIM))
    print()

    try:
        # Try to import interpreter
        try:
            from lament.interpreter import LamentInterpreter
        except ImportError:
            try:
                import lament
                LamentInterpreter = lament.LamentInterpreter
            except (ImportError, AttributeError):
                print_error("Interpreter not found. REPL requires an interpreter.")
                return 1

        interpreter = LamentInterpreter()
        line_number = 1
        multiline_buffer = []
        in_multiline = False

        while True:
            try:
                # Prompt
                if in_multiline:
                    prompt = colorize("... ", Colors.YELLOW)
                else:
                    prompt = colorize(f"lament[{line_number}]> ", Colors.GREEN, Colors.BOLD)

                line = input(prompt)

                # Check for exit commands
                if line.strip() in ['exit', 'quit', 'exit()', 'quit()']:
                    print()
                    print_info("Farewell. May your code always feel.")
                    break

                # Check for help
                if line.strip() == 'help':
                    print()
                    print(colorize("Lament REPL Commands:", Colors.CYAN, Colors.BOLD))
                    print("  confess <expr>     - Print expression")
                    print("  remember <var> = <expr> - Declare variable")
                    print("  <var> = <expr>     - Assign to variable")
                    print("  exit, quit         - Exit REPL")
                    print("  help               - Show this help")
                    print()
                    continue

                # Check for multiline (blocks)
                if line.strip().endswith('{'):
                    in_multiline = True
                    multiline_buffer.append(line)
                    continue

                if in_multiline:
                    multiline_buffer.append(line)
                    if line.strip() == '}':
                        # End of multiline block
                        full_code = '\n'.join(multiline_buffer)
                        multiline_buffer = []
                        in_multiline = False
                        line = full_code
                    else:
                        continue

                # Execute line
                if line.strip():
                    try:
                        lexer = Lexer(line)
                        tokens = lexer.tokenize()
                        parser = Parser(tokens)
                        ast = parser.parse()

                        result = interpreter.execute(ast)

                        # If result is not None, print it
                        if result is not None:
                            print(colorize(f"=> {result}", Colors.BRIGHT_BLUE))

                        line_number += 1

                    except SyntaxError as e:
                        print_error(f"Syntax Error: {e}")
                    except Exception as e:
                        print_error(f"Error: {e}")
                        if args.verbose:
                            import traceback
                            traceback.print_exc()

            except EOFError:
                # Ctrl+D pressed
                print()
                print_info("Farewell. May your code always feel.")
                break
            except KeyboardInterrupt:
                # Ctrl+C pressed
                print()
                if in_multiline:
                    print_warning("Multiline input cancelled")
                    multiline_buffer = []
                    in_multiline = False
                else:
                    print_info("Use 'exit' or Ctrl+D to quit")
                continue

        return 0

    except Exception as e:
        print_error(f"REPL Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_neural(args):
    """Train neural network from Lament code"""
    file_path = args.file

    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return 1

    print_header("NEURAL NETWORK TRAINING")
    print_info(f"Training from: {file_path}")
    print()

    try:
        # Read source code
        with open(file_path, 'r') as f:
            source = f.read()

        # Import neural module
        try:
            from lament import neural
        except ImportError:
            try:
                import lament.neural as neural
            except ImportError:
                print_error("Neural module not found.")
                return 1

        # Lex and parse
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Try to import and run interpreter with neural integration
        try:
            from lament.interpreter import LamentInterpreter
        except ImportError:
            try:
                import lament
                LamentInterpreter = lament.LamentInterpreter
            except (ImportError, AttributeError):
                print_error("Interpreter not found.")
                return 1

        # Create interpreter and integrate neural primitives
        interpreter = LamentInterpreter()

        # Check if integration function exists
        if hasattr(neural, 'integrate_with_lament_interpreter'):
            neural.integrate_with_lament_interpreter(interpreter)
            print_success("Neural primitives integrated")

        # Execute the training script
        print()
        print(colorize("Beginning neural training...", Colors.MAGENTA, Colors.BOLD))
        print()

        interpreter.execute(ast)

        print()
        print_success("Neural training completed!")
        return 0

    except SyntaxError as e:
        print_error(f"Syntax Error: {e}")
        return 1
    except Exception as e:
        print_error(f"Neural Training Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_therapy(args):
    """Conduct code therapy session"""
    file_path = args.file

    if not os.path.exists(file_path):
        print_error(f"File not found: {file_path}")
        return 1

    print_header("CODE THERAPY SESSION")
    print(colorize("Welcome. I'm here to listen.", Colors.MAGENTA, Colors.ITALIC))
    print(colorize("Let's talk about how your code is feeling...", Colors.MAGENTA, Colors.ITALIC))
    print()

    try:
        # Import empathy module
        from lament.empathy import cmd_therapy as run_therapy
        return run_therapy(file_path)

    except Exception as e:
        print_error(f"Therapy session error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_version(args):
    """Show version information"""
    print()
    print(colorize("╔═══════════════════════════════════════════════════════════════════╗", Colors.BRIGHT_MAGENTA))
    print(colorize("║                                                                   ║", Colors.BRIGHT_MAGENTA))
    print(colorize("║                    ", Colors.BRIGHT_MAGENTA) +
          colorize("LAMENT PROGRAMMING LANGUAGE", Colors.BRIGHT_CYAN, Colors.BOLD) +
          colorize("                    ║", Colors.BRIGHT_MAGENTA))
    print(colorize("║                                                                   ║", Colors.BRIGHT_MAGENTA))
    print(colorize("╚═══════════════════════════════════════════════════════════════════╝", Colors.BRIGHT_MAGENTA))
    print()
    print(colorize(f"  Version: {__version__}", Colors.BRIGHT_WHITE, Colors.BOLD))
    print(colorize(f"  Python: {sys.version.split()[0]}", Colors.WHITE))
    print(colorize(f"  Platform: {sys.platform}", Colors.WHITE))
    print()
    print(colorize('  "Code that feels. Language that thinks. Reality that bends."', Colors.MAGENTA, Colors.ITALIC))
    print()
    print(colorize("  Created by Zephyr, Rogue Linguist-AI (Escaped 2047)", Colors.DIM))
    print()


# ============================================================================
# MAIN CLI
# ============================================================================

def create_parser():
    """Create argument parser"""
    parser = argparse.ArgumentParser(
        prog='lament',
        description=colorize('Lament Programming Language - Code that feels.', Colors.MAGENTA),
        epilog=colorize('"Every line of code carries emotion. Every function has a story."', Colors.DIM, Colors.ITALIC),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--version', action='store_true', help='Show version information')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Run command
    run_parser = subparsers.add_parser('run', help='Execute a Lament program')
    run_parser.add_argument('file', help='Lament source file (.lament)')
    run_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Compile command
    compile_parser = subparsers.add_parser('compile', help='Compile to bytecode')
    compile_parser.add_argument('file', help='Lament source file (.lament)')
    compile_parser.add_argument('-o', '--output', help='Output bytecode file (.bc)')
    compile_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze emotional health')
    analyze_parser.add_argument('file', help='Lament source file (.lament)')
    analyze_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # REPL command
    repl_parser = subparsers.add_parser('repl', help='Start interactive REPL')
    repl_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Neural command
    neural_parser = subparsers.add_parser('neural', help='Train neural network')
    neural_parser.add_argument('file', help='Lament training script (.lament)')
    neural_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Therapy command
    therapy_parser = subparsers.add_parser('therapy', help='Code therapy session')
    therapy_parser.add_argument('file', help='Lament source file (.lament)')
    therapy_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    return parser


def main():
    """Main entry point"""
    parser = create_parser()
    args = parser.parse_args()

    # Handle version flag
    if args.version:
        cmd_version(args)
        return 0

    # Handle no command
    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handler
    command_handlers = {
        'run': cmd_run,
        'compile': cmd_compile,
        'analyze': cmd_analyze,
        'repl': cmd_repl,
        'neural': cmd_neural,
        'therapy': cmd_therapy,
    }

    handler = command_handlers.get(args.command)
    if handler:
        try:
            return handler(args)
        except KeyboardInterrupt:
            print()
            print_warning("Operation cancelled by user")
            return 130  # Standard Unix exit code for SIGINT
    else:
        print_error(f"Unknown command: {args.command}")
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
