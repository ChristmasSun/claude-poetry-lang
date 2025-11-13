"""
Lament Language Essential Features
===================================

This module extends the Lament language with three critical production features:

1. **Module System**: Import/export functionality with circular dependency detection
2. **Exception Handling**: Attempt/catch/finally blocks with custom exception types
3. **String Interpolation**: Template strings with expression evaluation

These features transform Lament from a toy language into a production-ready
programming environment capable of building large, maintainable applications.

Created by Claude for the Lament Language Project
"""

import os
import sys
import re
from typing import Any, List, Dict, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path

# Import base language components
from lament.lexer import Token, TokenType, Lexer
from lament.parser import ASTNode, Parser
from lament.interpreter import LamentInterpreter, ReturnValue


# ============================================================================
# EXTENDED TOKEN TYPES
# ============================================================================

from enum import Enum, auto

# Since we can't dynamically extend an existing Enum, we'll add them as attributes
# These will be recognized by the lexer keyword mapping
class ExtendedTokenType(Enum):
    """Additional token types for essential features."""
    IMPORT = auto()
    FROM = auto()
    EXPOSE = auto()
    AS = auto()
    ATTEMPT = auto()
    CATCH = auto()
    FINALLY = auto()
    RAISE = auto()
    TEMPLATE_STRING = auto()
    SEMICOLON = auto()

# Add to TokenType namespace for compatibility
if not hasattr(TokenType, 'IMPORT'):
    TokenType.IMPORT = ExtendedTokenType.IMPORT
    TokenType.FROM = ExtendedTokenType.FROM
    TokenType.EXPOSE = ExtendedTokenType.EXPOSE
    TokenType.AS = ExtendedTokenType.AS
    TokenType.ATTEMPT = ExtendedTokenType.ATTEMPT
    TokenType.CATCH = ExtendedTokenType.CATCH
    TokenType.FINALLY = ExtendedTokenType.FINALLY
    TokenType.RAISE = ExtendedTokenType.RAISE
    TokenType.TEMPLATE_STRING = ExtendedTokenType.TEMPLATE_STRING
    TokenType.SEMICOLON = ExtendedTokenType.SEMICOLON


# ============================================================================
# EXTENDED AST NODES
# ============================================================================

@dataclass
class ImportStmt(ASTNode):
    """Represents an import statement.

    Syntax: import { func1, func2 } from "module.lament"

    Attributes:
        items: List of names to import from the module
        module_path: Path to the module file (string literal)
        alias: Optional alias mapping {original_name: alias_name}
    """
    items: List[str]
    module_path: str
    alias: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExposeStmt(ASTNode):
    """Represents an expose (export) statement.

    Syntax: expose { func1, func2, variable }

    Attributes:
        names: List of variable/function names to export from this module
    """
    names: List[str]


@dataclass
class AttemptStmt(ASTNode):
    """Represents an attempt-catch-finally exception handling block.

    Syntax:
        attempt {
            <statements>
        } catch error {
            <error handling>
        } finally {
            <cleanup>
        }

    Attributes:
        try_block: Statements to execute in the attempt block
        catch_var: Variable name to bind the caught exception to
        catch_block: Statements to execute if exception occurs (optional)
        finally_block: Statements to always execute for cleanup (optional)
    """
    try_block: List[ASTNode]
    catch_var: Optional[str] = None
    catch_block: Optional[List[ASTNode]] = None
    finally_block: Optional[List[ASTNode]] = None


@dataclass
class RaiseStmt(ASTNode):
    """Represents a raise (throw) statement.

    Syntax: raise "Error message" or raise CustomError("message")

    Attributes:
        exception_expr: Expression that evaluates to exception message or object
    """
    exception_expr: ASTNode


@dataclass
class InterpolatedString(ASTNode):
    """Represents a template string with interpolated expressions.

    Syntax: "Hello ${name}, you are ${age} years old"

    Attributes:
        parts: List alternating between string literals and expression AST nodes
              Example: ["Hello ", <Identifier:name>, ", you are ", <Identifier:age>, " years old"]
    """
    parts: List[Any]  # Mix of strings and ASTNode objects


