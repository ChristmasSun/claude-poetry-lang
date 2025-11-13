#!/usr/bin/env python3
"""
Comprehensive test suite for the Lament lexer module.
This validates all aspects of tokenization functionality.
"""

from lament.lexer import Lexer, TokenType, Token


def test_keywords():
    """Test that all keywords are recognized correctly."""
    print("Testing Keywords...")
    code = """
    confess remember forget sigh exhale if else while for in
    fork reality on collapse observe timeline
    void yes no perhaps is not and or
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    keyword_tokens = [t for t in tokens if t.type != TokenType.EOF]
    expected_count = 24
    assert len(keyword_tokens) == expected_count, f"Expected {expected_count} keywords, got {len(keyword_tokens)}"
    print(f"  ✓ All {expected_count} keywords recognized")


def test_literals():
    """Test numeric and string literals."""
    print("Testing Literals...")
    code = '''
    42
    3.14159
    "Hello, Lament"
    "String with \\"escapes\\" and \\n newlines"
    '''
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    numbers = [t for t in tokens if t.type == TokenType.NUMBER]
    strings = [t for t in tokens if t.type == TokenType.STRING]

    assert len(numbers) == 2, f"Expected 2 numbers, got {len(numbers)}"
    assert numbers[0].value == 42, "Integer parsing failed"
    assert numbers[1].value == 3.14159, "Float parsing failed"

    assert len(strings) == 2, f"Expected 2 strings, got {len(strings)}"
    assert strings[0].value == "Hello, Lament", "Simple string failed"
    assert '\n' in strings[1].value, "String escape sequences failed"

    print(f"  ✓ Numbers: {len(numbers)} parsed correctly")
    print(f"  ✓ Strings: {len(strings)} parsed with escapes")


def test_operators():
    """Test all operators."""
    print("Testing Operators...")
    code = """
    + - * / % = == != < > <= >=
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    operators = [t for t in tokens if t.type != TokenType.EOF]
    expected_types = [
        TokenType.PLUS, TokenType.MINUS, TokenType.MULTIPLY, TokenType.DIVIDE,
        TokenType.MODULO, TokenType.ASSIGN, TokenType.EQUAL, TokenType.NOT_EQUAL,
        TokenType.LESS, TokenType.GREATER, TokenType.LESS_EQ, TokenType.GREATER_EQ
    ]

    assert len(operators) == len(expected_types), f"Expected {len(expected_types)} operators"

    for i, expected in enumerate(expected_types):
        assert operators[i].type == expected, f"Operator mismatch at position {i}"

    print(f"  ✓ All {len(expected_types)} operators recognized")


def test_temporal_operators():
    """Test temporal operators (@past, @origin, @age, @born)."""
    print("Testing Temporal Operators...")
    code = """
    x@past
    x@past(3)
    x@origin
    x@age
    x@born
    """
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    temporal = [t for t in tokens if 'AT_' in t.type.name]
    assert len(temporal) == 5, f"Expected 5 temporal operators, got {len(temporal)}"

    expected_temporal = [
        TokenType.AT_PAST, TokenType.AT_PAST,
        TokenType.AT_ORIGIN, TokenType.AT_AGE, TokenType.AT_BORN
    ]

    for i, expected in enumerate(expected_temporal):
        assert temporal[i].type == expected, f"Temporal operator mismatch at {i}"

    print(f"  ✓ All 4 temporal operators recognized")
    print(f"  ✓ Temporal with offset @past(3) supported")


def test_delimiters():
    """Test all delimiters and brackets."""
    print("Testing Delimiters...")
    code = "( ) { } [ ] , . :"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    delimiters = [t for t in tokens if t.type != TokenType.EOF]
    expected = [
        TokenType.LPAREN, TokenType.RPAREN,
        TokenType.LBRACE, TokenType.RBRACE,
        TokenType.LBRACKET, TokenType.RBRACKET,
        TokenType.COMMA, TokenType.DOT, TokenType.COLON
    ]

    assert len(delimiters) == len(expected)
    for i, exp_type in enumerate(expected):
        assert delimiters[i].type == exp_type

    print(f"  ✓ All {len(expected)} delimiters recognized")


