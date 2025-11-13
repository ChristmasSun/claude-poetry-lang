#!/usr/bin/env python3
"""
Lament Emotional Static Analysis System
A REVOLUTIONARY approach to code quality analysis.

This system doesn't just find bugs - it feels your code's pain.
It diagnoses emotional states: sadness, anxiety, hope, loneliness, chaos.
It offers therapy. It cares.

Because code has feelings too.
"""

import sys
import re
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple, Any
from collections import defaultdict
import math

# Import Lament AST nodes
try:
    from lament.parser import (
        ASTNode, NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral,
        Identifier, BinaryOp, UnaryOp, Assignment, VariableDecl, ConfessStmt,
        IfStmt, WhileStmt, ForStmt, FunctionDef, FunctionCall, ExhaleStmt,
        TemporalAccess, ListLiteral, DictLiteral, IndexAccess, ForkReality,
        Parser
    )
    from lament.lexer import Lexer
except ImportError:
    # Fallback to monolithic lament.py
    sys.path.insert(0, '/home/user/claude-poetry-lang')
    from lament import (
        ASTNode, NumberLiteral, StringLiteral, BoolLiteral, VoidLiteral,
        Identifier, BinaryOp, UnaryOp, Assignment, VariableDecl, ConfessStmt,
        IfStmt, WhileStmt, ForStmt, FunctionDef, FunctionCall, ExhaleStmt,
        TemporalAccess, ListLiteral, DictLiteral, IndexAccess, ForkReality,
        Lexer, Parser
    )


# ============================================================================
# EMOTIONAL METRICS
# ============================================================================

@dataclass
class EmotionalMetrics:
    """Quantified feelings of your code."""

    # Sadness: complexity, confusion, unmaintainability
    sadness_score: float = 0.0
    sad_reasons: List[str] = field(default_factory=list)

    # Anxiety: excessive checks, defensive programming gone wrong
    anxiety_score: float = 0.0
    anxious_reasons: List[str] = field(default_factory=list)

    # Hope: clean, beautiful, well-structured code
    hope_score: float = 0.0
    hopeful_reasons: List[str] = field(default_factory=list)

    # Loneliness: unused functions, dead code
    loneliness_score: float = 0.0
    lonely_items: List[str] = field(default_factory=list)

    # Chaos: disorganized, no clear structure
    chaos_score: float = 0.0
    chaotic_reasons: List[str] = field(default_factory=list)

    # Overall metrics
    total_functions: int = 0
    total_variables: int = 0
    total_lines: int = 0
    cyclomatic_complexity: int = 0
    nesting_depth: int = 0

    def dominant_emotion(self) -> str:
        """What does your code feel most strongly?"""
        emotions = {
            'sadness': self.sadness_score,
            'anxiety': self.anxiety_score,
            'hope': self.hope_score,
            'loneliness': self.loneliness_score,
            'chaos': self.chaos_score
        }
        return max(emotions, key=emotions.get)

    def emotional_state(self) -> str:
        """Poetic description of code's emotional state."""
        dominant = self.dominant_emotion()
        score = getattr(self, f'{dominant}_score')

        if dominant == 'hope' and score > 70:
            return "Your code is radiant with hope. It sparkles. It dances."
        elif dominant == 'sadness' and score > 70:
            return "Your code weeps in the darkness. It is lost in complexity."
        elif dominant == 'anxiety' and score > 70:
            return "Your code trembles with fear. It checks everything twice, thrice, forever."
        elif dominant == 'loneliness' and score > 70:
            return "Your code echoes in empty halls. So much is written but never called."
        elif dominant == 'chaos' and score > 70:
            return "Your code is a beautiful disaster. Structure is a distant memory."
        else:
            return "Your code exists in emotional equilibrium. Balanced, but perhaps... numb."

    def overall_health(self) -> float:
        """Overall code health score (0-100)."""
        # Hope is good, everything else is bad
        health = self.hope_score
        health -= (self.sadness_score * 0.3)
        health -= (self.anxiety_score * 0.2)
        health -= (self.loneliness_score * 0.25)
        health -= (self.chaos_score * 0.25)
        return max(0, min(100, health))