# ============================================================================
# CUSTOM EXCEPTION TYPES
# ============================================================================

class LamentException(Exception):
    """Base class for all Lament runtime exceptions.

    Provides stack trace information and custom exception types
    for the Lament language runtime.

    Attributes:
        message: Human-readable error message
        exception_type: Type name of the exception (e.g., "ValueError", "TypeError")
        stack_trace: List of (file, line, function) tuples for debugging
    """

    def __init__(self, message: str, exception_type: str = "LamentException"):
        """Initialize a Lament exception.

        Args:
            message: Error description
            exception_type: Name of the exception type
        """
        self.message = message
        self.exception_type = exception_type
        self.stack_trace = []
        super().__init__(message)

    def __str__(self):
        """Format exception as string with stack trace."""
        result = f"{self.exception_type}: {self.message}"
        if self.stack_trace:
            result += "\n\nStack trace:"
            for file, line, func in reversed(self.stack_trace):
                result += f"\n  at {func} ({file}:{line})"
        return result


class LamentRuntimeError(LamentException):
    """Runtime error in Lament code execution."""
    def __init__(self, message: str):
        super().__init__(message, "RuntimeError")


class LamentTypeError(LamentException):
    """Type mismatch error in Lament code."""
    def __init__(self, message: str):
        super().__init__(message, "TypeError")


class LamentValueError(LamentException):
    """Invalid value error in Lament code."""
    def __init__(self, message: str):
        super().__init__(message, "ValueError")


class LamentImportError(LamentException):
    """Module import/loading error."""
    def __init__(self, message: str):
        super().__init__(message, "ImportError")


class CircularDependencyError(LamentException):
    """Circular module dependency detected."""
    def __init__(self, message: str):
        super().__init__(message, "CircularDependencyError")


# ============================================================================
# EXTENDED LEXER
# ============================================================================