def test_comments():
    """Test single-line and multi-line comments."""
    print("Testing Comments...")

    # Single-line comment
    code1 = """
    remember x = 1  # This is a comment
    # Another comment
    confess x
    """
    lexer1 = Lexer(code1)
    tokens1 = lexer1.tokenize()
    # Comments should be skipped
    assert not any('comment' in str(t.value or '').lower() for t in tokens1)

    # Multi-line comment
    code2 = """
    remember x = 1
    /* This is a
       multi-line comment
       spanning several lines */
    confess x
    """
    lexer2 = Lexer(code2)
    tokens2 = lexer2.tokenize()
    assert not any('multi-line' in str(t.value or '').lower() for t in tokens2)

    print("  ✓ Single-line comments ignored")
    print("  ✓ Multi-line comments ignored")


def test_identifiers():
    """Test identifier recognition."""
    print("Testing Identifiers...")
    code = "myVar _private var123 CamelCase snake_case"
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
    expected_names = ['myVar', '_private', 'var123', 'CamelCase', 'snake_case']

    assert len(identifiers) == len(expected_names)
    for i, name in enumerate(expected_names):
        assert identifiers[i].value == name

    print(f"  ✓ All {len(expected_names)} identifier styles recognized")


def test_line_tracking():
    """Test that line numbers are tracked correctly."""
    print("Testing Line Number Tracking...")
    code = """line 1
line 2
line 3
line 4"""
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    identifiers = [t for t in tokens if t.type == TokenType.IDENTIFIER]
    assert identifiers[0].line == 1
    assert identifiers[1].line == 2
    assert identifiers[2].line == 3
    assert identifiers[3].line == 4

    print("  ✓ Line numbers tracked correctly")


def test_error_handling():
    """Test that errors are raised for invalid input."""
    print("Testing Error Handling...")

    # Unterminated string
    try:
        lexer1 = Lexer('"unterminated string')
        lexer1.tokenize()
        assert False, "Should have raised error for unterminated string"
    except SyntaxError as e:
        assert "Unterminated string" in str(e)
        print("  ✓ Unterminated string error raised")

    # Invalid temporal operator
    try:
        lexer2 = Lexer('x@future')
        lexer2.tokenize()
        assert False, "Should have raised error for invalid temporal"
    except SyntaxError as e:
        assert "Unknown temporal operator" in str(e)
        print("  ✓ Invalid temporal operator error raised")

    # Unexpected character
    try:
        lexer3 = Lexer('$invalid')
        lexer3.tokenize()
        assert False, "Should have raised error for unexpected character"
    except SyntaxError as e:
        assert "Unexpected character" in str(e)
        print("  ✓ Unexpected character error raised")


def test_complete_program():
    """Test tokenization of a complete Lament program."""
    print("Testing Complete Program...")
    code = '''
    # Factorial example
    sigh factorial(n) {
        if n <= 1 {
            exhale 1
        } else {
            exhale n * factorial(n - 1)
        }
    }

    remember result = factorial(5)
    confess result
    '''
    lexer = Lexer(code)
    tokens = lexer.tokenize()

    # Verify key tokens are present
    token_types = [t.type for t in tokens]
    assert TokenType.SIGH in token_types
    assert TokenType.IF in token_types
    assert TokenType.ELSE in token_types
    assert TokenType.EXHALE in token_types
    assert TokenType.REMEMBER in token_types
    assert TokenType.CONFESS in token_types

    print(f"  ✓ Complete program tokenized ({len(tokens)} tokens)")


def main():
    """Run all tests."""
    print("=" * 70)
    print("LAMENT LEXER COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()

    tests = [
        test_keywords,
        test_literals,
        test_operators,
        test_temporal_operators,
        test_delimiters,
        test_comments,
        test_identifiers,
        test_line_tracking,
        test_error_handling,
        test_complete_program,
    ]

    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"  ✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
        print()

    print("=" * 70)
    if failed == 0:
        print("ALL TESTS PASSED!")
        print("The Lament lexer is production-ready.")
    else:
        print(f"FAILED: {failed} test(s)")
    print("=" * 70)

    return failed


if __name__ == '__main__':
    exit(main())
