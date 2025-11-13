# Lament Language Guide

Complete reference for the Lament programming language.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Syntax Overview](#syntax-overview)
3. [Types](#types)
4. [Variables and Memory](#variables-and-memory)
5. [Operators](#operators)
6. [Control Flow](#control-flow)
7. [Functions](#functions)
8. [Collections](#collections)
9. [Temporal Features](#temporal-features)
10. [Metaprogramming](#metaprogramming)
11. [Neural Programming](#neural-programming)
12. [Concurrency](#concurrency)
13. [Error Handling](#error-handling)
14. [Modules and Packages](#modules-and-packages)
15. [Advanced Features](#advanced-features)

---

## Introduction

Lament is a programming language where:
- Every variable is a timeline
- Every execution can be rewound
- Code is data, manipulable at runtime
- Neural networks are first-class primitives
- Errors are compassionate teachers

### Philosophy

```lament
# Every program is a confession
remember pain = 42

# Every variable is a timeline
confess pain@past

# Every function is a sigh
sigh process(x) {
    exhale x + 1
}

# Every output carries weight
confess "Hello, World"  # 0.3s pause for emotional impact
```

---

## Syntax Overview

### Comments

```lament
# Single-line comment

/* Multi-line
   comment */
```

### Keywords

**Memory**:
- `remember` - Declare a variable
- `forget` - Delete a variable

**Functions**:
- `sigh` - Define a function
- `exhale` - Return from function

**I/O**:
- `confess` - Print output (with emotional weight)
- `listen` - Read input (future)

**Control Flow**:
- `if`, `else` - Conditional execution
- `while` - Loop while condition true
- `for`, `in` - Iterate over collection
- `break` - Exit loop
- `continue` - Skip to next iteration

**Temporal**:
- `rewind` - Go back in time
- `snapshot` - Capture current state
- `timeline` - Create/name execution timeline
- `fork` - Branch reality
- `collapse` - Merge realities
- `observe` - Trigger quantum collapse

**Metaprogramming**:
- `quote` - Capture code as AST
- `unquote` - Convert AST to code
- `macro` - Define compile-time transformation
- `eval` - Execute code dynamically

**Types**:
- `void` - Null/none value
- `maybe` - Boolean type keyword

---

## Types

### Basic Types

| Type | Description | Example |
|------|-------------|---------|
| `numb` | 64-bit signed integer | `42`, `-17`, `0` |
| `ache` | 64-bit floating point | `3.14`, `-2.5`, `1e-10` |
| `whisper` | UTF-8 string | `"hello"`, `'world'` |
| `maybe` | Boolean | `true`, `false`, `perhaps` |
| `void` | Null/None | `void` |
| `sigh` | Function | `sigh add(a, b) {...}` |

### Collection Types

```lament
# List (ordered collection)
remember numbers = [1, 2, 3, 4, 5]

# Dict (key-value mapping)
remember person = {
    "name": "Alice",
    "age": 30,
    "active": true
}
```

### Advanced Types

```lament
# Timeline (variable with history)
remember x = 1
x = 2
x = 3
# x is a TimelineValue

# Tensor (neural network primitive)
remember weights = Tensor([[1, 2], [3, 4]])

# AST (code as data)
remember code = quote(confess "hello")
```

### Type Checking

```lament
remember x = 42

# Check type
if is_numb(x) {
    confess "x is a number"
}

# Get type name
remember t = typeof(x)
confess t  # "numb"
```

Available type checkers:
- `is_numb(x)` - Check if integer
- `is_ache(x)` - Check if float
- `is_whisper(x)` - Check if string
- `is_maybe(x)` - Check if boolean
- `is_void(x)` - Check if null
- `is_list(x)` - Check if list
- `is_dict(x)` - Check if dict
- `typeof(x)` - Get type name

---

## Variables and Memory

### Declaration

```lament
# Declare and initialize
remember x = 42
remember name = "Alice"
remember items = [1, 2, 3]
```

### Assignment

```lament
# Reassignment
x = 100
name = "Bob"
```

### Multiple Assignment

```lament
# Destructuring (future feature)
remember a, b = 1, 2
```

### Timeline Variables

Every variable is a timeline that remembers its history:

```lament
remember x = 1
x = 2
x = 3

# Access history
confess x           # 3 (current)
confess x@past      # 2 (one step back)
confess x@past(2)   # 1 (two steps back)
confess x@origin    # 1 (first value ever)
confess x@age       # 3 (assignment count)
confess x@born      # timestamp when created
```

Timeline operators:
- `@past` - Previous value
- `@past(n)` - N steps back
- `@origin` - First value
- `@age` - Number of assignments
- `@born` - Creation timestamp

---

## Operators

### Arithmetic

```lament
remember a = 10
remember b = 3

confess a + b    # 13 (addition)
confess a - b    # 7 (subtraction)
confess a * b    # 30 (multiplication)
confess a / b    # 3 (integer division)
confess a % b    # 1 (modulo)
confess a ** b   # 1000 (exponentiation)
```

### Comparison

```lament
confess a == b   # false (equal)
confess a != b   # true (not equal)
confess a > b    # true (greater than)
confess a < b    # false (less than)
confess a >= b   # true (greater or equal)
confess a <= b   # false (less or equal)
```

### Logical

```lament
remember x = true
remember y = false

confess x and y  # false (logical AND)
confess x or y   # true (logical OR)
confess not x    # false (logical NOT)
```

### String Operations

```lament
remember s1 = "Hello"
remember s2 = "World"

confess s1 + " " + s2  # "Hello World" (concatenation)
confess s1 * 3         # "HelloHelloHello" (repetition)
confess "ll" in s1     # true (substring check)
```

### List Operations

```lament
remember list = [1, 2, 3]

confess list + [4, 5]  # [1, 2, 3, 4, 5] (concatenation)
confess list * 2       # [1, 2, 3, 1, 2, 3] (repetition)
confess 2 in list      # true (membership)
confess list[0]        # 1 (indexing)
```

---

## Control Flow

### If-Else

```lament
remember x = 42

if x > 50 {
    confess "Large"
} else if x > 20 {
    confess "Medium"
} else {
    confess "Small"
}
```

### While Loop

```lament
remember i = 0

while i < 5 {
    confess i
    i = i + 1
}
```

### For Loop

```lament
# Iterate over range
for i in range(5) {
    confess i
}

# Iterate over list
remember items = [1, 2, 3, 4, 5]
for item in items {
    confess item
}

# Iterate over dict keys
remember person = {"name": "Alice", "age": 30}
for key in person {
    confess key + ": " + person[key]
}
```

### Break and Continue

```lament
remember i = 0
while i < 10 {
    i = i + 1

    if i == 3 {
        continue  # Skip 3
    }

    if i == 7 {
        break  # Exit at 7
    }

    confess i
}
# Output: 1, 2, 4, 5, 6
```

---

## Functions

### Definition

```lament
# Basic function
sigh greet(name) {
    confess "Hello, " + name
}

# Function with return value
sigh add(a, b) {
    exhale a + b
}

# Multiple parameters
sigh calculate(x, y, z) {
    remember result = x * y + z
    exhale result
}
```

### Calling Functions

```lament
greet("Alice")
remember sum = add(5, 3)
confess sum  # 8
```

### Return Values

```lament
sigh get_sign(x) {
    if x > 0 {
        exhale "positive"
    } else if x < 0 {
        exhale "negative"
    } else {
        exhale "zero"
    }
}

confess get_sign(42)  # "positive"
```

### Default Parameters (Future)

```lament
# Coming in v1.1
sigh greet(name, greeting="Hello") {
    confess greeting + ", " + name
}
```

### Recursion

```lament
sigh factorial(n) {
    if n <= 1 {
        exhale 1
    }
    exhale n * factorial(n - 1)
}

confess factorial(5)  # 120
```

### Higher-Order Functions (Partial)

```lament
# Functions as values
remember fn = add
confess fn(3, 4)  # 7

# Pass functions as arguments (limited support)
sigh apply(f, x) {
    exhale f(x)
}
```

---

## Collections

### Lists

```lament
# Creation
remember nums = [1, 2, 3, 4, 5]
remember empty = []
remember mixed = [1, "two", true, void]

# Indexing
confess nums[0]      # 1 (first element)
confess nums[-1]     # 5 (last element, future)

# Slicing (future)
confess nums[1:3]    # [2, 3]

# Modification
nums[0] = 10
confess nums  # [10, 2, 3, 4, 5]

# Methods
remember length = length_of(nums)
confess length  # 5

# Iteration
for n in nums {
    confess n
}
```

### Dictionaries

```lament
# Creation
remember person = {
    "name": "Alice",
    "age": 30,
    "city": "NYC"
}

# Access
confess person["name"]  # "Alice"

# Modification
person["age"] = 31

# Add new key
person["email"] = "alice@example.com"

# Iteration
for key in person {
    confess key + ": " + person[key]
}
```

### Tuples (Future)

```lament
# Coming in v1.1
remember point = (10, 20)
remember x, y = point
```

---

## Temporal Features

### Timeline Variables

```lament
remember x = 1
x = 2
x = 3

# Query history
confess x@past      # 2
confess x@past(2)   # 1
confess x@origin    # 1
confess x@age       # 3
confess x@born      # timestamp
```

### Snapshots

```lament
# Create snapshot manually
remember s1 = snapshot()

remember x = 1
remember s2 = snapshot()

x = 2
remember s3 = snapshot()

# List all snapshots
confess list_snapshots()
```

### Time Travel

```lament
remember x = 1
x = 2
x = 3

# Rewind execution
rewind(1)
confess x  # 2

rewind(1)
confess x  # 1
```

### Causal Debugging

```lament
remember price = 100
remember quantity = 5
remember subtotal = price * quantity
remember tax = subtotal * 0.1
remember total = subtotal + tax

# Ask WHY total has its value
confess why(total)

# Output:
# total = 550
#   because: subtotal + tax
#   subtotal = 500
#     because: price * quantity
#     price = 100
#     quantity = 5
#   tax = 50
#     because: subtotal * 0.1
```

### Temporal Contracts

```lament
# Invariant: must ALWAYS be true
invariant balance >= 0

remember balance = 100
balance = balance - 50  # OK
balance = balance - 60  # VIOLATION! Beautiful error

# Ensures: must be true after function
sigh withdraw(amount) {
    ensures balance >= 0
    balance = balance - amount
}

# Eventually: must become true within N steps
eventually(10) balance > 1000
```

### Reality Branching

```lament
remember result = void

fork reality {
    on timeline("fast") {
        result = quick_sort(data)
    }

    on timeline("accurate") {
        result = bubble_sort(data)
    }

    on timeline("experimental") {
        result = quantum_sort(data)
    }
} collapse observe result

confess "Winner: " + current_timeline()
```

---

## Metaprogramming

### AST Reflection

```lament
# Quote: capture code as data
remember code = quote(confess "hello")

# Inspect AST structure
confess ast_of(code)

# Unquote: convert AST back to code
remember expr = unquote(code)

# Evaluate AST dynamically
eval_ast(code)  # Prints "hello"
```

### Macros

```lament
# Define a macro
macro unless(condition, body) {
    exhale quote(
        if not unquote(condition) {
            unquote(body)
        }
    )
}

# Use the macro
unless(x == 0, {
    confess "x is not zero"
})

# Expands to:
# if not (x == 0) {
#     confess "x is not zero"
# }
```

### Code Generation

```lament
# Generate function at runtime
remember fn_name = "add"
remember fn_body = quote(exhale a + b)

# Create function dynamically
remember code = generate_function(fn_name, ["a", "b"], fn_body)
eval_ast(code)

# Now 'add' function exists
confess add(5, 3)  # 8
```

### Introspection

```lament
# List all functions
confess list_functions()

# List all variables
confess list_variables()

# Get function source
confess source_of(add)

# Current timeline
confess current_timeline()
```

---

## Neural Programming

### Tensors

```lament
# Create tensors
remember x = Tensor([[1, 2], [3, 4]])
remember y = Tensor([[5, 6], [7, 8]])

# Arithmetic
remember z = x + y
remember w = x * y
remember m = x @ y  # Matrix multiplication

# With gradients
remember a = Tensor([[2, 3]], requires_grad=true)
remember b = Tensor([[4], [5]], requires_grad=true)
remember c = a @ b

# Backpropagation
c.backward()
confess a.grad  # Gradient of c with respect to a
```

### Neural Networks

```lament
# Create network
remember model = NeuralNetwork("brain")
model.add(Dense(10, 20, "hidden"))
model.add(relu())
model.add(Dense(20, 2, "output"))

# Summary
model.summary()
```

### Training

```lament
# Prepare data
remember train_data = [
    (Tensor([[0, 0]]), Tensor([[0]])),
    (Tensor([[0, 1]]), Tensor([[1]])),
    (Tensor([[1, 0]]), Tensor([[1]])),
    (Tensor([[1, 1]]), Tensor([[0]]))
]

# Create optimizer and loss
remember optimizer = Adam(model.parameters(), lr=0.01)
remember loss_fn = MSELoss()

# Train
remember history = train(
    model=model,
    train_data=train_data,
    optimizer=optimizer,
    loss_fn=loss_fn,
    epochs=100
)

# Evaluate
model.eval()
remember test_input = Tensor([[1, 0]])
remember output = model(test_input)
confess output
```

### Activation Functions

```lament
remember x = Tensor([[-2, -1, 0, 1, 2]])

confess relu(x)     # ReLU activation
confess sigmoid(x)  # Sigmoid activation
confess tanh(x)     # Tanh activation
confess softmax(x)  # Softmax (for classification)
```

---

## Concurrency

### Async/Await (Infrastructure Ready)

```lament
# Future syntax (requires parser support)
async sigh fetch_data(url) {
    confess "Fetching from: " + url
    await sleep_async(1)
    exhale "Data loaded"
}

async sigh main() {
    remember result = await fetch_data("https://example.com")
    confess result
}
```

### Current Async Support

```lament
# Cooperative yielding
sleep_async(2)  # Yields to event loop for 2 seconds
```

---

## Error Handling

### Empathetic Errors

Lament provides compassionate, educational error messages:

```lament
remember user_name = "Alice"
confess usrname  # Typo!

# Error output:
# 💔 LAMENT ERROR 💔
# ════════════════════════════════════════════
#
# I sense your frustration...
#
# I searched for 'usrname' in all the timelines,
#        through all the memories of the void—
#        but it was never remembered.
#        (Perhaps you meant 'user_name'?)
#
# Technical details:
#   Variable 'usrname' is not defined
#   Location: Line 2
#
# Suggested fixes:
#   1. Did you mean 'user_name'? (Check spelling)
#   2. Add: remember usrname = <value>
#
# Session: 7a3f9b2e | Time coding: 15.3 min | Errors: 1
# ════════════════════════════════════════════
```

### Try-Catch (Future)

```lament
# Coming in v1.2
try {
    remember x = risky_operation()
} catch error {
    confess "Error occurred: " + error
}
```

---

## Modules and Packages

### Importing (Future Full Support)

```lament
# Import module
import math

# Import specific functions
from math import sqrt, sin

# Import with alias
import collections as col
```

### Creating Modules

Create a file `mymodule.lament`:

```lament
# mymodule.lament
sigh add(a, b) {
    exhale a + b
}

remember VERSION = "1.0.0"
```

Use it:

```lament
import mymodule

confess mymodule.add(5, 3)
confess mymodule.VERSION
```

---

## Advanced Features

### Performance Hints

```lament
# Mark hot path for JIT compilation
sigh compute_intensive(n) {
    hot_path()

    remember result = 0
    for i in range(n) {
        result = result + i * i
    }
    exhale result
}

# Inline suggestion
sigh small_function(x) {
    inline()
    exhale x + 1
}
```

### Bytecode Compilation

```lament
# Compile to bytecode for faster execution
remember code = compile_to_bytecode("program.lament")

# Execute bytecode
execute_bytecode(code)
```

### Testing

```lament
# Register tests
sigh test_addition() {
    assert_equals(2 + 2, 4)
    assert_greater(5, 3)
}

sigh test_strings() {
    remember s = "Hello"
    assert_contains(s, "ell")
    assert_type(s, "whisper")
}

# Run tests
remember results = run_tests()
confess results
```

### File I/O

```lament
# Write file
write_file("/tmp/test.txt", "Hello, Lament!")

# Read file
remember content = read_file("/tmp/test.txt")
confess content

# Check existence
if file_exists("/tmp/test.txt") {
    confess "File exists"
}

# Directory operations
create_dir("/tmp/mydir")
remember files = list_dir("/tmp/mydir")

# Path manipulation
remember path = join_path("/home", "user", "file.txt")
remember filename = get_filename(path)
remember ext = get_extension(path)
```

### Code Therapy

```lament
# Analyze code emotional health
therapy("myprogram.lament")

# Output identifies:
# - Lonely functions (never called)
# - Anxious modules (too many checks)
# - Overwhelmed functions (too complex)
# - Deep nesting (too many levels)
```

---

## Standard Library

### Math Functions

```lament
confess ache_of(x)          # Absolute value
confess sqrt_of_pain(x)     # Square root
confess sin_of_loss(x)      # Sine (radians)
confess cos_of_hope(x)      # Cosine
confess tan_of_uncertainty(x)  # Tangent
confess floor_of_reality(x) # Floor
confess ceil_of_dreams(x)   # Ceiling
```

### String Functions

```lament
remember s = "Hello, World"

confess length_of(s)        # 12
confess upper_case(s)       # "HELLO, WORLD"
confess lower_case(s)       # "hello, world"
confess split(s, ",")       # ["Hello", " World"]
confess strip(s)            # Remove whitespace
confess replace(s, "World", "Lament")
```

### List Functions

```lament
remember nums = [3, 1, 4, 1, 5]

confess length_of(nums)     # 5
confess sum_of(nums)        # 14
confess max_of(nums)        # 5
confess min_of(nums)        # 1
confess sort(nums)          # [1, 1, 3, 4, 5]
confess reverse(nums)       # [5, 1, 4, 1, 3]
```

### Time Functions

```lament
confess now()               # Current timestamp
confess sleep(2)            # Sleep for 2 seconds
confess time_since(x@born)  # Time since x was created
```

---

## Code Examples

### Fibonacci

```lament
sigh fibonacci(n) {
    if n <= 1 {
        exhale n
    }
    exhale fibonacci(n - 1) + fibonacci(n - 2)
}

for i in range(10) {
    confess fibonacci(i)
}
```

### Factorial with Time Travel

```lament
sigh factorial(n) {
    if n <= 1 {
        exhale 1
    }
    exhale n * factorial(n - 1)
}

remember result = factorial(5)
confess result  # 120

# Check computation history
confess why(result)
```

### Bank Account with Contracts

```lament
remember balance = 1000

# Invariant: balance must always be non-negative
invariant balance >= 0

sigh withdraw(amount) {
    ensures balance >= 0
    balance = balance - amount
}

withdraw(500)   # OK, balance = 500
withdraw(600)   # VIOLATION! Contract fails
```

### Neural XOR

```lament
# XOR problem with neural network
remember X = [
    Tensor([[0, 0]]),
    Tensor([[0, 1]]),
    Tensor([[1, 0]]),
    Tensor([[1, 1]])
]
remember y = [
    Tensor([[0]]),
    Tensor([[1]]),
    Tensor([[1]]),
    Tensor([[0]])
]

remember model = NeuralNetwork("XOR")
model.add(Dense(2, 4))
model.add(Dense(4, 1))

remember optimizer = Adam(model.parameters(), lr=0.1)
remember loss_fn = MSELoss()

train(model, zip(X, y), optimizer, loss_fn, epochs=1000)

# Test
model.eval()
for i in range(4) {
    remember pred = model(X[i])
    confess "Input: " + X[i] + " -> " + pred
}
```

### Reality Branching Example

```lament
remember data = [5, 2, 8, 1, 9, 3]
remember result = void

fork reality {
    on timeline("quick") {
        result = quick_sort(data)
    }

    on timeline("merge") {
        result = merge_sort(data)
    }

    on timeline("insertion") {
        result = insertion_sort(data)
    }
} collapse observe result

confess "Sorted: " + result
confess "Winner: " + current_timeline()
```

---

## Style Guide

### Naming Conventions

```lament
# Variables: snake_case
remember user_name = "Alice"
remember total_count = 0

# Functions: snake_case
sigh calculate_total(items) {
    # ...
}

# Constants: UPPER_CASE
remember MAX_SIZE = 100
remember PI = 3.14159
```

### Indentation

```lament
# Use 4 spaces for indentation
sigh example() {
    if condition {
        remember x = 1
        while x < 10 {
            confess x
            x = x + 1
        }
    }
}
```

### Line Length

Keep lines under 80 characters when possible.

### Comments

```lament
# Use descriptive comments
remember balance = 1000  # Starting balance in cents

# Document complex logic
# This loop calculates the running average
# using a sliding window of size 5
for i in range(length_of(data) - 4) {
    remember window = data[i:i+5]
    remember avg = sum_of(window) / 5
    confess avg
}
```

---

## Best Practices

### 1. Use Timeline Features Wisely

```lament
# Good: Track important changes
remember account_balance = 1000
account_balance = account_balance - 500
confess "Previous balance: " + account_balance@past

# Avoid: Overusing temporal queries (performance cost)
```

### 2. Leverage Causal Debugging

```lament
# When debugging complex calculations
remember result = complex_calculation()
confess why(result)  # See complete dependency graph
```

### 3. Write Temporal Contracts

```lament
# Enforce invariants for critical state
invariant balance >= 0
invariant users.length > 0
```

### 4. Use Empathetic Errors

```lament
# Let errors teach you
# Read error messages carefully
# They suggest fixes and explain concepts
```

### 5. Experiment with Reality Branching

```lament
# Try multiple approaches
fork reality {
    on timeline("fast") { /* quick algorithm */ }
    on timeline("accurate") { /* precise algorithm */ }
} collapse observe result
```

---

## Next Steps

- Read the [Tutorial](TUTORIAL.md) for guided learning
- Explore [API Reference](API_REFERENCE.md) for detailed function docs
- Check [Examples](../examples/) for real-world code
- Join the [Community](https://discord.gg/lament) for help

---

**The language guide is your companion. May your code feel alive.**
