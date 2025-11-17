"""
Lament Language Parser Module
=============================

This module provides the Abstract Syntax Tree (AST) node definitions and
recursive descent parser for the Lament programming language.

The parser transforms a stream of tokens into a structured AST that can be
executed by the interpreter. It implements the full Lament grammar including:
- Emotional primitives and literals
- Binary and unary operations
- Control flow (if/else, while, for)
- Functions and returns
- Temporal operators (@past, @origin, @age, @born)
- Reality branching (fork/collapse/observe)
- Timeline variables

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union

# Import lexer components (assuming they will be in lament.lexer module)
try:
    from lament.lexer import Token, TokenType
except ImportError:
    # Fallback for development/testing
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lament.lexer import Token, TokenType


# ============================================================================
# AST NODE DEFINITIONS
# ============================================================================

@dataclass
class ASTNode:
    """Base class for all AST nodes."""
    pass


# --- Literal Nodes ---

@dataclass
class NumberLiteral(ASTNode):
    """
    Represents a numeric literal (integer or float).

    Attributes:
        value: The numeric value (int or float)
    """
    value: Union[int, float]


@dataclass
class StringLiteral(ASTNode):
    """
    Represents a string literal (whisper).

    Attributes:
        value: The string content
    """
    value: str


@dataclass
class BoolLiteral(ASTNode):
    """
    Represents a boolean/quantum literal.

    Attributes:
        value: One of 'yes' (true), 'no' (false), or 'perhaps' (quantum)
    """
    value: str  # 'yes', 'no', 'perhaps'


@dataclass
class VoidLiteral(ASTNode):
    """Represents the void (null/None) literal."""
    pass


@dataclass
class Identifier(ASTNode):
    """
    Represents a variable or function identifier.

    Attributes:
        name: The identifier name
    """
    name: str


# --- Operator Nodes ---

@dataclass
class BinaryOp(ASTNode):
    """
    Represents a binary operation (arithmetic, logical, comparison).

    Attributes:
        left: Left operand expression
        op: Operator string ('+', '-', '*', '/', '%', '==', '!=', '<', '>',
            '<=', '>=', 'and', 'or', 'is', 'is not')
        right: Right operand expression
    """
    left: ASTNode
    op: str
    right: ASTNode


@dataclass
class UnaryOp(ASTNode):
    """
    Represents a unary operation (negation, not).

    Attributes:
        op: Operator string ('-', 'not')
        operand: The operand expression
    """
    op: str
    operand: ASTNode


# --- Variable and Assignment Nodes ---

@dataclass
class Assignment(ASTNode):
    """
    Represents variable assignment (reassignment of existing variable).

    Attributes:
        name: Variable name
        value: Expression to assign
    """
    name: str
    value: ASTNode


@dataclass
class IndexAssignment(ASTNode):
    """
    Represents index/subscript assignment (e.g., arr[0] = 5, dict["key"] = value).

    Attributes:
        object: The object being indexed
        index: The index expression
        value: Expression to assign
    """
    object: ASTNode
    index: ASTNode
    value: ASTNode


@dataclass
class VariableDecl(ASTNode):
    """
    Represents variable declaration (remember statement).
    Creates a new timeline variable.

    Attributes:
        name: Variable name
        value: Initial value expression
    """
    name: str
    value: ASTNode


# --- Statement Nodes ---

@dataclass
class ConfessStmt(ASTNode):
    """
    Represents a confess statement (print/output).

    Attributes:
        value: Expression to confess/print
    """
    value: ASTNode


@dataclass
class IfStmt(ASTNode):
    """
    Represents an if-else conditional statement.

    Attributes:
        condition: Boolean condition expression
        then_block: List of statements to execute if condition is true
        else_block: Optional list of statements for else clause
    """
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None


@dataclass
class WhileStmt(ASTNode):
    """
    Represents a while loop statement.

    Attributes:
        condition: Loop continuation condition
        body: List of statements in loop body
    """
    condition: ASTNode
    body: List[ASTNode]


@dataclass
class ForStmt(ASTNode):
    """
    Represents a for-in loop statement.

    Attributes:
        var: Loop variable name
        iterable: Expression that evaluates to an iterable
        body: List of statements in loop body
    """
    var: str
    iterable: ASTNode
    body: List[ASTNode]


# --- Function Nodes ---

@dataclass
class FunctionDef(ASTNode):
    """
    Represents a function definition (sigh statement).

    Attributes:
        name: Function name
        params: List of parameter names
        body: List of statements in function body
    """
    name: str
    params: List[str]
    body: List[ASTNode]


@dataclass
class FunctionCall(ASTNode):
    """
    Represents a function call expression.

    Attributes:
        name: Function name
        args: List of argument expressions
    """
    name: str
    args: List[ASTNode]


@dataclass
class ExhaleStmt(ASTNode):
    """
    Represents a return statement (exhale).

    Attributes:
        value: Expression to return
    """
    value: ASTNode


# --- Temporal Nodes ---

@dataclass
class TemporalAccess(ASTNode):
    """
    Represents temporal variable access (@past, @origin, @age, @born).

    Attributes:
        var: Variable name
        operator: Temporal operator ('past', 'origin', 'age', 'born')
        offset: Optional offset for @past (number of steps back)
    """
    var: str
    operator: str  # 'past', 'origin', 'age', 'born'
    offset: Optional[int] = None


# --- Collection Nodes ---

@dataclass
class ListLiteral(ASTNode):
    """
    Represents a list literal.

    Attributes:
        elements: List of element expressions
    """
    elements: List[ASTNode]


@dataclass
class DictLiteral(ASTNode):
    """
    Represents a dictionary literal.

    Attributes:
        pairs: List of (key_expr, value_expr) tuples
    """
    pairs: List[tuple]  # [(key, value), ...]


@dataclass
class IndexAccess(ASTNode):
    """
    Represents indexed access to a collection (list[idx], dict[key]).

    Attributes:
        object: The collection expression
        index: The index/key expression
    """
    object: ASTNode
    index: ASTNode


# --- Reality Branching Nodes ---

@dataclass
class ForkReality(ASTNode):
    """
    Represents a reality fork statement (multiverse branching).

    Attributes:
        branches: List of (condition_expr, statements) tuples for each reality
        observe_var: Optional variable name to observe for collapse
    """
    branches: List[tuple]  # [(condition, body), ...]
    observe_var: Optional[str] = None


# ============================================================================
# PARSER
# ============================================================================

class Parser:
    """
    Recursive descent parser for the Lament language.

    Transforms a token stream into an Abstract Syntax Tree (AST) that
    represents the program structure. The parser implements operator
    precedence and associativity through the ordering of parse methods.

    Grammar precedence (lowest to highest):
        - or
        - and
        - comparison (==, !=, <, >, <=, >=)
        - is/is not
        - addition/subtraction (+, -)
        - multiplication/division/modulo (*, /, %)
        - unary (-, not)
        - postfix (function calls, indexing, temporal operators)
        - primary (literals, identifiers, parentheses)
    """

    def __init__(self, tokens: List[Token]):
        """
        Initialize parser with a token stream.

        Args:
            tokens: List of tokens from the lexer
        """
        self.tokens = tokens
        self.pos = 0

    def error(self, msg: str):
        """
        Raise a syntax error with line information.

        Args:
            msg: Error message

        Raises:
            SyntaxError: Always raises with formatted message
        """
        token = self.peek()
        raise SyntaxError(f"Line {token.line}: {msg}")

    def peek(self, offset: int = 0) -> Token:
        """
        Look ahead at a token without consuming it.

        Args:
            offset: Number of tokens ahead to peek (default 0 = current)

        Returns:
            The token at current position + offset, or EOF token if past end
        """
        pos = self.pos + offset
        return self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]

    def advance(self) -> Token:
        """
        Consume and return the current token, advancing position.

        Returns:
            The current token before advancing
        """
        token = self.peek()
        self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        """
        Consume a token and verify it matches the expected type.

        Args:
            token_type: Expected token type

        Returns:
            The consumed token if type matches

        Raises:
            SyntaxError: If token type doesn't match
        """
        token = self.advance()
        if token.type != token_type:
            self.error(f"Expected {token_type.name}, got {token.type.name}")
        return token

    def parse(self) -> List[ASTNode]:
        """
        Parse the entire program into a list of statement nodes.

        Returns:
            List of AST nodes representing the program
        """
        statements = []
        while self.peek().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements

    # --- Statement Parsing ---

    def parse_statement(self) -> ASTNode:
        """
        Parse a single statement based on the leading keyword.

        Returns:
            An AST node representing the statement

        Raises:
            SyntaxError: If statement syntax is invalid
        """
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
            # Could be assignment, index assignment, or function call
            # We need to parse the left side to handle cases like arr[0] = value
            if self.peek(1).type == TokenType.ASSIGN:
                return self.parse_assignment()
            elif self.peek(1).type == TokenType.LBRACKET:
                # Parse the index access, then check for assignment
                saved_pos = self.pos
                lhs = self.parse_postfix()
                if self.peek().type == TokenType.ASSIGN:
                    # It's an index assignment
                    self.advance()  # consume '='
                    value = self.parse_expression()
                    if isinstance(lhs, IndexAccess):
                        return IndexAssignment(lhs.object, lhs.index, value)
                    else:
                        self.error("Invalid assignment target")
                else:
                    # Not an assignment, restore and parse as expression statement
                    self.pos = saved_pos
                    return self.parse_expression()
            elif self.peek(1).type == TokenType.LPAREN:
                return self.parse_expression()  # function call as statement
            else:
                self.error("Unexpected identifier")
        else:
            self.error(f"Unexpected token: {token.type.name}")

    def parse_confess(self) -> ConfessStmt:
        """
        Parse a confess statement: confess <expression>

        Returns:
            ConfessStmt node
        """
        self.expect(TokenType.CONFESS)
        value = self.parse_expression()
        return ConfessStmt(value)

    def parse_variable_decl(self) -> VariableDecl:
        """
        Parse a variable declaration: remember <name> = <expression>

        Returns:
            VariableDecl node
        """
        self.expect(TokenType.REMEMBER)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return VariableDecl(name, value)

    def parse_assignment(self) -> Assignment:
        """
        Parse a variable assignment: <name> = <expression>

        Returns:
            Assignment node
        """
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        return Assignment(name, value)

    def parse_if(self) -> IfStmt:
        """
        Parse an if-else statement:
            if <condition> { <statements> } [else { <statements> }]

        Returns:
            IfStmt node
        """
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

    def parse_while(self) -> WhileStmt:
        """
        Parse a while loop: while <condition> { <statements> }

        Returns:
            WhileStmt node
        """
        self.expect(TokenType.WHILE)
        condition = self.parse_expression()
        self.expect(TokenType.LBRACE)
        body = []
        while self.peek().type != TokenType.RBRACE:
            body.append(self.parse_statement())
        self.expect(TokenType.RBRACE)
        return WhileStmt(condition, body)

    def parse_for(self) -> ForStmt:
        """
        Parse a for-in loop: for <var> in <iterable> { <statements> }

        Returns:
            ForStmt node
        """
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

    def parse_function_def(self) -> FunctionDef:
        """
        Parse a function definition:
            sigh <name>(<params>) { <statements> }

        Returns:
            FunctionDef node
        """
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

    def parse_exhale(self) -> ExhaleStmt:
        """
        Parse a return statement: exhale <expression>

        Returns:
            ExhaleStmt node
        """
        self.expect(TokenType.EXHALE)
        value = self.parse_expression()
        return ExhaleStmt(value)

    def parse_fork_reality(self) -> ForkReality:
        """
        Parse a reality fork statement:
            fork reality {
                on <condition> { <statements> }
                on <condition> { <statements> }
                ...
            } [collapse observe <var>]

        Returns:
            ForkReality node
        """
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

    # --- Expression Parsing (Precedence Climbing) ---

    def parse_expression(self) -> ASTNode:
        """
        Parse an expression (entry point for expression parsing).

        Returns:
            An AST node representing the expression
        """
        return self.parse_or()

    def parse_or(self) -> ASTNode:
        """
        Parse logical OR expressions (lowest precedence).

        Returns:
            BinaryOp node or lower precedence node
        """
        left = self.parse_and()
        while self.peek().type == TokenType.OR:
            self.advance()
            right = self.parse_and()
            left = BinaryOp(left, 'or', right)
        return left

    def parse_and(self) -> ASTNode:
        """
        Parse logical AND expressions.

        Returns:
            BinaryOp node or lower precedence node
        """
        left = self.parse_comparison()
        while self.peek().type == TokenType.AND:
            self.advance()
            right = self.parse_comparison()
            left = BinaryOp(left, 'and', right)
        return left

    def parse_comparison(self) -> ASTNode:
        """
        Parse comparison expressions (==, !=, <, >, <=, >=, in).

        Returns:
            BinaryOp node or lower precedence node
        """
        left = self.parse_is_check()

        comp_ops = {
            TokenType.EQUAL: '==',
            TokenType.NOT_EQUAL: '!=',
            TokenType.LESS: '<',
            TokenType.GREATER: '>',
            TokenType.LESS_EQ: '<=',
            TokenType.GREATER_EQ: '>=',
            TokenType.IN: 'in',
        }

        if self.peek().type in comp_ops:
            op_token = self.advance()
            right = self.parse_is_check()
            return BinaryOp(left, comp_ops[op_token.type], right)

        return left

    def parse_is_check(self) -> ASTNode:
        """
        Parse 'is' and 'is not' identity checks.

        Returns:
            BinaryOp node or lower precedence node
        """
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

    def parse_addition(self) -> ASTNode:
        """
        Parse addition and subtraction expressions.

        Returns:
            BinaryOp node or lower precedence node
        """
        left = self.parse_multiplication()

        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = '+' if self.peek().type == TokenType.PLUS else '-'
            self.advance()
            right = self.parse_multiplication()
            left = BinaryOp(left, op, right)

        return left

    def parse_multiplication(self) -> ASTNode:
        """
        Parse multiplication, division, and modulo expressions.

        Returns:
            BinaryOp node or lower precedence node
        """
        left = self.parse_unary()

        while self.peek().type in (TokenType.MULTIPLY, TokenType.DIVIDE, TokenType.MODULO):
            op_map = {TokenType.MULTIPLY: '*', TokenType.DIVIDE: '/', TokenType.MODULO: '%'}
            op = op_map[self.peek().type]
            self.advance()
            right = self.parse_unary()
            left = BinaryOp(left, op, right)

        return left

    def parse_unary(self) -> ASTNode:
        """
        Parse unary expressions (negation, logical not).

        Returns:
            UnaryOp node or lower precedence node
        """
        if self.peek().type == TokenType.NOT:
            self.advance()
            return UnaryOp('not', self.parse_unary())
        elif self.peek().type == TokenType.MINUS:
            self.advance()
            return UnaryOp('-', self.parse_unary())

        return self.parse_postfix()

    def parse_postfix(self) -> ASTNode:
        """
        Parse postfix expressions (function calls, indexing, temporal operators).

        Returns:
            FunctionCall, IndexAccess, TemporalAccess, or primary expression node
        """
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

    def parse_primary(self) -> ASTNode:
        """
        Parse primary expressions (literals, identifiers, parenthesized expressions).

        Returns:
            A literal, identifier, list, or parenthesized expression node

        Raises:
            SyntaxError: If no valid primary expression is found
        """
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
            self.advance()
            pairs = []
            while self.peek().type != TokenType.RBRACE:
                # Parse key expression
                key = self.parse_expression()
                self.expect(TokenType.COLON)
                # Parse value expression
                value = self.parse_expression()
                pairs.append((key, value))
                if self.peek().type == TokenType.COMMA:
                    self.advance()
            self.expect(TokenType.RBRACE)
            return DictLiteral(pairs)

        self.error(f"Unexpected token: {token.type.name}")
