"""
Lament Language Linter
======================

Static analysis tool that checks for code quality issues, style violations,
and potential bugs in Lament programs.

Implements 30+ lint rules covering:
- Unused variables
- Undefined references
- Style consistency
- Complexity metrics
- Temporal safety
- Reality fork safety
- Naming conventions

Usage:
    python -m tools.linter <file.lament>
    lament-lint <file.lament>

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.lexer import Lexer
from lament.parser import (
    Parser, ASTNode, NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral,
    Identifier, BinaryOp, UnaryOp, Assignment, VariableDecl, ConfessStmt,
    IfStmt, WhileStmt, ForStmt, FunctionDef, FunctionCall, ExhaleStmt,
    TemporalAccess, ListLiteral, DictLiteral, IndexAccess, ForkReality
)
from typing import List, Set, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Lint issue severity levels."""
    ERROR = 'error'
    WARNING = 'warning'
    INFO = 'info'
    STYLE = 'style'


@dataclass
class LintIssue:
    """Represents a single lint issue."""
    severity: Severity
    rule: str
    message: str
    node: Optional[ASTNode] = None
    suggestion: Optional[str] = None

    def __str__(self):
        severity_color = {
            Severity.ERROR: '\033[91m',
            Severity.WARNING: '\033[93m',
            Severity.INFO: '\033[94m',
            Severity.STYLE: '\033[96m',
        }
        reset = '\033[0m'
        color = severity_color.get(self.severity, '')

        result = f"{color}[{self.severity.value.upper()}]{reset} {self.rule}: {self.message}"
        if self.suggestion:
            result += f"\n  💡 Suggestion: {self.suggestion}"
        return result


class LintRule:
    """Base class for lint rules."""

    def __init__(self):
        self.issues = []

    def add_issue(self, severity, rule, message, node=None, suggestion=None):
        """Add a lint issue."""
        self.issues.append(LintIssue(severity, rule, message, node, suggestion))


