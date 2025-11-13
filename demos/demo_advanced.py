#!/usr/bin/env python3
"""
Lament Advanced Features Demo
==============================

Demonstrates:
1. Classes and Objects with Inheritance
2. Pattern Matching with Guards and Destructuring
3. Generators and Iterators with Lazy Evaluation

Run with: python3 demo_advanced.py
"""

from lament.advanced import run_advanced_lament


# ============================================================================
# DEMO 1: CLASSES AND OBJECTS WITH INHERITANCE
# ============================================================================

def demo_classes():
    """Demonstrate classes, objects, inheritance, and methods."""
    print("\n" + "="*70)
    print("DEMO 1: CLASSES AND OBJECTS WITH INHERITANCE")
    print("="*70 + "\n")

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

    run_advanced_lament(code)


# ============================================================================
# DEMO 2: PATTERN MATCHING
# ============================================================================

def demo_pattern_matching():
    """Demonstrate pattern matching with various patterns."""
    print("\n" + "="*70)
    print("DEMO 2: PATTERN MATCHING")
    print("="*70 + "\n")

    code = """
confess "=== Testing Literal Patterns ==="

remember x = 5
match x {
    case 0 => { confess "Zero" },
    case 5 => { confess "Found five!" },
    case _ => { confess "Something else" }
}

confess ""
confess "=== Testing Range Patterns ==="

remember score = 85
match score {
    case 0..59 => { confess "Grade: F" },
    case 60..69 => { confess "Grade: D" },
    case 70..79 => { confess "Grade: C" },
    case 80..89 => { confess "Grade: B" },
    case 90..100 => { confess "Grade: A" },
    case _ => { confess "Invalid score" }
}

confess ""
confess "=== Testing List Destructuring ==="

remember coords = [10, 20, 30]
match coords {
    case [x, y, z] => {
        confess "3D Point:"
        confess x
        confess y
        confess z
    },
    case [x, y] => {
        confess "2D Point"
    },
    case _ => {
        confess "Unknown structure"
    }
}

confess ""
confess "=== Testing Guard Clauses ==="

remember age = 25
match age {
    case n when n < 0 => { confess "Invalid age" },
    case n when n < 18 => { confess "Minor" },
    case n when n < 65 => { confess "Adult" },
    case _ => { confess "Senior" }
}

confess ""
confess "=== Testing Complex Patterns ==="

remember data = [1, 2, 3, 4, 5]
match data {
    case [] => { confess "Empty list" },
    case [a] => { confess "Single element" },
    case [first, second, ..rest] => {
        confess "First:"
        confess first
        confess "Second:"
        confess second
        confess "Rest:"
        confess rest
    }
}
"""

    run_advanced_lament(code)


# ============================================================================
# DEMO 3: GENERATORS AND LAZY EVALUATION
# ============================================================================

def demo_generators():
    """Demonstrate generators with yield."""
    print("\n" + "="*70)
    print("DEMO 3: GENERATORS AND LAZY EVALUATION")
    print("="*70 + "\n")

    code = """
confess "=== Simple Generator ==="

sigh count_up(n) {
    remember i = 0
    while i < n {
        yield i
        i = i + 1
    }
}

confess "Counting to 5:"
remember counter = count_up(5)
for num in counter {
    confess num
}

confess ""
confess "=== Fibonacci Generator ==="

sigh fibonacci(limit) {
    remember a = 0
    remember b = 1
    remember count = 0

    while count < limit {
        yield a
        remember temp = a + b
        a = b
        b = temp
        count = count + 1
    }
}

confess "First 10 Fibonacci numbers:"
remember fib = fibonacci(10)
for n in fib {
    confess n
}

confess ""
confess "=== Infinite Generator (limited iteration) ==="

sigh natural_numbers() {
    remember n = 1
    while yes {
        yield n
        n = n + 1
    }
}

confess "First 5 natural numbers:"
remember nums = natural_numbers()
remember count = 0
for n in nums {
    if count < 5 {
        confess n
        count = count + 1
    } else {
        # Break by exhausting
    }
}

confess ""
confess "=== Generator with Conditions ==="

sigh even_numbers(max_val) {
    remember n = 0
    while n <= max_val {
        if n % 2 == 0 {
            yield n
        }
        n = n + 1
    }
}

confess "Even numbers up to 10:"
remember evens = even_numbers(10)
for e in evens {
    confess e
}
"""

    run_advanced_lament(code)


# ============================================================================
# DEMO 4: COMBINING ALL FEATURES
# ============================================================================

