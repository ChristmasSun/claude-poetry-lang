"""
Lament Advanced Features
========================

This module extends the Lament language with advanced features:
1. Classes and Objects (with inheritance)
2. Pattern Matching (with guards and destructuring)
3. Generators and Iterators (with yield)

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, List, Optional, Dict, Union
import copy
import sys

from lament.lexer import Token, TokenType, Lexer
from lament.parser import (
    ASTNode, Parser, NumberLiteral, StringLiteral, BoolLiteral,
    VoidLiteral, Identifier, BinaryOp, UnaryOp, Assignment,
    VariableDecl, ConfessStmt, IfStmt, WhileStmt, ForStmt,
    FunctionDef, FunctionCall, ExhaleStmt, TemporalAccess,
    ListLiteral, DictLiteral, IndexAccess, ForkReality
)
from lament.interpreter import LamentInterpreter, ReturnValue
from lament.types import TimelineValue


# ============================================================================
# EXTENDED TOKEN TYPES
# ============================================================================

class AdvancedTokenType(Enum):
    """Extended token types for advanced features."""
    # Class/Object keywords
    CLASS = auto()
    NEW = auto()
    THIS = auto()
    EXTENDS = auto()
    SUPER = auto()

    # Pattern matching keywords
    MATCH = auto()
    CASE = auto()
    ARROW = auto()  # =>
    WHEN = auto()
    PIPE = auto()  # |
    UNDERSCORE = auto()  # _
    DOTDOT = auto()  # .. for ranges

    # Generator keywords
    YIELD = auto()


# ============================================================================
# EXTENDED LEXER
# ============================================================================

class AdvancedLexer(Lexer):
    """Extended lexer with support for advanced features."""

    # Extended keywords
    ADVANCED_KEYWORDS = {
        **Lexer.KEYWORDS,
        'class': AdvancedTokenType.CLASS,
        'new': AdvancedTokenType.NEW,
        'this': AdvancedTokenType.THIS,
        'extends': AdvancedTokenType.EXTENDS,
        'super': AdvancedTokenType.SUPER,
        'match': AdvancedTokenType.MATCH,
        'case': AdvancedTokenType.CASE,
        'when': AdvancedTokenType.WHEN,
        'yield': AdvancedTokenType.YIELD,
    }

    def __init__(self, source: str):
        super().__init__(source)
        self.KEYWORDS = self.ADVANCED_KEYWORDS

    def read_number(self):
        """Read a numeric literal (integer or float).

        Modified to handle range operator (..) by not consuming a dot
        if it's followed by another dot.

        Returns:
            An int or float depending on whether a decimal point was encountered
        """
        chars = []
        has_dot = False

        while self.peek().isdigit() or self.peek() == '.':
            if self.peek() == '.':
                # Don't consume the dot if it's part of a range operator (..)
                if self.peek(1) == '.':
                    break
                if has_dot:
                    break
                has_dot = True
            chars.append(self.advance())

        num_str = ''.join(chars)
        return float(num_str) if has_dot else int(num_str)

    def tokenize(self) -> List[Token]:
        """Extended tokenization with new operators."""
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

            # Identifiers and keywords (including underscore for wildcard)
            if self.peek().isalpha() or self.peek() == '_':
                if self.peek() == '_' and not self.peek(1).isalnum():
                    # Standalone underscore (wildcard pattern)
                    self.advance()
                    self.tokens.append(Token(AdvancedTokenType.UNDERSCORE, None, self.line))
                    continue

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

            # Arrow operator (=>)
            if self.peek() == '=' and self.peek(1) == '>':
                self.advance()
                self.advance()
                self.tokens.append(Token(AdvancedTokenType.ARROW, None, self.line))
                continue

            # Range operator (..)
            if self.peek() == '.' and self.peek(1) == '.':
                self.advance()
                self.advance()
                self.tokens.append(Token(AdvancedTokenType.DOTDOT, None, self.line))
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
                '|': AdvancedTokenType.PIPE,
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
# EXTENDED AST NODES
# ============================================================================

@dataclass
class ClassDef(ASTNode):
    """Represents a class definition.

    Attributes:
        name: Class name
        superclass: Optional parent class name
        methods: List of method definitions (FunctionDef nodes)
        fields: List of field initializations (assignments in constructor)
    """
    name: str
    superclass: Optional[str]
    methods: List[FunctionDef]
    constructor: Optional[FunctionDef] = None


@dataclass
class NewInstance(ASTNode):
    """Represents object instantiation.

    Attributes:
        class_name: Name of the class to instantiate
        args: Constructor arguments
    """
    class_name: str
    args: List[ASTNode]


@dataclass
class MemberAccess(ASTNode):
    """Represents member access (obj.field or obj.method()).

    Attributes:
        object: Object expression
        member: Member name
    """
    object: ASTNode
    member: str


@dataclass
class MemberAssignment(ASTNode):
    """Represents member assignment (obj.field = value).

    Attributes:
        object: Object expression
        member: Member name
        value: Value to assign
    """
    object: ASTNode
    member: str
    value: ASTNode


@dataclass
class ThisExpr(ASTNode):
    """Represents 'this' keyword."""
    pass


@dataclass
class SuperExpr(ASTNode):
    """Represents 'super' keyword for parent method calls."""
    member: str


@dataclass
class MatchStmt(ASTNode):
    """Represents a pattern matching statement.

    Attributes:
        value: Expression to match against
        cases: List of (pattern, guard, body) tuples
    """
    value: ASTNode
    cases: List[tuple]  # [(pattern, guard, body), ...]


@dataclass
class Pattern(ASTNode):
    """Base class for match patterns."""
    pass


@dataclass
class LiteralPattern(Pattern):
    """Matches a literal value."""
    value: Any


@dataclass
class RangePattern(Pattern):
    """Matches a range of values (e.g., 1..10)."""
    start: Any
    end: Any
    inclusive: bool = True


@dataclass
class ListPattern(Pattern):
    """Matches and destructures a list."""
    elements: List[Pattern]
    has_rest: bool = False  # For [a, b, ...rest] patterns


@dataclass
class WildcardPattern(Pattern):
    """Matches anything (underscore pattern)."""
    pass


@dataclass
class BindPattern(Pattern):
    """Binds matched value to a variable."""
    name: str


@dataclass
class YieldStmt(ASTNode):
    """Represents a yield statement.

    Attributes:
        value: Expression to yield
    """
    value: ASTNode


# ============================================================================
# EXTENDED PARSER
# ============================================================================

class AdvancedParser(Parser):
    """Extended parser with support for advanced features."""

    def parse_statement(self) -> ASTNode:
        """Extended statement parsing."""
        token = self.peek()
        token_type_str = str(token.type)

        # Check for advanced features first
        if 'CLASS' in token_type_str:
            return self.parse_class_def()
        elif 'MATCH' in token_type_str:
            return self.parse_match_stmt()
        elif 'YIELD' in token_type_str:
            return self.parse_yield_stmt()

        # Check for member access patterns (obj.member = value or obj.method())
        if token.type == TokenType.IDENTIFIER or 'THIS' in token_type_str:
            # Look ahead for member patterns
            if self.peek(1).type == TokenType.DOT and self.peek(2).type == TokenType.IDENTIFIER:
                if self.peek(3).type == TokenType.ASSIGN:
                    # Member assignment: obj.member = value
                    return self.parse_member_assignment_stmt()
                elif self.peek(3).type == TokenType.LPAREN:
                    # Method call as statement: obj.method()
                    return self.parse_expression()
                # Otherwise might be member access in expression

        # Fall back to base parser
        return super().parse_statement()

    def parse_class_def(self) -> ClassDef:
        """Parse class definition: class Name [extends Parent] { ... }"""
        self.advance()  # consume 'class'
        name = self.expect(TokenType.IDENTIFIER).value

        superclass = None
        extends_token_type_str = str(self.peek().type)
        if 'EXTENDS' in extends_token_type_str:
            self.advance()
            superclass = self.expect(TokenType.IDENTIFIER).value

        self.expect(TokenType.LBRACE)

        methods = []
        constructor = None

        while self.peek().type != TokenType.RBRACE:
            # Parse method (which is just a function definition)
            if self.peek().type == TokenType.SIGH:
                method = self.parse_function_def()
                if method.name == 'init':
                    constructor = method
                else:
                    methods.append(method)
            else:
                self.error("Expected method definition in class body")

        self.expect(TokenType.RBRACE)

        return ClassDef(name, superclass, methods, constructor)

    def parse_match_stmt(self) -> MatchStmt:
        """Parse match statement: match value { case pattern [when guard] => body, ... }"""
        self.advance()  # consume 'match'
        value = self.parse_expression()
        self.expect(TokenType.LBRACE)

        cases = []
        while True:
            token_type_str = str(self.peek().type)
            if 'CASE' in token_type_str:
                self.advance()
            else:
                break

            # Parse pattern
            pattern = self.parse_pattern()

            # Optional guard clause
            guard = None
            guard_token_type_str = str(self.peek().type)
            if 'WHEN' in guard_token_type_str:
                self.advance()
                guard = self.parse_expression()

            # Arrow
            arrow_token_type_str = str(self.peek().type)
            if 'ARROW' in arrow_token_type_str:
                self.advance()
            else:
                self.error("Expected '=>' after pattern")

            # Body (either single expression or block)
            if self.peek().type == TokenType.LBRACE:
                self.advance()
                body = []
                while self.peek().type != TokenType.RBRACE:
                    body.append(self.parse_statement())
                self.expect(TokenType.RBRACE)
            else:
                # Single expression
                body = [self.parse_expression()]

            cases.append((pattern, guard, body))

            # Optional comma
            if self.peek().type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RBRACE)

        return MatchStmt(value, cases)

    def parse_pattern(self) -> Pattern:
        """Parse a match pattern."""
        token = self.peek()
        token_type_str = str(token.type)

        # Wildcard pattern
        if 'UNDERSCORE' in token_type_str:
            self.advance()
            return WildcardPattern()

        # List pattern
        if token.type == TokenType.LBRACKET:
            return self.parse_list_pattern()

        # Try to parse as range or literal
        if token.type == TokenType.NUMBER:
            start_val = self.advance().value

            # Check for range pattern
            next_token_type_str = str(self.peek().type)
            if 'DOTDOT' in next_token_type_str:
                self.advance()
                end_val = self.expect(TokenType.NUMBER).value
                return RangePattern(start_val, end_val)

            return LiteralPattern(start_val)

        # String literal pattern
        if token.type == TokenType.STRING:
            value = self.advance().value
            return LiteralPattern(value)

        # Boolean patterns
        if token.type in (TokenType.YES, TokenType.NO):
            value = True if token.type == TokenType.YES else False
            self.advance()
            return LiteralPattern(value)

        # Identifier (bind pattern)
        if token.type == TokenType.IDENTIFIER:
            name = self.advance().value
            return BindPattern(name)

        self.error(f"Invalid pattern: {token_type_str}")

    def parse_list_pattern(self) -> ListPattern:
        """Parse list destructuring pattern: [a, b, c] or [a, b, ..rest]"""
        self.expect(TokenType.LBRACKET)
        elements = []
        has_rest = False

        while self.peek().type != TokenType.RBRACKET:
            # Check for rest pattern (..)
            rest_token_str = str(self.peek().type)
            if 'DOTDOT' in rest_token_str:
                has_rest = True
                self.advance()
                if self.peek().type == TokenType.IDENTIFIER:
                    # Named rest: ..rest
                    elements.append(BindPattern(self.advance().value))
                else:
                    # Anonymous rest: just ..
                    elements.append(WildcardPattern())
                break

            elements.append(self.parse_pattern())

            if self.peek().type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RBRACKET)
        return ListPattern(elements, has_rest)

    def parse_yield_stmt(self) -> YieldStmt:
        """Parse yield statement: yield expression"""
        self.advance()  # consume 'yield'
        value = self.parse_expression()
        return YieldStmt(value)

    def parse_member_assignment_stmt(self) -> MemberAssignment:
        """Parse member assignment: obj.member = value or this.member = value"""
        # Parse the object (could be identifier or 'this')
        token_type_str = str(self.peek().type)
        if 'THIS' in token_type_str:
            self.advance()
            obj = ThisExpr()
        else:
            obj = Identifier(self.expect(TokenType.IDENTIFIER).value)

        self.expect(TokenType.DOT)
        member = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return MemberAssignment(obj, member, value)

    def parse_primary(self) -> ASTNode:
        """Extended primary expression parsing."""
        token = self.peek()

        # Check for advanced token types by checking the type's name or value
        token_type_str = str(token.type)

        # New instance creation
        if 'NEW' in token_type_str:
            self.advance()
            class_name = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.LPAREN)
            args = []
            while self.peek().type != TokenType.RPAREN:
                args.append(self.parse_expression())
                if self.peek().type == TokenType.COMMA:
                    self.advance()
            self.expect(TokenType.RPAREN)
            return NewInstance(class_name, args)

        # This keyword
        if 'THIS' in token_type_str:
            self.advance()
            return ThisExpr()

        # Super keyword
        if 'SUPER' in token_type_str:
            self.advance()
            self.expect(TokenType.DOT)
            member = self.expect(TokenType.IDENTIFIER).value
            return SuperExpr(member)

        # Fall back to base parser
        return super().parse_primary()

    def parse_postfix(self) -> ASTNode:
        """Extended postfix parsing with member access."""
        left = self.parse_primary()

        while True:
            # Member access (obj.member)
            if self.peek().type == TokenType.DOT:
                # Don't consume if it's a range operator
                if self.peek(1).type == TokenType.DOT:
                    break

                self.advance()
                member = self.expect(TokenType.IDENTIFIER).value
                left = MemberAccess(left, member)

            # Function call
            elif self.peek().type == TokenType.LPAREN:
                self.advance()
                args = []
                while self.peek().type != TokenType.RPAREN:
                    args.append(self.parse_expression())
                    if self.peek().type == TokenType.COMMA:
                        self.advance()
                self.expect(TokenType.RPAREN)

                # Method call on member access
                if isinstance(left, MemberAccess):
                    # Convert to a special method call
                    left = FunctionCall(f"__method__{left.member}",
                                       [left.object] + args)
                    left.is_method_call = True
                    left.method_name = left.name.replace("__method__", "")
                    left.object_expr = left.args[0]
                    left.method_args = left.args[1:]
                elif isinstance(left, Identifier):
                    left = FunctionCall(left.name, args)
                else:
                    self.error("Can only call identifiers or methods")

            # Index access
            elif self.peek().type == TokenType.LBRACKET:
                self.advance()
                index = self.parse_expression()
                self.expect(TokenType.RBRACKET)
                left = IndexAccess(left, index)

            # Temporal access
            elif self.peek().type in (TokenType.AT_PAST, TokenType.AT_ORIGIN,
                                     TokenType.AT_AGE, TokenType.AT_BORN):
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


# ============================================================================
# RUNTIME OBJECTS
# ============================================================================

class LamentObject:
    """Runtime representation of a class instance."""

    def __init__(self, class_def, superclass_instance=None):
        self.class_def = class_def
        self.superclass = superclass_instance
        self.fields = {}

    def get_field(self, name):
        """Get field value, checking parent classes."""
        if name in self.fields:
            return self.fields[name]
        if self.superclass:
            return self.superclass.get_field(name)
        raise AttributeError(f"Object has no field '{name}'")

    def set_field(self, name, value):
        """Set field value."""
        self.fields[name] = value

    def get_method(self, name):
        """Get method definition, checking parent classes."""
        for method in self.class_def.methods:
            if method.name == name:
                return method
        if self.superclass:
            return self.superclass.get_method(name)
        return None

    def __repr__(self):
        return f"<{self.class_def.name} instance>"


class Generator:
    """Runtime representation of a generator.

    This is a simplified implementation that re-executes the function
    from the beginning each time, skipping previously yielded values.
    """

    def __init__(self, func_def, interpreter, args, closure_scope):
        self.func_def = func_def
        self.interpreter = interpreter
        self.args = args
        self.closure_scope = closure_scope
        self.exhausted = False
        self.yield_count = 0  # How many times we've yielded

    def __iter__(self):
        return self

    def __next__(self):
        if self.exhausted:
            raise StopIteration

        # Track how many yields we encounter in this execution
        yields_seen = 0

        # Set up execution context
        self.interpreter.scopes.append(self.closure_scope.copy())
        for param, arg in zip(self.func_def.params, self.args):
            self.interpreter.declare_var(param, arg)

        # Custom yield counter to skip already-yielded values
        original_execute_stmt = self.interpreter.execute_statement

        result_value = None
        found_yield = False

        def counting_execute_statement(stmt):
            nonlocal yields_seen, result_value, found_yield

            if isinstance(stmt, YieldStmt):
                if yields_seen == self.yield_count:
                    # This is the yield we want
                    result_value = self.interpreter.evaluate(stmt.value)
                    found_yield = True
                    raise YieldValue(result_value)
                else:
                    # Skip this yield, we've already returned it
                    yields_seen += 1
                    return
            else:
                # Use original execute for non-yield statements
                original_execute_stmt(stmt)

        # Replace execute method temporarily
        self.interpreter.execute_statement = counting_execute_statement

        try:
            # Execute function body
            for stmt in self.func_def.body:
                self.interpreter.execute_statement(stmt)

            # If we get here, no more yields
            self.exhausted = True
            self.interpreter.scopes.pop()
            self.interpreter.execute_statement = original_execute_stmt
            raise StopIteration

        except YieldValue:
            # Found the yield we wanted
            self.yield_count += 1
            self.interpreter.scopes.pop()
            self.interpreter.execute_statement = original_execute_stmt
            return result_value

        except ReturnValue:
            # Explicit return ends generator
            self.exhausted = True
            self.interpreter.scopes.pop()
            self.interpreter.execute_statement = original_execute_stmt
            raise StopIteration


class YieldValue(Exception):
    """Exception used to implement yield."""
    def __init__(self, value):
        self.value = value
        super().__init__()


# ============================================================================
# EXTENDED INTERPRETER
# ============================================================================

class AdvancedInterpreter(LamentInterpreter):
    """Extended interpreter with support for advanced features."""

    def __init__(self):
        super().__init__()
        self.classes = {}  # Class definitions
        self.current_object = None  # Current 'this' binding

    def execute_statement(self, stmt):
        """Extended statement execution."""
        if isinstance(stmt, ClassDef):
            self.classes[stmt.name] = stmt

        elif isinstance(stmt, MatchStmt):
            self.execute_match(stmt)

        elif isinstance(stmt, YieldStmt):
            # Yield in direct execution context (should be in generator)
            value = self.evaluate(stmt.value)
            raise YieldValue(value)

        elif isinstance(stmt, MemberAssignment):
            self.execute_member_assignment(stmt)

        else:
            # Fall back to base interpreter
            super().execute_statement(stmt)

    def execute_match(self, stmt):
        """Execute pattern matching statement."""
        value = self.evaluate(stmt.value)

        for pattern, guard, body in stmt.cases:
            # Try to match pattern
            bindings = self.match_pattern(pattern, value)

            if bindings is not None:
                # Pattern matched - check guard
                if guard is not None:
                    # Create scope with bindings for guard evaluation
                    self.scopes.append(bindings)
                    guard_result = self.is_truthy(self.evaluate(guard))
                    self.scopes.pop()

                    if not guard_result:
                        continue  # Guard failed, try next case

                # Execute body with bindings
                self.scopes.append(bindings)
                try:
                    self.execute(body)
                finally:
                    self.scopes.pop()
                return

        # No pattern matched
        self.error(
            "Pattern match failed",
            f"The value did not match any pattern.\n"
            f"       (All paths through the void lead nowhere.)"
        )

    def match_pattern(self, pattern, value) -> Optional[Dict]:
        """Match a pattern against a value. Returns bindings dict or None."""
        if isinstance(pattern, WildcardPattern):
            return {}

        elif isinstance(pattern, LiteralPattern):
            return {} if value == pattern.value else None

        elif isinstance(pattern, RangePattern):
            if isinstance(value, (int, float)):
                if pattern.inclusive:
                    if pattern.start <= value <= pattern.end:
                        return {}
                else:
                    if pattern.start <= value < pattern.end:
                        return {}
            return None

        elif isinstance(pattern, BindPattern):
            return {pattern.name: TimelineValue(current=value)}

        elif isinstance(pattern, ListPattern):
            if not isinstance(value, list):
                return None

            if pattern.has_rest:
                # Match with rest pattern
                if len(value) < len(pattern.elements) - 1:
                    return None

                bindings = {}
                for i, elem_pattern in enumerate(pattern.elements[:-1]):
                    elem_bindings = self.match_pattern(elem_pattern, value[i])
                    if elem_bindings is None:
                        return None
                    bindings.update(elem_bindings)

                # Bind rest
                rest_pattern = pattern.elements[-1]
                rest_values = value[len(pattern.elements)-1:]
                rest_bindings = self.match_pattern(rest_pattern, rest_values)
                if rest_bindings is None:
                    return None
                bindings.update(rest_bindings)

                return bindings
            else:
                # Exact length match
                if len(value) != len(pattern.elements):
                    return None

                bindings = {}
                for elem_pattern, elem_value in zip(pattern.elements, value):
                    elem_bindings = self.match_pattern(elem_pattern, elem_value)
                    if elem_bindings is None:
                        return None
                    bindings.update(elem_bindings)

                return bindings

        return None

    def execute_member_assignment(self, stmt):
        """Execute member assignment: obj.member = value"""
        obj = self.evaluate(stmt.object)
        value = self.evaluate(stmt.value)

        if not isinstance(obj, LamentObject):
            self.error(
                "Cannot assign to member of non-object",
                f"You tried to reach into something that has no form,\n"
                f"       no structure, no self.\n"
                f"       (Only objects have fields.)"
            )

        obj.set_field(stmt.member, value)

    def evaluate(self, expr):
        """Extended expression evaluation."""
        if isinstance(expr, NewInstance):
            return self.evaluate_new_instance(expr)

        elif isinstance(expr, MemberAccess):
            return self.evaluate_member_access(expr)

        elif isinstance(expr, ThisExpr):
            if self.current_object is None:
                self.error(
                    "'this' used outside of method",
                    f"You reached for 'this', but there is no self here,\n"
                    f"       no identity, no reflection.\n"
                    f"       ('this' can only be used inside methods.)"
                )
            return self.current_object

        elif isinstance(expr, SuperExpr):
            if self.current_object is None or self.current_object.superclass is None:
                self.error(
                    "Invalid 'super' access",
                    f"You called to the ancestors, but there is no lineage,\n"
                    f"       no inheritance, no parent.\n"
                    f"       (No superclass available.)"
                )
            # Return the parent method
            method = self.current_object.superclass.get_method(expr.member)
            if method is None:
                self.error(
                    f"Superclass has no method '{expr.member}'",
                    f"The ancestors do not know this sigh."
                )
            return method

        else:
            # Fall back to base interpreter
            return super().evaluate(expr)

    def evaluate_new_instance(self, expr):
        """Evaluate object instantiation."""
        if expr.class_name not in self.classes:
            self.error(
                f"Undefined class: {expr.class_name}",
                f"I searched for the class '{expr.class_name}',\n"
                f"       but it was never defined.\n"
                f"       (Perhaps you forgot to declare it?)"
            )

        class_def = self.classes[expr.class_name]

        # Create superclass instance if needed
        superclass_instance = None
        if class_def.superclass:
            if class_def.superclass not in self.classes:
                self.error(
                    f"Undefined superclass: {class_def.superclass}",
                    f"The parent class does not exist."
                )
            superclass_instance = LamentObject(self.classes[class_def.superclass])

        # Create object
        obj = LamentObject(class_def, superclass_instance)

        # Call constructor if exists
        if class_def.constructor:
            args = [self.evaluate(arg) for arg in expr.args]

            old_object = self.current_object
            self.current_object = obj

            try:
                # Create scope for constructor
                self.scopes.append({})
                for param, arg in zip(class_def.constructor.params, args):
                    self.declare_var(param, arg)

                # Execute constructor body
                self.execute(class_def.constructor.body)

                self.scopes.pop()
            finally:
                self.current_object = old_object

        return obj

    def evaluate_member_access(self, expr):
        """Evaluate member access (field or method)."""
        obj = self.evaluate(expr.object)

        if not isinstance(obj, LamentObject):
            self.error(
                "Cannot access member of non-object",
                f"You tried to reach into something that has no form.\n"
                f"       (Only objects have fields and methods.)"
            )

        # Try to get field first
        try:
            return obj.get_field(expr.member)
        except AttributeError:
            pass

        # Try to get method
        method = obj.get_method(expr.member)
        if method is not None:
            # Return a bound method (closure with 'this')
            return ('bound_method', obj, method)

        self.error(
            f"Object has no member '{expr.member}'",
            f"I searched the object's essence,\n"
            f"       but '{expr.member}' does not exist."
        )

    def evaluate_function_call(self, expr):
        """Extended function call evaluation with method support."""
        # Check for method call
        if hasattr(expr, 'is_method_call') and expr.is_method_call:
            obj = self.evaluate(expr.object_expr)

            if not isinstance(obj, LamentObject):
                self.error(
                    "Cannot call method on non-object",
                    f"You tried to call a method on something that has no form."
                )

            method = obj.get_method(expr.method_name)
            if method is None:
                self.error(
                    f"Object has no method '{expr.method_name}'",
                    f"The object does not know this sigh."
                )

            args = [self.evaluate(arg) for arg in expr.method_args]

            # Check if method is a generator (contains yield)
            has_yield = self._contains_yield(method.body)

            if has_yield:
                # Return generator
                return Generator(method, self, args, self.scopes[-1].copy())

            # Execute method with 'this' binding
            old_object = self.current_object
            self.current_object = obj

            try:
                self.scopes.append({})
                for param, arg in zip(method.params, args):
                    self.declare_var(param, arg)

                try:
                    self.execute(method.body)
                    result = None
                except ReturnValue as rv:
                    result = rv.value
                finally:
                    self.scopes.pop()

                return result
            finally:
                self.current_object = old_object

        # Check for bound method call
        func = None
        if expr.name in self.globals and callable(self.globals[expr.name]):
            func = self.globals[expr.name]
        elif expr.name in self.scopes[-1]:
            potential_func = self.scopes[-1][expr.name]
            if isinstance(potential_func, tuple) and potential_func[0] == 'bound_method':
                # Bound method call
                obj, method = potential_func[1], potential_func[2]
                args = [self.evaluate(arg) for arg in expr.args]

                # Check if method is a generator
                has_yield = self._contains_yield(method.body)

                if has_yield:
                    return Generator(method, self, args, self.scopes[-1].copy())

                old_object = self.current_object
                self.current_object = obj

                try:
                    self.scopes.append({})
                    for param, arg in zip(method.params, args):
                        self.declare_var(param, arg)

                    try:
                        self.execute(method.body)
                        result = None
                    except ReturnValue as rv:
                        result = rv.value
                    finally:
                        self.scopes.pop()

                    return result
                finally:
                    self.current_object = old_object

        # Check if function is a generator
        if expr.name in self.functions:
            func_def = self.functions[expr.name]
            has_yield = self._contains_yield(func_def.body)

            if has_yield:
                args = [self.evaluate(arg) for arg in expr.args]
                return Generator(func_def, self, args, self.scopes[-1].copy())

        # Fall back to base implementation
        return super().evaluate_function_call(expr)

    def _contains_yield(self, statements):
        """Check if a list of statements contains a yield."""
        for stmt in statements:
            if isinstance(stmt, YieldStmt):
                return True
            # Check nested statements
            if isinstance(stmt, IfStmt):
                if self._contains_yield(stmt.then_block):
                    return True
                if stmt.else_block and self._contains_yield(stmt.else_block):
                    return True
            elif isinstance(stmt, WhileStmt):
                if self._contains_yield(stmt.body):
                    return True
            elif isinstance(stmt, ForStmt):
                if self._contains_yield(stmt.body):
                    return True
        return False

    def register_builtins(self):
        """Register builtins including generator helpers."""
        super().register_builtins()

        # Add generator helper functions
        self.globals['is_generator'] = lambda x: isinstance(x, Generator)
        self.globals['collect'] = lambda gen: list(gen) if isinstance(gen, Generator) else list(gen)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def run_advanced_lament(source: str, debug: bool = False):
    """Run Lament code with advanced features.

    Args:
        source: Lament source code
        debug: If True, print AST before execution
    """
    try:
        # Lex
        lexer = AdvancedLexer(source)
        tokens = lexer.tokenize()

        if debug:
            print("=== TOKENS ===")
            for token in tokens:
                print(f"  {token}")
            print()

        # Parse
        parser = AdvancedParser(tokens)
        ast = parser.parse()

        if debug:
            print("=== AST ===")
            for node in ast:
                print(f"  {node}")
            print()

        # Execute
        interpreter = AdvancedInterpreter()
        interpreter.execute(ast)

    except SyntaxError as e:
        print(f"Syntax Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    # Simple test
    code = """
    class Point {
        sigh init(x, y) {
            this.x = x
            this.y = y
        }

        sigh distance() {
            exhale sqrt_of_pain(this.x * this.x + this.y * this.y)
        }
    }

    remember p = new Point(3, 4)
    confess p.distance()
    """

    run_advanced_lament(code)