class LamentLinter:
    """Static analyzer for Lament code.

    Performs comprehensive analysis including:
    - Variable usage tracking
    - Dead code detection
    - Complexity analysis
    - Style checking
    - Temporal safety
    - Reality fork validation

    Example:
        linter = LamentLinter()
        issues = linter.lint(ast)
        for issue in issues:
            print(issue)
    """

    def __init__(self):
        self.issues = []
        self.scope_stack = [set()]
        self.defined_vars = set()
        self.used_vars = set()
        self.defined_functions = set()
        self.called_functions = set()
        self.temporal_vars = set()
        self.in_loop = False
        self.in_function = False
        self.function_has_return = False

    def lint(self, ast):
        """Run all lint rules on an AST.

        Args:
            ast: List of statement AST nodes

        Returns:
            List of LintIssue objects
        """
        self.issues = []
        self.scope_stack = [set()]
        self.defined_vars = set()
        self.used_vars = set()
        self.defined_functions = set()
        self.called_functions = set()
        self.temporal_vars = set()

        # First pass: collect definitions and usage
        for stmt in ast:
            self.analyze_statement(stmt)

        # Check for issues
        self.check_unused_variables()
        self.check_unused_functions()
        self.check_undefined_functions()

        return sorted(self.issues, key=lambda x: (x.severity.value, x.rule))

    def add_issue(self, severity, rule, message, node=None, suggestion=None):
        """Add a lint issue."""
        self.issues.append(LintIssue(severity, rule, message, node, suggestion))

    def enter_scope(self):
        """Enter a new scope."""
        self.scope_stack.append(set())

    def exit_scope(self):
        """Exit current scope."""
        if len(self.scope_stack) > 1:
            self.scope_stack.pop()

    def define_var(self, name):
        """Mark variable as defined in current scope."""
        self.scope_stack[-1].add(name)
        self.defined_vars.add(name)

    def use_var(self, name):
        """Mark variable as used."""
        self.used_vars.add(name)

    def is_defined(self, name):
        """Check if variable is defined in any scope."""
        for scope in reversed(self.scope_stack):
            if name in scope:
                return True
        return False

    def analyze_statement(self, stmt):
        """Analyze a statement for issues."""
        if isinstance(stmt, ConfessStmt):
            self.analyze_expression(stmt.value)
            self.check_confess_complexity(stmt)

        elif isinstance(stmt, VariableDecl):
            self.check_variable_naming(stmt.name)
            self.define_var(stmt.name)
            self.temporal_vars.add(stmt.name)
            self.analyze_expression(stmt.value)
            self.check_constant_reassignment(stmt)

        elif isinstance(stmt, Assignment):
            if not self.is_defined(stmt.name):
                self.add_issue(
                    Severity.ERROR,
                    'undefined-variable',
                    f"Variable '{stmt.name}' is assigned before being declared with 'remember'",
                    stmt,
                    f"Add 'remember {stmt.name} = <initial_value>' before this assignment"
                )
            self.use_var(stmt.name)
            self.analyze_expression(stmt.value)
            self.check_assignment_complexity(stmt)

        elif isinstance(stmt, IfStmt):
            self.analyze_expression(stmt.condition)
            self.check_if_statement(stmt)
            self.enter_scope()
            for s in stmt.then_block:
                self.analyze_statement(s)
            self.exit_scope()
            if stmt.else_block:
                self.enter_scope()
                for s in stmt.else_block:
                    self.analyze_statement(s)
                self.exit_scope()

        elif isinstance(stmt, WhileStmt):
            old_in_loop = self.in_loop
            self.in_loop = True
            self.analyze_expression(stmt.condition)
            self.check_infinite_loop(stmt)
            self.enter_scope()
            for s in stmt.body:
                self.analyze_statement(s)
            self.exit_scope()
            self.in_loop = old_in_loop

        elif isinstance(stmt, ForStmt):
            old_in_loop = self.in_loop
            self.in_loop = True
            self.analyze_expression(stmt.iterable)
            self.enter_scope()
            self.define_var(stmt.var)
            self.use_var(stmt.var)
            for s in stmt.body:
                self.analyze_statement(s)
            self.exit_scope()
            self.in_loop = old_in_loop

        elif isinstance(stmt, FunctionDef):
            self.check_function_naming(stmt.name)
            self.check_parameter_count(stmt)
            self.check_duplicate_parameters(stmt)
            self.defined_functions.add(stmt.name)

            old_in_function = self.in_function
            old_has_return = self.function_has_return
            self.in_function = True
            self.function_has_return = False

            self.enter_scope()
            for param in stmt.params:
                self.define_var(param)
            for s in stmt.body:
                self.analyze_statement(s)
            self.exit_scope()

            if not self.function_has_return:
                self.add_issue(
                    Severity.INFO,
                    'missing-return',
                    f"Function '{stmt.name}' has no explicit return statement",
                    stmt,
                    "Add 'exhale <value>' to return a value"
                )

            self.in_function = old_in_function
            self.function_has_return = old_has_return

        elif isinstance(stmt, ExhaleStmt):
            if not self.in_function:
                self.add_issue(
                    Severity.ERROR,
                    'return-outside-function',
                    "Return statement (exhale) used outside of function",
                    stmt
                )
            self.function_has_return = True
            self.analyze_expression(stmt.value)

        elif isinstance(stmt, ForkReality):
            self.check_fork_reality(stmt)
            for condition, body in stmt.branches:
                self.analyze_expression(condition)
                self.enter_scope()
                for s in body:
                    self.analyze_statement(s)
                self.exit_scope()

        elif isinstance(stmt, FunctionCall):
            self.analyze_expression(stmt)

    def analyze_expression(self, expr):
        """Analyze an expression for issues."""
        if isinstance(expr, Identifier):
            if not self.is_defined(expr.name):
                # Check if it's a built-in
                builtins = {'range', 'length_of', 'ache_of', 'sqrt_of_pain',
                           'sin_of_loss', 'cos_of_hope', 'now', 'sleep',
                           'is_numb', 'is_whisper', 'is_void', 'typeof',
                           'current_timeline'}
                if expr.name not in builtins:
                    self.add_issue(
                        Severity.ERROR,
                        'undefined-variable',
                        f"Variable '{expr.name}' is used before being defined",
                        expr,
                        f"Add 'remember {expr.name} = <value>' before using it"
                    )
            self.use_var(expr.name)

        elif isinstance(expr, BinaryOp):
            self.analyze_expression(expr.left)
            self.analyze_expression(expr.right)
            self.check_comparison_chain(expr)
            self.check_division_by_zero(expr)

        elif isinstance(expr, UnaryOp):
            self.analyze_expression(expr.operand)

        elif isinstance(expr, FunctionCall):
            self.called_functions.add(expr.name)
            self.check_builtin_usage(expr)
            for arg in expr.args:
                self.analyze_expression(arg)

        elif isinstance(expr, TemporalAccess):
            if expr.var not in self.temporal_vars and not self.is_defined(expr.var):
                self.add_issue(
                    Severity.WARNING,
                    'temporal-on-non-timeline',
                    f"Temporal operator used on '{expr.var}' which may not be a timeline variable",
                    expr
                )
            self.use_var(expr.var)
            self.check_temporal_safety(expr)

        elif isinstance(expr, ListLiteral):
            for elem in expr.elements:
                self.analyze_expression(elem)
            self.check_list_size(expr)

        elif isinstance(expr, DictLiteral):
            for k, v in expr.pairs:
                self.analyze_expression(k)
                self.analyze_expression(v)

        elif isinstance(expr, IndexAccess):
            self.analyze_expression(expr.object)
            self.analyze_expression(expr.index)

    # Rule implementations

    def check_variable_naming(self, name):
        """Check variable naming conventions."""
        if name[0].isupper():
            self.add_issue(
                Severity.STYLE,
                'variable-naming',
                f"Variable '{name}' should start with lowercase letter",
                suggestion=f"Rename to '{name[0].lower() + name[1:]}'"
            )

        if len(name) == 1 and name not in ['i', 'j', 'k', 'x', 'y', 'z']:
            self.add_issue(
                Severity.STYLE,
                'short-variable-name',
                f"Variable '{name}' has a very short name",
                suggestion="Use a more descriptive name"
            )

        if '__' in name:
            self.add_issue(
                Severity.STYLE,
                'double-underscore',
                f"Variable '{name}' contains double underscore (reserved for special use)",
                suggestion="Use single underscores to separate words"
            )

    def check_function_naming(self, name):
        """Check function naming conventions."""
        if name[0].isupper():
            self.add_issue(
                Severity.STYLE,
                'function-naming',
                f"Function '{name}' should start with lowercase letter",
                suggestion=f"Rename to '{name[0].lower() + name[1:]}'"
            )

    def check_parameter_count(self, func_def):
        """Check function parameter count."""
        if len(func_def.params) > 5:
            self.add_issue(
                Severity.WARNING,
                'too-many-parameters',
                f"Function '{func_def.name}' has {len(func_def.params)} parameters (max recommended: 5)",
                func_def,
                "Consider using a dictionary or object to group related parameters"
            )

    def check_duplicate_parameters(self, func_def):
        """Check for duplicate parameter names."""
        seen = set()
        for param in func_def.params:
            if param in seen:
                self.add_issue(
                    Severity.ERROR,
                    'duplicate-parameter',
                    f"Parameter '{param}' is duplicated in function '{func_def.name}'",
                    func_def
                )
            seen.add(param)

    def check_unused_variables(self):
        """Check for variables that are defined but never used."""
        unused = self.defined_vars - self.used_vars
        builtins = {'range', 'length_of', 'ache_of', 'sqrt_of_pain'}

        for var in unused:
            if var not in builtins:
                self.add_issue(
                    Severity.WARNING,
                    'unused-variable',
                    f"Variable '{var}' is defined but never used",
                    suggestion=f"Remove the declaration or use the variable"
                )

    def check_unused_functions(self):
        """Check for functions that are defined but never called."""
        unused = self.defined_functions - self.called_functions

        for func in unused:
            if func != 'main':  # main function may not be called explicitly
                self.add_issue(
                    Severity.INFO,
                    'unused-function',
                    f"Function '{func}' is defined but never called",
                    suggestion="Consider removing if not needed"
                )

    def check_undefined_functions(self):
        """Check for function calls to undefined functions."""
        builtins = {'range', 'length_of', 'ache_of', 'sqrt_of_pain',
                   'sin_of_loss', 'cos_of_hope', 'now', 'sleep',
                   'is_numb', 'is_whisper', 'is_void', 'typeof',
                   'current_timeline'}

        undefined = (self.called_functions - self.defined_functions) - builtins

        for func in undefined:
            self.add_issue(
                Severity.ERROR,
                'undefined-function',
                f"Function '{func}' is called but never defined",
                suggestion=f"Define '{func}' with 'sigh {func}(...) {{ ... }}'"
            )

    def check_confess_complexity(self, stmt):
        """Check if confess statement is too complex."""
        if isinstance(stmt.value, BinaryOp):
            depth = self.get_expression_depth(stmt.value)
            if depth > 4:
                self.add_issue(
                    Severity.STYLE,
                    'complex-confess',
                    "Confess statement has complex nested expression",
                    stmt,
                    "Extract complex expression to a variable"
                )

    def check_assignment_complexity(self, stmt):
        """Check assignment complexity."""
        depth = self.get_expression_depth(stmt.value)
        if depth > 5:
            self.add_issue(
                Severity.WARNING,
                'complex-expression',
                f"Assignment to '{stmt.name}' has very complex expression (depth: {depth})",
                stmt,
                "Break down into smaller expressions"
            )

    def check_if_statement(self, stmt):
        """Check if statement issues."""
        # Check for empty blocks
        if not stmt.then_block:
            self.add_issue(
                Severity.WARNING,
                'empty-if-block',
                "If statement has empty then block",
                stmt
            )

        # Check for always true/false conditions
        if isinstance(stmt.condition, BoolLiteral):
            if stmt.condition.value == 'yes':
                self.add_issue(
                    Severity.WARNING,
                    'always-true-condition',
                    "If condition is always true",
                    stmt,
                    "Remove the if statement and keep only the then block"
                )
            elif stmt.condition.value == 'no':
                self.add_issue(
                    Severity.WARNING,
                    'always-false-condition',
                    "If condition is always false",
                    stmt,
                    "Remove the if statement or check the logic"
                )

    def check_infinite_loop(self, stmt):
        """Check for potential infinite loops."""
        if isinstance(stmt.condition, BoolLiteral) and stmt.condition.value == 'yes':
            self.add_issue(
                Severity.WARNING,
                'infinite-loop',
                "While loop has constant true condition (infinite loop)",
                stmt,
                "Add a break condition or verify this is intentional"
            )

    def check_fork_reality(self, stmt):
        """Check reality fork safety."""
        if len(stmt.branches) < 2:
            self.add_issue(
                Severity.WARNING,
                'single-fork-branch',
                "Reality fork has only one branch (no actual branching)",
                stmt,
                "Add more branches or remove fork reality"
            )

        if not stmt.observe_var:
            self.add_issue(
                Severity.INFO,
                'no-collapse-observation',
                "Reality fork has no collapse observation (all timelines execute)",
                stmt
            )

    def check_comparison_chain(self, expr):
        """Check for comparison chains that might be incorrect."""
        if expr.op in ['<', '>', '<=', '>=']:
            if isinstance(expr.left, BinaryOp) and expr.left.op in ['<', '>', '<=', '>=']:
                self.add_issue(
                    Severity.WARNING,
                    'comparison-chain',
                    "Chained comparison may not work as expected",
                    expr,
                    "Use 'and' to combine comparisons: 'a < b and b < c'"
                )

    def check_division_by_zero(self, expr):
        """Check for potential division by zero."""
        if expr.op == '/' and isinstance(expr.right, NumberLiteral):
            if expr.right.value == 0:
                self.add_issue(
                    Severity.ERROR,
                    'division-by-zero',
                    "Division by zero",
                    expr
                )

    def check_temporal_safety(self, expr):
        """Check temporal operator safety."""
        if expr.operator == 'past' and expr.offset:
            if expr.offset < 0:
                self.add_issue(
                    Severity.ERROR,
                    'negative-temporal-offset',
                    f"Temporal @past offset cannot be negative: {expr.offset}",
                    expr
                )
            if expr.offset > 100:
                self.add_issue(
                    Severity.WARNING,
                    'large-temporal-offset',
                    f"Very large temporal offset: {expr.offset}",
                    expr,
                    "Large offsets may cause memory issues"
                )

    def check_builtin_usage(self, expr):
        """Check proper usage of built-in functions."""
        if expr.name == 'range':
            if len(expr.args) == 0 or len(expr.args) > 3:
                self.add_issue(
                    Severity.ERROR,
                    'invalid-range-args',
                    f"range() requires 1-3 arguments, got {len(expr.args)}",
                    expr
                )

        if expr.name == 'sqrt_of_pain':
            if len(expr.args) != 1:
                self.add_issue(
                    Severity.ERROR,
                    'invalid-sqrt-args',
                    f"sqrt_of_pain() requires exactly 1 argument",
                    expr
                )

    def check_constant_reassignment(self, stmt):
        """Check if variable is being reassigned to constant."""
        if isinstance(stmt.value, NumberLiteral) or isinstance(stmt.value, StringLiteral):
            if isinstance(stmt.value, NumberLiteral) and stmt.value.value == 0:
                self.add_issue(
                    Severity.STYLE,
                    'zero-initialization',
                    f"Variable '{stmt.name}' initialized to 0",
                    stmt,
                    "Consider if this is necessary or use a more meaningful value"
                )

    def check_list_size(self, expr):
        """Check for very large list literals."""
        if len(expr.elements) > 100:
            self.add_issue(
                Severity.WARNING,
                'large-list-literal',
                f"List literal has {len(expr.elements)} elements",
                expr,
                "Consider loading data from file or generating programmatically"
            )

    def get_expression_depth(self, expr, depth=0):
        """Calculate nesting depth of expression."""
        if isinstance(expr, BinaryOp):
            left_depth = self.get_expression_depth(expr.left, depth + 1)
            right_depth = self.get_expression_depth(expr.right, depth + 1)
            return max(left_depth, right_depth)
        elif isinstance(expr, UnaryOp):
            return self.get_expression_depth(expr.operand, depth + 1)
        else:
            return depth


