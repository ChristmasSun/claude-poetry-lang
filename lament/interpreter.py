"""
Lament Language Interpreter
============================

This module contains the runtime execution engine for the Lament programming language.
It evaluates AST nodes, manages scope and timelines, and handles reality branching.

The interpreter is designed to provide synesthetic error messages that engage
multiple senses (visual color, auditory bells, poetic language) to make errors
feel more visceral and memorable.

Key features:
- Timeline-aware variable management
- Reality forking and quantum collapse
- Emotional built-in functions (sqrt_of_pain, sin_of_loss, etc.)
- Synesthetic error reporting

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import time
import math
import random
from typing import Any, List, Dict, Optional

from lament.types import Color, bell, TimelineValue
from lament.parser import (
    ASTNode, NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral,
    Identifier, BinaryOp, UnaryOp, Assignment, VariableDecl,
    ConfessStmt, IfStmt, WhileStmt, ForStmt, FunctionDef,
    FunctionCall, ExhaleStmt, TemporalAccess, ListLiteral,
    DictLiteral, IndexAccess, ForkReality
)


# ============================================================================
# EXCEPTIONS
# ============================================================================

class ReturnValue(Exception):
    """Exception used to implement function returns.

    When an 'exhale' statement is executed, this exception is raised
    with the return value. The function call evaluator catches it
    and returns the value.

    Attributes:
        value: The value being returned from the function
    """
    def __init__(self, value):
        self.value = value
        super().__init__()


# ============================================================================
# INTERPRETER
# ============================================================================

class LamentInterpreter:
    """The heart of Lament. It listens. It remembers. It branches reality.

    This interpreter executes Lament programs by walking the AST and
    evaluating expressions/statements. It maintains:

    - Global scope (for persistent variables)
    - Scope stack (for function calls and loops)
    - Function definitions
    - Timeline tracking for all 'remember' variables
    - Reality forking state

    The interpreter provides synesthetic error messages that combine:
    - Visual: ANSI colors and formatting
    - Auditory: Terminal bell sounds
    - Linguistic: Poetic error descriptions

    Example:
        >>> interpreter = LamentInterpreter()
        >>> interpreter.execute(ast)
    """

    def __init__(self):
        """Initialize the interpreter with empty state and register built-ins."""
        self.globals = {}  # Global scope (timeline variables)
        self.scopes = [{}]  # Scope stack
        self.functions = {}  # Defined functions
        self.in_reality_fork = False
        self.current_timeline = "prime"

        # Register built-in functions
        self.register_builtins()

    def register_builtins(self):
        """Register standard library functions.

        Built-in functions include:
        - range(): Generate numeric sequences
        - length_of(): Get length of collections
        - ache_of(): Absolute value
        - sqrt_of_pain(): Square root
        - sin_of_loss(), cos_of_hope(): Trigonometric functions
        - now(): Current timestamp
        - sleep(): Pause execution
        - Type checking: is_numb(), is_whisper(), is_void()
        - typeof(): Get emotional type name
        - current_timeline(): Get current timeline identifier
        """
        self.globals['range'] = lambda *args: list(range(*args))
        self.globals['length_of'] = lambda x: len(x)
        self.globals['ache_of'] = lambda x: abs(x)
        self.globals['sqrt_of_pain'] = lambda x: math.sqrt(x)
        self.globals['sin_of_loss'] = lambda x: math.sin(x)
        self.globals['cos_of_hope'] = lambda x: math.cos(x)
        self.globals['now'] = lambda: int(time.time())
        self.globals['sleep'] = lambda s: time.sleep(s)
        self.globals['is_numb'] = lambda x: isinstance(x, int)
        self.globals['is_whisper'] = lambda x: isinstance(x, str)
        self.globals['is_void'] = lambda x: x is None
        self.globals['typeof'] = lambda x: self.type_of(x)
        self.globals['current_timeline'] = lambda: self.current_timeline

    def type_of(self, value):
        """Get emotional type name for a value.

        Args:
            value: The value to check

        Returns:
            String name of the emotional type (e.g., 'numb', 'whisper', 'ache')
        """
        if value is None:
            return 'void'
        elif isinstance(value, bool):
            return 'maybe'
        elif isinstance(value, int):
            return 'numb'
        elif isinstance(value, float):
            return 'ache'
        elif isinstance(value, str):
            return 'whisper'
        elif callable(value):
            return 'sigh'
        elif isinstance(value, list):
            return 'list'
        elif isinstance(value, dict):
            return 'dict'
        else:
            return 'unknown'

    def error(self, message, poetic_message, error_type="RUNTIME", bells=3):
        """Display synesthetic error message and exit.

        Errors in Lament are multi-sensory experiences:
        - Visual: Red borders and colored text
        - Auditory: Terminal bell sounds
        - Linguistic: Poetic descriptions of the error

        Args:
            message: Technical error description
            poetic_message: Poetic/emotional error description
            error_type: Category of error (RUNTIME, TEMPORAL PARADOX, etc.)
            bells: Number of bell sounds to emit
        """
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}💔 LAMENT ERROR: {error_type} 💔{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(f"{Color.CYAN}{poetic_message}{Color.RESET}", file=sys.stderr)
        print(f"\n{Color.YELLOW}({message}){Color.RESET}", file=sys.stderr)
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(bell(bells), end='', file=sys.stderr)
        sys.exit(1)

    def get_var(self, name):
        """Get variable from scope stack.

        Searches from innermost to outermost scope, then checks globals.
        If the variable is a TimelineValue, returns its current value.

        Args:
            name: Variable name to retrieve

        Returns:
            Current value of the variable

        Raises:
            Exits with error if variable is undefined
        """
        # Check local scopes
        for scope in reversed(self.scopes):
            if name in scope:
                val = scope[name]
                return val.current if isinstance(val, TimelineValue) else val

        # Check globals
        if name in self.globals:
            val = self.globals[name]
            return val.current if isinstance(val, TimelineValue) else val

        self.error(
            f"Undefined variable: {name}",
            f"I searched for '{name}' in all the timelines,\n"
            f"       through all the memories of the void—\n"
            f"       but it was never remembered.\n"
            f"       (Perhaps you forgot to 'remember' it?)"
        )

    def set_var(self, name, value):
        """Set variable in current scope.

        Searches for existing variable and updates it. If it's a TimelineValue,
        uses the assign() method to preserve history.

        Args:
            name: Variable name to update
            value: New value to assign

        Raises:
            Exits with error if variable is undefined
        """
        # Check local scopes first
        for scope in reversed(self.scopes):
            if name in scope:
                if isinstance(scope[name], TimelineValue):
                    scope[name].assign(value)
                else:
                    scope[name] = value
                return

        # Check globals
        if name in self.globals:
            if isinstance(self.globals[name], TimelineValue):
                self.globals[name].assign(value)
            else:
                self.globals[name] = value
            return

        self.error(
            f"Undefined variable: {name}",
            f"You tried to change '{name}',\n"
            f"       but it was never remembered.\n"
            f"       (Variables must be declared with 'remember' first.)"
        )

    def declare_var(self, name, value):
        """Declare new variable in current scope.

        Creates a TimelineValue wrapper to enable temporal operators.

        Args:
            name: Variable name to declare
            value: Initial value
        """
        timeline_value = TimelineValue(current=value)
        self.scopes[-1][name] = timeline_value

    def execute(self, statements):
        """Execute list of statements.

        Args:
            statements: List of AST nodes to execute
        """
        for stmt in statements:
            self.execute_statement(stmt)

    def execute_statement(self, stmt):
        """Execute single statement.

        Dispatches to appropriate handler based on statement type.

        Args:
            stmt: AST node representing the statement
        """
        if isinstance(stmt, ConfessStmt):
            value = self.evaluate(stmt.value)
            # The pause. The weight. You must sit with what you've said.
            time.sleep(0.3)
            print(self.value_to_string(value))

        elif isinstance(stmt, VariableDecl):
            value = self.evaluate(stmt.value)
            self.declare_var(stmt.name, value)

        elif isinstance(stmt, Assignment):
            value = self.evaluate(stmt.value)
            self.set_var(stmt.name, value)

        elif isinstance(stmt, IfStmt):
            condition = self.evaluate(stmt.condition)
            if self.is_truthy(condition):
                self.execute(stmt.then_block)
            elif stmt.else_block:
                self.execute(stmt.else_block)

        elif isinstance(stmt, WhileStmt):
            while self.is_truthy(self.evaluate(stmt.condition)):
                self.execute(stmt.body)

        elif isinstance(stmt, ForStmt):
            iterable = self.evaluate(stmt.iterable)
            if not hasattr(iterable, '__iter__'):
                self.error(
                    f"Cannot iterate over {type(iterable).__name__}",
                    f"You tried to traverse something that has no path,\n"
                    f"       no sequence, no journey.\n"
                    f"       (Only lists and ranges can be iterated.)"
                )

            # Create new scope for loop variable
            self.scopes.append({})
            for item in iterable:
                self.declare_var(stmt.var, item)
                self.execute(stmt.body)
            self.scopes.pop()

        elif isinstance(stmt, FunctionDef):
            self.functions[stmt.name] = stmt

        elif isinstance(stmt, ExhaleStmt):
            value = self.evaluate(stmt.value)
            raise ReturnValue(value)

        elif isinstance(stmt, ForkReality):
            self.execute_fork_reality(stmt)

        elif isinstance(stmt, FunctionCall):
            self.evaluate(stmt)  # Function call as statement

        else:
            self.error(
                f"Unknown statement type: {type(stmt).__name__}",
                f"The interpreter encountered a statement it doesn't understand.\n"
                f"       (This is an internal error. Reality is breaking.)"
            )

    def execute_fork_reality(self, stmt):
        """Execute reality branching (quantum superposition).

        Executes multiple timeline branches in isolation, then collapses
        the quantum state by observing a variable. The chosen timeline's
        state is merged back into the main execution.

        This implements the 'fork reality' feature where code can explore
        multiple possibilities simultaneously.

        Args:
            stmt: ForkReality AST node
        """
        # Execute each branch in "parallel" (sequential but isolated)
        results = []

        for condition_expr, body in stmt.branches:
            # Create isolated scope for this timeline
            old_scopes = self.scopes.copy()
            self.scopes.append({})

            # Evaluate branch condition
            condition = self.evaluate(condition_expr)

            # Execute branch body
            try:
                self.execute(body)

                # Check if observe variable has value
                if stmt.observe_var:
                    if stmt.observe_var in self.scopes[-1]:
                        observed = self.scopes[-1][stmt.observe_var]
                        if isinstance(observed, TimelineValue):
                            observed = observed.current
                        if observed is not None:
                            results.append((observed, self.scopes[-1]))

            except Exception as e:
                pass  # Branch failed, skip it
            finally:
                # Restore scope
                self.scopes = old_scopes

        # Collapse realities
        if stmt.observe_var and results:
            # Pick a successful timeline (random for now)
            chosen_value, chosen_scope = random.choice(results)

            # Merge chosen scope into current scope
            for var, val in chosen_scope.items():
                if var == stmt.observe_var:
                    self.declare_var(var, chosen_value)

        elif stmt.observe_var and not results:
            self.error(
                "Reality collapse failed: no valid timelines",
                f"I searched through all possible realities,\n"
                f"       but in none of them did '{stmt.observe_var}' have a value.\n"
                f"       All timelines ended in void.\n"
                f"       (Reality cannot collapse. Too many contradictions.)",
                error_type="TEMPORAL PARADOX",
                bells=5
            )

    def evaluate(self, expr):
        """Evaluate expression and return its value.

        Dispatches to appropriate evaluator based on expression type.

        Args:
            expr: AST node representing the expression

        Returns:
            The evaluated value
        """
        if isinstance(expr, NumberLiteral):
            return expr.value

        elif isinstance(expr, StringLiteral):
            return expr.value

        elif isinstance(expr, BoolLiteral):
            if expr.value == 'yes':
                return True
            elif expr.value == 'no':
                return False
            elif expr.value == 'perhaps':
                return 'perhaps'  # Quantum state

        elif isinstance(expr, VoidLiteral):
            return None

        elif isinstance(expr, Identifier):
            return self.get_var(expr.name)

        elif isinstance(expr, BinaryOp):
            return self.evaluate_binary_op(expr)

        elif isinstance(expr, UnaryOp):
            return self.evaluate_unary_op(expr)

        elif isinstance(expr, FunctionCall):
            return self.evaluate_function_call(expr)

        elif isinstance(expr, TemporalAccess):
            return self.evaluate_temporal_access(expr)

        elif isinstance(expr, ListLiteral):
            return [self.evaluate(elem) for elem in expr.elements]

        elif isinstance(expr, DictLiteral):
            return {self.evaluate(k): self.evaluate(v) for k, v in expr.pairs}

        elif isinstance(expr, IndexAccess):
            obj = self.evaluate(expr.object)
            index = self.evaluate(expr.index)
            try:
                return obj[index]
            except (KeyError, IndexError, TypeError):
                self.error(
                    f"Invalid index access",
                    f"I tried to find something at that location,\n"
                    f"       but there was only absence.\n"
                    f"       (Index out of range or invalid type.)"
                )

        else:
            self.error(
                f"Unknown expression type: {type(expr).__name__}",
                f"The interpreter doesn't know how to evaluate this.\n"
                f"       (Reality is fracturing.)"
            )

    def evaluate_binary_op(self, expr):
        """Evaluate binary operation.

        Handles arithmetic, comparison, logical, and type-checking operators.

        Args:
            expr: BinaryOp AST node

        Returns:
            Result of the operation
        """
        left = self.evaluate(expr.left)
        right = self.evaluate(expr.right)
        op = expr.op

        # Arithmetic
        if op == '+':
            return left + right
        elif op == '-':
            return left - right
        elif op == '*':
            return left * right
        elif op == '/':
            if right == 0:
                self.error(
                    "Division by zero",
                    f"You tried to divide by zero,\n"
                    f"       to split the void itself—\n"
                    f"       but infinity refuses to answer."
                )
            return left / right
        elif op == '%':
            return left % right

        # Comparison
        elif op == '==':
            return left == right
        elif op == '!=':
            return left != right
        elif op == '<':
            return left < right
        elif op == '>':
            return left > right
        elif op == '<=':
            return left <= right
        elif op == '>=':
            return left >= right

        # Logical
        elif op == 'and':
            return self.is_truthy(left) and self.is_truthy(right)
        elif op == 'or':
            return self.is_truthy(left) or self.is_truthy(right)

        # Type check
        elif op == 'is':
            if isinstance(right, type(None)):
                return left is None
            return left == right
        elif op == 'is not':
            if isinstance(right, type(None)):
                return left is not None
            return left != right

    def evaluate_unary_op(self, expr):
        """Evaluate unary operation.

        Args:
            expr: UnaryOp AST node

        Returns:
            Result of the operation
        """
        operand = self.evaluate(expr.operand)

        if expr.op == '-':
            return -operand
        elif expr.op == 'not':
            return not self.is_truthy(operand)

    def evaluate_function_call(self, expr):
        """Evaluate function call.

        Handles both built-in and user-defined functions.
        Creates new scope for user functions and manages return values.

        Args:
            expr: FunctionCall AST node

        Returns:
            Return value of the function (or None if no explicit return)
        """
        # Check built-ins first
        if expr.name in self.globals and callable(self.globals[expr.name]):
            func = self.globals[expr.name]
            args = [self.evaluate(arg) for arg in expr.args]
            return func(*args)

        # Check user-defined functions
        if expr.name not in self.functions:
            self.error(
                f"Undefined function: {expr.name}",
                f"I searched for the sigh named '{expr.name}',\n"
                f"       but it was never defined.\n"
                f"       (Perhaps you forgot to declare it with 'sigh'?)"
            )

        func_def = self.functions[expr.name]
        args = [self.evaluate(arg) for arg in expr.args]

        if len(args) != len(func_def.params):
            self.error(
                f"Argument count mismatch",
                f"The sigh '{expr.name}' expects {len(func_def.params)} sorrows,\n"
                f"       but you gave it {len(args)}.\n"
                f"       (Check your function call.)"
            )

        # Create new scope for function
        self.scopes.append({})
        for param, arg in zip(func_def.params, args):
            self.declare_var(param, arg)

        try:
            self.execute(func_def.body)
            result = None  # No explicit return
        except ReturnValue as rv:
            result = rv.value
        finally:
            self.scopes.pop()

        return result

    def evaluate_temporal_access(self, expr):
        """Evaluate temporal operators (@past, @origin, @age, @born).

        These operators allow access to a variable's history:
        - @past(N): Value from N steps ago
        - @origin: Original value
        - @age: Number of assignments
        - @born: Timestamp when created

        Args:
            expr: TemporalAccess AST node

        Returns:
            Historical value or metadata
        """
        # Find the timeline value
        timeline_val = None
        for scope in reversed(self.scopes):
            if expr.var in scope:
                timeline_val = scope[expr.var]
                break

        if timeline_val is None and expr.var in self.globals:
            timeline_val = self.globals[expr.var]

        if timeline_val is None:
            self.error(
                f"Undefined variable: {expr.var}",
                f"I searched for '{expr.var}' in the timelines,\n"
                f"       but it never existed."
            )

        if not isinstance(timeline_val, TimelineValue):
            self.error(
                f"Variable '{expr.var}' is not a timeline",
                f"Temporal operators only work on remembered variables.\n"
                f"       (Internal error: variable not wrapped in TimelineValue.)"
            )

        if expr.operator == 'past':
            offset = expr.offset if expr.offset else 1
            return timeline_val.get_past(offset)
        elif expr.operator == 'origin':
            return timeline_val.get_origin()
        elif expr.operator == 'age':
            return timeline_val.get_age()
        elif expr.operator == 'born':
            return int(timeline_val.born)

    def is_truthy(self, value):
        """Determine truthiness of a value.

        Special handling for:
        - None/void: False
        - 'perhaps': Randomly True or False (quantum collapse)
        - Booleans: Standard behavior
        - Numbers: False if zero
        - Strings: False if empty

        Args:
            value: Value to check

        Returns:
            Boolean truthiness
        """
        if value is None:
            return False
        if value == 'perhaps':
            return random.choice([True, False])  # Quantum collapse
        if isinstance(value, bool):
            return value
        if isinstance(value, (int, float)):
            return value != 0
        if isinstance(value, str):
            return len(value) > 0
        return True

    def value_to_string(self, value):
        """Convert value to string for output.

        Uses emotional names for boolean values (yes/no/perhaps).

        Args:
            value: Value to convert

        Returns:
            String representation
        """
        if value is None:
            return 'void'
        elif value is True:
            return 'yes'
        elif value is False:
            return 'no'
        elif value == 'perhaps':
            return 'perhaps'
        elif isinstance(value, str):
            return value
        elif isinstance(value, list):
            return '[' + ', '.join(self.value_to_string(v) for v in value) + ']'
        elif isinstance(value, dict):
            pairs = [f'"{k}": {self.value_to_string(v)}' for k, v in value.items()]
            return '{' + ', '.join(pairs) + '}'
        else:
            return str(value)
