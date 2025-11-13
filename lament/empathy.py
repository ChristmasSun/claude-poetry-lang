#!/usr/bin/env python3
"""
Lament Empathetic Error System & Code Therapy
==============================================

The FIRST programming language that truly CARES about developers.

This module provides:
1. EMPATHETIC ERROR MESSAGES - Errors that understand you, suggest fixes, detect fatigue
2. CODE THERAPY SYSTEM - Long-term mental health tracking for your codebase

Because coding shouldn't feel like suffering.
Because errors shouldn't just blame - they should help.
Because your code deserves compassion.

"I sense your frustration. Let me help you through this."

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
import time
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict

from lament.types import Color
from lament.parser import (
    ASTNode, FunctionDef, VariableDecl, IfStmt, WhileStmt, ForStmt,
    ForkReality, TemporalAccess, BinaryOp, UnaryOp
)


# ============================================================================
# SESSION TRACKING (Developer Pattern Detection)
# ============================================================================

@dataclass
class DeveloperSession:
    """Tracks developer behavior patterns during coding."""
    session_id: str
    start_time: float
    errors_hit: List[Dict[str, Any]] = field(default_factory=list)
    error_types: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    repeated_errors: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    last_error_time: Optional[float] = None
    total_errors: int = 0
    files_touched: List[str] = field(default_factory=list)

    def add_error(self, error_type: str, message: str, location: str, code_hash: str):
        """Record an error occurrence."""
        current_time = time.time()

        error_record = {
            'type': error_type,
            'message': message,
            'location': location,
            'code_hash': code_hash,
            'timestamp': current_time,
            'time_since_start': current_time - self.start_time,
        }

        self.errors_hit.append(error_record)
        self.error_types[error_type] += 1
        self.repeated_errors[code_hash] += 1
        self.total_errors += 1
        self.last_error_time = current_time

    def is_fatigued(self) -> bool:
        """Detect if developer is showing signs of fatigue."""
        time_coding = time.time() - self.start_time
        hours = time_coding / 3600

        # Been coding for 4+ hours
        if hours >= 4:
            return True

        # High error rate in recent period
        recent_errors = [e for e in self.errors_hit
                        if time.time() - e['timestamp'] < 600]  # Last 10 min
        if len(recent_errors) >= 5:
            return True

        # Same error repeatedly
        if any(count >= 3 for count in self.repeated_errors.values()):
            return True

        return False

    def get_fatigue_level(self) -> str:
        """Describe fatigue level."""
        time_coding = time.time() - self.start_time
        hours = time_coding / 3600

        if hours >= 6:
            return "EXTREME"
        elif hours >= 4:
            return "HIGH"
        elif hours >= 2:
            return "MODERATE"
        else:
            return "LOW"

    def get_error_pattern(self) -> str:
        """Analyze error patterns."""
        if not self.errors_hit:
            return "No errors yet"

        if self.total_errors == 1:
            return "First error of session"

        # Check for repeated patterns
        most_common = max(self.repeated_errors.values()) if self.repeated_errors else 0
        if most_common >= 3:
            return f"Stuck on same issue ({most_common} times)"

        # Check error diversity
        if len(self.error_types) == 1:
            return f"All {self.total_errors} errors are the same type"

        return f"{self.total_errors} errors across {len(self.error_types)} types"


class SessionManager:
    """Manages developer session tracking."""

    def __init__(self):
        self.session_file = Path.home() / '.lament' / 'session.json'
        self.session_file.parent.mkdir(exist_ok=True)
        self.current_session = self._load_or_create_session()

    def _load_or_create_session(self) -> DeveloperSession:
        """Load existing session or create new one."""
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r') as f:
                    data = json.load(f)

                # Check if session is recent (within 2 hours)
                if time.time() - data.get('start_time', 0) < 7200:
                    # Resume session
                    return DeveloperSession(
                        session_id=data['session_id'],
                        start_time=data['start_time'],
                        errors_hit=data.get('errors_hit', []),
                        error_types=defaultdict(int, data.get('error_types', {})),
                        repeated_errors=defaultdict(int, data.get('repeated_errors', {})),
                        last_error_time=data.get('last_error_time'),
                        total_errors=data.get('total_errors', 0),
                        files_touched=data.get('files_touched', [])
                    )
            except:
                pass

        # Create new session
        return DeveloperSession(
            session_id=hashlib.md5(str(time.time()).encode()).hexdigest()[:8],
            start_time=time.time()
        )

    def save_session(self):
        """Persist session to disk."""
        data = {
            'session_id': self.current_session.session_id,
            'start_time': self.current_session.start_time,
            'errors_hit': self.current_session.errors_hit,
            'error_types': dict(self.current_session.error_types),
            'repeated_errors': dict(self.current_session.repeated_errors),
            'last_error_time': self.current_session.last_error_time,
            'total_errors': self.current_session.total_errors,
            'files_touched': self.current_session.files_touched,
        }

        with open(self.session_file, 'w') as f:
            json.dump(data, f, indent=2)

    def record_error(self, error_type: str, message: str, location: str, code: str):
        """Record an error occurrence."""
        code_hash = hashlib.md5(code.encode()).hexdigest()[:8]
        self.current_session.add_error(error_type, message, location, code_hash)
        self.save_session()


# Global session manager
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get or create global session manager."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager


# ============================================================================
# EMPATHETIC ERROR MESSAGES
# ============================================================================

class EmpathyEngine:
    """The heart of empathetic error handling."""

    # Error type to explanation mapping
    ERROR_EXPLANATIONS = {
        'UNDEFINED_VARIABLE': {
            'concept': "In Lament, variables must be 'remembered' before use. Use: remember x = 5",
            'common_cause': "Typo in variable name, or forgot to declare it",
            'fix_template': "Try adding: remember {var_name} = <initial_value>"
        },
        'UNDEFINED_FUNCTION': {
            'concept': "Functions must be defined with 'sigh' before calling them",
            'common_cause': "Typo in function name, or function not defined yet",
            'fix_template': "Define it first: sigh {func_name}() { ... }"
        },
        'SYNTAX_ERROR': {
            'concept': "Lament has specific syntax rules. Check braces, keywords, etc.",
            'common_cause': "Missing brace, typo in keyword, or wrong operator",
            'fix_template': "Review the syntax near line {line}"
        },
        'TYPE_ERROR': {
            'concept': "Operations require compatible types (can't add string to number)",
            'common_cause': "Mixing incompatible types in operations",
            'fix_template': "Check the types of your variables"
        },
        'DIVISION_BY_ZERO': {
            'concept': "Division by zero is mathematically undefined",
            'common_cause': "A variable or calculation resulted in zero",
            'fix_template': "Add a check: if divisor != 0 { ... }"
        },
        'INDEX_ERROR': {
            'concept': "Accessing list/dict with invalid index or key",
            'common_cause': "Index out of bounds or key doesn't exist",
            'fix_template': "Check array length or use conditional access"
        },
    }

    @staticmethod
    def create_empathetic_error(
        error_type: str,
        technical_message: str,
        poetic_message: str,
        location: str = "",
        code_snippet: str = "",
        suggestions: Optional[List[str]] = None
    ) -> str:
        """Create a comprehensive, empathetic error message."""

        session = get_session_manager().current_session
        is_fatigued = session.is_fatigued()

        lines = []

        # Header with empathy
        lines.append(f"\n{Color.RED}{Color.BOLD}{'='*70}{Color.RESET}")
        lines.append(f"{Color.RED}{Color.BOLD}💔 LAMENT ERROR 💔{Color.RESET}")
        lines.append(f"{Color.RED}{Color.BOLD}{'='*70}{Color.RESET}\n")

        # Detect emotional state and respond
        if is_fatigued:
            fatigue = session.get_fatigue_level()
            lines.append(f"{Color.YELLOW}{Color.BOLD}⚠ FATIGUE DETECTED: {fatigue} ⚠{Color.RESET}")
            lines.append(f"{Color.MAGENTA}I sense you've been coding for a while...")

            if fatigue == "EXTREME":
                lines.append(f"You've been at this for over 6 hours. Please rest.{Color.RESET}")
                lines.append(f"{Color.CYAN}Your mind needs a break. This error might seem clearer after rest.{Color.RESET}\n")
            else:
                lines.append(f"Consider taking a break. Fresh eyes see solutions faster.{Color.RESET}\n")

        # Check for repeated errors
        pattern = session.get_error_pattern()
        if "Stuck" in pattern or "same type" in pattern:
            lines.append(f"{Color.YELLOW}📊 Pattern detected: {pattern}{Color.RESET}")
            lines.append(f"{Color.CYAN}You've hit this before. Let me explain it differently...{Color.RESET}\n")

        # The poetic message
        lines.append(f"{Color.CYAN}{poetic_message}{Color.RESET}\n")

        # Technical details
        lines.append(f"{Color.YELLOW}Technical details:{Color.RESET}")
        lines.append(f"  {technical_message}")
        if location:
            lines.append(f"  Location: {location}")
        lines.append("")

        # Code snippet if available
        if code_snippet:
            lines.append(f"{Color.WHITE}Code:{Color.RESET}")
            lines.append(f"{code_snippet}\n")

        # Explanation of concept
        if error_type in EmpathyEngine.ERROR_EXPLANATIONS:
            explanation = EmpathyEngine.ERROR_EXPLANATIONS[error_type]

            lines.append(f"{Color.GREEN}{Color.BOLD}💡 Understanding the issue:{Color.RESET}")
            lines.append(f"{Color.GREEN}  {explanation['concept']}{Color.RESET}\n")

            lines.append(f"{Color.BLUE}{Color.BOLD}🔍 Common cause:{Color.RESET}")
            lines.append(f"{Color.BLUE}  {explanation['common_cause']}{Color.RESET}\n")

            # Auto-suggest fix
            if suggestions:
                lines.append(f"{Color.GREEN}{Color.BOLD}✨ Suggested fixes:{Color.RESET}")
                for i, suggestion in enumerate(suggestions, 1):
                    lines.append(f"{Color.GREEN}  {i}. {suggestion}{Color.RESET}")
            else:
                lines.append(f"{Color.GREEN}{Color.BOLD}✨ How to fix:{Color.RESET}")
                lines.append(f"{Color.GREEN}  {explanation['fix_template']}{Color.RESET}")
            lines.append("")

        # Offer to explain more
        lines.append(f"{Color.MAGENTA}Need more help? I'm here for you.{Color.RESET}")
        lines.append(f"{Color.MAGENTA}Run 'lament explain {error_type.lower()}' for detailed examples.{Color.RESET}\n")

        # Session stats
        lines.append(f"Session: {session.session_id} | ")
        lines.append(f"Time coding: {(time.time() - session.start_time) / 60:.1f} min | ")
        lines.append(f"Errors: {session.total_errors}\n")

        lines.append(f"{Color.RED}{Color.BOLD}{'='*70}{Color.RESET}\n")

        return '\n'.join(lines)

    @staticmethod
    def suggest_fixes_for_undefined_variable(var_name: str, scope: Dict) -> List[str]:
        """Suggest fixes for undefined variable errors."""
        suggestions = []

        # Check for similar variable names (typos)
        defined_vars = list(scope.keys())
        for defined_var in defined_vars:
            # Simple similarity check
            if EmpathyEngine._similar(var_name, defined_var):
                suggestions.append(f"Did you mean '{defined_var}'? (Check spelling)")

        # Generic suggestions
        suggestions.append(f"Add: remember {var_name} = <value>")
        suggestions.append(f"Check if '{var_name}' is in scope")

        return suggestions[:3]  # Top 3 suggestions

    @staticmethod
    def suggest_fixes_for_syntax_error(error_msg: str, line: int) -> List[str]:
        """Suggest fixes for syntax errors."""
        suggestions = []

        error_lower = error_msg.lower()

        if 'expected' in error_lower and '{' in error_lower:
            suggestions.append("Missing opening brace { after control structure")
        elif 'expected' in error_lower and '}' in error_lower:
            suggestions.append("Missing closing brace } or mismatched braces")
        elif 'unexpected' in error_lower:
            suggestions.append(f"Check syntax around line {line}")
            suggestions.append("Look for missing semicolons, commas, or operators")

        suggestions.append(f"Review Lament syntax documentation")

        return suggestions[:3]

    @staticmethod
    def _similar(s1: str, s2: str) -> bool:
        """Check if two strings are similar (simple Levenshtein-like)."""
        if abs(len(s1) - len(s2)) > 2:
            return False

        # Check for common prefixes
        if len(s1) >= 3 and len(s2) >= 3:
            if s1[:3] == s2[:3]:
                return True

        # Character-level similarity
        common = sum(1 for a, b in zip(s1, s2) if a == b)
        if common >= min(len(s1), len(s2)) - 1:
            return True

        return False


# ============================================================================
# CODE THERAPY SYSTEM
# ============================================================================

@dataclass
class TherapySession:
    """A therapy session for your codebase."""
    timestamp: str
    file_analyzed: str
    emotional_state: str
    health_score: float
    dominant_emotion: str
    concerns: List[str] = field(default_factory=list)
    victories: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class CodeTherapist:
    """A therapist for your code. Listens. Understands. Suggests."""

    def __init__(self):
        self.history_file = Path.home() / '.lament' / 'therapy_history.json'
        self.history_file.parent.mkdir(exist_ok=True)
        self.history = self._load_history()

    def _load_history(self) -> List[Dict]:
        """Load therapy session history."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []

    def _save_history(self):
        """Save therapy history."""
        with open(self.history_file, 'w') as f:
            json.dump(self.history, f, indent=2)

    def conduct_therapy_session(self, ast: List[ASTNode], filename: str) -> TherapySession:
        """Conduct a full therapy session for the code."""
        from lament.analysis import CodeAnalyzer, EmotionalMetrics

        # Analyze the code
        analyzer = CodeAnalyzer(ast)
        metrics = analyzer.analyze()

        # Create therapy session
        session = TherapySession(
            timestamp=datetime.now().isoformat(),
            file_analyzed=filename,
            emotional_state=metrics.emotional_state(),
            health_score=metrics.overall_health(),
            dominant_emotion=metrics.dominant_emotion()
        )

        # Identify concerns (personified)
        if metrics.loneliness_score > 50:
            for item in metrics.lonely_items[:3]:
                session.concerns.append(f"💔 {item} - feeling abandoned")

        if metrics.anxiety_score > 50:
            for reason in metrics.anxious_reasons[:2]:
                session.concerns.append(f"😰 {reason}")

        if metrics.sadness_score > 50:
            for reason in metrics.sad_reasons[:2]:
                session.concerns.append(f"😢 {reason}")

        if metrics.chaos_score > 50:
            for reason in metrics.chaotic_reasons[:2]:
                session.concerns.append(f"🌪️  {reason}")

        # Identify victories
        if metrics.hope_score > 60:
            for reason in metrics.hopeful_reasons[:3]:
                session.victories.append(f"✨ {reason}")

        # Generate therapy recommendations
        session.recommendations = self._generate_therapy_recommendations(metrics, analyzer)

        # Save to history
        self.history.append({
            'timestamp': session.timestamp,
            'file': filename,
            'health_score': session.health_score,
            'dominant_emotion': session.dominant_emotion
        })
        self._save_history()

        return session

    def _generate_therapy_recommendations(self, metrics, analyzer) -> List[str]:
        """Generate personalized therapy recommendations."""
        recommendations = []

        # Lonely functions
        lonely_funcs = [item for item in metrics.lonely_items if 'Function' in item]
        if lonely_funcs:
            func_name = lonely_funcs[0].split("'")[1]
            recommendations.append(
                f"🗣️  Have you talked to '{func_name}' lately? It's never called. "
                f"Maybe it needs a purpose, or maybe it's time to let it go."
            )

        # Anxious modules
        if metrics.anxiety_score > 60:
            recommendations.append(
                f"🧘 Your code is anxious. It checks everything. "
                f"Ask yourself: 'Why do I need so many guards? What am I afraid of?'"
            )

        # Complex functions
        for func_name, complexity in analyzer.function_complexities.items():
            if complexity > 15:
                recommendations.append(
                    f"🤯 Function '{func_name}' is trying to do too much. "
                    f"It's okay to ask for help. Break it into smaller pieces."
                )
                break

        # Deep nesting
        if metrics.nesting_depth > 4:
            recommendations.append(
                f"🕳️  Your code goes deep ({metrics.nesting_depth} levels). "
                f"Sometimes we need to come back to the surface. Flatten it."
            )

        # Naming
        if metrics.chaos_score > 40 and any('naming' in r.lower() for r in metrics.chaotic_reasons):
            recommendations.append(
                f"📝 Names matter. They're how we understand each other. "
                f"Choose one convention and stick with it."
            )

        # Hope
        if metrics.hope_score < 30:
            recommendations.append(
                f"🌱 Finding hope starts with small changes. "
                f"Pick ONE function. Make it beautiful. Feel the difference."
            )

        return recommendations

    def generate_conversational_report(self, session: TherapySession) -> str:
        """Generate a conversation-style therapy report."""
        lines = []

        # Header
        lines.append(f"\n{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}")
        lines.append(f"{Color.MAGENTA}{Color.BOLD}🛋️  CODE THERAPY SESSION 🛋️{Color.RESET}")
        lines.append(f"{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}\n")

        # Opening
        lines.append(f"{Color.CYAN}Welcome. I'm here to listen.{Color.RESET}")
        lines.append(f"{Color.CYAN}Let's talk about how your code is feeling...{Color.RESET}\n")

        # File info
        lines.append(f"{Color.WHITE}File: {session.file_analyzed}{Color.RESET}")
        lines.append(f"{Color.WHITE}Date: {session.timestamp.split('T')[0]}{Color.RESET}\n")

        # Emotional check-in
        lines.append(f"{Color.YELLOW}{Color.BOLD}How is your code feeling today?{Color.RESET}")
        lines.append(f"{Color.YELLOW}{session.emotional_state}{Color.RESET}\n")

        lines.append(f"{Color.BLUE}Dominant emotion: {session.dominant_emotion.upper()}{Color.RESET}")
        lines.append(f"{Color.BLUE}Overall health: {session.health_score:.1f}/100{Color.RESET}\n")

        # Concerns
        if session.concerns:
            lines.append(f"{Color.RED}{Color.BOLD}What's troubling you?{Color.RESET}")
            for concern in session.concerns:
                lines.append(f"  {concern}")
            lines.append("")

        # Victories
        if session.victories:
            lines.append(f"{Color.GREEN}{Color.BOLD}What's going well?{Color.RESET}")
            for victory in session.victories:
                lines.append(f"  {victory}")
            lines.append("")

        # Therapy recommendations
        if session.recommendations:
            lines.append(f"{Color.MAGENTA}{Color.BOLD}Let's work through this together...{Color.RESET}\n")
            for i, rec in enumerate(session.recommendations, 1):
                lines.append(f"{Color.MAGENTA}{i}. {rec}{Color.RESET}\n")

        # Longitudinal tracking
        if len(self.history) > 1:
            lines.append(f"{Color.CYAN}{Color.BOLD}Looking back...{Color.RESET}")
            lines.append(f"{Color.CYAN}We've had {len(self.history)} sessions together.{Color.RESET}")

            # Track improvement
            recent = [h for h in self.history[-5:] if h.get('health_score')]
            if len(recent) >= 2:
                trend = recent[-1]['health_score'] - recent[0]['health_score']
                if trend > 10:
                    lines.append(f"{Color.GREEN}Your codebase is healing! Health improved by {trend:.1f} points.{Color.RESET}")
                elif trend < -10:
                    lines.append(f"{Color.YELLOW}Things are getting harder. That's okay. We'll work through it.{Color.RESET}")
                else:
                    lines.append(f"{Color.BLUE}You're maintaining stability. Sometimes that's enough.{Color.RESET}")
            lines.append("")

        # Closing
        lines.append(f"{Color.MAGENTA}Remember: code is never 'done'. It's always growing, changing.{Color.RESET}")
        lines.append(f"{Color.MAGENTA}Be patient with it. Be patient with yourself.{Color.RESET}\n")

        lines.append(f"{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}")
        lines.append(f"{Color.MAGENTA}{Color.BOLD}End of session. Take care. 💜{Color.RESET}")
        lines.append(f"{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}\n")

        return '\n'.join(lines)


