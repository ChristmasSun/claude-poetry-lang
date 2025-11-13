#!/usr/bin/env python3
"""
Demonstration of Lament Emotional Static Analysis
Shows both CLI and programmatic usage
"""

from lament import Lexer, Parser, CodeAnalyzer, EmotionalReport

# Example Lament code to analyze
code_example = """
# A simple example with various emotional states

sigh unused_function() {
    confess "I am never called"
}

sigh overly_nested(x) {
    if x > 0 {
        if x < 10 {
            if x != 5 {
                if x != 3 {
                    confess "Too deep!"
                }
            }
        }
    }
}

sigh clean_function(numbers) {
    remember total = 0
    for num in numbers {
        total = total + num
    }
    exhale total
}

# Actually use one function
remember data = [1, 2, 3]
remember result = clean_function(data)
confess result
"""

def main():
    print("="*70)
    print("LAMENT EMOTIONAL STATIC ANALYSIS DEMO")
    print("="*70)
    print("\nAnalyzing code example...")
    print("\n" + "-"*70)
    print("CODE:")
    print("-"*70)
    print(code_example)
    print("-"*70)

    # Parse the code
    lexer = Lexer(code_example)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()

    # Analyze
    analyzer = CodeAnalyzer(ast)
    metrics = analyzer.analyze()

    # Generate report
    report = EmotionalReport.generate(metrics, "code_example")
    print(report)

    # Programmatic access to metrics
    print("\n" + "="*70)
    print("PROGRAMMATIC ACCESS TO METRICS")
    print("="*70)
    print(f"Overall Health Score: {metrics.overall_health():.1f}/100")
    print(f"Dominant Emotion: {metrics.dominant_emotion()}")
    print(f"Cyclomatic Complexity: {metrics.cyclomatic_complexity}")
    print(f"Max Nesting Depth: {metrics.nesting_depth}")
    print(f"\nEmotional Breakdown:")
    print(f"  Hope: {metrics.hope_score:.1f}%")
    print(f"  Sadness: {metrics.sadness_score:.1f}%")
    print(f"  Anxiety: {metrics.anxiety_score:.1f}%")
    print(f"  Loneliness: {metrics.loneliness_score:.1f}%")
    print(f"  Chaos: {metrics.chaos_score:.1f}%")

if __name__ == '__main__':
    main()
