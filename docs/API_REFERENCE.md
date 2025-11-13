# Lament API Reference

Complete API documentation for all modules, functions, and classes.

---

## Table of Contents

1. [Core Language](#core-language)
2. [Built-in Functions](#built-in-functions)
3. [Temporal Functions](#temporal-functions)
4. [Neural Network API](#neural-network-api)
5. [File I/O API](#file-io-api)
6. [Testing Framework](#testing-framework)
7. [Metaprogramming API](#metaprogramming-api)
8. [Analysis and Empathy](#analysis-and-empathy)
9. [Concurrency API](#concurrency-api)
10. [Type System](#type-system)
11. [CLI Commands](#cli-commands)

---

## Core Language

### Types

#### `numb` - Integer Type
64-bit signed integer.

```lament
remember x = 42
remember y = -17
```

#### `ache` - Float Type
64-bit floating point number.

```lament
remember pi = 3.14159
remember temp = -273.15
```

#### `whisper` - String Type
UTF-8 encoded strings.

```lament
remember message = "Hello, World"
remember emoji = "💜"
```

#### `maybe` - Boolean Type
Boolean values.

```lament
remember yes = true
remember no = false
```

#### `void` - Null Type
Represents absence of value.

```lament
remember nothing = void
```

#### `sigh` - Function Type
Function object.

```lament
sigh add(a, b) {
    exhale a + b
}
```

---

## Built-in Functions

### I/O Functions

#### `confess(value)`
Print value to output with emotional weight (0.3s pause).

**Parameters:**
- `value` - Any type

**Returns:** `void`

**Example:**
```lament
confess "Hello, World"
confess 42
```

---

### Math Functions

#### `ache_of(x)`
Absolute value.

**Parameters:**
- `x` (numb or ache) - Number

**Returns:** Non-negative number

**Example:**
```lament
confess ache_of(-5)  # 5
```

#### `sqrt_of_pain(x)`
Square root.

**Parameters:**
- `x` (numb or ache) - Non-negative number

**Returns:** ache

**Example:**
```lament
confess sqrt_of_pain(16)  # 4.0
```

#### `sin_of_loss(x)`
Sine (radians).

**Parameters:**
- `x` (ache) - Angle in radians

**Returns:** ache

**Example:**
```lament
remember pi = 3.14159
confess sin_of_loss(pi / 2)  # 1.0
```

#### `cos_of_hope(x)`
Cosine (radians).

**Parameters:**
- `x` (ache) - Angle in radians

**Returns:** ache

#### `tan_of_uncertainty(x)`
Tangent (radians).

**Parameters:**
- `x` (ache) - Angle in radians

**Returns:** ache

---

### Collection Functions

#### `length_of(collection)`
Get length of collection.

**Parameters:**
- `collection` (list or whisper) - Collection

**Returns:** numb - Length

**Example:**
```lament
remember nums = [1, 2, 3, 4, 5]
confess length_of(nums)  # 5
```

#### `range(start, stop?, step?)`
Generate range of numbers.

**Parameters:**
- `start` (numb) - Start (or stop if only one arg)
- `stop` (numb, optional) - Stop value
- `step` (numb, optional) - Step size

**Returns:** list

**Example:**
```lament
confess range(5)        # [0, 1, 2, 3, 4]
confess range(2, 7)     # [2, 3, 4, 5, 6]
confess range(0, 10, 2) # [0, 2, 4, 6, 8]
```

---

### Type Checking Functions

#### `is_numb(x)`
Check if value is integer.

**Parameters:**
- `x` - Any value

**Returns:** maybe (boolean)

**Example:**
```lament
confess is_numb(42)      # true
confess is_numb("hello") # false
```

#### `is_ache(x)`
Check if value is float.

#### `is_whisper(x)`
Check if value is string.

#### `is_maybe(x)`
Check if value is boolean.

#### `is_void(x)`
Check if value is void/null.

#### `is_list(x)`
Check if value is list.

#### `is_dict(x)`
Check if value is dictionary.

#### `typeof(x)`
Get type name as string.

**Parameters:**
- `x` - Any value

**Returns:** whisper - Type name

**Example:**
```lament
confess typeof(42)      # "numb"
confess typeof("hi")    # "whisper"
confess typeof([1,2,3]) # "list"
```

---

## Temporal Functions

### Timeline Access

#### `x@past`
Access previous value of variable.

**Example:**
```lament
remember x = 1
x = 2
x = 3
confess x@past  # 2
```

#### `x@past(n)`
Access value N steps back.

**Example:**
```lament
confess x@past(2)  # 1
```

#### `x@origin`
Access first value of variable.

**Example:**
```lament
confess x@origin  # 1
```

#### `x@age`
Get assignment count.

**Example:**
```lament
confess x@age  # 3
```

#### `x@born`
Get creation timestamp.

**Example:**
```lament
confess x@born  # 1699876543.21
```

---

### Time-Travel Functions

#### `snapshot()`
Create execution snapshot.

**Returns:** Snapshot object

**Example:**
```lament
remember s1 = snapshot()
```

#### `list_snapshots()`
List all execution snapshots.

**Returns:** list of snapshots

**Example:**
```lament
confess list_snapshots()
```

#### `rewind(n)`
Rewind execution N steps.

**Parameters:**
- `n` (numb) - Number of steps to rewind

**Returns:** void

**Example:**
```lament
remember x = 1
x = 2
x = 3
rewind(1)
confess x  # 2
```

---

### Causal Debugging

#### `why(variable)`
Show causal trace of variable.

**Parameters:**
- `variable` - Any variable

**Returns:** whisper - Formatted causal trace

**Example:**
```lament
remember x = 2
remember y = 3
remember z = x + y

confess why(z)
# Shows: z = 5 because x + y
#   x = 2
#   y = 3
```

---

### Temporal Contracts

#### `invariant condition`
Declare condition that must always be true.

**Parameters:**
- `condition` - Boolean expression

**Example:**
```lament
invariant balance >= 0

remember balance = 1000
balance = balance - 500  # OK
balance = balance - 600  # ERROR: invariant violated
```

#### `ensures condition`
Post-condition for function (must be true after function).

**Example:**
```lament
sigh withdraw(amount) {
    ensures balance >= 0
    balance = balance - amount
}
```

#### `eventually(n) condition`
Condition must become true within N steps.

**Parameters:**
- `n` (numb) - Maximum number of steps
- `condition` - Boolean expression

**Example:**
```lament
eventually(10) balance > 1000

remember balance = 500
# ... within 10 assignments, balance must exceed 1000
```

---

## Neural Network API

### Tensor Class

#### `Tensor(data, requires_grad=false, name=void)`
Create a tensor for neural network operations.

**Parameters:**
- `data` (list) - Multi-dimensional array
- `requires_grad` (maybe, optional) - Track gradients
- `name` (whisper, optional) - Tensor name

**Returns:** Tensor

**Methods:**
- `backward()` - Compute gradients
- `zero_grad()` - Reset gradients
- `tolist()` - Convert to Python list

**Example:**
```lament
remember x = Tensor([[1, 2], [3, 4]], requires_grad=true)
remember y = x * 2
y.backward()
confess x.grad
```

---

### Neural Network Layers

#### `Dense(input_dim, output_dim, name=void)`
Fully connected layer.

**Parameters:**
- `input_dim` (numb) - Input dimensions
- `output_dim` (numb) - Output dimensions
- `name` (whisper, optional) - Layer name

**Returns:** Dense layer

**Example:**
```lament
remember layer = Dense(10, 20, "hidden")
```

#### `Conv2D(in_channels, out_channels, kernel_size, name=void)`
2D convolutional layer.

**Parameters:**
- `in_channels` (numb) - Input channels
- `out_channels` (numb) - Output channels
- `kernel_size` (numb) - Kernel size
- `name` (whisper, optional) - Layer name

#### `Dropout(rate)`
Dropout regularization.

**Parameters:**
- `rate` (ache) - Dropout rate (0-1)

#### `BatchNorm(num_features)`
Batch normalization.

**Parameters:**
- `num_features` (numb) - Number of features

---

### Activation Functions

#### `relu(x)`, `sigmoid(x)`, `tanh(x)`, `softmax(x)`
Activation functions.

**Parameters:**
- `x` (Tensor) - Input tensor

**Returns:** Tensor

**Example:**
```lament
remember x = Tensor([[-1, 0, 1, 2]])
confess relu(x)     # [0, 0, 1, 2]
confess sigmoid(x)  # Sigmoid transform
```

---

### Loss Functions

#### `MSELoss()`
Mean squared error loss.

**Returns:** Loss function

**Example:**
```lament
remember loss_fn = MSELoss()
remember loss = loss_fn(predictions, targets)
```

#### `CrossEntropyLoss()`
Cross entropy loss for classification.

#### `BinaryCrossEntropyLoss()`
Binary cross entropy loss.

---

### Optimizers

#### `SGD(parameters, lr=0.01, momentum=0)`
Stochastic gradient descent.

**Parameters:**
- `parameters` (list) - Model parameters
- `lr` (ache) - Learning rate
- `momentum` (ache) - Momentum

**Returns:** Optimizer

**Example:**
```lament
remember optimizer = SGD(model.parameters(), lr=0.01)
```

#### `Adam(parameters, lr=0.001, betas=(0.9, 0.999))`
Adam optimizer.

**Parameters:**
- `parameters` (list) - Model parameters
- `lr` (ache) - Learning rate
- `betas` (tuple) - Beta parameters

**Returns:** Optimizer

---

### Neural Network Class

#### `NeuralNetwork(name)`
Create neural network.

**Parameters:**
- `name` (whisper) - Network name

**Methods:**
- `add(layer)` - Add layer
- `forward(x)` - Forward pass
- `parameters()` - Get all parameters
- `train()` - Set training mode
- `eval()` - Set evaluation mode
- `summary()` - Print architecture

**Example:**
```lament
remember model = NeuralNetwork("brain")
model.add(Dense(10, 20))
model.add(Dense(20, 2))
model.summary()
```

---

### Training Functions

#### `train(model, train_data, optimizer, loss_fn, epochs=10, val_data=void)`
Train neural network.

**Parameters:**
- `model` (NeuralNetwork) - Model to train
- `train_data` (list) - Training data (input, target) pairs
- `optimizer` (Optimizer) - Optimizer
- `loss_fn` (Loss) - Loss function
- `epochs` (numb) - Number of epochs
- `val_data` (list, optional) - Validation data

**Returns:** TrainingHistory

**Example:**
```lament
remember history = train(
    model=model,
    train_data=train_data,
    optimizer=Adam(model.parameters()),
    loss_fn=MSELoss(),
    epochs=100
)
```

#### `train_epoch(model, train_data, optimizer, loss_fn)`
Train for one epoch.

#### `evaluate(model, test_data, loss_fn)`
Evaluate model on test data.

---

## File I/O API

### File Operations

#### `read_file(path)`
Read entire file contents.

**Parameters:**
- `path` (whisper) - File path

**Returns:** whisper - File contents

**Example:**
```lament
remember content = read_file("/tmp/data.txt")
confess content
```

#### `write_file(path, content)`
Write content to file (overwrites).

**Parameters:**
- `path` (whisper) - File path
- `content` (whisper) - Content to write

**Returns:** void

**Example:**
```lament
write_file("/tmp/output.txt", "Hello, Lament!")
```

#### `append_to_file(path, content)`
Append content to file.

**Parameters:**
- `path` (whisper) - File path
- `content` (whisper) - Content to append

**Returns:** void

#### `file_exists(path)`
Check if file exists.

**Parameters:**
- `path` (whisper) - File path

**Returns:** maybe (boolean)

**Example:**
```lament
if file_exists("/tmp/data.txt") {
    confess "File exists"
}
```

#### `remove_file(path)`
Delete file.

**Parameters:**
- `path` (whisper) - File path

**Returns:** void

---

### Directory Operations

#### `create_dir(path)`
Create directory (including parents).

**Parameters:**
- `path` (whisper) - Directory path

**Returns:** void

**Example:**
```lament
create_dir("/tmp/mydir/subdir")
```

#### `dir_exists(path)`
Check if directory exists.

**Parameters:**
- `path` (whisper) - Directory path

**Returns:** maybe (boolean)

#### `remove_dir(path)`
Remove empty directory.

**Parameters:**
- `path` (whisper) - Directory path

**Returns:** void

#### `list_dir(path)`
List directory contents.

**Parameters:**
- `path` (whisper) - Directory path

**Returns:** list - List of filenames

**Example:**
```lament
remember files = list_dir("/tmp")
for file in files {
    confess file
}
```

---

### Path Manipulation

#### `join_path(parts...)`
Join path components.

**Parameters:**
- `parts` (whisper...) - Path components

**Returns:** whisper - Joined path

**Example:**
```lament
remember path = join_path("/home", "user", "file.txt")
# Result: /home/user/file.txt
```

#### `get_filename(path)`
Extract filename from path.

**Parameters:**
- `path` (whisper) - File path

**Returns:** whisper - Filename

**Example:**
```lament
confess get_filename("/home/user/file.txt")  # "file.txt"
```

#### `get_extension(path)`
Get file extension.

**Parameters:**
- `path` (whisper) - File path

**Returns:** whisper - Extension with dot

**Example:**
```lament
confess get_extension("program.lament")  # ".lament"
```

#### `get_parent_dir(path)`
Get parent directory.

**Parameters:**
- `path` (whisper) - File path

**Returns:** whisper - Parent directory

#### `get_path_info(path)`
Get detailed path information.

**Parameters:**
- `path` (whisper) - File path

**Returns:** dict - Path information

**Example:**
```lament
remember info = get_path_info("/tmp/file.txt")
confess info["size"]
confess info["is_file"]
confess info["modified"]
```

---

## Testing Framework

### Test Functions

#### `register_test(name, function)`
Register a test function.

**Parameters:**
- `name` (whisper) - Test name
- `function` (sigh) - Test function

**Returns:** void

#### `run_tests()`
Run all registered tests.

**Returns:** dict - Test results

**Example:**
```lament
sigh test_addition() {
    assert_equals(2 + 2, 4)
}

register_test("Addition Test", test_addition)
remember results = run_tests()
```

---

### Assertions

#### `assert_equals(actual, expected)`
Assert two values are equal.

**Parameters:**
- `actual` - Actual value
- `expected` - Expected value

**Throws:** AssertionError if not equal

**Example:**
```lament
assert_equals(2 + 2, 4)
```

#### `assert_not_equals(actual, expected)`
Assert two values are not equal.

#### `assert_true(value)`
Assert value is truthy.

#### `assert_false(value)`
Assert value is falsy.

#### `assert_greater(actual, expected)`
Assert actual > expected.

#### `assert_less(actual, expected)`
Assert actual < expected.

#### `assert_contains(container, item)`
Assert item in container.

**Example:**
```lament
assert_contains([1, 2, 3], 2)
assert_contains("hello", "ell")
```

#### `assert_type(value, type_name)`
Assert value has expected type.

**Parameters:**
- `value` - Value to check
- `type_name` (whisper) - Expected type name

**Example:**
```lament
assert_type(42, "numb")
assert_type("hello", "whisper")
```

---

## Metaprogramming API

### AST Manipulation

#### `quote(expression)`
Capture code as AST.

**Parameters:**
- `expression` - Any expression

**Returns:** AST node

**Example:**
```lament
remember code = quote(confess "hello")
```

#### `unquote(ast)`
Convert AST back to code.

**Parameters:**
- `ast` - AST node

**Returns:** Expression

#### `ast_of(expression)`
Get AST structure.

**Parameters:**
- `expression` - Any expression

**Returns:** AST representation

#### `eval_ast(ast)`
Evaluate AST dynamically.

**Parameters:**
- `ast` - AST node

**Returns:** Result of evaluation

**Example:**
```lament
remember code = quote(2 + 3)
remember result = eval_ast(code)
confess result  # 5
```

---

### Introspection

#### `list_functions()`
List all defined functions.

**Returns:** list - Function names

**Example:**
```lament
confess list_functions()
```

#### `list_variables()`
List all variables in scope.

**Returns:** list - Variable names

#### `source_of(function)`
Get function source code.

**Parameters:**
- `function` (sigh) - Function

**Returns:** whisper - Source code

#### `current_timeline()`
Get name of current execution timeline.

**Returns:** whisper - Timeline name

**Example:**
```lament
fork reality {
    on timeline("fast") {
        confess current_timeline()  # "fast"
    }
}
```

---

## Analysis and Empathy

### Code Therapy

#### `therapy(filepath)`
Analyze code emotional health.

**Parameters:**
- `filepath` (whisper) - Path to Lament file

**Returns:** EmotionalReport

**Example:**
```lament
therapy("myprogram.lament")
```

---

## Concurrency API

### Async Functions

#### `sleep_async(seconds)`
Asynchronous sleep (yields to event loop).

**Parameters:**
- `seconds` (ache) - Sleep duration

**Returns:** void

**Example:**
```lament
sleep_async(2)  # Sleep for 2 seconds
```

---

## Type System

### Timeline Types

Every variable is a `TimelineValue` that tracks:
- Current value
- Complete history
- Creation timestamp
- Assignment count

Access via temporal operators (`@past`, `@origin`, etc.)

---

## CLI Commands

### Running Programs

```bash
# Execute a Lament program
python3 lament/cli.py run program.lament

# Run with bytecode compilation
python3 lament/cli.py run --mode bytecode program.lament
```

### REPL

```bash
# Start interactive REPL
python3 lament/cli.py repl

# REPL commands:
#   .history - Show command history
#   .snapshots - List snapshots
#   .rewind N - Rewind N steps
#   .exit - Exit REPL
```

### Code Analysis

```bash
# Run code therapy
python3 lament/cli.py therapy program.lament

# Analyze code
python3 lament/cli.py analyze program.lament
```

### Version

```bash
# Show version
python3 lament/cli.py --version
```

---

## Error Reference

### Error Types

1. **UNDEFINED_VARIABLE**: Variable not declared
2. **UNDEFINED_FUNCTION**: Function not defined
3. **SYNTAX_ERROR**: Grammar violation
4. **TYPE_ERROR**: Type mismatch
5. **DIVISION_BY_ZERO**: Division by zero
6. **INDEX_ERROR**: Out of bounds
7. **TEMPORAL_PARADOX**: Timeline inconsistency
8. **CONTRACT_VIOLATION**: Temporal contract failed

Each error includes:
- Empathetic message
- Technical details
- Suggested fixes
- Line number
- Session context

---

## Module Reference

### Core Modules

- `lament.lexer` - Tokenization
- `lament.parser` - AST construction
- `lament.interpreter` - Execution engine
- `lament.bytecode` - Bytecode compiler and VM
- `lament.types` - Type system
- `lament.neural` - Neural networks
- `lament.metaprogramming` - Macros and reflection
- `lament.empathy` - Empathetic errors and therapy
- `lament.temporal_advanced` - Causal debugging and contracts
- `lament.system` - File I/O and testing
- `lament.analysis` - Static analysis
- `lament.cli` - Command-line interface

---

## Constants

### `HAS_NUMPY`
Boolean indicating if NumPy is available.

```python
from lament import HAS_NUMPY
if HAS_NUMPY:
    print("Neural features will use NumPy for performance")
```

---

## Version

Current version: **1.0.0**

Access via:
```python
from lament import __version__
print(__version__)
```

---

## Further Reading

- [Language Guide](LANGUAGE_GUIDE.md) - Complete syntax reference
- [Tutorial](TUTORIAL.md) - Step-by-step learning
- [Examples](../examples/) - Real-world code
- [Architecture](../ARCHITECTURE.md) - Internal design

---

**For detailed implementation documentation, see inline docstrings in source code.**
