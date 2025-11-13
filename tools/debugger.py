"""
Lament Language Interactive Debugger
====================================

Interactive debugger with advanced features:
- Breakpoints (line-based and conditional)
- Step through execution (step, next, continue)
- Variable inspection
- Timeline navigation
- Time-travel debugging (rewind/replay)
- Reality fork inspection
- Call stack visualization

Usage:
    python -m tools.debugger <file.lament>
    lament-debug <file.lament>

Commands:
    break <line>     - Set breakpoint at line
    continue         - Continue execution
    step             - Step into next statement
    next             - Step over next statement
    vars             - Show all variables
    print <expr>     - Evaluate and print expression
    timeline <var>   - Show variable timeline
    rewind [steps]   - Rewind execution
    replay           - Replay to current point
    stack            - Show call stack
    quit             - Exit debugger

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
import cmd
import copy
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.lexer import Lexer
from lament.parser import (
    Parser, ASTNode, NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral,
    Identifier, BinaryOp, UnaryOp, Assignment, VariableDecl, ConfessStmt,
    IfStmt, WhileStmt, ForStmt, FunctionDef, FunctionCall, ExhaleStmt,
    TemporalAccess, ListLiteral, DictLiteral, IndexAccess, ForkReality
)
from lament.interpreter import LamentInterpreter, ReturnValue
from lament.types import TimelineValue


@dataclass
class ExecutionSnapshot:
    """Snapshot of execution state for time-travel."""
    statement_index: int
    globals: Dict[str, Any]
    scopes: List[Dict[str, Any]]
    output: List[str]
    call_stack: List[Tuple[str, int]]


@dataclass
class Breakpoint:
    """Breakpoint configuration."""
    line: int
    condition: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0


class LamentDebugger(LamentInterpreter):
    """Interactive debugger for Lament programs.

    Extends the interpreter with debugging capabilities:
    - Breakpoint management
    - Step-by-step execution
    - State inspection
    - Timeline navigation
    - Time-travel (rewind/replay)

    Example:
        debugger = LamentDebugger(ast, source_lines)
        debugger.run()
    """

    def __init__(self, ast, source_lines):
        """Initialize debugger.

        Args:
            ast: Parsed AST
            source_lines: Source code split into lines
        """
        super().__init__()

        self.ast = ast
        self.source_lines = source_lines
        self.breakpoints = {}  # line -> Breakpoint
        self.current_statement = 0
        self.execution_history = []  # List of ExecutionSnapshot
        self.step_mode = False
        self.next_mode = False
        self.running = False
        self.output_buffer = []
        self.call_stack = []  # [(function_name, statement_index)]

        # Override confess to capture output
        self.original_confess = self.execute_statement

    def add_breakpoint(self, line, condition=None):
        """Add a breakpoint at line."""
        self.breakpoints[line] = Breakpoint(line=line, condition=condition)
        print(f"Breakpoint set at line {line}")

    def remove_breakpoint(self, line):
        """Remove breakpoint at line."""
        if line in self.breakpoints:
            del self.breakpoints[line]
            print(f"Breakpoint removed from line {line}")
        else:
            print(f"No breakpoint at line {line}")

    def list_breakpoints(self):
        """List all breakpoints."""
        if not self.breakpoints:
            print("No breakpoints set")
            return

        print("\nBreakpoints:")
        for line, bp in sorted(self.breakpoints.items()):
            status = "enabled" if bp.enabled else "disabled"
            condition = f" (condition: {bp.condition})" if bp.condition else ""
            hits = f" [hit {bp.hit_count} times]" if bp.hit_count > 0 else ""
            print(f"  Line {line}: {status}{condition}{hits}")

    def should_break(self, line):
        """Check if execution should break at line."""
        if line not in self.breakpoints:
            return False

        bp = self.breakpoints[line]
        if not bp.enabled:
            return False

        bp.hit_count += 1

        # Check condition if set
        if bp.condition:
            try:
                # Evaluate condition in current context
                from lament.parser import Parser
                from lament.lexer import Lexer

                lexer = Lexer(bp.condition)
                tokens = lexer.tokenize()
                parser = Parser(tokens)
                expr = parser.parse_expression()
                result = self.evaluate(expr)
                return self.is_truthy(result)
            except:
                print(f"Warning: Breakpoint condition failed to evaluate: {bp.condition}")
                return True

        return True

    def save_snapshot(self):
        """Save current execution state."""
        snapshot = ExecutionSnapshot(
            statement_index=self.current_statement,
            globals=copy.deepcopy(self.globals),
            scopes=copy.deepcopy(self.scopes),
            output=self.output_buffer.copy(),
            call_stack=self.call_stack.copy()
        )
        self.execution_history.append(snapshot)

    def restore_snapshot(self, snapshot):
        """Restore execution state from snapshot."""
        self.current_statement = snapshot.statement_index
        self.globals = copy.deepcopy(snapshot.globals)
        self.scopes = copy.deepcopy(snapshot.scopes)
        self.output_buffer = snapshot.output.copy()
        self.call_stack = snapshot.call_stack.copy()

    def rewind(self, steps=1):
        """Rewind execution by N steps."""
        if len(self.execution_history) <= steps:
            print("Cannot rewind that far")
            return

        # Go back N snapshots
        target = len(self.execution_history) - steps - 1
        snapshot = self.execution_history[target]
        self.restore_snapshot(snapshot)

        # Truncate history
        self.execution_history = self.execution_history[:target + 1]

        print(f"Rewound {steps} step(s)")
        self.show_current_line()

    def show_current_line(self):
        """Display current line with context."""
        if self.current_statement >= len(self.ast):
            print("(end of program)")
            return

        # Try to find line number (approximate)
        print(f"\n--- Statement {self.current_statement} ---")

        # Show surrounding source (if available)
        if self.source_lines:
            start = max(0, self.current_statement - 2)
            end = min(len(self.source_lines), self.current_statement + 3)

            for i in range(start, end):
                marker = ">>>" if i == self.current_statement else "   "
                line_num = i + 1
                line = self.source_lines[i] if i < len(self.source_lines) else ""
                print(f"{marker} {line_num:4d} | {line}")

    def show_variables(self):
        """Show all variables in current scope."""
        print("\n=== Variables ===")

        # Show local scopes
        for i, scope in enumerate(self.scopes):
            if scope:
                print(f"\n Scope {i}:")
                for name, value in scope.items():
                    if isinstance(value, TimelineValue):
                        print(f"   {name} = {value.current} (timeline, age: {value.get_age()})")
                    else:
                        print(f"   {name} = {value}")

        # Show globals
        if self.globals:
            print(f"\n Globals:")
            for name, value in self.globals.items():
                if not callable(value):
                    if isinstance(value, TimelineValue):
                        print(f"   {name} = {value.current} (timeline, age: {value.get_age()})")
                    else:
                        print(f"   {name} = {value}")

    def show_timeline(self, var_name):
        """Show timeline history for a variable."""
        # Find variable
        timeline_val = None

        for scope in reversed(self.scopes):
            if var_name in scope:
                timeline_val = scope[var_name]
                break

        if timeline_val is None and var_name in self.globals:
            timeline_val = self.globals[var_name]

        if timeline_val is None:
            print(f"Variable '{var_name}' not found")
            return

        if not isinstance(timeline_val, TimelineValue):
            print(f"Variable '{var_name}' is not a timeline variable")
            return

        print(f"\n=== Timeline for '{var_name}' ===")
        print(f"Current value: {timeline_val.current}")
        print(f"Origin value: {timeline_val.get_origin()}")
        print(f"Age: {timeline_val.get_age()}")
        print(f"Born: {timeline_val.born}")

        print("\nHistory:")
        for i, value in enumerate(timeline_val.history):
            marker = ">>>" if i == len(timeline_val.history) - 1 else "   "
            print(f"{marker} [{i}] {value}")

    def show_call_stack(self):
        """Show call stack."""
        if not self.call_stack:
            print("(no active function calls)")
            return

        print("\n=== Call Stack ===")
        for i, (func_name, stmt_idx) in enumerate(reversed(self.call_stack)):
            print(f"  {i}: {func_name} (statement {stmt_idx})")

    def execute_statement(self, stmt):
        """Override to add debugging hooks."""
        # Save snapshot before execution
        self.save_snapshot()

        # Check for breakpoints
        if self.should_break(self.current_statement):
            self.step_mode = True
            print(f"\nBreakpoint hit at statement {self.current_statement}")
            self.show_current_line()
            return

        # Execute with output capture
        if isinstance(stmt, ConfessStmt):
            value = self.evaluate(stmt.value)
            output = self.value_to_string(value)
            self.output_buffer.append(output)
            print(output)
        else:
            super().execute_statement(stmt)

        self.current_statement += 1

    def run_interactive(self):
        """Run in interactive mode with command prompt."""
        print("Lament Debugger")
        print("Type 'help' for commands\n")

        debugger_shell = DebuggerShell(self)
        debugger_shell.cmdloop()


class DebuggerShell(cmd.Cmd):
    """Interactive shell for debugger commands."""

    intro = "Lament Debugger. Type 'help' or '?' for commands."
    prompt = "(lament-debug) "

    def __init__(self, debugger):
        super().__init__()
        self.debugger = debugger

    def do_break(self, arg):
        """Set a breakpoint: break <line> [condition]"""
        parts = arg.split(None, 1)
        if not parts:
            self.debugger.list_breakpoints()
            return

        try:
            line = int(parts[0])
            condition = parts[1] if len(parts) > 1 else None
            self.debugger.add_breakpoint(line, condition)
        except ValueError:
            print("Invalid line number")

    def do_delete(self, arg):
        """Delete breakpoint: delete <line>"""
        try:
            line = int(arg)
            self.debugger.remove_breakpoint(line)
        except ValueError:
            print("Invalid line number")

    def do_continue(self, arg):
        """Continue execution until next breakpoint"""
        self.debugger.step_mode = False

        try:
            while self.debugger.current_statement < len(self.debugger.ast):
                stmt = self.debugger.ast[self.debugger.current_statement]
                self.debugger.execute_statement(stmt)

                if self.debugger.step_mode:
                    break

            if self.debugger.current_statement >= len(self.debugger.ast):
                print("\nProgram finished")
        except Exception as e:
            print(f"Error: {e}")

    def do_step(self, arg):
        """Execute next statement (step into)"""
        if self.debugger.current_statement >= len(self.debugger.ast):
            print("Program finished")
            return

        try:
            stmt = self.debugger.ast[self.debugger.current_statement]
            self.debugger.execute_statement(stmt)
            self.debugger.show_current_line()
        except Exception as e:
            print(f"Error: {e}")

    def do_next(self, arg):
        """Execute next statement (step over)"""
        # Same as step for now (proper implementation would track call depth)
        self.do_step(arg)

    def do_vars(self, arg):
        """Show all variables"""
        self.debugger.show_variables()

    def do_print(self, arg):
        """Evaluate and print expression: print <expression>"""
        if not arg:
            print("Usage: print <expression>")
            return

        try:
            from lament.lexer import Lexer
            from lament.parser import Parser

            lexer = Lexer(arg)
            tokens = lexer.tokenize()
            parser = Parser(tokens)
            expr = parser.parse_expression()

            result = self.debugger.evaluate(expr)
            print(self.debugger.value_to_string(result))
        except Exception as e:
            print(f"Error evaluating expression: {e}")

    def do_timeline(self, arg):
        """Show timeline for variable: timeline <variable>"""
        if not arg:
            print("Usage: timeline <variable>")
            return

        self.debugger.show_timeline(arg)

    def do_rewind(self, arg):
        """Rewind execution: rewind [steps]"""
        steps = int(arg) if arg else 1
        self.debugger.rewind(steps)

    def do_replay(self, arg):
        """Replay execution from start to current point"""
        if not self.debugger.execution_history:
            print("No history to replay")
            return

        print("Replaying execution...")
        current = self.debugger.current_statement

        # Go back to start
        self.debugger.restore_snapshot(self.debugger.execution_history[0])

        # Replay to current
        for i in range(current):
            if i < len(self.debugger.ast):
                stmt = self.debugger.ast[i]
                self.debugger.execute_statement(stmt)

        print("Replay complete")
        self.debugger.show_current_line()

    def do_stack(self, arg):
        """Show call stack"""
        self.debugger.show_call_stack()

    def do_list(self, arg):
        """Show source code around current line"""
        self.debugger.show_current_line()

    def do_quit(self, arg):
        """Exit debugger"""
        print("Exiting debugger")
        return True

    def do_help(self, arg):
        """Show help"""
        if arg:
            super().do_help(arg)
        else:
            print("\nDebugger Commands:")
            print("  break <line>      - Set breakpoint")
            print("  delete <line>     - Remove breakpoint")
            print("  continue          - Continue execution")
            print("  step              - Step to next statement")
            print("  next              - Step over function calls")
            print("  vars              - Show all variables")
            print("  print <expr>      - Evaluate expression")
            print("  timeline <var>    - Show variable timeline")
            print("  rewind [steps]    - Rewind execution")
            print("  replay            - Replay execution")
            print("  stack             - Show call stack")
            print("  list              - Show source code")
            print("  quit              - Exit debugger")
            print()

    # Aliases
    do_b = do_break
    do_d = do_delete
    do_c = do_continue
    do_s = do_step
    do_n = do_next
    do_p = do_print
    do_l = do_list
    do_q = do_quit


def main():
    """CLI entry point for debugger."""
    if len(sys.argv) < 2:
        print("Usage: lament-debug <file.lament>")
        print("\nInteractive debugger for Lament programs.")
        print("\nCommands:")
        print("  break, continue, step, next, vars, print, timeline")
        print("  rewind, replay, stack, list, quit")
        sys.exit(1)

    filename = sys.argv[1]

    try:
        # Load and parse file
        with open(filename, 'r') as f:
            source = f.read()

        source_lines = source.split('\n')

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        # Create and run debugger
        debugger = LamentDebugger(ast, source_lines)
        debugger.run_interactive()

    except FileNotFoundError:
        print(f"Error: File not found: {filename}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