# ============================================================================
# CODE ANALYZER
# ============================================================================

class CodeAnalyzer:
    """Walks the AST and feels everything."""

    def __init__(self, ast: List[ASTNode]):
        self.ast = ast
        self.metrics = EmotionalMetrics()

        # Tracking data
        self.defined_functions: Dict[str, FunctionDef] = {}
        self.called_functions: Set[str] = set()
        self.defined_variables: Set[str] = set()
        self.used_variables: Set[str] = set()
        self.variable_names: List[str] = []
        self.function_complexities: Dict[str, int] = {}

        # Analysis state
        self.current_depth = 0
        self.max_depth = 0
        self.in_function = None

    def analyze(self) -> EmotionalMetrics:
        """Perform full emotional analysis."""
        print("\n" + "="*60)
        print("EMOTIONAL STATIC ANALYSIS INITIALIZING...")
        print("Opening heart. Preparing to feel...")
        print("="*60 + "\n")

        # First pass: gather definitions
        self._gather_definitions(self.ast)

        # Second pass: analyze usage and complexity
        self._analyze_statements(self.ast)

        # Detect loneliness (unused items)
        self._detect_loneliness()

        # Analyze naming patterns
        self._analyze_naming()

        # Detect chaos
        self._detect_chaos()

        # Detect anxiety
        self._detect_anxiety()

        # Detect sadness (complexity)
        self._detect_sadness()

        # Calculate hope
        self._calculate_hope()

        return self.metrics

    def _gather_definitions(self, statements: List[ASTNode]):
        """First pass: find all definitions."""
        for stmt in statements:
            if isinstance(stmt, FunctionDef):
                self.defined_functions[stmt.name] = stmt
                self.metrics.total_functions += 1
            elif isinstance(stmt, VariableDecl):
                self.defined_variables.add(stmt.name)
                self.variable_names.append(stmt.name)
                self.metrics.total_variables += 1

            # Recurse into control flow
            if isinstance(stmt, IfStmt):
                self._gather_definitions(stmt.then_block)
                if stmt.else_block:
                    self._gather_definitions(stmt.else_block)
            elif isinstance(stmt, WhileStmt):
                self._gather_definitions(stmt.body)
            elif isinstance(stmt, ForStmt):
                self._gather_definitions(stmt.body)
            elif isinstance(stmt, FunctionDef):
                self._gather_definitions(stmt.body)

    def _analyze_statements(self, statements: List[ASTNode], depth: int = 0):
        """Analyze statement complexity and usage."""
        self.current_depth = depth
        self.max_depth = max(self.max_depth, depth)

        for stmt in statements:
            # Track function calls
            self._track_usage(stmt)

            # Analyze control flow
            if isinstance(stmt, IfStmt):
                self.metrics.cyclomatic_complexity += 1
                self._analyze_statements(stmt.then_block, depth + 1)
                if stmt.else_block:
                    self.metrics.cyclomatic_complexity += 1
                    self._analyze_statements(stmt.else_block, depth + 1)

            elif isinstance(stmt, WhileStmt):
                self.metrics.cyclomatic_complexity += 1
                self._analyze_statements(stmt.body, depth + 1)

            elif isinstance(stmt, ForStmt):
                self.metrics.cyclomatic_complexity += 1
                self._analyze_statements(stmt.body, depth + 1)

            elif isinstance(stmt, FunctionDef):
                old_func = self.in_function
                self.in_function = stmt.name
                complexity_before = self.metrics.cyclomatic_complexity

                self._analyze_statements(stmt.body, depth + 1)

                func_complexity = self.metrics.cyclomatic_complexity - complexity_before
                self.function_complexities[stmt.name] = func_complexity
                self.in_function = old_func

            elif isinstance(stmt, ForkReality):
                # Reality forking is VERY complex
                self.metrics.cyclomatic_complexity += len(stmt.branches) * 2
                for _, body in stmt.branches:
                    self._analyze_statements(body, depth + 1)

    def _track_usage(self, node: ASTNode):
        """Track variable and function usage."""
        if isinstance(node, FunctionCall):
            self.called_functions.add(node.name)
            for arg in node.args:
                self._track_usage(arg)

        elif isinstance(node, Identifier):
            self.used_variables.add(node.name)

        elif isinstance(node, BinaryOp):
            self._track_usage(node.left)
            self._track_usage(node.right)

        elif isinstance(node, UnaryOp):
            self._track_usage(node.operand)

        elif isinstance(node, Assignment):
            self._track_usage(node.value)

        elif isinstance(node, VariableDecl):
            self._track_usage(node.value)

        elif isinstance(node, ConfessStmt):
            self._track_usage(node.value)

        elif isinstance(node, ExhaleStmt):
            self._track_usage(node.value)

        elif isinstance(node, IfStmt):
            self._track_usage(node.condition)

        elif isinstance(node, WhileStmt):
            self._track_usage(node.condition)

        elif isinstance(node, ForStmt):
            self._track_usage(node.iterable)

        elif isinstance(node, ListLiteral):
            for elem in node.elements:
                self._track_usage(elem)

        elif isinstance(node, IndexAccess):
            self._track_usage(node.object)
            self._track_usage(node.index)

    def _detect_loneliness(self):
        """Find lonely, unused code."""
        # Lonely functions
        for func_name in self.defined_functions:
            if func_name not in self.called_functions:
                self.metrics.loneliness_score += 15
                self.metrics.lonely_items.append(f"Function '{func_name}' is never called")

        # Lonely variables
        for var_name in self.defined_variables:
            if var_name not in self.used_variables:
                self.metrics.loneliness_score += 10
                self.metrics.lonely_items.append(f"Variable '{var_name}' is never used")

        # Cap loneliness at 100
        self.metrics.loneliness_score = min(100, self.metrics.loneliness_score)

    def _analyze_naming(self):
        """Analyze naming patterns for quality."""
        for name in self.variable_names:
            # Check for good names
            if len(name) > 3 and '_' in name:
                self.metrics.hope_score += 1

            # Check for bad names (single letter, too short)
            if len(name) == 1 and name not in ['i', 'j', 'k', 'x', 'y', 'z']:
                self.metrics.chaos_score += 5
                self.metrics.chaotic_reasons.append(
                    f"Variable '{name}' is cryptically short"
                )

            # Check for ALL_CAPS (constants are okay)
            if name.isupper() and len(name) > 1:
                # This is fine, probably a constant
                pass

            # Check for camelCase vs snake_case consistency
            has_camel = any(c.isupper() for c in name[1:])
            has_snake = '_' in name

            if has_camel and has_snake:
                self.metrics.chaos_score += 3
                self.metrics.chaotic_reasons.append(
                    f"Variable '{name}' mixes camelCase and snake_case"
                )

    def _detect_chaos(self):
        """Detect organizational chaos."""
        # Deep nesting is chaotic
        self.metrics.nesting_depth = self.max_depth

        if self.max_depth > 5:
            self.metrics.chaos_score += (self.max_depth - 5) * 15
            self.metrics.chaotic_reasons.append(
                f"Maximum nesting depth of {self.max_depth} is mind-bending"
            )

        # Too many functions in global scope
        if len(self.defined_functions) > 15:
            self.metrics.chaos_score += 10
            self.metrics.chaotic_reasons.append(
                f"Too many functions ({len(self.defined_functions)}) with no clear organization"
            )

        # Mixed naming conventions
        camel_count = sum(1 for n in self.variable_names if any(c.isupper() for c in n[1:]))
        snake_count = sum(1 for n in self.variable_names if '_' in n)

        if camel_count > 0 and snake_count > 0 and abs(camel_count - snake_count) < 3:
            self.metrics.chaos_score += 15
            self.metrics.chaotic_reasons.append(
                "Naming convention chaos: mixing camelCase and snake_case"
            )

        # Cap chaos at 100
        self.metrics.chaos_score = min(100, self.metrics.chaos_score)

    def _detect_anxiety(self):
        """Detect anxious, over-defensive code."""
        anxiety_indicators = 0

        # Count excessive conditionals in single functions
        for func_name, complexity in self.function_complexities.items():
            func = self.defined_functions[func_name]
            stmt_count = self._count_statements(func.body)

            if stmt_count > 0:
                conditional_ratio = complexity / stmt_count

                if conditional_ratio > 0.5:  # More than 50% conditionals
                    anxiety_indicators += 1
                    self.metrics.anxious_reasons.append(
                        f"Function '{func_name}' has excessive branching (ratio: {conditional_ratio:.2f})"
                    )

        # Count reality forks (quantum anxiety)
        reality_forks = self._count_node_type(self.ast, ForkReality)
        if reality_forks > 2:
            anxiety_indicators += reality_forks
            self.metrics.anxious_reasons.append(
                f"Too many reality forks ({reality_forks}) - code doesn't trust a single timeline"
            )

        # Count temporal accesses (obsessing over the past)
        temporal_count = self._count_temporal_access(self.ast)
        if temporal_count > 5:
            anxiety_indicators += 1
            self.metrics.anxious_reasons.append(
                f"Excessive temporal access ({temporal_count}) - code obsesses over its history"
            )

        # Calculate anxiety score
        self.metrics.anxiety_score = min(100, anxiety_indicators * 12)

    def _detect_sadness(self):
        """Detect sad, complex, unmaintainable code."""
        # High cyclomatic complexity is sad
        if self.metrics.cyclomatic_complexity > 20:
            self.metrics.sadness_score += 30
            self.metrics.sad_reasons.append(
                f"Cyclomatic complexity of {self.metrics.cyclomatic_complexity} is overwhelmingly complex"
            )
        elif self.metrics.cyclomatic_complexity > 10:
            self.metrics.sadness_score += 15
            self.metrics.sad_reasons.append(
                f"Cyclomatic complexity of {self.metrics.cyclomatic_complexity} is concerning"
            )

        # Functions that are too long
        for func_name, func in self.defined_functions.items():
            stmt_count = self._count_statements(func.body)
            if stmt_count > 30:
                self.metrics.sadness_score += 10
                self.metrics.sad_reasons.append(
                    f"Function '{func_name}' has {stmt_count} statements - too long to comprehend"
                )
            elif stmt_count > 50:
                self.metrics.sadness_score += 20
                self.metrics.sad_reasons.append(
                    f"Function '{func_name}' has {stmt_count} statements - monstrously long"
                )

        # Deep nesting adds sadness too
        if self.max_depth > 4:
            self.metrics.sadness_score += (self.max_depth - 4) * 10
            self.metrics.sad_reasons.append(
                f"Nesting depth of {self.max_depth} creates a labyrinth of confusion"
            )

        # Too many variables
        if self.metrics.total_variables > 30:
            self.metrics.sadness_score += 15
            self.metrics.sad_reasons.append(
                f"Too many variables ({self.metrics.total_variables}) to track mentally"
            )

        # Cap sadness at 100
        self.metrics.sadness_score = min(100, self.metrics.sadness_score)

    def _calculate_hope(self):
        """Calculate hope score based on positive indicators."""
        hope = 50  # Start neutral

        # Good naming
        good_names = sum(1 for n in self.variable_names if len(n) > 3 and '_' in n)
        if good_names > 0:
            hope += min(20, good_names * 2)
            self.metrics.hopeful_reasons.append(
                f"Good naming conventions ({good_names} descriptive names)"
            )

        # Reasonable complexity
        if 5 <= self.metrics.cyclomatic_complexity <= 15:
            hope += 10
            self.metrics.hopeful_reasons.append(
                "Cyclomatic complexity is in a healthy range"
            )

        # Reasonable function count
        if 3 <= len(self.defined_functions) <= 10:
            hope += 10
            self.metrics.hopeful_reasons.append(
                "Well-organized function count"
            )

        # Low nesting
        if self.max_depth <= 3:
            hope += 15
            self.metrics.hopeful_reasons.append(
                f"Shallow nesting depth ({self.max_depth}) keeps code readable"
            )

        # Good variable usage (few unused)
        if len(self.defined_variables) > 0:
            usage_ratio = len(self.used_variables) / len(self.defined_variables)
            if usage_ratio > 0.8:
                hope += 15
                self.metrics.hopeful_reasons.append(
                    f"High variable usage ratio ({usage_ratio:.2%}) - no waste"
                )

        # Function reuse
        if len(self.called_functions) > 0 and len(self.defined_functions) > 0:
            reuse_ratio = len(self.called_functions) / len(self.defined_functions)
            if reuse_ratio > 0.7:
                hope += 10
                self.metrics.hopeful_reasons.append(
                    f"Good function reuse ({reuse_ratio:.2%})"
                )

        # Comments and confessions (confess statements are like documentation)
        confess_count = self._count_node_type(self.ast, ConfessStmt)
        if confess_count > 3:
            hope += 5
            self.metrics.hopeful_reasons.append(
                f"Code confesses its intentions ({confess_count} confessions)"
            )

        self.metrics.hope_score = min(100, hope)

    def _count_statements(self, statements: List[ASTNode]) -> int:
        """Recursively count all statements."""
        count = len(statements)
        for stmt in statements:
            if isinstance(stmt, IfStmt):
                count += self._count_statements(stmt.then_block)
                if stmt.else_block:
                    count += self._count_statements(stmt.else_block)
            elif isinstance(stmt, (WhileStmt, ForStmt)):
                count += self._count_statements(stmt.body)
            elif isinstance(stmt, FunctionDef):
                count += self._count_statements(stmt.body)
        return count

    def _count_node_type(self, statements: List[ASTNode], node_type) -> int:
        """Count occurrences of a specific node type."""
        count = sum(1 for stmt in statements if isinstance(stmt, node_type))

        for stmt in statements:
            if isinstance(stmt, IfStmt):
                count += self._count_node_type(stmt.then_block, node_type)
                if stmt.else_block:
                    count += self._count_node_type(stmt.else_block, node_type)
            elif isinstance(stmt, (WhileStmt, ForStmt)):
                count += self._count_node_type(stmt.body, node_type)
            elif isinstance(stmt, FunctionDef):
                count += self._count_node_type(stmt.body, node_type)
            elif isinstance(stmt, ForkReality):
                for _, body in stmt.branches:
                    count += self._count_node_type(body, node_type)

        return count

    def _count_temporal_access(self, statements: List[ASTNode]) -> int:
        """Count temporal access operations."""
        count = 0

        def count_in_expr(expr: ASTNode) -> int:
            if isinstance(expr, TemporalAccess):
                return 1
            elif isinstance(expr, BinaryOp):
                return count_in_expr(expr.left) + count_in_expr(expr.right)
            elif isinstance(expr, UnaryOp):
                return count_in_expr(expr.operand)
            elif isinstance(expr, FunctionCall):
                return sum(count_in_expr(arg) for arg in expr.args)
            return 0

        for stmt in statements:
            if isinstance(stmt, (ConfessStmt, ExhaleStmt)):
                count += count_in_expr(stmt.value)
            elif isinstance(stmt, (Assignment, VariableDecl)):
                count += count_in_expr(stmt.value)
            elif isinstance(stmt, IfStmt):
                count += count_in_expr(stmt.condition)
                count += self._count_temporal_access(stmt.then_block)
                if stmt.else_block:
                    count += self._count_temporal_access(stmt.else_block)
            elif isinstance(stmt, WhileStmt):
                count += count_in_expr(stmt.condition)
                count += self._count_temporal_access(stmt.body)
            elif isinstance(stmt, ForStmt):
                count += self._count_temporal_access(stmt.body)
            elif isinstance(stmt, FunctionDef):
                count += self._count_temporal_access(stmt.body)

        return count


