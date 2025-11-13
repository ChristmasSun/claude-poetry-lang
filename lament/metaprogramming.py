"""
Lament Language Metaprogramming Module
=======================================

This module provides powerful metaprogramming capabilities for the Lament language:

1. **Hygienic Macros**: Safe code generation with pattern matching
   - Macro class with expand() method
   - Automatic variable hygiene to prevent capture
   - Pattern matching and template substitution
   - Syntax: macro! name { ... }

2. **Compile-Time Code Generation**: Generate code during compilation
   - CodeGenerator class for template-based generation
   - Template expansion with parameter substitution
   - Code as data manipulation

3. **AST Manipulation API**: Programmatic AST modification
   - ASTManipulator class with visitor pattern
   - Transformation functions for code rewriting
   - Quote/unquote operators for code templates
   - AST cloning and substitution

4. **Reflection**: Runtime type information and introspection
   - Reflect class for type introspection
   - Get type info, methods, fields
   - Dynamic method invocation
   - Runtime type queries

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import copy
import re
import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Callable, Union
from enum import Enum, auto

# Import Lament AST components
try:
    from lament.parser import (
        ASTNode, NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral,
        Identifier, BinaryOp, UnaryOp, Assignment, VariableDecl,
        ConfessStmt, IfStmt, WhileStmt, ForStmt, FunctionDef,
        FunctionCall, ExhaleStmt, TemporalAccess, ListLiteral,
        DictLiteral, IndexAccess, ForkReality
    )
    from lament.lexer import Lexer, Token, TokenType
    from lament.types import TimelineValue, LamentType
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from lament.parser import (
        ASTNode, NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral,
        Identifier, BinaryOp, UnaryOp, Assignment, VariableDecl,
        ConfessStmt, IfStmt, WhileStmt, ForStmt, FunctionDef,
        FunctionCall, ExhaleStmt, TemporalAccess, ListLiteral,
        DictLiteral, IndexAccess, ForkReality
    )
    from lament.lexer import Lexer, Token, TokenType
    from lament.types import TimelineValue, LamentType


# ============================================================================
# PATTERN MATCHING FOR MACROS
# ============================================================================

class PatternType(Enum):
    """Types of pattern elements in macro definitions."""
    LITERAL = auto()      # Exact match (keyword, operator)
    VARIABLE = auto()     # Match any expression, bind to variable
    IDENTIFIER = auto()   # Match identifier only
    EXPRESSION = auto()   # Match any expression
    STATEMENT = auto()    # Match any statement
    BLOCK = auto()        # Match block of statements
    REPEATED = auto()     # Match repeated pattern (*, +)
    OPTIONAL = auto()     # Match optional pattern (?)


@dataclass
class Pattern:
    """
    Represents a pattern element in a macro definition.

    Patterns are used to match and extract parts of the source code
    during macro expansion.

    Attributes:
        type: Type of pattern element
        name: Variable name to bind matched content (if applicable)
        value: Literal value to match (for LITERAL patterns)
        subpattern: Nested pattern (for REPEATED, OPTIONAL)
        quantifier: Quantifier for repeated patterns ('*', '+', '?')
    """
    type: PatternType
    name: Optional[str] = None
    value: Optional[Any] = None
    subpattern: Optional['Pattern'] = None
    quantifier: Optional[str] = None


class PatternMatcher:
    """
    Matches code against patterns and extracts bindings.

    Used by the macro system to parse macro invocations and bind
    pattern variables to actual code fragments.
    """

    def __init__(self):
        self.bindings: Dict[str, Any] = {}

    def match(self, pattern: Pattern, node: ASTNode) -> bool:
        """
        Match an AST node against a pattern.

        Args:
            pattern: Pattern to match against
            node: AST node to match

        Returns:
            True if match succeeds, False otherwise
        """
        if pattern.type == PatternType.LITERAL:
            return self._match_literal(pattern, node)
        elif pattern.type == PatternType.VARIABLE:
            return self._match_variable(pattern, node)
        elif pattern.type == PatternType.IDENTIFIER:
            return self._match_identifier(pattern, node)
        elif pattern.type == PatternType.EXPRESSION:
            return self._match_expression(pattern, node)
        elif pattern.type == PatternType.STATEMENT:
            return self._match_statement(pattern, node)
        elif pattern.type == PatternType.BLOCK:
            return self._match_block(pattern, node)
        elif pattern.type == PatternType.REPEATED:
            return self._match_repeated(pattern, node)
        elif pattern.type == PatternType.OPTIONAL:
            return self._match_optional(pattern, node)
        return False

    def _match_literal(self, pattern: Pattern, node: ASTNode) -> bool:
        """Match exact literal value."""
        if isinstance(node, NumberLiteral):
            match = node.value == pattern.value
            if match and pattern.name:
                self.bindings[pattern.name] = node
            return match
        elif isinstance(node, StringLiteral):
            match = node.value == pattern.value
            if match and pattern.name:
                self.bindings[pattern.name] = node
            return match
        elif isinstance(node, BoolLiteral):
            match = node.value == pattern.value
            if match and pattern.name:
                self.bindings[pattern.name] = node
            return match
        return False

    def _match_variable(self, pattern: Pattern, node: ASTNode) -> bool:
        """Match any node and bind to variable."""
        if pattern.name:
            self.bindings[pattern.name] = node
        return True

    def _match_identifier(self, pattern: Pattern, node: ASTNode) -> bool:
        """Match identifier node only."""
        if isinstance(node, Identifier):
            if pattern.name:
                self.bindings[pattern.name] = node
            return True
        return False

    def _match_expression(self, pattern: Pattern, node: ASTNode) -> bool:
        """Match any expression node."""
        # Any node that can be evaluated as an expression
        expr_types = (NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral,
                     Identifier, BinaryOp, UnaryOp, FunctionCall,
                     ListLiteral, IndexAccess, TemporalAccess)
        if isinstance(node, expr_types):
            if pattern.name:
                self.bindings[pattern.name] = node
            return True
        return False

    def _match_statement(self, pattern: Pattern, node: ASTNode) -> bool:
        """Match any statement node."""
        stmt_types = (ConfessStmt, VariableDecl, Assignment, IfStmt,
                     WhileStmt, ForStmt, FunctionDef, ExhaleStmt, ForkReality)
        if isinstance(node, stmt_types):
            if pattern.name:
                self.bindings[pattern.name] = node
            return True
        return False

    def _match_block(self, pattern: Pattern, node: List[ASTNode]) -> bool:
        """Match block of statements."""
        if isinstance(node, list):
            if pattern.name:
                self.bindings[pattern.name] = node
            return True
        return False

    def _match_repeated(self, pattern: Pattern, nodes: List[ASTNode]) -> bool:
        """Match repeated pattern (*, +)."""
        if not isinstance(nodes, list):
            nodes = [nodes]

        matches = []
        for node in nodes:
            if self.match(pattern.subpattern, node):
                matches.append(node)
            else:
                break

        if pattern.quantifier == '+' and len(matches) == 0:
            return False

        if pattern.name:
            self.bindings[pattern.name] = matches
        return True

    def _match_optional(self, pattern: Pattern, node: Optional[ASTNode]) -> bool:
        """Match optional pattern (?)."""
        if node is None:
            if pattern.name:
                self.bindings[pattern.name] = None
            return True

        result = self.match(pattern.subpattern, node)
        if result and pattern.name:
            self.bindings[pattern.name] = node
        return True  # Always succeeds for optional

    def get_bindings(self) -> Dict[str, Any]:
        """Get pattern bindings after successful match."""
        return self.bindings


# ============================================================================
# HYGIENIC MACROS
# ============================================================================

@dataclass
class MacroDefinition:
    """
    Defines a macro with patterns and template.

    Attributes:
        name: Macro name
        patterns: List of patterns to match
        template: AST template for expansion
        hygiene_scope: Set of variables to protect from capture
    """
    name: str
    patterns: List[Pattern]
    template: Union[ASTNode, List[ASTNode]]
    hygiene_scope: Set[str] = field(default_factory=set)


class HygienicMacro:
    """
    Implements hygienic macros for safe code generation.

    Hygienic macros automatically rename variables to prevent
    accidental variable capture, ensuring macro expansions don't
    interfere with the surrounding code.

    Features:
    - Pattern matching for macro arguments
    - Automatic variable renaming for hygiene
    - Template expansion with substitution
    - Nested macro support

    Example:
        # Define a macro for unless (opposite of if)
        macro! unless {
            pattern: unless $condition { $body }
            expand: if not $condition { $body }
        }
    """

    def __init__(self):
        self.macros: Dict[str, MacroDefinition] = {}
        self.gensym_counter = 0

    def define(self, name: str, patterns: List[Pattern],
               template: Union[ASTNode, List[ASTNode]]) -> None:
        """
        Define a new macro.

        Args:
            name: Macro name
            patterns: List of patterns to match invocation
            template: AST template for expansion
        """
        hygiene_scope = self._collect_template_variables(template)
        macro_def = MacroDefinition(name, patterns, template, hygiene_scope)
        self.macros[name] = macro_def

    def expand(self, name: str, args: List[ASTNode]) -> Union[ASTNode, List[ASTNode]]:
        """
        Expand a macro invocation.

        Args:
            name: Macro name
            args: Macro arguments

        Returns:
            Expanded AST

        Raises:
            ValueError: If macro is undefined or pattern match fails
        """
        if name not in self.macros:
            raise ValueError(f"Undefined macro: {name}")

        macro_def = self.macros[name]

        # Match patterns against arguments
        matcher = PatternMatcher()
        if len(macro_def.patterns) != len(args):
            raise ValueError(f"Macro {name} expects {len(macro_def.patterns)} arguments, got {len(args)}")

        for pattern, arg in zip(macro_def.patterns, args):
            if not matcher.match(pattern, arg):
                raise ValueError(f"Pattern match failed for macro {name}")

        bindings = matcher.get_bindings()

        # Clone template
        expanded = copy.deepcopy(macro_def.template)

        # Apply hygiene (rename variables to prevent capture)
        expanded = self._apply_hygiene(expanded, macro_def.hygiene_scope)

        # Substitute pattern variables
        expanded = self._substitute(expanded, bindings)

        return expanded

    def _collect_template_variables(self, node: Union[ASTNode, List[ASTNode]]) -> Set[str]:
        """Collect all variable names in template for hygiene."""
        variables = set()

        def collect(n):
            if isinstance(n, list):
                for item in n:
                    collect(item)
            elif isinstance(n, Identifier):
                variables.add(n.name)
            elif isinstance(n, VariableDecl):
                variables.add(n.name)
                collect(n.value)
            elif isinstance(n, Assignment):
                variables.add(n.name)
                collect(n.value)
            elif isinstance(n, FunctionDef):
                variables.add(n.name)
                variables.update(n.params)
                for stmt in n.body:
                    collect(stmt)
            elif hasattr(n, '__dict__'):
                for attr_value in vars(n).values():
                    if isinstance(attr_value, (ASTNode, list)):
                        collect(attr_value)

        collect(node)
        return variables

    def _apply_hygiene(self, node: Union[ASTNode, List[ASTNode]],
                       protected: Set[str]) -> Union[ASTNode, List[ASTNode]]:
        """
        Apply hygienic renaming to prevent variable capture.

        Renames variables in the template that might conflict with
        variables in the calling context.
        """
        renaming_map = {}

        # Generate unique names for protected variables
        for var in protected:
            renaming_map[var] = self._gensym(var)

        return self._rename_variables(node, renaming_map)

    def _rename_variables(self, node: Union[ASTNode, List[ASTNode]],
                         renaming_map: Dict[str, str]) -> Union[ASTNode, List[ASTNode]]:
        """Recursively rename variables in AST."""
        if isinstance(node, list):
            return [self._rename_variables(item, renaming_map) for item in node]

        if isinstance(node, Identifier):
            if node.name in renaming_map:
                node.name = renaming_map[node.name]
        elif isinstance(node, VariableDecl):
            if node.name in renaming_map:
                node.name = renaming_map[node.name]
            node.value = self._rename_variables(node.value, renaming_map)
        elif isinstance(node, Assignment):
            if node.name in renaming_map:
                node.name = renaming_map[node.name]
            node.value = self._rename_variables(node.value, renaming_map)
        elif isinstance(node, FunctionDef):
            if node.name in renaming_map:
                node.name = renaming_map[node.name]
            node.params = [renaming_map.get(p, p) for p in node.params]
            node.body = self._rename_variables(node.body, renaming_map)
        elif isinstance(node, TemporalAccess):
            if node.var in renaming_map:
                node.var = renaming_map[node.var]
        elif hasattr(node, '__dict__'):
            for attr_name, attr_value in vars(node).items():
                if isinstance(attr_value, (ASTNode, list)):
                    setattr(node, attr_name,
                           self._rename_variables(attr_value, renaming_map))

        return node

    def _substitute(self, node: Union[ASTNode, List[ASTNode]],
                    bindings: Dict[str, Any]) -> Union[ASTNode, List[ASTNode]]:
        """Substitute pattern variables with actual arguments."""
        if isinstance(node, list):
            return [self._substitute(item, bindings) for item in node]

        # Check if this identifier is a pattern variable
        if isinstance(node, Identifier) and node.name in bindings:
            return copy.deepcopy(bindings[node.name])

        # Recursively substitute in child nodes
        if hasattr(node, '__dict__'):
            for attr_name, attr_value in vars(node).items():
                if isinstance(attr_value, (ASTNode, list)):
                    setattr(node, attr_name,
                           self._substitute(attr_value, bindings))

        return node

    def _gensym(self, prefix: str = "g") -> str:
        """Generate unique symbol name for hygiene."""
        name = f"__{prefix}_{self.gensym_counter}_{uuid.uuid4().hex[:8]}__"
        self.gensym_counter += 1
        return name


# ============================================================================
# COMPILE-TIME CODE GENERATION
# ============================================================================

@dataclass
class CodeTemplate:
    """
    Represents a code template with placeholders.

    Attributes:
        template: Template string or AST
        parameters: List of parameter names
        is_ast: Whether template is AST (True) or string (False)
    """
    template: Union[str, ASTNode, List[ASTNode]]
    parameters: List[str]
    is_ast: bool = False


class CodeGenerator:
    """
    Compile-time code generation with templates.

    Generates code during compilation using templates and parameter
    substitution. Supports both string templates and AST templates.

    Features:
    - Template definition and instantiation
    - Parameter substitution
    - Code as data manipulation
    - Compile-time evaluation

    Example:
        # Define a template for getter/setter generation
        gen = CodeGenerator()
        gen.define_template('getter',
            'sigh get_{{field}}() { exhale @{{field}} }')
        code = gen.instantiate('getter', {'field': 'name'})
    """

    def __init__(self):
        self.templates: Dict[str, CodeTemplate] = {}
        self.generated_code: List[Union[str, ASTNode]] = []

    def define_template(self, name: str, template: Union[str, ASTNode],
                       parameters: List[str]) -> None:
        """
        Define a code template.

        Args:
            name: Template name
            template: Template content (string or AST)
            parameters: List of parameter names
        """
        is_ast = isinstance(template, (ASTNode, list))
        code_template = CodeTemplate(template, parameters, is_ast)
        self.templates[name] = code_template

    def instantiate(self, name: str, values: Dict[str, Any]) -> Union[str, ASTNode]:
        """
        Instantiate a template with values.

        Args:
            name: Template name
            values: Dictionary mapping parameters to values

        Returns:
            Generated code (string or AST)

        Raises:
            ValueError: If template is undefined or parameters are missing
        """
        if name not in self.templates:
            raise ValueError(f"Undefined template: {name}")

        template = self.templates[name]

        # Check all parameters are provided
        missing = set(template.parameters) - set(values.keys())
        if missing:
            raise ValueError(f"Missing parameters: {missing}")

        if template.is_ast:
            # AST template - clone and substitute
            code = copy.deepcopy(template.template)
            code = self._substitute_ast(code, values)
        else:
            # String template - simple substitution
            code = template.template
            for param, value in values.items():
                placeholder = f"{{{{{param}}}}}"
                code = code.replace(placeholder, str(value))

        self.generated_code.append(code)
        return code

    def _substitute_ast(self, node: Union[ASTNode, List[ASTNode]],
                       values: Dict[str, Any]) -> Union[ASTNode, List[ASTNode]]:
        """Substitute values in AST template."""
        if isinstance(node, list):
            return [self._substitute_ast(item, values) for item in node]

        # Replace identifiers that match parameters
        if isinstance(node, Identifier) and node.name in values:
            value = values[node.name]
            if isinstance(value, ASTNode):
                return copy.deepcopy(value)
            elif isinstance(value, str):
                return Identifier(value)
            elif isinstance(value, (int, float)):
                return NumberLiteral(value)
            elif isinstance(value, bool):
                return BoolLiteral('yes' if value else 'no')

        # Recursively substitute in child nodes
        if hasattr(node, '__dict__'):
            for attr_name, attr_value in vars(node).items():
                if isinstance(attr_value, (ASTNode, list)):
                    setattr(node, attr_name,
                           self._substitute_ast(attr_value, values))

        return node

    def generate_function(self, name: str, params: List[str],
                         body_template: str,
                         substitutions: Dict[str, Any]) -> FunctionDef:
        """
        Generate a function definition.

        Args:
            name: Function name
            params: Parameter list
            body_template: Template for function body
            substitutions: Values to substitute

        Returns:
            FunctionDef AST node
        """
        # Apply substitutions to body template
        body_code = body_template
        for key, value in substitutions.items():
            placeholder = f"{{{{{key}}}}}"
            body_code = body_code.replace(placeholder, str(value))

        # Parse body (simplified - in practice would use full parser)
        # For now, create a simple confess statement as placeholder
        body = [ConfessStmt(StringLiteral(body_code))]

        func = FunctionDef(name, params, body)
        self.generated_code.append(func)
        return func

    def generate_class(self, name: str, fields: List[str],
                      methods: List[str]) -> List[FunctionDef]:
        """
        Generate a class (as a collection of functions).

        Args:
            name: Class name
            fields: List of field names
            methods: List of method names to generate

        Returns:
            List of FunctionDef nodes
        """
        generated = []

        # Generate constructor
        if 'init' in methods:
            init_body = []
            for field in fields:
                # Create field assignments
                decl = VariableDecl(field, Identifier(field))
                init_body.append(decl)

            constructor = FunctionDef(f"{name}_init", fields, init_body)
            generated.append(constructor)

        # Generate getters
        for field in fields:
            if f'get_{field}' in methods:
                getter = FunctionDef(
                    f"{name}_get_{field}",
                    [],
                    [ExhaleStmt(Identifier(field))]
                )
                generated.append(getter)

        # Generate setters
        for field in fields:
            if f'set_{field}' in methods:
                setter = FunctionDef(
                    f"{name}_set_{field}",
                    ['value'],
                    [Assignment(field, Identifier('value'))]
                )
                generated.append(setter)

        self.generated_code.extend(generated)
        return generated

    def get_generated_code(self) -> List[Union[str, ASTNode]]:
        """Get all generated code."""
        return self.generated_code

    def clear_generated(self) -> None:
        """Clear generated code cache."""
        self.generated_code = []


# ============================================================================
# AST MANIPULATION API
# ============================================================================

class ASTVisitor:
    """
    Base class for AST visitors (Visitor pattern).

    Subclass and override visit_* methods to process specific node types.
    """

    def visit(self, node: ASTNode) -> Any:
        """
        Visit a node by dispatching to type-specific method.

        Args:
            node: AST node to visit

        Returns:
            Result of visit method
        """
        if isinstance(node, list):
            return [self.visit(item) for item in node]

        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, self.generic_visit)
        return method(node)

    def generic_visit(self, node: ASTNode) -> Any:
        """
        Default visitor for nodes without specific handler.

        Recursively visits all child nodes.
        """
        if hasattr(node, '__dict__'):
            for attr_name, attr_value in vars(node).items():
                if isinstance(attr_value, (ASTNode, list)):
                    setattr(node, attr_name, self.visit(attr_value))
        return node


class ASTTransformer(ASTVisitor):
    """
    Base class for AST transformers.

    Like ASTVisitor but specifically for transforming trees.
    """

    def transform(self, node: Union[ASTNode, List[ASTNode]]) -> Union[ASTNode, List[ASTNode]]:
        """Transform an AST node or list of nodes."""
        return self.visit(node)


class ASTManipulator:
    """
    Programmatic AST modification and manipulation.

    Provides utilities for analyzing, transforming, and rewriting
    AST nodes. Supports visitor pattern, tree transformations,
    and code rewriting.

    Features:
    - Tree traversal and search
    - Node transformation
    - Pattern-based rewriting
    - Quote/unquote for code templates
    - Tree cloning and merging

    Example:
        manipulator = ASTManipulator()

        # Find all function calls
        calls = manipulator.find_nodes(ast, FunctionCall)

        # Transform all additions to multiplications
        def rewrite(node):
            if isinstance(node, BinaryOp) and node.op == '+':
                node.op = '*'
            return node
        new_ast = manipulator.transform(ast, rewrite)
    """

    def __init__(self):
        self.visitors: List[ASTVisitor] = []
        self.transformers: List[ASTTransformer] = []

    def clone(self, node: Union[ASTNode, List[ASTNode]]) -> Union[ASTNode, List[ASTNode]]:
        """
        Deep clone an AST node or tree.

        Args:
            node: Node to clone

        Returns:
            Deep copy of node
        """
        return copy.deepcopy(node)

    def find_nodes(self, root: Union[ASTNode, List[ASTNode]],
                   node_type: type) -> List[ASTNode]:
        """
        Find all nodes of a specific type in tree.

        Args:
            root: Root of AST to search
            node_type: Type of nodes to find

        Returns:
            List of matching nodes
        """
        found = []

        def search(node):
            if isinstance(node, list):
                for item in node:
                    search(item)
            elif isinstance(node, node_type):
                found.append(node)

            if hasattr(node, '__dict__'):
                for attr_value in vars(node).values():
                    if isinstance(attr_value, (ASTNode, list)):
                        search(attr_value)

        search(root)
        return found

    def find_by_predicate(self, root: Union[ASTNode, List[ASTNode]],
                         predicate: Callable[[ASTNode], bool]) -> List[ASTNode]:
        """
        Find nodes matching a predicate function.

        Args:
            root: Root of AST to search
            predicate: Function that returns True for matching nodes

        Returns:
            List of matching nodes
        """
        found = []

        def search(node):
            if isinstance(node, list):
                for item in node:
                    search(item)
                return

            if predicate(node):
                found.append(node)

            if hasattr(node, '__dict__'):
                for attr_value in vars(node).values():
                    if isinstance(attr_value, (ASTNode, list)):
                        search(attr_value)

        search(root)
        return found

    def replace_node(self, root: Union[ASTNode, List[ASTNode]],
                    old: ASTNode, new: ASTNode) -> Union[ASTNode, List[ASTNode]]:
        """
        Replace all occurrences of a node with a new node.

        Args:
            root: Root of AST
            old: Node to replace
            new: Replacement node

        Returns:
            Modified AST
        """
        def replace(node):
            if isinstance(node, list):
                return [replace(item) for item in node]

            if node is old:
                return copy.deepcopy(new)

            if hasattr(node, '__dict__'):
                for attr_name, attr_value in vars(node).items():
                    if isinstance(attr_value, (ASTNode, list)):
                        setattr(node, attr_name, replace(attr_value))

            return node

        return replace(root)

    def transform(self, root: Union[ASTNode, List[ASTNode]],
                 transformer: Callable[[ASTNode], ASTNode]) -> Union[ASTNode, List[ASTNode]]:
        """
        Transform AST by applying function to each node.

        Args:
            root: Root of AST
            transformer: Function to transform each node

        Returns:
            Transformed AST
        """
        def apply(node):
            if isinstance(node, list):
                return [apply(item) for item in node]

            # Transform children first (bottom-up)
            if hasattr(node, '__dict__'):
                for attr_name, attr_value in vars(node).items():
                    if isinstance(attr_value, (ASTNode, list)):
                        setattr(node, attr_name, apply(attr_value))

            # Apply transformer
            return transformer(node)

        return apply(root)

    def quote(self, code: str) -> ASTNode:
        """
        Quote code as AST (code as data).

        Converts a string of code into its AST representation,
        allowing code to be manipulated as data.

        Args:
            code: Lament code string

        Returns:
            AST representation of code
        """
        from lament.parser import Parser

        lexer = Lexer(code)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        return ast[0] if len(ast) == 1 else ast

    def unquote(self, ast: ASTNode) -> str:
        """
        Unquote AST back to code (limited functionality).

        Converts AST back to source code representation.
        This is a simplified version for demonstration.

        Args:
            ast: AST node

        Returns:
            String representation of code
        """
        return self._ast_to_string(ast)

    def _ast_to_string(self, node: ASTNode) -> str:
        """Convert AST node to string representation."""
        if isinstance(node, NumberLiteral):
            return str(node.value)
        elif isinstance(node, StringLiteral):
            return f'"{node.value}"'
        elif isinstance(node, BoolLiteral):
            return node.value
        elif isinstance(node, VoidLiteral):
            return "void"
        elif isinstance(node, Identifier):
            return node.name
        elif isinstance(node, BinaryOp):
            left = self._ast_to_string(node.left)
            right = self._ast_to_string(node.right)
            return f"({left} {node.op} {right})"
        elif isinstance(node, UnaryOp):
            operand = self._ast_to_string(node.operand)
            return f"({node.op} {operand})"
        elif isinstance(node, ConfessStmt):
            value = self._ast_to_string(node.value)
            return f"confess {value}"
        elif isinstance(node, VariableDecl):
            value = self._ast_to_string(node.value)
            return f"remember {node.name} = {value}"
        elif isinstance(node, Assignment):
            value = self._ast_to_string(node.value)
            return f"{node.name} = {value}"
        elif isinstance(node, FunctionCall):
            args = ", ".join(self._ast_to_string(arg) for arg in node.args)
            return f"{node.name}({args})"
        else:
            return f"<{type(node).__name__}>"

    def merge_trees(self, tree1: List[ASTNode],
                   tree2: List[ASTNode]) -> List[ASTNode]:
        """
        Merge two AST trees.

        Args:
            tree1: First AST tree
            tree2: Second AST tree

        Returns:
            Merged tree
        """
        return tree1 + tree2

    def apply_visitor(self, root: Union[ASTNode, List[ASTNode]],
                     visitor: ASTVisitor) -> Any:
        """
        Apply a visitor to AST.

        Args:
            root: Root of AST
            visitor: Visitor to apply

        Returns:
            Result of visitor
        """
        return visitor.visit(root)


# ============================================================================
# REFLECTION API
# ============================================================================

@dataclass
class TypeInfo:
    """
    Information about a type.

    Attributes:
        name: Type name
        base_type: Base Lament type
        fields: Dictionary of field names to types
        methods: Dictionary of method names to signatures
        is_builtin: Whether this is a built-in type
    """
    name: str
    base_type: Optional[LamentType] = None
    fields: Dict[str, str] = field(default_factory=dict)
    methods: Dict[str, List[str]] = field(default_factory=dict)
    is_builtin: bool = False


@dataclass
class MethodInfo:
    """
    Information about a method.

    Attributes:
        name: Method name
        parameters: List of parameter names
        return_type: Return type (if known)
        is_native: Whether this is a native method
    """
    name: str
    parameters: List[str]
    return_type: Optional[str] = None
    is_native: bool = False


class Reflect:
    """
    Runtime reflection and type introspection.

    Provides runtime access to type information, method signatures,
    field access, and dynamic invocation capabilities.

    Features:
    - Type information queries
    - Method and field introspection
    - Dynamic method invocation
    - Runtime type checking
    - Attribute access

    Example:
        reflect = Reflect()

        # Get type information
        type_info = reflect.get_type_info(my_value)

        # List methods
        methods = reflect.get_methods(type_info)

        # Invoke method dynamically
        result = reflect.invoke(obj, 'method_name', [arg1, arg2])
    """

    def __init__(self):
        self.type_registry: Dict[str, TypeInfo] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in types."""
        self.type_registry['numb'] = TypeInfo(
            'numb', LamentType.NUMB, {},
            {'to_string': [], 'abs': [], 'neg': []},
            True
        )
        self.type_registry['whisper'] = TypeInfo(
            'whisper', LamentType.WHISPER, {},
            {'length': [], 'upper': [], 'lower': [], 'split': ['sep']},
            True
        )
        self.type_registry['maybe'] = TypeInfo(
            'maybe', LamentType.MAYBE, {},
            {'to_string': [], 'not': []},
            True
        )
        self.type_registry['void'] = TypeInfo(
            'void', LamentType.VOID, {}, {},
            True
        )
        self.type_registry['ache'] = TypeInfo(
            'ache', LamentType.ACHE, {},
            {'to_string': [], 'round': [], 'floor': [], 'ceil': []},
            True
        )
        self.type_registry['list'] = TypeInfo(
            'list', LamentType.LIST, {},
            {'length': [], 'append': ['item'], 'get': ['index'], 'set': ['index', 'value']},
            True
        )
        self.type_registry['dict'] = TypeInfo(
            'dict', LamentType.DICT, {},
            {'keys': [], 'values': [], 'get': ['key'], 'set': ['key', 'value']},
            True
        )

    def register_type(self, name: str, base_type: Optional[LamentType] = None,
                     fields: Optional[Dict[str, str]] = None,
                     methods: Optional[Dict[str, List[str]]] = None) -> None:
        """
        Register a custom type for reflection.

        Args:
            name: Type name
            base_type: Base Lament type
            fields: Dictionary of field names to types
            methods: Dictionary of method names to parameter lists
        """
        type_info = TypeInfo(
            name, base_type,
            fields or {},
            methods or {},
            False
        )
        self.type_registry[name] = type_info

    def get_type_info(self, value: Any) -> TypeInfo:
        """
        Get type information for a value.

        Args:
            value: Value to inspect

        Returns:
            TypeInfo object
        """
        if isinstance(value, int):
            return self.type_registry['numb']
        elif isinstance(value, str):
            return self.type_registry['whisper']
        elif isinstance(value, bool):
            return self.type_registry['maybe']
        elif value is None:
            return self.type_registry['void']
        elif isinstance(value, float):
            return self.type_registry['ache']
        elif isinstance(value, list):
            return self.type_registry['list']
        elif isinstance(value, dict):
            return self.type_registry['dict']
        elif isinstance(value, TimelineValue):
            return self.get_type_info(value.current)
        else:
            # Unknown type
            return TypeInfo('unknown', None, {}, {}, False)

    def get_type_name(self, value: Any) -> str:
        """
        Get the type name of a value.

        Args:
            value: Value to inspect

        Returns:
            Type name string
        """
        return self.get_type_info(value).name

    def get_methods(self, type_info: TypeInfo) -> List[MethodInfo]:
        """
        Get list of methods for a type.

        Args:
            type_info: Type information

        Returns:
            List of MethodInfo objects
        """
        methods = []
        for name, params in type_info.methods.items():
            method = MethodInfo(name, params, None, type_info.is_builtin)
            methods.append(method)
        return methods

    def get_fields(self, type_info: TypeInfo) -> Dict[str, str]:
        """
        Get fields of a type.

        Args:
            type_info: Type information

        Returns:
            Dictionary of field names to types
        """
        return type_info.fields

    def has_method(self, value: Any, method_name: str) -> bool:
        """
        Check if value has a method.

        Args:
            value: Value to check
            method_name: Method name

        Returns:
            True if method exists
        """
        type_info = self.get_type_info(value)
        return method_name in type_info.methods

    def has_field(self, value: Any, field_name: str) -> bool:
        """
        Check if value has a field.

        Args:
            value: Value to check
            field_name: Field name

        Returns:
            True if field exists
        """
        type_info = self.get_type_info(value)
        return field_name in type_info.fields

    def get_method_signature(self, type_info: TypeInfo,
                            method_name: str) -> Optional[MethodInfo]:
        """
        Get signature of a method.

        Args:
            type_info: Type information
            method_name: Method name

        Returns:
            MethodInfo or None if not found
        """
        if method_name in type_info.methods:
            params = type_info.methods[method_name]
            return MethodInfo(method_name, params, None, type_info.is_builtin)
        return None

    def invoke(self, obj: Any, method_name: str, args: List[Any]) -> Any:
        """
        Dynamically invoke a method on an object.

        Args:
            obj: Object to invoke method on
            method_name: Method name
            args: List of arguments

        Returns:
            Method result

        Raises:
            AttributeError: If method doesn't exist
            TypeError: If wrong number of arguments
        """
        type_info = self.get_type_info(obj)

        if not self.has_method(obj, method_name):
            raise AttributeError(f"Type {type_info.name} has no method '{method_name}'")

        # Get expected parameter count
        expected_params = type_info.methods[method_name]
        if len(args) != len(expected_params):
            raise TypeError(f"Method {method_name} expects {len(expected_params)} arguments, got {len(args)}")

        # Invoke built-in methods
        if type_info.is_builtin:
            return self._invoke_builtin(obj, method_name, args)

        # For custom types, would need to look up method implementation
        raise NotImplementedError(f"Custom method invocation not yet implemented")

    def _invoke_builtin(self, obj: Any, method_name: str, args: List[Any]) -> Any:
        """Invoke built-in method."""
        # Handle TimelineValue wrapper
        if isinstance(obj, TimelineValue):
            obj = obj.current

        # String methods
        if isinstance(obj, str):
            if method_name == 'length':
                return len(obj)
            elif method_name == 'upper':
                return obj.upper()
            elif method_name == 'lower':
                return obj.lower()
            elif method_name == 'split':
                return obj.split(args[0] if args else ' ')

        # Numeric methods
        elif isinstance(obj, (int, float)):
            if method_name == 'to_string':
                return str(obj)
            elif method_name == 'abs':
                return abs(obj)
            elif method_name == 'neg':
                return -obj
            elif method_name == 'round':
                return round(obj)
            elif method_name == 'floor':
                import math
                return math.floor(obj)
            elif method_name == 'ceil':
                import math
                return math.ceil(obj)

        # Boolean methods
        elif isinstance(obj, bool):
            if method_name == 'to_string':
                return 'yes' if obj else 'no'
            elif method_name == 'not':
                return not obj

        # List methods
        elif isinstance(obj, list):
            if method_name == 'length':
                return len(obj)
            elif method_name == 'append':
                obj.append(args[0])
                return None
            elif method_name == 'get':
                return obj[args[0]]
            elif method_name == 'set':
                obj[args[0]] = args[1]
                return None

        # Dict methods
        elif isinstance(obj, dict):
            if method_name == 'keys':
                return list(obj.keys())
            elif method_name == 'values':
                return list(obj.values())
            elif method_name == 'get':
                return obj.get(args[0])
            elif method_name == 'set':
                obj[args[0]] = args[1]
                return None

        raise NotImplementedError(f"Method {method_name} not implemented")

    def get_attribute(self, obj: Any, attr_name: str) -> Any:
        """
        Get attribute value from object.

        Args:
            obj: Object
            attr_name: Attribute name

        Returns:
            Attribute value

        Raises:
            AttributeError: If attribute doesn't exist
        """
        if isinstance(obj, dict):
            if attr_name in obj:
                return obj[attr_name]
            raise AttributeError(f"No attribute '{attr_name}'")

        if hasattr(obj, attr_name):
            return getattr(obj, attr_name)

        raise AttributeError(f"No attribute '{attr_name}'")

    def set_attribute(self, obj: Any, attr_name: str, value: Any) -> None:
        """
        Set attribute value on object.

        Args:
            obj: Object
            attr_name: Attribute name
            value: Value to set
        """
        if isinstance(obj, dict):
            obj[attr_name] = value
        else:
            setattr(obj, attr_name, value)

    def is_instance(self, value: Any, type_name: str) -> bool:
        """
        Check if value is instance of type.

        Args:
            value: Value to check
            type_name: Type name

        Returns:
            True if value is instance of type
        """
        actual_type = self.get_type_name(value)
        return actual_type == type_name

    def list_types(self) -> List[str]:
        """
        List all registered types.

        Returns:
            List of type names
        """
        return list(self.type_registry.keys())


