"""
Lament Language Lexer

This module provides lexical analysis (tokenization) for the Lament programming language.
Converts raw source code into a stream of tokens for parsing.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

from enum import Enum, auto
from dataclasses import dataclass
from typing import Any, List


# ============================================================================
# TOKEN TYPES
# ============================================================================

class TokenType(Enum):
    """Enumeration of all token types in the Lament language.

    Categories:
    - Literals: NUMBER, STRING
    - Keywords: CONFESS, REMEMBER, FORGET, SIGH, EXHALE, IF, ELSE, WHILE, FOR, IN, etc.
    - Constants: VOID, YES, NO, PERHAPS
    - Operators: PLUS, MINUS, MULTIPLY, DIVIDE, MODULO, ASSIGN, EQUAL, etc.
    - Temporal Operators: AT_PAST, AT_ORIGIN, AT_AGE, AT_BORN
    - Delimiters: LPAREN, RPAREN, LBRACE, RBRACE, LBRACKET, RBRACKET, COMMA, DOT, COLON
    - Special: IDENTIFIER, NEWLINE, EOF
    """

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


# ============================================================================
# TOKEN DATA STRUCTURE
# ============================================================================

@dataclass
class Token:
    """Represents a single token in the source code.

    Attributes:
        type: The category of token (from TokenType enum)
        value: The literal value of the token (e.g., number value, string content, identifier name)
        line: The line number where this token appears in the source code
    """
    type: TokenType
    value: Any
    line: int


# ============================================================================
# LEXER
# ============================================================================

class Lexer:
    """Tokenizes Lament source code into a stream of tokens.

    The lexer performs lexical analysis, converting raw text into structured tokens
    that can be consumed by the parser. It handles:
    - String literals with escape sequences
    - Numeric literals (integers and floats)
    - Keywords and identifiers
    - Single and multi-line comments
    - Temporal operators (@past, @origin, @age, @born)
    - All operators and delimiters

    Usage:
        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
    """

    # Keyword mapping: Maps keyword strings to their corresponding TokenType
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
        """Initialize the lexer with source code.

        Args:
            source: The raw source code string to tokenize
        """
        self.source = source
        self.pos = 0
        self.line = 1
        self.tokens = []

    def error(self, msg: str):
        """Raise a syntax error with line number information.

        Args:
            msg: The error message to display

        Raises:
            SyntaxError: Always raised with formatted message
        """
        raise SyntaxError(f"Line {self.line}: {msg}")

    def peek(self, offset: int = 0) -> str:
        """Look ahead at a character without consuming it.

        Args:
            offset: How many characters ahead to look (default: 0 for current)

        Returns:
            The character at the specified offset, or '\\0' if past end of source
        """
        pos = self.pos + offset
        return self.source[pos] if pos < len(self.source) else '\0'

    def advance(self) -> str:
        """Consume and return the current character, advancing the position.

        Also tracks line numbers for error reporting.

        Returns:
            The character that was consumed
        """
        ch = self.peek()
        self.pos += 1
        if ch == '\n':
            self.line += 1
        return ch

    def skip_whitespace(self):
        """Skip over whitespace characters (space, tab, carriage return).

        Note: Newlines are not considered whitespace and are handled separately.
        """
        while self.peek() in ' \t\r':
            self.advance()

    def skip_comment(self):
        """Skip over single-line (#) and multi-line (/* */) comments.

        Raises:
            SyntaxError: If a multi-line comment is not terminated
        """
        if self.peek() == '#':
            # Single-line comment
            while self.peek() not in '\n\0':
                self.advance()
        elif self.peek() == '/' and self.peek(1) == '*':
            # Multi-line comment
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

    def read_string(self) -> str:
        """Read a string literal enclosed in double quotes.

        Handles escape sequences: \\n, \\t, \\", \\\\

        Returns:
            The string content (without surrounding quotes)

        Raises:
            SyntaxError: If the string is not terminated
        """
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
        """Read a numeric literal (integer or float).

        Returns:
            An int or float depending on whether a decimal point was encountered
        """
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

    def read_identifier(self) -> str:
        """Read an identifier or keyword.

        Identifiers consist of alphanumeric characters and underscores.

        Returns:
            The identifier string
        """
        chars = []
        while self.peek().isalnum() or self.peek() == '_':
            chars.append(self.advance())
        return ''.join(chars)

    def tokenize(self) -> List[Token]:
        """Convert the entire source code into a list of tokens.

        This is the main entry point for lexical analysis. It processes the source
        code character by character, identifying and creating tokens.

        Returns:
            A list of Token objects, terminated by an EOF token

        Raises:
            SyntaxError: If an unexpected character is encountered or other syntax errors occur
        """
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