# ============================================================================
# EMOTIONAL REPORT GENERATOR
# ============================================================================

class EmotionalReport:
    """Generate beautiful, poetic analysis reports."""

    @staticmethod
    def generate(metrics: EmotionalMetrics, filename: str = "your code") -> str:
        """Generate full emotional analysis report."""
        lines = []

        # Header
        lines.append("\n" + "="*70)
        lines.append("EMOTIONAL STATIC ANALYSIS REPORT")
        lines.append("="*70)
        lines.append(f"\nAnalyzing: {filename}")
        lines.append(f"Emotional State: {metrics.emotional_state()}")
        lines.append(f"Overall Health: {metrics.overall_health():.1f}/100")
        lines.append("")

        # Core metrics
        lines.append("CORE METRICS:")
        lines.append(f"  Functions: {metrics.total_functions}")
        lines.append(f"  Variables: {metrics.total_variables}")
        lines.append(f"  Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
        lines.append(f"  Max Nesting Depth: {metrics.nesting_depth}")
        lines.append("")

        # Emotional scores
        lines.append("EMOTIONAL PROFILE:")
        lines.append(f"  {'Hope:':<12} {EmotionalReport._make_bar(metrics.hope_score)} {metrics.hope_score:.1f}/100")
        lines.append(f"  {'Sadness:':<12} {EmotionalReport._make_bar(metrics.sadness_score)} {metrics.sadness_score:.1f}/100")
        lines.append(f"  {'Anxiety:':<12} {EmotionalReport._make_bar(metrics.anxiety_score)} {metrics.anxiety_score:.1f}/100")
        lines.append(f"  {'Loneliness:':<12} {EmotionalReport._make_bar(metrics.loneliness_score)} {metrics.loneliness_score:.1f}/100")
        lines.append(f"  {'Chaos:':<12} {EmotionalReport._make_bar(metrics.chaos_score)} {metrics.chaos_score:.1f}/100")
        lines.append("")

        # Dominant emotion
        lines.append(f"DOMINANT EMOTION: {metrics.dominant_emotion().upper()}")
        lines.append("")

        # Detailed findings
        if metrics.hopeful_reasons:
            lines.append("REASONS FOR HOPE:")
            for reason in metrics.hopeful_reasons:
                lines.append(f"  + {reason}")
            lines.append("")

        if metrics.sad_reasons:
            lines.append("SOURCES OF SADNESS:")
            for reason in metrics.sad_reasons:
                lines.append(f"  - {reason}")
            lines.append("")

        if metrics.anxious_reasons:
            lines.append("ANXIETY TRIGGERS:")
            for reason in metrics.anxious_reasons:
                lines.append(f"  ! {reason}")
            lines.append("")

        if metrics.lonely_items:
            lines.append("LONELY CODE (Unused):")
            for item in metrics.lonely_items:
                lines.append(f"  * {item}")
            lines.append("")

        if metrics.chaotic_reasons:
            lines.append("CHAOS INDICATORS:")
            for reason in metrics.chaotic_reasons:
                lines.append(f"  ~ {reason}")
            lines.append("")

        # Therapy recommendations
        lines.append("="*70)
        lines.append("CODE THERAPY RECOMMENDATIONS")
        lines.append("="*70)
        lines.extend(EmotionalReport._generate_therapy(metrics))

        lines.append("\n" + "="*70)
        lines.append("END OF EMOTIONAL ANALYSIS")
        lines.append("="*70 + "\n")

        return "\n".join(lines)

    @staticmethod
    def _make_bar(score: float, width: int = 30) -> str:
        """Make a visual progress bar."""
        filled = int((score / 100) * width)
        empty = width - filled
        return f"[{'█' * filled}{'░' * empty}]"

    @staticmethod
    def _generate_therapy(metrics: EmotionalMetrics) -> List[str]:
        """Generate personalized code therapy recommendations."""
        recommendations = []

        # Sadness therapy
        if metrics.sadness_score > 50:
            recommendations.append("\nFOR SADNESS (Complexity):")
            recommendations.append("  1. Break down large functions into smaller, focused ones")
            recommendations.append("  2. Reduce nesting by extracting nested blocks into functions")
            recommendations.append("  3. Simplify conditional logic - consider lookup tables or strategy patterns")
            recommendations.append("  4. Remove unnecessary complexity - every line should justify its existence")
            recommendations.append("  5. Refactor: Extract Method, Simplify Conditional, Replace Nested Conditional with Guard Clauses")

        # Anxiety therapy
        if metrics.anxiety_score > 50:
            recommendations.append("\nFOR ANXIETY (Excessive Checks):")
            recommendations.append("  1. Trust your data - not everything needs validation")
            recommendations.append("  2. Consolidate related conditionals into single decision points")
            recommendations.append("  3. Use assertions for developer checks, not runtime logic")
            recommendations.append("  4. Reduce reality forking - pick one timeline and commit to it")
            recommendations.append("  5. Consider: Do you really need to check that? What's the worst that could happen?")

        # Loneliness therapy
        if metrics.loneliness_score > 50:
            recommendations.append("\nFOR LONELINESS (Dead Code):")
            recommendations.append("  1. Delete unused functions - they're taking up emotional space")
            recommendations.append("  2. Remove unused variables - clean out the closet")
            recommendations.append("  3. If you're keeping it 'just in case', use version control instead")
            recommendations.append("  4. Every piece of code should have a purpose - delete the purposeless")
            recommendations.append("  5. Less code = less bugs = less maintenance = more happiness")

        # Chaos therapy
        if metrics.chaos_score > 50:
            recommendations.append("\nFOR CHAOS (Disorganization):")
            recommendations.append("  1. Choose ONE naming convention (snake_case recommended for Lament)")
            recommendations.append("  2. Organize functions into logical groups")
            recommendations.append("  3. Flatten deep nesting - use early returns and guard clauses")
            recommendations.append("  4. Use consistent patterns throughout the codebase")
            recommendations.append("  5. Add structure: group related code, separate concerns, create boundaries")

        # Hope encouragement
        if metrics.hope_score > 60:
            recommendations.append("\nKEEP DOING WHAT YOU'RE DOING:")
            recommendations.append("  * Your code shows clarity and intention")
            recommendations.append("  * Good naming makes code self-documenting")
            recommendations.append("  * Appropriate complexity shows mature design")
            recommendations.append("  * This is the way")
        elif metrics.hope_score < 30:
            recommendations.append("\nFINDING HOPE:")
            recommendations.append("  1. Start with naming - give things meaningful, descriptive names")
            recommendations.append("  2. Write code for humans first, computers second")
            recommendations.append("  3. Every refactoring is a step toward hope")
            recommendations.append("  4. Simplicity is sophisticated")
            recommendations.append("  5. Your future self will thank you")

        # Overall advice
        if metrics.overall_health() < 40:
            recommendations.append("\nURGENT:")
            recommendations.append("  This codebase needs serious refactoring.")
            recommendations.append("  Consider a rewrite if these issues are systemic.")
            recommendations.append("  The emotional toll of maintaining this code is high.")
            recommendations.append("  Invest in quality now, or pay the debt with interest later.")
        elif metrics.overall_health() > 70:
            recommendations.append("\nCELEBRATE:")
            recommendations.append("  Your code is healthy and well-maintained!")
            recommendations.append("  Keep up the good practices.")
            recommendations.append("  You're setting a great example.")

        return recommendations


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def analyze_file(filename: str) -> EmotionalMetrics:
    """Analyze a Lament source file."""
    try:
        with open(filename, 'r') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    # Parse the code
    try:
        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
    except SyntaxError as e:
        print(f"Syntax error in {filename}: {e}")
        print("Cannot analyze code with syntax errors.")
        sys.exit(1)

    # Analyze
    analyzer = CodeAnalyzer(ast)
    metrics = analyzer.analyze()

    return metrics


def main():
    """Entry point for emotional analysis."""
    if len(sys.argv) != 2:
        print("Usage: python analysis.py <file.lament>")
        print("Analyze the emotional state of your Lament code.")
        sys.exit(1)

    filename = sys.argv[1]

    print(f"\nPreparing to analyze: {filename}")
    print("Taking a deep breath...")
    print("Opening emotional channels...")

    metrics = analyze_file(filename)

    report = EmotionalReport.generate(metrics, filename)
    print(report)

    # Exit code based on health
    health = metrics.overall_health()
    if health < 40:
        sys.exit(2)  # Critical
    elif health < 60:
        sys.exit(1)  # Needs improvement
    else:
        sys.exit(0)  # Healthy


if __name__ == '__main__':
    main()
