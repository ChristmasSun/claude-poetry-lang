#!/usr/bin/env python3
"""
Lament Language Interpreter
Version 0.5: THE VERSIONED REALITY SYSTEM

A programming language that feels alive.
Every program is a confession. Every variable is a timeline. Every execution is a multiverse.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import time
import re
import math
import random
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Union
from datetime import datetime


# ============================================================================
# ANSI COLOR CODES (For synesthetic errors)
# ============================================================================

class Color:
    RESET = '\033[0m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'


def bell(count=1):
    """Terminal bell - auditory error feedback"""
    return '\a' * count


# ============================================================================
# TYPE SYSTEM (Emotional Primitives)
# ============================================================================

class LamentType(Enum):
    NUMB = auto()      # integers
    WHISPER = auto()   # strings
    MAYBE = auto()     # booleans/quantum
    VOID = auto()      # null
    ACHE = auto()      # floats
    SIGH = auto()      # functions
    LIST = auto()      # collections
    DICT = auto()      # mappings


@dataclass
class TimelineValue:
    """A value that remembers its history"""
    current: Any
    history: List[Any] = field(default_factory=list)
    born: float = field(default_factory=time.time)

    def assign(self, value):
        """Assign new value, remembering the old"""
        self.history.append(self.current)
        self.current = value

    def get_past(self, steps=1):
        """Retrieve value from N steps ago"""
        if steps <= 0:
            return self.current
        idx = len(self.history) - steps
        if idx < 0:
            return self.history[0] if self.history else self.current
        return self.history[idx]

    def get_origin(self):
        """First value ever assigned"""
        return self.history[0] if self.history else self.current

    def get_age(self):
        """Number of assignments"""
        return len(self.history) + 1


# ============================================================================
# LEXER (Tokenization)
# ============================================================================

class TokenType(Enum):
    # Literals
    NUMBER = auto()
    STRING = auto()

    # Keywords (emotional)
    CONFESS = auto()
    REMEMBER = auto()
    FORGET = auto()
    SIGH = auto()
    EXHALE = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    FORK = auto()
    REALITY = auto()
    ON = auto()
    COLLAPSE = auto()
    OBSERVE = auto()
    TIMELINE = auto()

    # Literals/constants
    VOID = auto()
    YES = auto()
    NO = auto()
    PERHAPS = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    MODULO = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS = auto()
    GREATER = auto()
    LESS_EQ = auto()
    GREATER_EQ = auto()
    IS = auto()
    NOT = auto()
    AND = auto()
    OR = auto()

    # Temporal operators
    AT_PAST = auto()
    AT_ORIGIN = auto()
    AT_AGE = auto()
    AT_BORN = auto()

    # Delimiters
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()

    # Special
    IDENTIFIER = auto()
    NEWLINE = auto()
    EOF = auto()


@dataclass
class Token:
    type: TokenType
    value: Any
    line: int


class Lexer:
    """Tokenize Lament source code"""

    KEYWORDS = {
        'confess': TokenType.CONFESS,
        'remember': TokenType.REMEMBER,
        'forget': TokenType.FORGET,
        'sigh': TokenType.SIGH,
        'exhale': TokenType.EXHALE,
        'if': TokenType.IF,
        'else': TokenType.ELSE,
        'while': TokenType.WHILE,
        'for': TokenType.FOR,
        'in': TokenType.IN,
        'fork': TokenType.FORK,
        'reality': TokenType.REALITY,
        'on': TokenType.ON,
        'collapse': TokenType.COLLAPSE,
        'observe': TokenType.OBSERVE,
        'timeline': TokenType.TIMELINE,
        'void': TokenType.VOID,
        'yes': TokenType.YES,
        'no': TokenType.NO,
        'perhaps': TokenType.PERHAPS,
        'is': TokenType.IS,
        'not': TokenType.NOT,
        'and': TokenType.AND,
        'or': TokenType.OR,
    }

    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens = []

    def error(self, msg):
        raise SyntaxError(f"Line {self.line}: {msg}")

    def peek(self, offset=0):
        pos = self.pos + offset
        return self.source[pos] if pos < len(self.source) else '\0'

    def advance(self):
        ch = self.peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def skip_whitespace(self):
        while self.peek() in ' \t\r':
            self.advance()

    def skip_comment(self):
        if self.peek() == '#':
            while self.peek() not in '\n\0':
                self.advance()
        elif self.peek() == '/' and self.peek(1) == '*':
            self.advance()
            self.advance()
            while True:
                if self.peek() == '\0':
                    self.error("Unterminated multi-line comment")
                if self.peek() == '*' and self.peek(1) == '/':
                    self.advance()
                    self.advance()
                    break
                self.advance()

    def read_string(self):
        """Read string literal"""
        self.advance()  # opening quote
        chars = []
        while self.peek() not in '"\0':
            if self.peek() == '\\':
                self.advance()
                escape = self.advance()
                if escape == 'n':
                    chars.append('\n')
                elif escape == 't':
                    chars.append('\t')
                elif escape == '"':
                    chars.append('"')
                elif escape == '\\':
                    chars.append('\\')
                else:
                    chars.append(escape)
            else:
                chars.append(self.advance())

        if self.peek() == '\0':
            self.error("Unterminated string literal")

        self.advance()  # closing quote
        return ''.join(chars)

    def read_number(self):
        """Read numeric literal"""
        chars = []
        has_dot = False

        while self.peek().isdigit() or self.peek() == '.':
            if self.peek() == '.':
                if has_dot:
                    break
                has_dot = True
            chars.append(self.advance())

        num_str = ''.join(chars)
        return float(num_str) if has_dot else int(num_str)

    def read_identifier(self):
        """Read identifier or keyword"""
        chars = []
        while self.peek().isalnum() or self.peek() == '_':
            chars.append(self.advance())
        return ''.join(chars)

    def tokenize(self):
        """Convert source to token stream"""
        while self.pos < len(self.source):
            self.skip_whitespace()

            if self.peek() == '\0':
                break

            # Comments
            if self.peek() == '#' or (self.peek() == '/' and self.peek(1) == '*'):
                self.skip_comment()
                continue

            # Newlines
            if self.peek() == '\n':
                self.advance()
                # Ignore newlines for now (statement separators)
                continue

            # Strings
            if self.peek() == '"':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, self.line))
                continue

            # Numbers
            if self.peek().isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, self.line))
                continue

            # Identifiers and keywords
            if self.peek().isalpha() or self.peek() == '_':
                ident = self.read_identifier()
                token_type = self.KEYWORDS.get(ident, TokenType.IDENTIFIER)
                self.tokens.append(Token(token_type, ident, self.line))
                continue

            # Temporal operators
            if self.peek() == '@':
                self.advance()
                temporal = self.read_identifier()
                if temporal == 'past':
                    self.tokens.append(Token(TokenType.AT_PAST, None, self.line))
                elif temporal == 'origin':
                    self.tokens.append(Token(TokenType.AT_ORIGIN, None, self.line))
                elif temporal == 'age':
                    self.tokens.append(Token(TokenType.AT_AGE, None, self.line))
                elif temporal == 'born':
                    self.tokens.append(Token(TokenType.AT_BORN, None, self.line))
                else:
                    self.error(f"Unknown temporal operator: @{temporal}")
                continue

            # Two-character operators
            if self.peek() == '=' and self.peek(1) == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.EQUAL, None, self.line))
                continue

            if self.peek() == '!' and self.peek(1) == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.NOT_EQUAL, None, self.line))
                continue

            if self.peek() == '<' and self.peek(1) == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.LESS_EQ, None, self.line))
                continue

            if self.peek() == '>' and self.peek(1) == '=':
                self.advance()
                self.advance()
                self.tokens.append(Token(TokenType.GREATER_EQ, None, self.line))
                continue

            # Single-character tokens
            single_chars = {
                '+': TokenType.PLUS,
                '-': TokenType.MINUS,
                '*': TokenType.MULTIPLY,
                '/': TokenType.DIVIDE,
                '%': TokenType.MODULO,
                '=': TokenType.ASSIGN,
                '<': TokenType.LESS,
                '>': TokenType.GREATER,
                '(': TokenType.LPAREN,
                ')': TokenType.RPAREN,
                '{': TokenType.LBRACE,
                '}': TokenType.RBRACE,
                '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET,
                ',': TokenType.COMMA,
                '.': TokenType.DOT,
                ':': TokenType.COLON,
            }

            ch = self.peek()
            if ch in single_chars:
                self.advance()
                self.tokens.append(Token(single_chars[ch], None, self.line))
                continue

            self.error(f"Unexpected character: {ch}")

        self.tokens.append(Token(TokenType.EOF, None, self.line))
        return self.tokens


# ============================================================================
# AST (Abstract Syntax Tree)
# ============================================================================

@dataclass
class ASTNode:
    pass


@dataclass
class NumberLiteral(ASTNode):
    value: Union[int, float]


@dataclass
class StringLiteral(ASTNode):
    value: str


@dataclass
class BoolLiteral(ASTNode):
    value: str  # 'yes', 'no', 'perhaps'


@dataclass
class VoidLiteral(ASTNode):
    pass


@dataclass
class Identifier(ASTNode):
    name: str


@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode


@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode


@dataclass
class VariableDecl(ASTNode):
    name: str
    value: ASTNode


@dataclass
class ConfessStmt(ASTNode):
    value: ASTNode


@dataclass
class IfStmt(ASTNode):
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None


@dataclass
class WhileStmt(ASTNode):
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class ForStmt(ASTNode):
    var: str
    iterable: ASTNode
    body: List[ASTNode]


@dataclass
class FunctionDef(ASTNode):
    name: str
    params: List[str]
    body: List[ASTNode]


@dataclass
class FunctionCall(ASTNode):
    name: str
    args: List[ASTNode]


@dataclass
class ExhaleStmt(ASTNode):
    value: ASTNode


@dataclass
class TemporalAccess(ASTNode):
    var: str
    operator: str  # 'past', 'origin', 'age', 'born'
    offset: Optional[int] = None


@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]


@dataclass
class DictLiteral(ASTNode):
    pairs: List[tuple]  # [(key, value), ...]


@dataclass
class IndexAccess(ASTNode):
    object: ASTNode
    index: ASTNode


@dataclass
class ForkReality(ASTNode):
    branches: List[tuple]  # [(condition, body), ...]
    observe_var: Optional[str] = None


# ============================================================================
# PARSER
# ============================================================================

class Parser:
    """Parse tokens into AST"""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def error(self, msg):
        token = self.peek()
        raise SyntaxError(f"Line {token.line}: {msg}")

    def peek(self, offset=0):
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]

    def advance(self):
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, token_type):
        token = self.advance()
        if token.type != token_type:
            self.error(f"Expected {token_type.name}, got {token.type.name}")
        return token

    def parse(self):
        """Parse entire program"""
        statements = []
        while self.peek().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    def parse_statement(self):
        """Parse single statement"""
        token = self.peek()

        if token.type == TokenType.CONFESS:
            return self.parse_confess()
        elif token.type == TokenType.REMEMBER:
            return self.parse_variable_decl()
        elif token.type == TokenType.IF:
            return self.parse_if()
        elif token.type == TokenType.WHILE:
            return self.parse_while()
        elif token.type == TokenType.FOR:
            return self.parse_for()
        elif token.type == TokenType.SIGH:
            return self.parse_function_def()
        elif token.type == TokenType.EXHALE:
            return self.parse_exhale()
        elif token.type == TokenType.FORK:
            return self.parse_fork_reality()
        elif token.type == TokenType.IDENTIFIER:
            # Could be assignment or function call
            if self.peek(1).type == TokenType.ASSIGN:
                return self.parse_assignment()
            elif self.peek(1).type == TokenType.LPAREN:
                return self.parse_expression()  # function call as statement
            else:
                self.error("Unexpected identifier")
        else:
            self.error(f"Unexpected token: {token.type.name}")

    def parse_confess(self):
        self.expect(TokenType.CONFESS)
        value = self.parse_expression()
        return ConfessStmt(value)

    def parse_variable_decl(self):
        self.expect(TokenType.REMEMBER)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return VariableDecl(name, value)

    def parse_assignment(self):
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return Assignment(name, value)

    def parse_if(self):
        self.expect(TokenType.IF)
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        then_block = []
        while self.peek().type != TokenType.RBRACE:
            then_block.append(self.parse_statement())
        self.expect(TokenType.RBRACE)

        else_block = None
        if self.peek().type == TokenType.ELSE:
            self.advance()
            self.expect(TokenType.LBRACE)
            else_block = []
            while self.peek().type != TokenType.RBRACE:
                else_block.append(self.parse_statement())
            self.expect(TokenType.RBRACE)

        return IfStmt(condition, then_block, else_block)

    def parse_while(self):
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        body = []
        while self.peek().type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return WhileStmt(condition, body)

    def parse_for(self):
        self.expect(TokenType.FOR)
        var = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.IN)
        iterable = self.parse_expression()
        self.expect(TokenType.LBRACE)
        body = []
        while self.peek().type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return ForStmt(var, iterable, body)

    def parse_function_def(self):
        self.expect(TokenType.SIGH)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        params = []
        while self.peek().type != TokenType.RPAREN:
            params.append(self.expect(TokenType.IDENTIFIER).value)
            if self.peek().type == TokenType.COMMA:
                self.advance()
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.LBRACE)
        body = []
        while self.peek().type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return FunctionDef(name, params, body)

    def parse_exhale(self):
        self.expect(TokenType.EXHALE)
        value = self.parse_expression()
        return ExhaleStmt(value)

    def parse_fork_reality(self):
        self.expect(TokenType.FORK)
        self.expect(TokenType.REALITY)
        self.expect(TokenType.LBRACE)

        branches = []
        while self.peek().type == TokenType.ON:
            self.advance()
            condition = self.parse_expression()
            self.expect(TokenType.LBRACE)
            body = []
            while self.peek().type != TokenType.RBRACE:
                body.append(self.parse_statement())
            self.expect(TokenType.RBRACE)
            branches.append((condition, body))

        self.expect(TokenType.RBRACE)

        observe_var = None
        if self.peek().type == TokenType.COLLAPSE:
            self.advance()
            self.expect(TokenType.OBSERVE)
            observe_var = self.expect(TokenType.IDENTIFIER).value

        return ForkReality(branches, observe_var)

    def parse_expression(self):
        return self.parse_or()

    def parse_or(self):
        left = self.parse_and()
        while self.peek().type == TokenType.OR:
            self.advance()
            right = self.parse_and()
            left = BinaryOp(left, 'or', right)
        return left

    def parse_and(self):
        left = self.parse_comparison()
        while self.peek().type == TokenType.AND:
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, 'and', right)
        return left

    def parse_comparison(self):
        left = self.parse_is_check()

        comp_ops = {
            TokenType.EQUAL: '==',
            TokenType.NOT_EQUAL: '!=',
            TokenType.LESS: '<',
            TokenType.GREATER: '>',
            TokenType.LESS_EQ: '<=',
            TokenType.GREATER_EQ: '>=',
        }

        if self.peek().type in comp_ops:
            op_token = self.advance()
            right = self.parse_is_check()
            return BinaryOp(left, comp_ops[op_token.type], right)

        return left

    def parse_is_check(self):
        left = self.parse_addition()

        if self.peek().type == TokenType.IS:
            self.advance()
            negated = False
            if self.peek().type == TokenType.NOT:
                self.advance()
                negated = True
            right = self.parse_addition()
            op = 'is not' if negated else 'is'
            return BinaryOp(left, op, right)

        return left

    def parse_addition(self):
        left = self.parse_multiplication()

        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = '+' if self.peek().type == TokenType.PLUS else '-'
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOp(left, op, right)

        return left

    def parse_multiplication(self):
        left = self.parse_unary()

        while self.peek().type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_map = {TokenType.MULTIPLY: '*', TokenType.DIVIDE: '/', TokenType.MODULO: '%'}
            op = op_map[self.peek().type]
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op, right)

        return left

    def parse_unary(self):
        if self.peek().type == TokenType.NOT:
            self.advance()
            return UnaryOp('not', self.parse_unary())
        elif self.peek().type == TokenType.MINUS:
            self.advance()
            return UnaryOp('-', self.parse_unary())

        return self.parse_postfix()

    def parse_postfix(self):
        left = self.parse_primary()

        while True:
            # Function call
            if self.peek().type == TokenType.LPAREN:
                self.advance()
                args = []
                while self.peek().type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    if self.peek().type == TokenType.COMMA:
                        self.advance()
                self.expect(TokenType.RPAREN)
                if isinstance(left, Identifier):
                    left = FunctionCall(left.name, args)
                else:
                    self.error("Can only call identifiers")

            # Index access
            elif self.peek().type == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                left = IndexAccess(left, index)

            # Temporal access
            elif self.peek().type in (TokenType.AT_PAST, TokenType.AT_ORIGIN, TokenType.AT_AGE, TokenType.AT_BORN):
                if not isinstance(left, Identifier):
                    self.error("Temporal operators can only be applied to variables")

                op_token = self.advance()
                op_map = {
                    TokenType.AT_PAST: 'past',
                    TokenType.AT_ORIGIN: 'origin',
                    TokenType.AT_AGE: 'age',
                    TokenType.AT_BORN: 'born',
                }
                op = op_map[op_token.type]

                offset = None
                if op == 'past' and self.peek().type == TokenType.LPAREN:
                    self.advance()
                    offset_expr = self.parse_expression()
                    if not isinstance(offset_expr, NumberLiteral):
                        self.error("Temporal offset must be a number")
                    offset = int(offset_expr.value)
                    self.expect(TokenType.RPAREN)

                left = TemporalAccess(left.name, op, offset)

            else:
                break

        return left

    def parse_primary(self):
        token = self.peek()

        # Numbers
        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberLiteral(token.value)

        # Strings
        if token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token.value)

        # Booleans
        if token.type in (TokenType.YES, TokenType.NO, TokenType.PERHAPS):
            self.advance()
            return BoolLiteral(token.type.name.lower())

        # Void
        if token.type == TokenType.VOID:
            self.advance()
            return VoidLiteral()

        # Identifier
        if token.type == TokenType.IDENTIFIER:
            self.advance()
            return Identifier(token.value)

        # Parenthesized expression
        if token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        # List literal
        if token.type == TokenType.LBRACKET:
            self.advance()
            elements = []
            while self.peek().type != TokenType.RBRACKET:
                elements.append(self.parse_expression())
                if self.peek().type == TokenType.COMMA:
                    self.advance()
            self.expect(TokenType.RBRACKET)
            return ListLiteral(elements)

        # Dict literal
        if token.type == TokenType.LBRACE:
            # Check if it's a dict (has ':') or just a block
            # For simplicity, we'll require explicit dict syntax
            self.error("Unexpected '{'")

        self.error(f"Unexpected token: {token.type.name}")


# ============================================================================
# INTERPRETER (Runtime)
# ============================================================================

class ReturnValue(Exception):
    """Exception for function returns"""
    def __init__(self, value):
        self.value = value


class LamentInterpreter:
    """The heart of Lament. It listens. It remembers. It branches reality."""

    def __init__(self):
        self.globals = {}  # Global scope (timeline variables)
        self.scopes = [{}]  # Scope stack
        self.functions = {}  # Defined functions
        self.in_reality_fork = False
        self.current_timeline = "prime"

        # Register built-in functions
        self.register_builtins()

    def register_builtins(self):
        """Register standard library functions"""
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
        """Get emotional type name"""
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
        """Synesthetic error messages"""
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}💔 LAMENT ERROR: {error_type} 💔{Color.RESET}", file=sys.stderr)
        print(f"{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(f"{Color.CYAN}{poetic_message}{Color.RESET}", file=sys.stderr)
        print(f"\n{Color.YELLOW}({message}){Color.RESET}", file=sys.stderr)
        print(f"\n{Color.RED}{Color.BOLD}{'='*60}{Color.RESET}\n", file=sys.stderr)
        print(bell(bells), end='', file=sys.stderr)
        sys.exit(1)

    def get_var(self, name):
        """Get variable from scope stack"""
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
        """Set variable in current scope"""
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
        """Declare new variable in current scope"""
        timeline_value = TimelineValue(current=value)
        self.scopes[-1][name] = timeline_value

    def execute(self, statements):
        """Execute list of statements"""
        for stmt in statements:
            self.execute_statement(stmt)

    def execute_statement(self, stmt):
        """Execute single statement"""
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
        """Execute reality branching"""
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
        """Evaluate expression"""
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
        """Evaluate binary operation"""
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
        """Evaluate unary operation"""
        operand = self.evaluate(expr.operand)

        if expr.op == '-':
            return -operand
        elif expr.op == 'not':
            return not self.is_truthy(operand)

    def evaluate_function_call(self, expr):
        """Evaluate function call"""
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
        """Evaluate temporal operators"""
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
        """Determine truthiness"""
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
        """Convert value to string for output"""
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


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Entry point. The beginning of all confessions."""

    if len(sys.argv) != 2:
        print(f"\n{Color.CYAN}Usage: lament.py <filename.lament>{Color.RESET}", file=sys.stderr)
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
