# Lament Quick Start Guide

## Installation

Already done! You're ready to go.

## Running Lament

### Interactive REPL
```bash
python3 -m lament.cli repl
```

### Run a File
```bash
python3 -m lament.cli run myfile.lament
```

### Run an Example
```bash
python3 -m lament.cli run examples/getting_started.lament
```

---

## Syntax Cheat Sheet

### Variables
```lament
remember x = 10              # Declare variable
remember name = "Alice"      # Strings
remember pi = 3.14          # Floats
x = 20                      # Reassign
```

### Output
```lament
confess "Hello"             # Print
confess x                   # Print variable
confess x + y              # Print expression
```

### Functions
```lament
sigh add(a, b) {           # Define function
    exhale a + b           # Return value
}

remember result = add(5, 3)
confess result             # 8
```

### Data Structures
```lament
# Lists
remember nums = [1, 2, 3, 4]
confess nums[0]            # 1
nums[0] = 10              # Modify

# Dictionaries
remember person = {"name": "Bob", "age": 30}
confess person["name"]     # Bob
person["age"] = 31        # Modify
person["city"] = "NYC"    # Add new key
```

### Control Flow
```lament
# If/Else
if x > 10 {
    confess "Big"
} else {
    confess "Small"
}

# While Loop
remember i = 0
while i < 5 {
    confess i
    i = i + 1
}

# For Loop
for item in list {
    confess item
}
```

### Operators
```lament
# Arithmetic
x + y    # Add
x - y    # Subtract
x * y    # Multiply
x / y    # Divide
x % y    # Modulo

# Comparison
x == y   # Equal
x != y   # Not equal
x < y    # Less than
x > y    # Greater than
x <= y   # Less or equal
x >= y   # Greater or equal

# Logical
x and y
x or y
not x

# Membership
x in list
key in dict
```

### Built-in Functions
```lament
length_of(list)           # Get length
range(5)                  # [0, 1, 2, 3, 4]
dict()                    # Create empty dict
list()                    # Create empty list
```

---

## Your First Programs

### 1. Calculator
```lament
sigh calculator(op, a, b) {
    if op == "add" {
        exhale a + b
    }
    if op == "sub" {
        exhale a - b
    }
    if op == "mul" {
        exhale a * b
    }
    if op == "div" {
        exhale a / b
    }
    exhale void
}

confess calculator("add", 10, 5)  # 15
confess calculator("mul", 10, 5)  # 50
```

### 2. FizzBuzz
```lament
remember i = 1
while i <= 20 {
    if i % 15 == 0 {
        confess "FizzBuzz"
    } else {
        if i % 3 == 0 {
            confess "Fizz"
        } else {
            if i % 5 == 0 {
                confess "Buzz"
            } else {
                confess i
            }
        }
    }
    i = i + 1
}
```

### 3. Fibonacci
```lament
sigh fibonacci(n) {
    if n <= 1 {
        exhale n
    }
    exhale fibonacci(n - 1) + fibonacci(n - 2)
}

remember i = 0
while i <= 10 {
    confess fibonacci(i)
    i = i + 1
}
```

### 4. Word Counter
```lament
sigh count_words(text) {
    remember words = ["hello", "world", "hello", "test"]
    remember counts = {}
    
    for word in words {
        if word in counts {
            counts[word] = counts[word] + 1
        } else {
            counts[word] = 1
        }
    }
    
    exhale counts
}

remember result = count_words("sample")
confess result
```

---

## Explore Examples

The `examples/` directory has many programs:

```bash
# Basic examples
python3 -m lament.cli run examples/getting_started.lament

# Temporal features (time-travel)
python3 -m lament.cli run examples/temporal_advanced_example.lament

# System features (file I/O, etc)
python3 -m lament.cli run examples/system_features.lament

# Self-hosting demos
python3 -m lament.cli run compiler/final_compiler.lament
python3 -m lament.cli run compiler/fixed_point.lament
```

---

## Tips

1. **Emotional Syntax**: Lament uses "emotional" keywords
   - `remember` instead of `var/let`
   - `confess` instead of `print`
   - `sigh` instead of `function`
   - `exhale` instead of `return`

2. **No Semicolons**: Newlines separate statements

3. **Strong Types**: Numbers, strings, lists, dicts, booleans

4. **Everything Returns**: All functions return values (void if none)

5. **Read the Examples**: Best way to learn is reading `examples/*.lament`

---

## Next Steps

1. Try the REPL: `python3 -m lament.cli repl`
2. Run examples: `python3 -m lament.cli run examples/getting_started.lament`
3. Write your own `.lament` files
4. Check out `docs/TUTORIAL.md` for more in-depth guide
5. Read `SELF_HOSTING.md` to see how Lament compiles itself!

---

## Getting Help

- **Examples**: `examples/` directory
- **Documentation**: `docs/` directory  
- **Self-Hosting**: `SELF_HOSTING.md`
- **Full Guide**: `docs/LANGUAGE_GUIDE.md`

---

## Quick Reference Card

```
DECLARE:  remember x = value
PRINT:    confess expression
FUNCTION: sigh name(params) { ... exhale result }
IF:       if condition { } else { }
WHILE:    while condition { }
FOR:      for item in list { }
LIST:     [1, 2, 3]
DICT:     {"key": value}
COMMENT:  # This is a comment
```

---

**Happy coding in Lament!** 💜⏰

*"A language that feels is a language that lives."*
