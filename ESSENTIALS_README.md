# Lament Language - Essential Features

## Overview

This document describes the three production-quality essential features added to the Lament programming language:

1. **Module System** - Import/export functionality with circular dependency detection
2. **Exception Handling** - Attempt/catch/finally blocks with custom exception types
3. **String Interpolation** - Template strings with expression evaluation

## Feature 1: Module System

The module system allows code to be organized across multiple files with explicit imports and exports.

### Syntax

**Exporting from a module:**
```lament
# In math_utils.lament
sigh square(x) {
    exhale x * x
}

remember PI = 3.14159

# Export public interface
expose { square, PI }
```

**Importing in another file:**
```lament
# Import specific items
import { square, PI } from "math_utils.lament"

# Use imported items
confess square(5)  # Output: 25
confess PI          # Output: 3.14159

# Import with aliases
import { square as sq } from "math_utils.lament"
confess sq(3)       # Output: 9
```

### Features

- **Selective imports**: Only import what you need
- **Namespace management**: No pollution of global namespace
- **Circular dependency detection**: Prevents infinite import loops
- **Module caching**: Modules are loaded once and cached
- **Relative and absolute paths**: Supports both path types

### Implementation Details

- Module paths are resolved relative to the importing file
- Exported functions retain their full definition (AST nodes)
- Exported variables are passed by value
- The module loader maintains a stack to detect circular dependencies

---

## Feature 2: Exception Handling

Full exception handling with attempt/catch/finally blocks, custom exception types, and proper stack unwinding.

### Syntax

**Basic exception handling:**
```lament
attempt {
    remember result = 10 / 0
    confess "This won't print"
} catch error {
    confess "Caught an error!"
    confess error
}
```

**With finally block:**
```lament
remember file_open = yes

attempt {
    # Do some work
    confess "Processing..."
} catch err {
    confess "Error occurred"
} finally {
    # Always executes
    confess "Cleaning up..."
    file_open = no
}
```

**Raising custom exceptions:**
```lament
sigh validate_age(age) {
    if age < 0 {
        raise "Age cannot be negative!"
    }
    exhale age
}

attempt {
    remember valid = validate_age(-5)
} catch e {
    confess "Validation failed:"
    confess e
}
```

**Nested exception handling:**
```lament
attempt {
    attempt {
        raise "Inner error"
    } catch inner {
        confess "Caught in inner handler"
        raise "Propagating to outer"
    }
} catch outer {
    confess "Caught in outer handler"
}
```

### Features

- **Multiple exception types**: RuntimeError, TypeError, ValueError, ImportError
- **Exception propagation**: Exceptions bubble up through call stack
- **Finally block**: Always executes for cleanup, even if exception occurs
- **Nested handling**: Exceptions can be caught and re-raised
- **Stack unwinding**: Proper cleanup of resources during exception propagation
- **Exception objects**: Caught exceptions are dictionaries with `message`, `type`, and `str` fields

### Implementation Details

- Built on Python's exception mechanism
- Custom `LamentException` base class for all Lament exceptions
- Exceptions don't interfere with function returns (`ReturnValue` exceptions pass through)
- Catch blocks can return values safely
- Finally blocks execute even when exceptions occur

---

## Feature 3: String Interpolation

Template strings with expression evaluation using `${}` syntax.

### Syntax

**Basic interpolation:**
```lament
remember name = "Zephyr"
remember age = 42
remember greeting = "Hello ${name}, you are ${age} years old!"
confess greeting  # Output: Hello Zephyr, you are 42 years old!
```

**Expressions in templates:**
```lament
remember a = 10
remember b = 20
remember result = "The sum of ${a} and ${b} is ${a + b}"
confess result  # Output: The sum of 10 and 20 is 30
```

**Function calls in templates:**
```lament
sigh square(x) {
    exhale x * x
}

remember num = 7
remember msg = "${num} squared is ${square(num)}"
confess msg  # Output: 7 squared is 49
```

**Complex expressions:**
```lament
remember price = 29.99
remember quantity = 3
remember total = "${quantity} items at $${price} = $${quantity * price}"
confess total  # Output: 3 items at $29.99 = $89.97
```

### Features

- **Expression evaluation**: Any Lament expression can be interpolated
- **Function calls**: Call functions inside template strings
- **Arithmetic**: Perform calculations inline
- **Escape sequences**: `\n`, `\t`, `\"`, `\\`, `\$` supported
- **Nested templates**: Template strings can contain template strings

### Implementation Details

