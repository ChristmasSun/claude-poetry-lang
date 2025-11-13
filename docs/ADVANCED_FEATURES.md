# Lament Advanced Features

This document describes the three essential advanced features added to the Lament programming language.

## 1. Classes and Objects

### Syntax

```lament
class ClassName {
    sigh init(param1, param2) {
        this.field1 = param1
        this.field2 = param2
    }

    sigh method_name(arg) {
        # Method body
        exhale result
    }
}
```

### Features

- **Class definitions** with `class ClassName { ... }` syntax
- **Constructor** using `sigh init(...)` method
- **Instance fields** accessed via `this.fieldname`
- **Methods** defined as regular functions within the class
- **Instance creation** using `new ClassName(args)`
- **Inheritance** with `class Child extends Parent` syntax
- **`this` keyword** for accessing current instance
- **`super` keyword** for accessing parent class methods (planned)

### Example

```lament
class Shape {
    sigh init(name) {
        this.name = name
    }

    sigh describe() {
        confess "I am a shape called:"
        confess this.name
    }
}

class Circle extends Shape {
    sigh init(name, radius) {
        this.name = name
        this.radius = radius
    }

    sigh area() {
        remember pi = 3.14159
        exhale pi * this.radius * this.radius
    }
}

remember circle = new Circle("BigCircle", 5)
confess circle.area()  # 78.53975
circle.describe()      # Calls inherited method
```

## 2. Pattern Matching

### Syntax

```lament
match expression {
    case pattern1 [when guard] => { body },
    case pattern2 [when guard] => { body },
    case _ => { default_body }
}
```

### Pattern Types

1. **Literal Patterns**: Match exact values
   ```lament
   case 0 => { confess "Zero" }
   case 5 => { confess "Five" }
   ```

2. **Range Patterns**: Match ranges of numbers
   ```lament
   case 0..59 => { confess "Grade: F" }
   case 60..69 => { confess "Grade: D" }
   case 90..100 => { confess "Grade: A" }
   ```

3. **Wildcard Pattern**: Match anything
   ```lament
   case _ => { confess "Default case" }
   ```

4. **Bind Pattern**: Bind matched value to variable
   ```lament
   case n => { confess n }
   ```

5. **List Destructuring**: Match and extract list elements
   ```lament
   case [x, y, z] => { confess "3D point" }
   case [first, second, ..rest] => { confess "Rest pattern" }
   ```

6. **Guard Clauses**: Add conditions to patterns
   ```lament
   case n when n < 0 => { confess "Negative" }
   case n when n < 18 => { confess "Minor" }
   case n when n < 65 => { confess "Adult" }
   ```

### Example

```lament
remember score = 85
match score {
    case 0..59 => { confess "Grade: F" },
    case 60..69 => { confess "Grade: D" },
    case 70..79 => { confess "Grade: C" },
    case 80..89 => { confess "Grade: B" },
    case 90..100 => { confess "Grade: A" },
    case _ => { confess "Invalid score" }
}

remember coords = [10, 20, 30]
match coords {
    case [x, y, z] => {
        confess "3D Point:"
        confess x
        confess y
        confess z
    },
    case _ => { confess "Not a 3D point" }
}
```

## 3. Generators and Iterators

### Syntax

```lament
sigh generator_name(params) {
    # Generator body with yield statements
    yield value
}
```

### Features

- **`yield` keyword**: Pause execution and return a value
- **Lazy evaluation**: Values generated on-demand
- **Iterable**: Can be used in `for` loops
- **Infinite sequences**: Generate unbounded sequences
- **State preservation**: Variables maintain values between yields

### Examples

```lament
# Simple counter generator
sigh count_up(n) {
    remember i = 0
    while i < n {
        yield i
        i = i + 1
    }
}

remember counter = count_up(5)
for num in counter {
    confess num  # Prints: 0, 1, 2, 3, 4
}

# Fibonacci generator
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

remember fib = fibonacci(10)
for n in fib {
    confess n  # Prints first 10 Fibonacci numbers
}

# Infinite generator
sigh natural_numbers() {
    remember n = 1
    while yes {
        yield n
        n = n + 1
    }
}

remember nums = natural_numbers()
# Use with care - this generates infinite values!
```

## Implementation Details

### File Structure

- **/home/user/claude-poetry-lang/lament/advanced.py**: Complete implementation
  - Extended lexer (`AdvancedLexer`)
  - Extended parser (`AdvancedParser`)
  - Extended interpreter (`AdvancedInterpreter`)
  - Runtime classes (`LamentObject`, `Generator`)

### New Token Types

- `CLASS`, `NEW`, `THIS`, `EXTENDS`, `SUPER`
- `MATCH`, `CASE`, `WHEN`, `ARROW` (=>)
- `YIELD`
- `UNDERSCORE` (_), `DOTDOT` (..), `PIPE` (|)

### New AST Nodes

**Classes:**
- `ClassDef`: Class definition
- `NewInstance`: Object instantiation
- `MemberAccess`: Member access (obj.field)
- `MemberAssignment`: Member assignment (obj.field = value)
- `ThisExpr`: `this` keyword
- `SuperExpr`: `super` keyword

**Pattern Matching:**
- `MatchStmt`: Match statement
- `Pattern`: Base pattern class
- `LiteralPattern`: Literal value pattern
- `RangePattern`: Range pattern (start..end)
- `ListPattern`: List destructuring pattern
- `WildcardPattern`: Wildcard (_) pattern
- `BindPattern`: Variable binding pattern

**Generators:**
- `YieldStmt`: Yield statement
- `Generator`: Runtime generator object
- `YieldValue`: Exception for yield control flow

## Running Examples

```bash
# Run comprehensive demo
python3 demo_advanced.py

# Run individual tests
python3 test_simple_class.py
python3 test_pattern_match.py
python3 test_generator.py
```

## Features Summary

| Feature | Status | Notes |
|---------|--------|-------|
| Class definitions | ✅ | Fully working |
| Constructors | ✅ | Using `init` method |
| Instance fields | ✅ | Access via `this.field` |
| Methods | ✅ | Defined as functions in class |
| Inheritance | ✅ | Using `extends` keyword |
| Method calls | ✅ | obj.method() syntax |
| Pattern matching | ✅ | All pattern types working |
| Range patterns | ✅ | Using `..` operator |
| Guard clauses | ✅ | Using `when` keyword |
| List destructuring | ✅ | Including rest patterns |
| Generators | ✅ | Using `yield` keyword |
| Lazy evaluation | ✅ | Values generated on-demand |
| Infinite sequences | ✅ | Can create unbounded generators |

## Production Quality Features

1. **Comprehensive Error Handling**: All edge cases handled with clear error messages
2. **Full Lexer Support**: All new operators and keywords properly tokenized
3. **Robust Parser**: Handles complex nested structures
4. **Efficient Interpreter**: Optimized execution model
5. **Demo Coverage**: Complete demonstration of all features
6. **Documentation**: Fully documented code with docstrings

## Future Enhancements

- `super` method calls for parent class access
- Multiple inheritance support
- Abstract classes and interfaces
- Property decorators
- Generator expressions
- Async/await for generators
- Pattern guards on multiple variables
- Enum patterns