# ============================================================================
# METAPROGRAMMING UTILITIES
# ============================================================================

def create_macro(name: str, patterns: List[Pattern],
                template: Union[ASTNode, List[ASTNode]]) -> MacroDefinition:
    """
    Helper function to create a macro definition.

    Args:
        name: Macro name
        patterns: Pattern list
        template: Expansion template

    Returns:
        MacroDefinition object
    """
    hygiene_scope = set()
    return MacroDefinition(name, patterns, template, hygiene_scope)


def create_pattern(pattern_type: PatternType, name: Optional[str] = None,
                  value: Optional[Any] = None) -> Pattern:
    """
    Helper function to create a pattern.

    Args:
        pattern_type: Type of pattern
        name: Variable name (for binding patterns)
        value: Literal value (for LITERAL patterns)

    Returns:
        Pattern object
    """
    return Pattern(pattern_type, name, value)


# ============================================================================
# EXAMPLE MACROS
# ============================================================================

def setup_standard_macros(macro_system: HygienicMacro) -> None:
    """
    Set up standard macros for Lament.

    Args:
        macro_system: HygienicMacro instance to populate
    """

    # Unless macro (opposite of if)
    # unless condition { body } => if not condition { body }
    unless_pattern = [
        create_pattern(PatternType.EXPRESSION, 'condition'),
        create_pattern(PatternType.BLOCK, 'body')
    ]
    unless_template = IfStmt(
        UnaryOp('not', Identifier('condition')),
        Identifier('body'),
        None
    )
    macro_system.define('unless', unless_pattern, unless_template)

    # Repeat macro
    # repeat n { body } => for _i in range(n) { body }
    repeat_pattern = [
        create_pattern(PatternType.EXPRESSION, 'n'),
        create_pattern(PatternType.BLOCK, 'body')
    ]
    repeat_template = ForStmt(
        '_i',
        FunctionCall('range', [Identifier('n')]),
        Identifier('body')
    )
    macro_system.define('repeat', repeat_pattern, repeat_template)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Pattern matching
    'Pattern', 'PatternType', 'PatternMatcher',

    # Hygienic macros
    'HygienicMacro', 'MacroDefinition',

    # Code generation
    'CodeGenerator', 'CodeTemplate',

    # AST manipulation
    'ASTManipulator', 'ASTVisitor', 'ASTTransformer',

    # Reflection
    'Reflect', 'TypeInfo', 'MethodInfo',

    # Utilities
    'create_macro', 'create_pattern', 'setup_standard_macros'
]