class EssentialLexer(Lexer):
    """Extended lexer with support for essential features.

    Adds tokenization for:
    - Module system keywords (import, from, expose)
    - Exception handling keywords (attempt, catch, finally, raise)
    - Template strings with ${} interpolation
    """

    def __init__(self, source: str):
        """Initialize extended lexer.

        Args:
            source: Source code string to tokenize
        """
        super().__init__(source)

        # Extend keyword mapping
        self.KEYWORDS = {
            **self.KEYWORDS,
            'import': TokenType.IMPORT,
            'from': TokenType.FROM,
            'expose': TokenType.EXPOSE,
            'as': TokenType.AS,
            'attempt': TokenType.ATTEMPT,
            'catch': TokenType.CATCH,
            'finally': TokenType.FINALLY,
            'raise': TokenType.RAISE,
        }

    def tokenize(self) -> List[Token]:
        """Tokenize with template string support.

        Overrides base tokenize to check for template strings.

        Returns:
            List of tokens including template string tokens
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
                continue

            # Check for template strings (strings with ${})
            if self.peek() == '"':
                # Look ahead to see if this is a template string
                start_pos = self.pos
                start_line = self.line
                test_pos = self.pos + 1

                is_template = False
                while test_pos < len(self.source) and self.source[test_pos] != '"':
                    if self.source[test_pos] == '\\':
                        test_pos += 2  # Skip escaped character
                        continue
                    if self.source[test_pos:test_pos+2] == '${':
                        is_template = True
                        break
                    test_pos += 1

                if is_template:
                    # Parse as template string
                    parts = self.read_template_string()
                    self.tokens.append(Token(TokenType.TEMPLATE_STRING, parts, start_line))
                else:
                    # Parse as regular string
                    value = self.read_string()
                    self.tokens.append(Token(TokenType.STRING, value, start_line))
                continue

            # Fall back to base tokenization for everything else
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
                ';': TokenType.SEMICOLON,
            }

            ch = self.peek()
            if ch in single_chars:
                self.advance()
                self.tokens.append(Token(single_chars[ch], None, self.line))
                continue

            self.error(f"Unexpected character: {ch}")

        self.tokens.append(Token(TokenType.EOF, None, self.line))
        return self.tokens

    def read_template_string(self) -> List[Any]:
        """Read a template string with ${} interpolations.

        Parses strings like "Hello ${name}" into a list of string parts
        and expression parts that need to be evaluated.

        Returns:
            List alternating between string literals and expression strings
            Example: ["Hello ", "name"] for "Hello ${name}"

        Raises:
            SyntaxError: If template string or interpolation is malformed
        """
        self.advance()  # opening quote
        parts = []
        current_str = []

        while self.peek() not in '"\0':
            if self.peek() == '$' and self.peek(1) == '{':
                # Save current string part
                if current_str:
                    parts.append(('string', ''.join(current_str)))
                    current_str = []

                # Read interpolation expression
                self.advance()  # $
                self.advance()  # {

                expr_chars = []
                brace_depth = 1

                while brace_depth > 0 and self.peek() != '\0':
                    ch = self.peek()
                    if ch == '{':
                        brace_depth += 1
                    elif ch == '}':
                        brace_depth -= 1
                        if brace_depth == 0:
                            break
                    expr_chars.append(self.advance())

                if brace_depth != 0:
                    self.error("Unterminated template expression")

                self.advance()  # closing }

                expr_str = ''.join(expr_chars).strip()
                if expr_str:
                    parts.append(('expr', expr_str))

            elif self.peek() == '\\':
                # Handle escape sequences
                self.advance()
                escape = self.advance()
                if escape == 'n':
                    current_str.append('\n')
                elif escape == 't':
                    current_str.append('\t')
                elif escape == '"':
                    current_str.append('"')
                elif escape == '\\':
                    current_str.append('\\')
                elif escape == '$':
                    current_str.append('$')
                else:
                    current_str.append(escape)
            else:
                current_str.append(self.advance())

        # Save final string part
        if current_str:
            parts.append(('string', ''.join(current_str)))

        if self.peek() == '\0':
            self.error("Unterminated template string")

        self.advance()  # closing quote
        return parts


# ============================================================================
# EXTENDED PARSER
# ============================================================================

class EssentialParser(Parser):
    """Extended parser with support for essential features.

    Adds parsing for:
    - Import/export statements
    - Attempt/catch/finally exception handling
    - Template string interpolation
    - Raise statements
    """

    def parse_statement(self) -> ASTNode:
        """Parse a statement with extended syntax support.

        Returns:
            AST node representing the statement

        Raises:
            SyntaxError: If statement syntax is invalid
        """
        token = self.peek()

        # Check for essential feature statements
        if token.type == TokenType.IMPORT:
            return self.parse_import()
        elif token.type == TokenType.EXPOSE:
            return self.parse_expose()
        elif token.type == TokenType.ATTEMPT:
            return self.parse_attempt()
        elif token.type == TokenType.RAISE:
            return self.parse_raise()

        # Fall back to base parser
        return super().parse_statement()

    def parse_import(self) -> ImportStmt:
        """Parse an import statement.

        Syntax: import { name1, name2 as alias2 } from "module.lament"

        Returns:
            ImportStmt AST node

        Raises:
            SyntaxError: If import syntax is invalid
        """
        self.expect(TokenType.IMPORT)
        self.expect(TokenType.LBRACE)

        items = []
        aliases = {}

        while self.peek().type != TokenType.RBRACE:
            name = self.expect(TokenType.IDENTIFIER).value
            items.append(name)

            # Check for alias
            if self.peek().type == TokenType.AS:
                self.advance()
                alias = self.expect(TokenType.IDENTIFIER).value
                aliases[name] = alias

            if self.peek().type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RBRACE)
        self.expect(TokenType.FROM)

        module_path = self.expect(TokenType.STRING).value

        return ImportStmt(items, module_path, aliases)

    def parse_expose(self) -> ExposeStmt:
        """Parse an expose (export) statement.

        Syntax: expose { name1, name2, name3 }

        Returns:
            ExposeStmt AST node

        Raises:
            SyntaxError: If expose syntax is invalid
        """
        self.expect(TokenType.EXPOSE)
        self.expect(TokenType.LBRACE)

        names = []
        while self.peek().type != TokenType.RBRACE:
            name = self.expect(TokenType.IDENTIFIER).value
            names.append(name)

            if self.peek().type == TokenType.COMMA:
                self.advance()

        self.expect(TokenType.RBRACE)

        return ExposeStmt(names)

    def parse_attempt(self) -> AttemptStmt:
        """Parse an attempt-catch-finally exception handling block.

        Syntax:
            attempt {
                <statements>
            } catch error {
                <statements>
            } finally {
                <statements>
            }

        Returns:
            AttemptStmt AST node

        Raises:
            SyntaxError: If attempt block syntax is invalid
        """
        self.expect(TokenType.ATTEMPT)
        self.expect(TokenType.LBRACE)

        # Parse try block
        try_block = []
        while self.peek().type != TokenType.RBRACE:
            try_block.append(self.parse_statement())
        self.expect(TokenType.RBRACE)

        # Parse optional catch block
        catch_var = None
        catch_block = None
        if self.peek().type == TokenType.CATCH:
            self.advance()
            catch_var = self.expect(TokenType.IDENTIFIER).value
            self.expect(TokenType.LBRACE)

            catch_block = []
            while self.peek().type != TokenType.RBRACE:
                catch_block.append(self.parse_statement())
            self.expect(TokenType.RBRACE)

        # Parse optional finally block
        finally_block = None
        if self.peek().type == TokenType.FINALLY:
            self.advance()
            self.expect(TokenType.LBRACE)

            finally_block = []
            while self.peek().type != TokenType.RBRACE:
                finally_block.append(self.parse_statement())
            self.expect(TokenType.RBRACE)

        return AttemptStmt(try_block, catch_var, catch_block, finally_block)

    def parse_raise(self) -> RaiseStmt:
        """Parse a raise statement.

        Syntax: raise <expression>

        Returns:
            RaiseStmt AST node
        """
        self.expect(TokenType.RAISE)
        exception_expr = self.parse_expression()
        return RaiseStmt(exception_expr)

    def parse_primary(self) -> ASTNode:
        """Parse primary expressions with template string support.

        Returns:
            AST node for the primary expression

        Raises:
            SyntaxError: If no valid primary expression found
        """
        token = self.peek()

        # Check for template string (detected by lexer)
        if token.type == TokenType.TEMPLATE_STRING:
            self.advance()
            return self.parse_interpolated_string(token.value)

        # Fall back to base parser
        return super().parse_primary()

    def parse_interpolated_string(self, parts: List[tuple]) -> InterpolatedString:
        """Parse template string parts into an InterpolatedString node.

        Args:
            parts: List of (type, content) tuples from lexer
                   where type is 'string' or 'expr'

        Returns:
            InterpolatedString AST node

        Raises:
            SyntaxError: If expression parsing fails
        """
        parsed_parts = []

        for part_type, content in parts:
            if part_type == 'string':
                parsed_parts.append(content)
            else:  # 'expr'
                # Parse the expression string
                expr_lexer = EssentialLexer(content)
                expr_tokens = expr_lexer.tokenize()
                expr_parser = EssentialParser(expr_tokens)
                expr_ast = expr_parser.parse_expression()
                parsed_parts.append(expr_ast)

        return InterpolatedString(parsed_parts)



# ============================================================================
# MODULE SYSTEM
# ============================================================================

class ModuleLoader:
    """Manages module loading, caching, and circular dependency detection.

    The module loader maintains a cache of loaded modules and tracks the
    current import chain to detect circular dependencies.

    Attributes:
        module_cache: Dictionary mapping module paths to their exported symbols
        loading_stack: Stack of currently loading modules for cycle detection
        search_paths: List of directories to search for modules
    """

    def __init__(self, search_paths: List[str] = None):
        """Initialize module loader.

        Args:
            search_paths: List of directories to search for modules
                         Defaults to current directory
        """
        self.module_cache: Dict[str, Dict[str, Any]] = {}
        self.loading_stack: List[str] = []
        self.search_paths = search_paths or [os.getcwd()]

    def resolve_module_path(self, module_name: str, current_file: str = None) -> str:
        """Resolve module name to absolute file path.

        Searches for the module in:
        1. Directory of the current file (if provided)
        2. Configured search paths

        Args:
            module_name: Name of module to import (e.g., "utils.lament")
            current_file: Path of the file doing the import

        Returns:
            Absolute path to the module file

        Raises:
            LamentImportError: If module file cannot be found
        """
        # If module_name is absolute, use it directly
        if os.path.isabs(module_name):
            if os.path.exists(module_name):
                return os.path.abspath(module_name)
            raise LamentImportError(f"Module not found: {module_name}")

        # Search in directory of current file
        if current_file:
            current_dir = os.path.dirname(os.path.abspath(current_file))
            candidate = os.path.join(current_dir, module_name)
            if os.path.exists(candidate):
                return os.path.abspath(candidate)

        # Search in search paths
        for search_path in self.search_paths:
            candidate = os.path.join(search_path, module_name)
            if os.path.exists(candidate):
                return os.path.abspath(candidate)

        raise LamentImportError(f"Module not found: {module_name}")

    def load_module(self, module_path: str, current_file: str = None) -> Dict[str, Any]:
        """Load a module and return its exported symbols.

        Uses caching to avoid reloading the same module. Detects circular
        dependencies during the loading process.

        Args:
            module_path: Path to module file (relative or absolute)
            current_file: Path of file doing the import

        Returns:
            Dictionary of exported symbols {name: value}

        Raises:
            CircularDependencyError: If circular dependency detected
            LamentImportError: If module cannot be loaded
        """
        # Resolve to absolute path
        abs_path = self.resolve_module_path(module_path, current_file)

        # Check cache
        if abs_path in self.module_cache:
            return self.module_cache[abs_path]

        # Check for circular dependency
        if abs_path in self.loading_stack:
            cycle = self.loading_stack[self.loading_stack.index(abs_path):] + [abs_path]
            cycle_str = ' -> '.join(cycle)
            raise CircularDependencyError(
                f"Circular dependency detected: {cycle_str}"
            )

        # Load module
        self.loading_stack.append(abs_path)

        try:
            # Read source code
            with open(abs_path, 'r') as f:
                source = f.read()

            # Parse and execute module
            from lament.essentials import EssentialInterpreter
            interpreter = EssentialInterpreter(module_loader=self)

            # Tokenize
            lexer = EssentialLexer(source)
            tokens = lexer.tokenize()

            # Parse
            parser = EssentialParser(tokens)
            ast = parser.parse()

            # Execute
            interpreter.execute(ast)

            # Get exported symbols
            exports = interpreter.module_exports

            # Cache the module
            self.module_cache[abs_path] = exports

            return exports

        except Exception as e:
            raise LamentImportError(f"Failed to load module {module_path}: {str(e)}")

        finally:
            self.loading_stack.pop()


# ============================================================================
# EXTENDED INTERPRETER
# ============================================================================

class EssentialInterpreter(LamentInterpreter):
    """Extended interpreter with essential features support.

    Adds execution support for:
    - Module imports and exports
    - Exception handling (attempt/catch/finally)
    - String interpolation
    - Custom exception raising

    Attributes:
        module_loader: ModuleLoader instance for handling imports
        module_exports: Dictionary of symbols exposed by this module
        current_file: Path to currently executing file (for imports)
    """

    def __init__(self, module_loader: ModuleLoader = None):
        """Initialize extended interpreter.

        Args:
            module_loader: Optional ModuleLoader instance (creates new if None)
        """
        super().__init__()
        self.module_loader = module_loader or ModuleLoader()
        self.module_exports: Dict[str, Any] = {}
        self.current_file: Optional[str] = None

        # Register exception constructor built-ins
        self.globals['RuntimeError'] = lambda msg: LamentRuntimeError(msg)
        self.globals['TypeError'] = lambda msg: LamentTypeError(msg)
        self.globals['ValueError'] = lambda msg: LamentValueError(msg)
        self.globals['ImportError'] = lambda msg: LamentImportError(msg)

    def execute_statement(self, stmt: ASTNode):
        """Execute a statement with essential features support.

        Args:
            stmt: AST node representing the statement

        Raises:
            LamentException: If an error occurs during execution
        """
        if isinstance(stmt, ImportStmt):
            self.execute_import(stmt)

        elif isinstance(stmt, ExposeStmt):
            self.execute_expose(stmt)

        elif isinstance(stmt, AttemptStmt):
            self.execute_attempt(stmt)

        elif isinstance(stmt, RaiseStmt):
            self.execute_raise(stmt)

        else:
            # Fall back to base interpreter
            super().execute_statement(stmt)

    def execute_import(self, stmt: ImportStmt):
        """Execute an import statement.

        Loads the specified module and imports requested symbols into
        current scope.

        Args:
            stmt: ImportStmt AST node

        Raises:
            LamentImportError: If import fails
        """
        # Load the module
        exports = self.module_loader.load_module(stmt.module_path, self.current_file)

        # Import requested items
        for item in stmt.items:
            if item not in exports:
                raise LamentImportError(
                    f"Module '{stmt.module_path}' does not export '{item}'"
                )

            # Use alias if provided, otherwise use original name
            name = stmt.alias.get(item, item)

            exported_value = exports[item]

            # If it's a FunctionDef, add to functions dictionary
            from lament.parser import FunctionDef
            if isinstance(exported_value, FunctionDef):
                self.functions[name] = exported_value
            else:
                # Otherwise add to current scope as variable
                self.scopes[-1][name] = exported_value

    def execute_expose(self, stmt: ExposeStmt):
        """Execute an expose (export) statement.

        Marks variables/functions as exported from this module.

        Args:
            stmt: ExposeStmt AST node

        Raises:
            LamentException: If exported name is undefined
        """
        for name in stmt.names:
            # Check if it's a function first
            if name in self.functions:
                self.module_exports[name] = self.functions[name]
                continue

            # Otherwise try to get as variable
            try:
                value = self.get_var(name)
                self.module_exports[name] = value
            except:
                raise LamentRuntimeError(
                    f"Cannot expose undefined symbol: {name}"
                )

    def execute_attempt(self, stmt: AttemptStmt):
        """Execute an attempt-catch-finally exception handling block.

        Implements full exception handling with:
        - Try block execution
        - Exception catching and binding
        - Finally block (always executed)
        - Proper stack unwinding

        Note: ReturnValue exceptions are not caught (they're for function returns).

        Args:
            stmt: AttemptStmt AST node
        """
        exception_occurred = None

        # Execute try block
        try:
            self.execute(stmt.try_block)

        except ReturnValue:
            # Don't catch return values - let them propagate
            raise

        except LamentException as e:
            exception_occurred = e

            # Execute catch block if present
            if stmt.catch_block and stmt.catch_var:
                # Create new scope for catch block
                self.scopes.append({})

                # Bind exception to catch variable
                self.scopes[-1][stmt.catch_var] = {
                    'message': e.message,
                    'type': e.exception_type,
                    'str': str(e)
                }

                scope_popped = False
                try:
                    self.execute(stmt.catch_block)
                    exception_occurred = None  # Exception was handled
                except ReturnValue:
                    # Catch block is returning - clear exception and re-raise return
                    exception_occurred = None
                    self.scopes.pop()
                    scope_popped = True
                    raise
                except LamentException as new_exc:
                    # New exception raised in catch block - propagate it
                    exception_occurred = new_exc
                finally:
                    # Pop scope if we haven't already
                    if not scope_popped:
                        self.scopes.pop()

            elif not stmt.catch_block:
                # No catch block, exception will propagate
                pass

        except Exception as e:
            # Catch Python exceptions and wrap them
            exception_occurred = LamentRuntimeError(str(e))

            if stmt.catch_block and stmt.catch_var:
                self.scopes.append({})
                self.scopes[-1][stmt.catch_var] = {
                    'message': str(e),
                    'type': type(e).__name__,
                    'str': str(e)
                }

                scope_popped = False
                try:
                    self.execute(stmt.catch_block)
                    exception_occurred = None
                except ReturnValue:
                    # Catch block is returning - clear exception and re-raise return
                    exception_occurred = None
                    self.scopes.pop()
                    scope_popped = True
                    raise
                except LamentException as new_exc:
                    # New exception raised in catch block - propagate it
                    exception_occurred = new_exc
                finally:
                    # Pop scope if we haven't already
                    if not scope_popped:
                        self.scopes.pop()

        finally:
            # Always execute finally block
            if stmt.finally_block:
                self.execute(stmt.finally_block)

            # Re-raise exception if it wasn't handled
            if exception_occurred:
                raise exception_occurred

    def execute_raise(self, stmt: RaiseStmt):
        """Execute a raise statement.

        Raises an exception that can be caught by attempt-catch blocks.

        Args:
            stmt: RaiseStmt AST node

        Raises:
            LamentException: The exception specified in the raise statement
        """
        exception_value = self.evaluate(stmt.exception_expr)

        # If it's already a LamentException, raise it
        if isinstance(exception_value, LamentException):
            raise exception_value

        # If it's a string, create a generic exception
        if isinstance(exception_value, str):
            raise LamentRuntimeError(exception_value)

        # If it's a dict with type and message, create appropriate exception
        if isinstance(exception_value, dict):
            msg = exception_value.get('message', 'Unknown error')
            exc_type = exception_value.get('type', 'RuntimeError')

            if exc_type == 'TypeError':
                raise LamentTypeError(msg)
            elif exc_type == 'ValueError':
                raise LamentValueError(msg)
            elif exc_type == 'ImportError':
                raise LamentImportError(msg)
            else:
                raise LamentRuntimeError(msg)

        # Otherwise, convert to string
        raise LamentRuntimeError(str(exception_value))

    def evaluate(self, expr: ASTNode) -> Any:
        """Evaluate an expression with essential features support.

        Args:
            expr: AST node representing the expression

        Returns:
            The evaluated value
        """
        if isinstance(expr, InterpolatedString):
            return self.evaluate_interpolated_string(expr)

        # Fall back to base interpreter
        return super().evaluate(expr)

    def evaluate_binary_op(self, expr):
        """Evaluate binary operation with exception handling.

        Overrides base method to raise LamentException instead of calling sys.exit.

        Args:
            expr: BinaryOp AST node

        Returns:
            Result of the operation

        Raises:
            LamentException: If operation fails (e.g., division by zero)
        """
        from lament.parser import BinaryOp

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
                raise LamentRuntimeError("Division by zero")
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

    def evaluate_interpolated_string(self, expr: InterpolatedString) -> str:
        """Evaluate a template string with interpolated expressions.

        Args:
            expr: InterpolatedString AST node

        Returns:
            Final string with all expressions evaluated and interpolated
        """
        result = []

        for part in expr.parts:
            if isinstance(part, str):
                # String literal part
                result.append(part)
            else:
                # Expression part - evaluate and convert to string
                value = self.evaluate(part)
                result.append(self.value_to_string(value))

        return ''.join(result)


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def parse_with_essentials(source: str) -> List[ASTNode]:
    """Parse Lament source code with essential features.

    Convenience function that handles tokenization and parsing in one call.

    Args:
        source: Lament source code string

    Returns:
        List of AST nodes representing the program

    Raises:
        SyntaxError: If parsing fails
    """
    lexer = EssentialLexer(source)
    tokens = lexer.tokenize()
    parser = EssentialParser(tokens)
    return parser.parse()


def execute_with_essentials(source: str, module_loader: ModuleLoader = None) -> EssentialInterpreter:
    """Execute Lament source code with essential features.

    Convenience function that handles tokenization, parsing, and execution.

    Args:
        source: Lament source code string
        module_loader: Optional ModuleLoader instance

    Returns:
        The interpreter instance after execution (for inspection)

    Raises:
        SyntaxError: If parsing fails
        LamentException: If execution fails
    """
    ast = parse_with_essentials(source)
    interpreter = EssentialInterpreter(module_loader)
    interpreter.execute(ast)
    return interpreter
