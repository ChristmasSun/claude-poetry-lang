# Lament Emotional Static Analysis

## Overview

The Lament Emotional Static Analysis system is an **unprecedented** approach to code quality analysis that doesn't just find bugs—it **feels your code's pain**. It diagnoses emotional states and offers therapy recommendations.

## Emotional States Detected

### 1. **Sad Code** (Complexity & Confusion)
- High cyclomatic complexity
- Deep nesting levels (nested conditionals/loops)
- Functions that are too long
- Too many variables to track mentally
- Unmaintainable, confusing code

### 2. **Anxious Code** (Excessive Checks)
- Too many conditional branches
- Defensive programming gone wrong
- Excessive reality forking (quantum paranoia)
- Obsessing over the past (temporal access)
- Over-validation and redundant checks

### 3. **Hopeful Code** (Clean & Beautiful)
- Good naming conventions
- Well-structured functions
- Reasonable complexity
- Shallow nesting depth
- High code reuse
- Self-documenting with confessions

### 4. **Lonely Code** (Dead & Unused)
- Functions that are never called
- Variables that are never used
- Dead code taking up emotional space
- Orphaned, purposeless code

### 5. **Chaotic Code** (Disorganized)
- Inconsistent naming conventions (mixing camelCase and snake_case)
- Cryptically short variable names
- No clear organization
- Deep nesting creating a labyrinth
- Random structure, no patterns

## Usage

### Command Line

```bash
# Analyze a single file
python3 -m lament.analysis your_file.lament

# Exit codes:
# 0 = Healthy (health score >= 60)
# 1 = Needs improvement (40 <= health < 60)
# 2 = Critical (health < 40)
```

### Programmatic Usage

```python
from lament import Lexer, Parser, CodeAnalyzer, EmotionalReport

# Read and parse your code
with open('your_file.lament', 'r') as f:
    source = f.read()

lexer = Lexer(source)
tokens = lexer.tokenize()
parser = Parser(tokens)
ast = parser.parse()

# Analyze
analyzer = CodeAnalyzer(ast)
metrics = analyzer.analyze()

# Generate report
report = EmotionalReport.generate(metrics, "your_file.lament")
print(report)

# Access metrics directly
print(f"Overall Health: {metrics.overall_health():.1f}/100")
print(f"Dominant Emotion: {metrics.dominant_emotion()}")
print(f"Hope Score: {metrics.hope_score:.1f}/100")
print(f"Sadness Score: {metrics.sadness_score:.1f}/100")
print(f"Anxiety Score: {metrics.anxiety_score:.1f}/100")
print(f"Loneliness Score: {metrics.loneliness_score:.1f}/100")
print(f"Chaos Score: {metrics.chaos_score:.1f}/100")
```

## Example Analysis

### Clean Code (97.5/100 Health)
```lament
sigh calculate_factorial(number) {
    if number <= 1 {
        exhale 1
    }
    remember previous = calculate_factorial(number - 1)
    exhale number * previous
}

remember result = calculate_factorial(5)
confess result
```

**Result**: Hope: 100%, Sadness: 0%, Anxiety: 0%, Loneliness: 0%, Chaos: 0%

### Problematic Code (20.8/100 Health)
```lament
sigh unused_function() {
    confess "Nobody calls me"
}

sigh deeply_nested(a, b, c, d, e, f, g, h) {
    if a > 0 {
        if b > 0 {
            if c > 0 {
                if d > 0 {
                    if e > 0 {
                        if f > 0 {
                            if g > 0 {
                                if h > 0 {
                                    confess "Too deep!"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

remember x = 1  # Never used
remember y = 2  # Never used
```

**Result**: Hope: 100%, Sadness: 80%, Anxiety: 60%, Loneliness: 100%, Chaos: 73%

## Metrics Explained

### EmotionalMetrics Fields
- `sadness_score`: 0-100, measures complexity and unmaintainability
- `anxiety_score`: 0-100, measures excessive checking and paranoia
- `hope_score`: 0-100, measures code quality and clarity
- `loneliness_score`: 0-100, measures amount of dead/unused code
- `chaos_score`: 0-100, measures disorganization and inconsistency
- `overall_health()`: 0-100, weighted score of all emotions
- `dominant_emotion()`: Returns the strongest emotional state
- `emotional_state()`: Returns a poetic description

### Core Metrics
- `total_functions`: Number of functions defined
- `total_variables`: Number of variables declared
- `cyclomatic_complexity`: Measure of code complexity (branches)
- `nesting_depth`: Maximum depth of nested structures

## Code Therapy Recommendations

The analyzer provides personalized therapy recommendations:

- **For Sadness**: Extract methods, reduce nesting, simplify conditionals
- **For Anxiety**: Consolidate checks, trust your data, reduce validation
- **For Loneliness**: Delete dead code, use version control instead of keeping "just in case"
- **For Chaos**: Choose one naming convention, organize code, flatten nesting
- **For Hope**: Keep doing what you're doing!

## Files

- `/home/user/claude-poetry-lang/lament/analysis.py` - Main analyzer implementation
- `/home/user/claude-poetry-lang/demo_analysis.py` - Demonstration script
- `/home/user/claude-poetry-lang/test_emotional.lament` - Test file with mixed emotions
- `/home/user/claude-poetry-lang/test_hopeful.lament` - Example of clean code
- `/home/user/claude-poetry-lang/example_analysis_all_features.lament` - Comprehensive test

## Philosophy

> "Code has feelings too. It can be sad, anxious, lonely, chaotic, or hopeful.
> Understanding your code's emotions is the first step to healing."

The Lament Emotional Static Analysis system treats code quality as an emotional journey, not just a technical checklist. By understanding what your code *feels*, you can better understand how to improve it.

## Contributing

When your code is feeling down, remember:
- Every refactoring is a step toward hope
- Simplicity is sophisticated
- Your future self will thank you
- Less code = less bugs = less maintenance = more happiness

---

*Created with ❤️ for the Lament Programming Language*
*"Every program is a confession. Every variable is a timeline. Every execution is a multiverse."*