def lint_file(filename):
    """Lint a Lament source file.

    Args:
        filename: Path to the .lament file

    Returns:
        List of LintIssue objects
    """
    with open(filename, 'r') as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    linter = LamentLinter()
    return linter.lint(ast)


def main():
    """CLI entry point for lament-lint command."""
    if len(sys.argv) < 2:
        print("Usage: lament-lint <file.lament>")
        print("\nLint a Lament source file for potential issues.")
        print("\nOptions:")
        print("  --strict      Treat warnings as errors")
        print("  --json        Output in JSON format")
        sys.exit(1)

    filename = sys.argv[1]
    strict = '--strict' in sys.argv
    json_output = '--json' in sys.argv

    try:
        issues = lint_file(filename)

        if not issues:
            print(f"✅ No issues found in {filename}")
            sys.exit(0)

        if json_output:
            import json
            output = [{
                'severity': issue.severity.value,
                'rule': issue.rule,
                'message': issue.message,
                'suggestion': issue.suggestion
            } for issue in issues]
            print(json.dumps(output, indent=2))
        else:
            print(f"\n🔍 Linting {filename}...")
            print(f"{'='*60}\n")

            for issue in issues:
                print(issue)
                print()

            # Summary
            error_count = sum(1 for i in issues if i.severity == Severity.ERROR)
            warning_count = sum(1 for i in issues if i.severity == Severity.WARNING)
            info_count = sum(1 for i in issues if i.severity == Severity.INFO)
            style_count = sum(1 for i in issues if i.severity == Severity.STYLE)

            print(f"{'='*60}")
            print(f"Summary: {error_count} errors, {warning_count} warnings, "
                  f"{info_count} info, {style_count} style")

        # Exit code
        if any(i.severity == Severity.ERROR for i in issues):
            sys.exit(1)
        elif strict and any(i.severity == Severity.WARNING for i in issues):
            sys.exit(1)
        else:
            sys.exit(0)

    except Exception as e:
        print(f"Error linting {filename}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