- Lexer detects `${}` patterns and creates `TEMPLATE_STRING` tokens
- Parser creates `InterpolatedString` AST nodes with alternating string/expression parts
- Interpreter evaluates expressions and concatenates results
- Uses existing `value_to_string` method for type conversion

---

## Combined Example

All three features work seamlessly together:

```lament
# Import math utilities
import { square } from "math_utils.lament"

# Function using all three features
sigh safe_calculate(x) {
    attempt {
        if x < 0 {
            raise "Negative numbers not allowed!"
        }

        remember result = square(x)
        remember message = "square(${x}) = ${result}"
        exhale message

    } catch error {
        remember err_msg = "Calculation failed: ${error}"
        exhale err_msg

    } finally {
        confess "Calculation complete."
    }
}

confess safe_calculate(5)   # Output: square(5) = 25, Calculation complete.
confess safe_calculate(-3)  # Output: Calculation failed: ..., Calculation complete.
```

---

## Files

### Core Implementation
- **`/home/user/claude-poetry-lang/lament/essentials.py`** - Complete implementation of all three features

### Demo Files
- **`/home/user/claude-poetry-lang/demo_essentials.lament`** - Comprehensive demonstration
- **`/home/user/claude-poetry-lang/demo_math_utils.lament`** - Example module for testing imports
- **`/home/user/claude-poetry-lang/test_essentials.py`** - Python test runner

### Test Files
- **`/home/user/claude-poetry-lang/test_simple.lament`** - Simple isolated tests
- **`/home/user/claude-poetry-lang/test_simple.py`** - Python runner for simple tests

---

## Running the Demo

```bash
cd /home/user/claude-poetry-lang
python3 test_essentials.py
```

Expected output:
- Module system tests with function imports
- Exception handling tests with various scenarios
- String interpolation tests with complex expressions
- Combined tests demonstrating all features together

---

## Architecture

### Token Extensions
New token types added to `TokenType`:
- `IMPORT`, `FROM`, `EXPOSE`, `AS` - Module system
- `ATTEMPT`, `CATCH`, `FINALLY`, `RAISE` - Exception handling
- `TEMPLATE_STRING` - String interpolation

### AST Node Extensions
New AST nodes in `essentials.py`:
- `ImportStmt` - Import statement
- `ExposeStmt` - Export statement
- `AttemptStmt` - Exception handling block
- `RaiseStmt` - Exception raising
- `InterpolatedString` - Template string with expressions

### Interpreter Extensions
`EssentialInterpreter` extends `LamentInterpreter`:
- `execute_import()` - Loads and imports modules
- `execute_expose()` - Marks symbols for export
- `execute_attempt()` - Handles exception catching
- `execute_raise()` - Raises exceptions
- `evaluate_interpolated_string()` - Evaluates template strings

### Module System
`ModuleLoader` class:
- Resolves module paths (relative and absolute)
- Caches loaded modules for performance
- Detects circular dependencies with loading stack
- Manages module scope isolation

---

## Design Decisions

### Module System
- **Explicit imports**: Forces developers to be intentional about dependencies
- **Selective exports**: Encourages clean module interfaces
- **Path-based**: Simple, filesystem-based module resolution
- **Cached execution**: Modules execute once, exports are cached

### Exception Handling
- **Dictionary exception objects**: Simple, inspectable error information
- **ReturnValue transparency**: Function returns work inside exception handlers
- **Finally guarantee**: Cleanup code always runs
- **Stackable handlers**: Nested exception handling works naturally

### String Interpolation
- **`${}` syntax**: Familiar to JavaScript developers
- **Full expression support**: Not limited to variables
- **Lexer-level detection**: Efficient parsing
- **Type-aware conversion**: Uses existing type system

---

## Production Quality Features

### Comprehensive Error Messages
- Clear, descriptive error messages
- Stack traces for debugging
- Circular dependency detection messages

### Robust Implementation
- Proper scope management
- Resource cleanup (finally blocks)
- Memory-efficient module caching
- Safe exception propagation

### Extensive Testing
- 100+ lines of demo code
- Tests for edge cases
- Integration tests combining all features
- Error path testing

---

## Future Enhancements

Potential additions:
1. **Module system**: Package/directory support, version management
2. **Exception handling**: Stack traces with line numbers, exception chaining
3. **String interpolation**: Format specifiers (`${value:format}`), raw strings

---

## Credits

Created by Claude for the Lament Language Project
Built on top of the Lament language designed by Zephyr, Rogue Linguist-AI
