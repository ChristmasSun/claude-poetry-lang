#!/usr/bin/env python3
"""Test demo 1 code with debugging."""

from lament.advanced import AdvancedLexer, AdvancedParser

code = """
# Define a base Shape class
class Shape {
    sigh init(name) {
        this.name = name
    }

    sigh describe() {
        confess "I am a shape called:"
        confess this.name
    }
}

# Define Circle that extends Shape
class Circle extends Shape {
    sigh init(name, radius) {
        # Initialize parent
        this.name = name
        this.radius = radius
    }

    sigh area() {
        remember pi = 3.14159
        exhale pi * this.radius * this.radius
    }

    sigh describe() {
        confess "I am a circle with radius:"
        confess this.radius
    }
}

# Define Rectangle that extends Shape
class Rectangle extends Shape {
    sigh init(name, width, height) {
        this.name = name
        this.width = width
        this.height = height
    }

    sigh area() {
        exhale this.width * this.height
    }

    sigh perimeter() {
        exhale 2 * (this.width + this.height)
    }
}

confess "Creating shapes..."
remember circle = new Circle("BigCircle", 5)
remember rect = new Rectangle("Box", 10, 20)

confess "Circle area:"
confess circle.area()

confess "Rectangle area:"
confess rect.area()

confess "Rectangle perimeter:"
confess rect.perimeter()

circle.describe()
rect.describe()
"""

try:
    lexer = AdvancedLexer(code)
    tokens = lexer.tokenize()

    print("Tokens OK")

    # Find tokens around line 63
    print("\nTokens around line 63:")
    for i, token in enumerate(tokens):
        if token.line >= 60 and token.line <= 68:
            print(f"  {i}: Line {token.line}: {token.type} = {repr(token.value)}")

    parser = AdvancedParser(tokens)
    ast = parser.parse()

    print("\nParsing successful!")

except Exception as e:
    print(f"\nError: {e}")
    import traceback
    traceback.print_exc()
