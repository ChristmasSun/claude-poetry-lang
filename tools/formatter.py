"""
Lament Language Code Formatter
===============================

Automatically formats Lament source code to maintain consistent style.
Ensures emotional consistency while preserving semantic meaning.

Usage:
    python -m tools.formatter <file.lament>
    lament-fmt <file.lament>

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


class FormatterConfig:
    """Configuration for code formatting rules."""

    def __init__(self):
        self.indent_size = 4
        self.indent_char = ' '
        self.max_line_length = 88
        self.spaces_around_operators = True
        self.blank_lines_between_functions = 2
        self.blank_lines_between_statements = 0
        self.align_assignments = False
        self.trailing_comma_in_lists = False
        self.space_after_confess = True
        self.space_after_remember = True
        self.brace_style = 'same_line'  # 'same_line' or 'next_line'


class LamentFormatter:
    """Formats Lament AST into beautiful, consistent code.

    The formatter preserves all semantic meaning while ensuring:
    - Consistent indentation
    - Proper spacing around operators
    - Aligned blocks
    - Readable temporal expressions
    - Emotional consistency

    Example:
        formatter = LamentFormatter()
        formatted_code = formatter.format_ast(ast)
    """

    def __init__(self, config=None):
        """Initialize formatter with optional configuration.

        Args:
            config: FormatterConfig instance or None for defaults
        """
        self.config = config or FormatterConfig()
        self.indent_level = 0
        self.output = []

    def indent(self):
        """Increase indentation level."""
        self.indent_level += 1

    def dedent(self):
        """Decrease indentation level."""
        self.indent_level = max(0, self.indent_level - 1)

    def get_indent(self):
        """Get current indentation string."""
        return self.config.indent_char * (self.indent_level * self.config.indent_size)

    def emit(self, text=''):
        """Add text to output buffer."""
        self.output.append(text)

    def emit_line(self, text=''):
        """Add a complete line with indentation."""
        if text:
            self.emit(self.get_indent() + text + '\n')
        else:
            self.emit('\n')

    def format_ast(self, ast):
        """Format a complete AST into source code.

        Args:
            ast: List of statement AST nodes

        Returns:
            Formatted source code string
        """
        self.output = []
        self.indent_level = 0

        prev_was_function = False
        for i, stmt in enumerate(ast):
            # Add blank lines between functions
            if isinstance(stmt, FunctionDef):
                if prev_was_function or i > 0:
                    for _ in range(self.config.blank_lines_between_functions):
                        self.emit_line()
                prev_was_function = True
            else:
                if prev_was_function and i > 0:
                    self.emit_line()
                prev_was_function = False

            self.format_statement(stmt)

        return ''.join(self.output)

    def format_statement(self, stmt):
        """Format a single statement.

        Args:
            stmt: AST node representing the statement
        """
        if isinstance(stmt, ConfessStmt):
            space = ' ' if self.config.space_after_confess else ''
            self.emit_line(f'confess{space}{self.format_expression(stmt.value)}')

        elif isinstance(stmt, VariableDecl):
            space = ' ' if self.config.space_after_remember else ''
            self.emit_line(f'remember{space}{stmt.name} = {self.format_expression(stmt.value)}')

        elif isinstance(stmt, Assignment):
            op = ' = ' if self.config.spaces_around_operators else '='
            self.emit_line(f'{stmt.name}{op}{self.format_expression(stmt.value)}')

        elif isinstance(stmt, IfStmt):
            self.format_if_statement(stmt)

        elif isinstance(stmt, WhileStmt):
            self.format_while_statement(stmt)

        elif isinstance(stmt, ForStmt):
            self.format_for_statement(stmt)

        elif isinstance(stmt, FunctionDef):
            self.format_function_def(stmt)

        elif isinstance(stmt, ExhaleStmt):
            self.emit_line(f'exhale {self.format_expression(stmt.value)}')

        elif isinstance(stmt, ForkReality):
            self.format_fork_reality(stmt)

        elif isinstance(stmt, FunctionCall):
            self.emit_line(self.format_expression(stmt))

    def format_if_statement(self, stmt):
        """Format if-else statement."""
        condition = self.format_expression(stmt.condition)

        if self.config.brace_style == 'same_line':
            self.emit_line(f'if {condition} {{')
        else:
            self.emit_line(f'if {condition}')
            self.emit_line('{')

        self.indent()
        for s in stmt.then_block:
            self.format_statement(s)
        self.dedent()

        if stmt.else_block:
            self.emit_line('} else {')
            self.indent()
            for s in stmt.else_block:
                self.format_statement(s)
            self.dedent()

        self.emit_line('}')

    def format_while_statement(self, stmt):
        """Format while loop."""
        condition = self.format_expression(stmt.condition)

        if self.config.brace_style == 'same_line':
            self.emit_line(f'while {condition} {{')
        else:
            self.emit_line(f'while {condition}')
            self.emit_line('{')

        self.indent()
        for s in stmt.body:
            self.format_statement(s)
        self.dedent()
        self.emit_line('}')

    def format_for_statement(self, stmt):
        """Format for loop."""
        iterable = self.format_expression(stmt.iterable)

        if self.config.brace_style == 'same_line':
            self.emit_line(f'for {stmt.var} in {iterable} {{')
        else:
            self.emit_line(f'for {stmt.var} in {iterable}')
            self.emit_line('{')

        self.indent()
        for s in stmt.body:
            self.format_statement(s)
        self.dedent()
        self.emit_line('}')

    def format_function_def(self, stmt):
        """Format function definition."""
        params = ', '.join(stmt.params)

        if self.config.brace_style == 'same_line':
            self.emit_line(f'sigh {stmt.name}({params}) {{')
        else:
            self.emit_line(f'sigh {stmt.name}({params})')
            self.emit_line('{')

        self.indent()
        for s in stmt.body:
            self.format_statement(s)
        self.dedent()
        self.emit_line('}')

    def format_fork_reality(self, stmt):
        """Format reality fork statement."""
        self.emit_line('fork reality {')
        self.indent()

        for condition, body in stmt.branches:
            condition_str = self.format_expression(condition)
            self.emit_line(f'on {condition_str} {{')
            self.indent()
            for s in body:
                self.format_statement(s)
            self.dedent()
            self.emit_line('}')

        self.dedent()

        if stmt.observe_var:
            self.emit_line(f'}} collapse observe {stmt.observe_var}')
        else:
            self.emit_line('}')

    def format_expression(self, expr):
        """Format an expression into a string.

        Args:
            expr: AST node representing the expression

        Returns:
            Formatted expression string
        """
        if isinstance(expr, NumberLiteral):
            return str(expr.value)

        elif isinstance(expr, StringLiteral):
            # Escape special characters
            escaped = expr.value.replace('\\', '\\\\').replace('"', '\\"')
            escaped = escaped.replace('\n', '\\n').replace('\t', '\\t')
            return f'"{escaped}"'

        elif isinstance(expr, BoolLiteral):
            return expr.value

        elif isinstance(expr, VoidLiteral):
            return 'void'

        elif isinstance(expr, Identifier):
            return expr.name

        elif isinstance(expr, BinaryOp):
            return self.format_binary_op(expr)

        elif isinstance(expr, UnaryOp):
            return self.format_unary_op(expr)

        elif isinstance(expr, FunctionCall):
            return self.format_function_call(expr)

        elif isinstance(expr, TemporalAccess):
            return self.format_temporal_access(expr)

        elif isinstance(expr, ListLiteral):
            return self.format_list_literal(expr)

        elif isinstance(expr, DictLiteral):
            return self.format_dict_literal(expr)

        elif isinstance(expr, IndexAccess):
            obj = self.format_expression(expr.object)
            idx = self.format_expression(expr.index)
            return f'{obj}[{idx}]'

        else:
            return str(expr)

    def format_binary_op(self, expr):
        """Format binary operation with proper spacing."""
        left = self.format_expression(expr.left)
        right = self.format_expression(expr.right)

        if self.config.spaces_around_operators:
            return f'{left} {expr.op} {right}'
        else:
            return f'{left}{expr.op}{right}'

    def format_unary_op(self, expr):
        """Format unary operation."""
        operand = self.format_expression(expr.operand)

        if expr.op == 'not':
            return f'not {operand}'
        else:
            return f'{expr.op}{operand}'

    def format_function_call(self, expr):
        """Format function call."""
        args = ', '.join(self.format_expression(arg) for arg in expr.args)
        return f'{expr.name}({args})'

    def format_temporal_access(self, expr):
        """Format temporal operator."""
        if expr.operator == 'past' and expr.offset:
            return f'{expr.var}@past({expr.offset})'
        else:
            return f'{expr.var}@{expr.operator}'

    def format_list_literal(self, expr):
        """Format list literal."""
        if not expr.elements:
            return '[]'

        elements = [self.format_expression(e) for e in expr.elements]

        # Check if list fits on one line
        one_line = '[' + ', '.join(elements) + ']'
        if len(one_line) <= self.config.max_line_length:
            return one_line

        # Multi-line list
        result = '[\n'
        self.indent()
        for i, elem in enumerate(elements):
            comma = ',' if i < len(elements) - 1 or self.config.trailing_comma_in_lists else ''
            result += f'{self.get_indent()}{elem}{comma}\n'
        self.dedent()
        result += self.get_indent() + ']'
        return result

    def format_dict_literal(self, expr):
        """Format dictionary literal."""
        if not expr.pairs:
            return '{}'

        pairs = [f'{self.format_expression(k)}: {self.format_expression(v)}'
                 for k, v in expr.pairs]

        # Check if dict fits on one line
        one_line = '{' + ', '.join(pairs) + '}'
        if len(one_line) <= self.config.max_line_length:
            return one_line

        # Multi-line dict
        result = '{\n'
        self.indent()
        for i, (k, v) in enumerate(expr.pairs):
            k_str = self.format_expression(k)
            v_str = self.format_expression(v)
            comma = ',' if i < len(expr.pairs) - 1 or self.config.trailing_comma_in_lists else ''
            result += f'{self.get_indent()}{k_str}: {v_str}{comma}\n'
        self.dedent()
        result += self.get_indent() + '}'
        return result


def format_file(filename, config=None):
    """Format a Lament source file.

    Args:
        filename: Path to the .lament file
        config: Optional FormatterConfig

    Returns:
        Formatted source code string
    """
    with open(filename, 'r') as f:
        source = f.read()

    lexer = Lexer(source)
    tokens = lexer.tokenize()

    parser = Parser(tokens)
    ast = parser.parse()

    formatter = LamentFormatter(config)
    return formatter.format_ast(ast)


def main():
    """CLI entry point for lament-fmt command."""
    if len(sys.argv) < 2:
        print("Usage: lament-fmt <file.lament>")
        print("\nFormat a Lament source file to consistent style.")
        print("\nOptions:")
        print("  -i, --in-place    Format file in place")
        print("  -c, --check       Check if file is formatted (exit 1 if not)")
        print("  -o, --output FILE Write formatted code to FILE")
        sys.exit(1)

    filename = sys.argv[-1]
    in_place = '-i' in sys.argv or '--in-place' in sys.argv
    check_only = '-c' in sys.argv or '--check' in sys.argv

    output_file = None
    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        output_file = sys.argv[idx + 1]
    elif '--output' in sys.argv:
        idx = sys.argv.index('--output')
        output_file = sys.argv[idx + 1]

    try:
        formatted = format_file(filename)

        if check_only:
            with open(filename, 'r') as f:
                original = f.read()
            if original.strip() != formatted.strip():
                print(f"File {filename} is not formatted correctly.")
                sys.exit(1)
            else:
                print(f"File {filename} is properly formatted.")
                sys.exit(0)

        elif in_place:
            with open(filename, 'w') as f:
                f.write(formatted)
            print(f"Formatted {filename}")

        elif output_file:
            with open(output_file, 'w') as f:
                f.write(formatted)
            print(f"Formatted {filename} -> {output_file}")

        else:
            print(formatted)

    except Exception as e:
        print(f"Error formatting {filename}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
