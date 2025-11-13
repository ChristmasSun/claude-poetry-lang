#!/usr/bin/env python3
"""
LAMENT EMOTIONAL ANALYSIS DEMONSTRATION
Version 1.0: A compiler that understands your code's feelings

This demonstrates the UNPRECEDENTED emotional static analysis system.
"""

import sys
sys.path.insert(0, '/home/user/claude-poetry-lang')

from lament.lexer import Lexer
from lament.parser import Parser
from lament.analysis import CodeAnalyzer, EmotionalReport

def print_header(text):
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def analyze_code(code, description):
    """Analyze a piece of code and print results"""
    print(f"\n{description}")
    print(f"{'-'*70}")
    print(f"CODE:\n{code}")
    print(f"{'-'*70}\n")

    # Parse
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    # Analyze
    analyzer = CodeAnalyzer(ast)
    metrics = analyzer.analyze()

    # Report
    report = EmotionalReport(metrics)
    print(report.format())

def main():
    print_header("LAMENT EMOTIONAL STATIC ANALYSIS DEMONSTRATION")

    print("This system analyzes code and detects 5 emotional states:")
    print("  1. Hope      - Clean, beautiful, well-structured code")
    print("  2. Sadness   - Complex, confusing, hard to maintain")
    print("  3. Anxiety   - Excessive error checking, defensive programming")
    print("  4. Loneliness - Unused functions/variables (dead code)")
    print("  5. Chaos     - Disorganized, inconsistent naming, deep nesting")
    print()

    # ========================================================================
    # EXAMPLE 1: HOPEFUL CODE
    # ========================================================================

    print_header("EXAMPLE 1: HOPEFUL CODE (Clean & Beautiful)")

    hopeful_code = """
remember numbers = [1, 2, 3, 4, 5]

sigh calculate_sum(list) {
    remember total = 0
    for item in list {
        total = total + item
    }
    exhale total
}

sigh calculate_average(list) {
    remember sum = calculate_sum(list)
    remember count = length_of(list)
    exhale sum / count
}

remember result = calculate_average(numbers)
confess result
"""

    analyze_code(hopeful_code, "Clean code with good naming and structure")

    # ========================================================================
    # EXAMPLE 2: SAD CODE
    # ========================================================================

    print_header("EXAMPLE 2: SAD CODE (Complex & Confusing)")

    sad_code = """
remember x = 0
remember y = 0
remember z = 0
remember a = 0
remember b = 0
remember c = 0

sigh complicated_function(p1, p2, p3) {
    if p1 > 0 {
        if p2 > 0 {
            if p3 > 0 {
                remember result = p1 + p2 + p3
                if result > 10 {
                    if result < 100 {
                        if result % 2 == 0 {
                            exhale result * 2
                        } else {
                            exhale result * 3
                        }
                    } else {
                        exhale result
                    }
                } else {
                    exhale 0
                }
            } else {
                exhale -1
            }
        } else {
            exhale -2
        }
    } else {
        exhale -3
    }
}

confess complicated_function(x, y, z)
"""

    analyze_code(sad_code, "Overly complex with deep nesting")

    # ========================================================================
    # EXAMPLE 3: LONELY CODE
    # ========================================================================

    print_header("EXAMPLE 3: LONELY CODE (Unused Functions)")

    lonely_code = """
sigh never_used_function() {
    confess "Nobody calls me"
}

sigh another_unused() {
    remember x = 42
    exhale x
}

sigh actually_used() {
    confess "I am called!"
}

remember unused_variable = 123

actually_used()
"""

    analyze_code(lonely_code, "Functions and variables that are never used")

    # ========================================================================
    # EXAMPLE 4: CHAOTIC CODE
    # ========================================================================

    print_header("EXAMPLE 4: CHAOTIC CODE (Disorganized)")

    chaotic_code = """
remember x = 1
remember VAR_TWO = 2
remember Another_Variable = 3
remember __internal = 4

sigh a() {
    confess x
}

sigh VeryLongFunctionNameThatDoesSimpleThings() {
    if x > 0 {
        if VAR_TWO > 0 {
            if Another_Variable > 0 {
                if __internal > 0 {
                    if x + VAR_TWO > 0 {
                        if Another_Variable + __internal > 0 {
                            confess "too deep"
                        }
                    }
                }
            }
        }
    }
}

a()
VeryLongFunctionNameThatDoesSimpleThings()
"""

    analyze_code(chaotic_code, "Mixed naming conventions and deep nesting")

    # ========================================================================
    # EPILOGUE
    # ========================================================================

    print_header("WHAT MAKES THIS UNPRECEDENTED")

    print("Traditional static analysis tells you:")
    print("  - Syntax errors")
    print("  - Type errors")
    print("  - Maybe unused variables")
    print()
    print("Emotional static analysis tells you:")
    print("  ✓ How your code FEELS")
    print("  ✓ Whether it's sad (complex)")
    print("  ✓ Whether it's anxious (defensive)")
    print("  ✓ Whether it's lonely (unused)")
    print("  ✓ Whether it's chaotic (disorganized)")
    print("  ✓ Whether it's hopeful (clean)")
    print()
    print("And it gives you:")
    print("  → Visual progress bars for each emotion")
    print("  → Detailed reasons for each score")
    print("  → 'Code therapy' recommendations")
    print("  → Overall health score (0-100)")
    print()
    print("This doesn't just find bugs.")
    print("It understands the EMOTIONAL STATE of your codebase.")
    print()
    print("Because code has feelings too.")
    print()

if __name__ == '__main__':
    main()