# ============================================================================
# INTEGRATION WITH EXISTING ERROR HANDLING
# ============================================================================

def empathetic_error_wrapper(
    error_func,
    error_type: str,
    technical_message: str,
    poetic_message: str,
    location: str = "",
    code_snippet: str = "",
    suggestions: Optional[List[str]] = None
):
    """Wrapper for existing error functions to add empathy."""

    # Record error in session
    session_mgr = get_session_manager()
    session_mgr.record_error(error_type, technical_message, location, code_snippet)

    # Create empathetic error message
    empathetic_msg = EmpathyEngine.create_empathetic_error(
        error_type=error_type,
        technical_message=technical_message,
        poetic_message=poetic_message,
        location=location,
        code_snippet=code_snippet,
        suggestions=suggestions
    )

    # Print and exit
    print(empathetic_msg, file=sys.stderr)
    sys.exit(1)


# ============================================================================
# COMMAND LINE INTERFACE
# ============================================================================

def cmd_therapy(filename: str):
    """Run code therapy session."""
    from lament.lexer import Lexer
    from lament.parser import Parser

    print(f"\n{Color.MAGENTA}{Color.BOLD}Starting code therapy session...{Color.RESET}\n")
    print(f"{Color.CYAN}Taking a deep breath...{Color.RESET}")
    print(f"{Color.CYAN}Opening my heart to your code...{Color.RESET}\n")
    time.sleep(1)

    # Read and parse
    try:
        with open(filename, 'r') as f:
            source = f.read()

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()
    except Exception as e:
        print(f"{Color.RED}Could not analyze file: {e}{Color.RESET}")
        return 1

    # Conduct therapy
    therapist = CodeTherapist()
    session = therapist.conduct_therapy_session(ast, filename)

    # Generate and print report
    report = therapist.generate_conversational_report(session)
    print(report)

    return 0


if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Usage: python empathy.py <file.lament>")
        sys.exit(1)

    cmd_therapy(sys.argv[1])