def demo_combined():
    """Demonstrate all three features working together."""
    print("\n" + "="*70)
    print("DEMO 4: COMBINING ALL FEATURES")
    print("="*70 + "\n")

    code = """
confess "=== Building a Number Sequence Analyzer ==="

# Class hierarchy for different sequence types
class Sequence {
    sigh init(name) {
        this.name = name
    }

    sigh describe() {
        confess this.name
    }
}

class RangeSequence extends Sequence {
    sigh init(start, end) {
        this.name = "Range Sequence"
        this.start = start
        this.end = end
    }

    sigh generate() {
        remember n = this.start
        while n <= this.end {
            yield n
            n = n + 1
        }
    }
}

class FibonacciSequence extends Sequence {
    sigh init(count) {
        this.name = "Fibonacci Sequence"
        this.count = count
    }

    sigh generate() {
        remember a = 0
        remember b = 1
        remember i = 0

        while i < this.count {
            yield a
            remember temp = a + b
            a = b
            b = temp
            i = i + 1
        }
    }
}

confess "Creating sequences..."
remember range_seq = new RangeSequence(1, 10)
remember fib_seq = new FibonacciSequence(8)

confess ""
confess "Analyzing range sequence:"
range_seq.describe()

remember gen = range_seq.generate()
for num in gen {
    # Pattern match on each number
    match num {
        case 1..3 => { confess "Small" },
        case 4..7 => { confess "Medium" },
        case 8..10 => { confess "Large" },
        case _ => { confess "Out of range" }
    }
}

confess ""
confess "Analyzing Fibonacci sequence:"
fib_seq.describe()

remember fib_gen = fib_seq.generate()
for num in fib_gen {
    # Pattern match on Fibonacci numbers
    match num {
        case 0 => { confess "Zero - the beginning" },
        case 1 => { confess "One - the seed" },
        case n when n < 10 => { confess "Single digit Fib" },
        case _ => { confess "Growing larger..." }
    }
}

confess ""
confess "Demo complete!"
"""

    run_advanced_lament(code)


# ============================================================================
# DEMO 5: ADVANCED OOP PATTERNS
# ============================================================================

def demo_oop_patterns():
    """Demonstrate advanced OOP patterns."""
    print("\n" + "="*70)
    print("DEMO 5: ADVANCED OOP PATTERNS")
    print("="*70 + "\n")

    code = """
confess "=== Employee Management System ==="

class Person {
    sigh init(name, age) {
        this.name = name
        this.age = age
    }

    sigh greet() {
        confess "Hello, I am:"
        confess this.name
    }
}

class Employee extends Person {
    sigh init(name, age, employee_id, salary) {
        this.name = name
        this.age = age
        this.employee_id = employee_id
        this.salary = salary
    }

    sigh give_raise(amount) {
        this.salary = this.salary + amount
        confess "New salary:"
        confess this.salary
    }

    sigh classify_salary() {
        match this.salary {
            case 0..30000 => { confess "Entry level" },
            case 30001..60000 => { confess "Mid level" },
            case 60001..100000 => { confess "Senior level" },
            case _ => { confess "Executive level" }
        }
    }
}

confess "Creating employees..."
remember emp1 = new Employee("Alice", 28, 1001, 45000)
remember emp2 = new Employee("Bob", 35, 1002, 75000)

confess ""
confess "Employee 1:"
emp1.greet()
confess "Salary classification:"
emp1.classify_salary()

confess ""
confess "Giving raise to Employee 1:"
emp1.give_raise(10000)
confess "New classification:"
emp1.classify_salary()

confess ""
confess "Employee 2:"
emp2.greet()
confess "Salary classification:"
emp2.classify_salary()
"""

    run_advanced_lament(code)


# ============================================================================
# DEMO 6: PRACTICAL GENERATOR PATTERNS
# ============================================================================

def demo_practical_generators():
    """Demonstrate practical generator use cases."""
    print("\n" + "="*70)
    print("DEMO 6: PRACTICAL GENERATOR PATTERNS")
    print("="*70 + "\n")

    code = """
confess "=== Practical Generator Patterns ==="

# Generator for filtering
sigh filter_positive(numbers) {
    for n in numbers {
        if n > 0 {
            yield n
        }
    }
}

# Generator for transforming
sigh double_values(numbers) {
    for n in numbers {
        yield n * 2
    }
}

# Generator for arithmetic sequences
sigh arithmetic_seq(start, step, count) {
    remember current = start
    remember i = 0
    while i < count {
        yield current
        current = current + step
        i = i + 1
    }
}

confess "Original numbers:"
remember nums = [1, -2, 3, -4, 5, -6, 7]
for n in nums {
    confess n
}

confess ""
confess "Positive numbers only:"
remember positive = filter_positive(nums)
for n in positive {
    confess n
}

confess ""
confess "Arithmetic sequence (start=5, step=3, count=7):"
remember arith = arithmetic_seq(5, 3, 7)
for n in arith {
    confess n
}

confess ""
confess "Powers of 2 (using generator):"
sigh powers_of_two(limit) {
    remember power = 1
    remember exp = 0
    while exp <= limit {
        yield power
        power = power * 2
        exp = exp + 1
    }
}

remember powers = powers_of_two(8)
for p in powers {
    confess p
}
"""

    run_advanced_lament(code)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("LAMENT ADVANCED FEATURES DEMONSTRATION")
    print("="*70)

    demos = [
        ("Classes and Objects", demo_classes),
        ("Pattern Matching", demo_pattern_matching),
        ("Generators", demo_generators),
        ("Combined Features", demo_combined),
        ("OOP Patterns", demo_oop_patterns),
        ("Practical Generators", demo_practical_generators),
    ]

    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\nError in {name} demo: {e}\n")
            import traceback
            traceback.print_exc()

    print("\n" + "="*70)
    print("ALL DEMOS COMPLETE!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
