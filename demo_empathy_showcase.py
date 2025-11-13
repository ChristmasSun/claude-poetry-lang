#!/usr/bin/env python3
"""
Comprehensive Demo: Empathy System Showcase
===========================================

This demo script showcases BOTH groundbreaking features:
1. Empathetic Error Messages
2. Code Therapy System

Run this to see the full power of Lament's emotional intelligence.
"""

import sys
import os
import time
import subprocess
from pathlib import Path

# Add lament to path
sys.path.insert(0, '/home/user/claude-poetry-lang')

from lament.types import Color


def print_section(title):
    """Print a beautiful section header."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{title.center(70)}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}\n")


def print_demo_info(info):
    """Print demo information."""
    print(f"{Color.MAGENTA}{info}{Color.RESET}\n")


def wait_for_user():
    """Wait for user to press enter."""
    print(f"Press Enter to continue...")
    input()


def main():
    print(f"\n{Color.MAGENTA}{Color.BOLD}")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║                                                                   ║")
    print("║         LAMENT EMPATHY SYSTEM - COMPREHENSIVE SHOWCASE           ║")
    print("║                                                                   ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print(f"{Color.RESET}\n")

    print(f"{Color.CYAN}Welcome to the FIRST programming language that truly CARES.{Color.RESET}")
    print(f"{Color.CYAN}Let's explore two groundbreaking features:{Color.RESET}\n")
    print(f"{Color.GREEN}1. EMPATHETIC ERROR MESSAGES - Errors that help, not blame{Color.RESET}")
    print(f"{Color.GREEN}2. CODE THERAPY SYSTEM - Mental health for your codebase{Color.RESET}\n")

    wait_for_user()

    # ========================================================================
    # PART 1: EMPATHETIC ERROR MESSAGES
    # ========================================================================

    print_section("PART 1: EMPATHETIC ERROR MESSAGES")

    print_demo_info(
        "Lament doesn't just throw errors at you. It understands.\n"
        "It tracks your session, detects fatigue, suggests fixes,\n"
        "and speaks with compassion."
    )

    print(f"{Color.YELLOW}Key Features:{Color.RESET}")
    print(f"  • Tracks developer patterns (how often you hit errors)")
    print(f"  • Detects fatigue (been coding 4+ hours)")
    print(f"  • Auto-suggests fixes based on error type")
    print(f"  • Offers to explain concepts")
    print(f"  • Uses compassionate, helpful tone")
    print(f"  • 'I sense your frustration. Let me help you through this.'\n")

    print(f"{Color.WHITE}Let's trigger some empathetic errors...{Color.RESET}\n")

    wait_for_user()

    # Demonstrate empathetic errors
    print(f"{Color.CYAN}Example 1: Undefined Variable with Typo Detection{Color.RESET}\n")

    from lament.empathy import EmpathyEngine, get_session_manager
    from lament.lexer import Lexer
    from lament.parser import Parser

    # Simulate session with errors
    session_mgr = get_session_manager()

    code1 = "remember user_name = 'Alice'\nconfess usrname"
    print(f"Code:")
    print(f"{code1}\n")

    # Create empathetic error
    suggestions = ["Did you mean 'user_name'? (Check spelling)", "Add: remember usrname = <value>"]
    error_msg = EmpathyEngine.create_empathetic_error(
        error_type='UNDEFINED_VARIABLE',
        technical_message="Variable 'usrname' is not defined",
        poetic_message="I searched for 'usrname' in all the timelines,\n"
                      "       through all the memories of the void—\n"
                      "       but it was never remembered.\n"
                      "       (Perhaps you meant 'user_name'?)",
        location="Line 2",
        code_snippet=code1,
        suggestions=suggestions
    )
    print(error_msg)

    wait_for_user()

    # ========================================================================
    # PART 2: FATIGUE DETECTION
    # ========================================================================

    print_section("PART 2: FATIGUE DETECTION")

    print_demo_info(
        "Lament tracks how long you've been coding.\n"
        "If you've been at it for hours, errors become more compassionate.\n"
        "The system CARES about your wellbeing."
    )

    # Simulate fatigue
    print(f"{Color.YELLOW}Simulating a developer who's been coding for 5 hours...{Color.RESET}\n")

    # Artificially set session start time to 5 hours ago
    session_mgr.current_session.start_time = time.time() - (5 * 3600)
    session_mgr.current_session.total_errors = 12

    error_msg = EmpathyEngine.create_empathetic_error(
        error_type='SYNTAX_ERROR',
        technical_message="Expected '}', got EOF",
        poetic_message="The code ended too soon,\n"
                      "       leaving structures incomplete,\n"
                      "       leaving meaning suspended in void.",
        location="End of file",
        suggestions=["Check for missing closing brace }", "Count your braces: { and }"]
    )
    print(error_msg)

    # Reset session
    session_mgr.current_session.start_time = time.time()

    wait_for_user()

    # ========================================================================
    # PART 3: CODE THERAPY SYSTEM
    # ========================================================================

    print_section("PART 3: CODE THERAPY SYSTEM")

    print_demo_info(
        "The CODE THERAPY SYSTEM is unprecedented.\n"
        "It analyzes your codebase's emotional health,\n"
        "identifies lonely functions, anxious modules,\n"
        "and provides conversation-style recommendations."
    )

    print(f"{Color.YELLOW}What the Therapist Detects:{Color.RESET}")
    print(f"  • Lonely functions (never called) - 'feeling abandoned'")
    print(f"  • Anxious code (too many guards) - 'What are you afraid of?'")
    print(f"  • Complex functions (doing too much) - 'It's okay to ask for help'")
    print(f"  • Deep nesting (lost in layers) - 'Come back to the surface'")
    print(f"  • Long-term health tracking - 'We've had N sessions together'\n")

    print(f"{Color.WHITE}Let's conduct a therapy session...{Color.RESET}\n")

    wait_for_user()

    # Run therapy on demo file
    print(f"{Color.CYAN}Analyzing: demo_therapy_clean.lament{Color.RESET}\n")

    therapy_file = Path('/home/user/claude-poetry-lang/demo_therapy_clean.lament')
    if therapy_file.exists():
        from lament.empathy import CodeTherapist

        # Parse the file
        with open(therapy_file, 'r') as f:
            source = f.read()

        lexer = Lexer(source)
        tokens = lexer.tokenize()
        parser = Parser(tokens)
        ast = parser.parse()

        # Conduct therapy
        therapist = CodeTherapist()
        session = therapist.conduct_therapy_session(ast, str(therapy_file))

        # Generate and print report
        report = therapist.generate_conversational_report(session)
        print(report)
    else:
        print(f"{Color.RED}Demo file not found. Please create demo_therapy_session.lament{Color.RESET}")

    wait_for_user()

    # ========================================================================
    # PART 4: LONGITUDINAL TRACKING
    # ========================================================================

    print_section("PART 4: LONGITUDINAL TRACKING")

    print_demo_info(
        "The therapy system remembers your history.\n"
        "It tracks improvement over time.\n"
        "It celebrates victories and supports through challenges."
    )

    print(f"{Color.GREEN}After multiple therapy sessions, the system says:{Color.RESET}\n")
    print(f"{Color.CYAN}\"We've had 5 sessions together.\"")
    print(f"\"Your codebase is healing! Health improved by 23.4 points.\"")
    print(f"\"Keep up the good practices.\"{Color.RESET}\n")

    print(f"{Color.MAGENTA}This is the future of developer experience.{Color.RESET}")
    print(f"{Color.MAGENTA}Compassionate. Helpful. Human.{Color.RESET}\n")

    # ========================================================================
    # CONCLUSION
    # ========================================================================

    print_section("CONCLUSION")

    print(f"{Color.GREEN}{Color.BOLD}You've just witnessed the future of programming languages.{Color.RESET}\n")

    print(f"{Color.CYAN}Key Innovations:{Color.RESET}")
    print(f"  ✓ Session tracking with pattern detection")
    print(f"  ✓ Fatigue detection (4+ hours coding)")
    print(f"  ✓ Auto-suggested fixes for common errors")
    print(f"  ✓ Concept explanations on demand")
    print(f"  ✓ Compassionate, empathetic tone")
    print(f"  ✓ Code therapy with conversation-style reports")
    print(f"  ✓ Lonely function detection")
    print(f"  ✓ Anxiety pattern analysis")
    print(f"  ✓ Long-term health tracking")
    print(f"  ✓ Personalized recommendations\n")

    print(f"{Color.MAGENTA}Because code has feelings too.{Color.RESET}")
    print(f"{Color.MAGENTA}Because developers deserve compassion.{Color.RESET}")
    print(f"{Color.MAGENTA}Because errors should help, not hurt.{Color.RESET}\n")

    print(f"{Color.MAGENTA}{Color.BOLD}Welcome to Lament. The language that cares.{Color.RESET}\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Color.YELLOW}Demo interrupted. That's okay. Take a break.{Color.RESET}\n")
        sys.exit(0)
