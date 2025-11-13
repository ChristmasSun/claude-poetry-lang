# Contributing to Lament

Thank you for your interest in contributing to Lament! This document provides guidelines and instructions for contributing.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Setup](#development-setup)
4. [How to Contribute](#how-to-contribute)
5. [Coding Standards](#coding-standards)
6. [Testing Guidelines](#testing-guidelines)
7. [Documentation](#documentation)
8. [Pull Request Process](#pull-request-process)
9. [Areas Needing Help](#areas-needing-help)
10. [Community](#community)

---

## Code of Conduct

This project adheres to the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code. Please report unacceptable behavior to hello@lament-lang.org.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Familiarity with programming language implementation (helpful but not required)
- Enthusiasm for innovative language design!

### First Steps

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/lament.git
   cd lament
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

4. **Test your changes**
   ```bash
   python3 -m pytest tests/
   ```

5. **Submit a pull request**
   - Push to your fork
   - Open a PR on the main repository

---

## Development Setup

### Install Development Dependencies

```bash
pip3 install -r requirements-dev.txt
```

Or manually:
```bash
pip3 install pytest pytest-cov black flake8 mypy numpy rich
```

### Development Tools

- **pytest**: Testing framework
- **black**: Code formatter
- **flake8**: Linter
- **mypy**: Type checker
- **numpy**: For neural features
- **rich**: Enhanced terminal output

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_lexer.py

# Run with coverage
pytest --cov=lament tests/

# Run verbose
pytest -v tests/
```

### Code Formatting

```bash
# Format code
black lament/

# Check formatting
black --check lament/
```

### Linting

```bash
# Run linter
flake8 lament/

# With specific rules
flake8 --max-line-length=100 lament/
```

### Type Checking

```bash
# Run type checker
mypy lament/
```

---

## How to Contribute

### Types of Contributions

1. **Bug Fixes**
   - Find a bug
   - Create an issue (if not exists)
   - Fix the bug
   - Add tests
   - Submit PR

2. **New Features**
   - Discuss in an issue first
   - Implement the feature
   - Add comprehensive tests
   - Update documentation
   - Submit PR

3. **Documentation**
   - Improve existing docs
   - Add examples
   - Fix typos
   - Translate docs
   - Submit PR

4. **Tests**
   - Improve test coverage
   - Add edge case tests
   - Submit PR

5. **Examples**
   - Add example programs
   - Improve existing examples
   - Submit PR

---

## Coding Standards

### Python Style

Follow **PEP 8** with these modifications:
- Maximum line length: 100 characters
- Use double quotes for strings
- Use f-strings for formatting

### Example

```python
def calculate_total(price: float, quantity: int, tax_rate: float = 0.1) -> float:
    """Calculate total price including tax.

    Args:
        price: Unit price
        quantity: Number of items
        tax_rate: Tax rate (default 0.1)

    Returns:
        Total price including tax

    Example:
        >>> calculate_total(100, 5, 0.1)
        550.0
    """
    subtotal = price * quantity
    tax = subtotal * tax_rate
    total = subtotal + tax
    return total
```

### Code Structure

```python
# 1. Imports (standard library, then third-party, then local)
import os
import sys
from typing import List, Optional

import numpy as np

from lament.lexer import Lexer
from lament.parser import Parser

# 2. Constants
MAX_ITERATIONS = 1000
DEFAULT_TIMEOUT = 30

# 3. Classes and functions
class MyClass:
    """Docstring for class."""

    def __init__(self, param: int):
        """Initialize."""
        self.param = param

    def method(self) -> str:
        """Method docstring."""
        return f"Value: {self.param}"

# 4. Main execution (if applicable)
if __name__ == "__main__":
    main()
```

### Naming Conventions

```python
# Classes: PascalCase
class LamentInterpreter:
    pass

# Functions and methods: snake_case
def parse_expression():
    pass

# Constants: UPPER_CASE
MAX_STACK_SIZE = 1000

# Private members: _leading_underscore
def _internal_function():
    pass

# Very private members: __double_underscore
class MyClass:
    def __init__(self):
        self.__private = 42
```

### Documentation

Every public function/class must have a docstring:

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description.

    Detailed description (if needed).

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When param2 is negative

    Example:
        >>> function_name("test", 5)
        True
    """
    pass
```

---

## Testing Guidelines

### Writing Tests

Use **pytest** for all tests:

```python
# tests/test_feature.py
import pytest
from lament.feature import MyFeature

def test_basic_functionality():
    """Test basic functionality."""
    feature = MyFeature()
    result = feature.process(42)
    assert result == 84

def test_edge_case():
    """Test edge case."""
    feature = MyFeature()
    with pytest.raises(ValueError):
        feature.process(-1)

@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (5, 10),
    (0, 0),
])
def test_multiple_cases(input, expected):
    """Test multiple cases."""
    feature = MyFeature()
    assert feature.process(input) == expected
```

### Test Coverage

- Aim for **80%+ coverage**
- Cover happy paths
- Cover edge cases
- Cover error conditions

### Running Specific Tests

```bash
# Run one test file
pytest tests/test_lexer.py

# Run one test function
pytest tests/test_lexer.py::test_tokenize_number

# Run tests matching pattern
pytest -k "temporal"
```

---

## Documentation

### Types of Documentation

1. **Code Comments**
   - Explain **why**, not what
   - Use for complex logic

2. **Docstrings**
   - Every public function/class
   - Follow Google style

3. **Markdown Documentation**
   - User guides
   - Tutorials
   - API reference

### Example Documentation

```python
def why(variable: TimelineValue) -> str:
    """Generate causal trace showing why variable has its current value.

    This function performs computational archaeology, tracing back through
    all dependencies to show how the current value was computed.

    Args:
        variable: The variable to trace

    Returns:
        Formatted causal trace as a string

    Example:
        >>> x = 2
        >>> y = 3
        >>> z = x + y
        >>> print(why(z))
        z = 5 because x + y
            x = 2
            y = 3
    """
    # Build dependency tree
    tree = build_dependency_tree(variable)

    # Format for display
    return format_causal_trace(tree)
```

---

## Pull Request Process

### Before Submitting

1. **Test your changes**
   ```bash
   pytest tests/
   ```

2. **Format your code**
   ```bash
   black lament/
   ```

3. **Lint your code**
   ```bash
   flake8 lament/
   ```

4. **Update documentation**
   - Update relevant .md files
   - Update docstrings
   - Add examples

5. **Write descriptive commit messages**
   ```
   Add causal debugging for neural networks

   - Implement why() function for tensors
   - Track dependencies in computational graph
   - Add tests for causal tracing
   - Update API documentation

   Fixes #123
   ```

### PR Checklist

- [ ] Tests pass (`pytest tests/`)
- [ ] Code is formatted (`black --check lament/`)
- [ ] Code is linted (`flake8 lament/`)
- [ ] Documentation is updated
- [ ] Commit messages are descriptive
- [ ] PR description explains the change
- [ ] Related issues are linked

### PR Template

When opening a PR, include:

```markdown
## Description
Brief description of the change.

## Motivation
Why is this change needed?

## Changes Made
- Change 1
- Change 2
- Change 3

## Testing
How was this tested?

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Tests pass
- [ ] Code formatted
- [ ] Documentation updated
- [ ] No breaking changes (or documented)

## Related Issues
Fixes #123
Related to #456
```

### Review Process

1. **Submit PR**
2. **Automated checks run** (CI/CD)
3. **Maintainer review** (within 1-3 days)
4. **Address feedback** (if needed)
5. **Approval and merge**

---

## Areas Needing Help

### High Priority

1. **Pattern Matching** (v1.1)
   - Implement pattern matching syntax
   - Parser support
   - Tests

2. **JIT Compilation** (v1.2)
   - LLVM backend
   - Hot path detection
   - Optimization passes

3. **IDE Support**
   - Language Server Protocol (LSP)
   - Syntax highlighting
   - VS Code extension

4. **Package Ecosystem**
   - Package manager improvements
   - Standard library expansion
   - Third-party packages

### Medium Priority

1. **Documentation**
   - More examples
   - Video tutorials
   - Translations

2. **Testing**
   - Increase coverage
   - Stress tests
   - Performance benchmarks

3. **Error Messages**
   - More error types
   - Better suggestions
   - More empathy

4. **Tooling**
   - Code formatter (lament-fmt)
   - Linter (lament-lint)
   - Debugger integration

### Low Priority (but welcome!)

1. **Website**
   - Landing page
   - Documentation site
   - Blog

2. **Community**
   - Discord bot
   - GitHub actions
   - CI/CD improvements

3. **Experimental Features**
   - Quantum backend
   - Logic programming
   - Mythic programming

---

## Community

### Communication Channels

- **Discord**: [Join our server](https://discord.gg/lament) (coming soon)
- **Forum**: [discuss.lament-lang.org](https://discuss.lament-lang.org) (coming soon)
- **GitHub Issues**: For bugs and features
- **Email**: hello@lament-lang.org

### Asking for Help

Don't hesitate to ask questions!

- **Stuck on implementation?** Open a discussion issue
- **Not sure about approach?** Ask on Discord
- **Found a bug?** Open an issue with details
- **Want to contribute but don't know where?** Check "good first issue" label

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Credited in release notes
- Thanked in community channels
- Given contributor badge (coming soon)

---

## Git Workflow

### Branch Naming

```
feature/add-pattern-matching
bugfix/fix-temporal-access
docs/improve-tutorial
test/add-bytecode-tests
refactor/simplify-parser
```

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add pattern matching support
fix: resolve temporal paradox in rewind
docs: update API reference for neural module
test: add tests for causal debugging
refactor: simplify AST visitor pattern
chore: update dependencies
```

### Keeping Your Fork Updated

```bash
# Add upstream remote
git remote add upstream https://github.com/original/lament.git

# Fetch upstream changes
git fetch upstream

# Merge upstream main into your branch
git merge upstream/main

# Or rebase
git rebase upstream/main
```

---

## Development Tips

### Debugging

```python
# Use breakpoints
import pdb; pdb.set_trace()

# Or
breakpoint()

# Print debugging
print(f"DEBUG: {variable}")

# Logging
import logging
logging.debug("Debug message")
```

### Testing Locally

```bash
# Test your changes in REPL
python3 lament/cli.py repl

# Test with a file
echo 'confess "test"' > test.lament
python3 lament/cli.py run test.lament

# Run benchmarks
python3 benchmarks/run_benchmarks.py
```

### Understanding the Codebase

1. Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. Explore `lament/__init__.py` for module overview
3. Read tests to understand usage
4. Check existing issues and PRs

---

## Release Process

(For maintainers)

1. Update version in `__init__.py`
2. Update [CHANGELOG.md](CHANGELOG.md)
3. Create release branch
4. Run full test suite
5. Build documentation
6. Create GitHub release
7. Publish to PyPI (when available)
8. Announce on community channels

---

## Legal

By contributing, you agree that:
- Your contributions are your original work
- You have the right to submit your contributions
- Your contributions will be licensed under the MIT License
- You grant us the right to use your contributions

---

## Questions?

If you have questions about contributing:

1. Check existing documentation
2. Search closed issues/PRs
3. Ask on Discord
4. Open a discussion issue
5. Email hello@lament-lang.org

---

## Thank You!

Every contribution makes Lament better. Whether you:
- Fix a typo
- Report a bug
- Add a feature
- Improve documentation
- Help other users

**You're making a difference.** Thank you for being part of the Lament community!

---

**"A language built by the community, for the community."**

— The Lament Team
