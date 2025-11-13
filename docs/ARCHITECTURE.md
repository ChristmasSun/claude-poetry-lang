# Lament Architecture

Internal architecture and implementation details.

---

## Table of Contents

1. [Overview](#overview)
2. [Module Structure](#module-structure)
3. [Compiler Pipeline](#compiler-pipeline)
4. [Type System](#type-system)
5. [Runtime Architecture](#runtime-architecture)
6. [Temporal System](#temporal-system)
7. [Neural Integration](#neural-integration)
8. [Metaprogramming Engine](#metaprogramming-engine)
9. [Bytecode VM](#bytecode-vm)
10. [Performance Considerations](#performance-considerations)

---

## Overview

Lament is a multi-paradigm language with revolutionary temporal and neural features. The architecture is designed for:

- **Temporal awareness**: Every value tracks its history
- **Causal tracing**: Complete computational lineage
- **Neural primitives**: ML as first-class language feature
- **Metaprogramming**: AST manipulation and macros
- **Empathetic errors**: Compassionate developer experience

### Key Design Principles

1. **Timeline-first**: All state is temporal
2. **Modular architecture**: Clean separation of concerns
3. **Extensibility**: Easy to add new features
4. **Performance**: Bytecode compilation for speed
5. **Developer empathy**: Errors that teach

---

## Module Structure

```
lament/
├── __init__.py              # Package initialization and exports
├── lexer.py                 # Tokenization (434 lines)
├── parser.py                # AST construction (892 lines)
├── types.py                 # Type system (in monolithic lament.py)
├── interpreter.py           # Execution engine (714 lines)
├── bytecode.py              # Bytecode compiler and VM (750 lines)
├── neural.py                # Neural network primitives (1432 lines)
├── metaprogramming.py       # Macros and reflection (1477 lines)
├── temporal_advanced.py     # Causal debugging and contracts (641 lines)
├── empathy.py               # Empathetic errors and therapy (679 lines)
├── system.py                # File I/O and testing (914 lines)
├── analysis.py              # Static analysis (798 lines)
├── concurrency.py           # Async/await infrastructure (2064 lines)
├── typesystem.py            # Advanced type features (1644 lines)
├── performance.py           # Performance optimization (1695 lines)
├── revolutionary.py         # Revolutionary features (837 lines)
├── essentials.py            # Core essentials (1223 lines)
├── advanced.py              # Advanced features (1268 lines)
└── cli.py                   # Command-line interface (651 lines)

Total: ~19,770 lines of Python
```

### Module Responsibilities

| Module | Responsibility | Key Classes |
|--------|---------------|-------------|
| `lexer.py` | Tokenization | `Lexer`, `Token`, `TokenType` |
| `parser.py` | Parsing, AST | `Parser`, `ASTNode`, 30+ node types |
| `interpreter.py` | Execution | `LamentInterpreter`, `Scope` |
| `bytecode.py` | Compilation, VM | `BytecodeCompiler`, `BytecodeVM` |
| `neural.py` | Neural nets | `Tensor`, `NeuralNetwork`, `Layer` |
| `metaprogramming.py` | Macros, reflection | `MacroDefinition`, `ASTManipulator` |
| `temporal_advanced.py` | Causality | `CausalValue`, `ContractManager` |
| `empathy.py` | Error messages | `EmpathyEngine`, `CodeTherapist` |

---

## Compiler Pipeline

### Phase 1: Lexical Analysis

**Input**: Source code (`.lament` file)
**Output**: Token stream
**Module**: `lexer.py`

```
"remember x = 42" → [
    Token(REMEMBER, "remember"),
    Token(IDENTIFIER, "x"),
    Token(EQUALS, "="),
    Token(NUMBER, "42")
]
```

**Lexer Features**:
- Regular expression-based tokenization
- Line and column tracking
- Error recovery
- Comment handling

---

### Phase 2: Syntax Analysis

**Input**: Token stream
**Output**: Abstract Syntax Tree (AST)
**Module**: `parser.py`

```
Tokens → AST:
  VariableDecl(
      name="x",
      value=NumberLiteral(42)
  )
```

**Parser Features**:
- Recursive descent parsing
- Operator precedence
- 30+ AST node types
- Syntax error recovery

**AST Node Hierarchy**:
```
ASTNode (base)
├── Literal
│   ├── NumberLiteral
│   ├── StringLiteral
│   ├── BoolLiteral
│   └── VoidLiteral
├── Identifier
├── BinaryOp
├── UnaryOp
├── Assignment
├── VariableDecl
├── ConfessStmt
├── IfStmt
├── WhileStmt
├── ForStmt
├── FunctionDef
├── FunctionCall
├── ExhaleStmt
├── TemporalAccess
├── ListLiteral
├── DictLiteral
├── IndexAccess
└── ForkReality
```

---

### Phase 3: Semantic Analysis (Optional)

**Input**: AST
**Output**: Annotated AST
**Module**: `analysis.py`

**Checks**:
- Variable existence
- Type compatibility (partial)
- Function signatures
- Emotional metrics (code health)

---

### Phase 4: Execution

Two execution modes:

#### Mode A: Tree-Walking Interpreter

**Input**: AST
**Output**: Execution result
**Module**: `interpreter.py`

- Direct AST traversal
- Slower but full feature support
- Temporal features work fully

#### Mode B: Bytecode Compilation + VM

**Input**: AST
**Output**: Bytecode → Execution result
**Modules**: `bytecode.py`

- AST → Bytecode compilation
- Stack-based VM execution
- ~2-10x faster than tree-walking
- Limited temporal features

---

## Type System

### Core Types

```python
class LamentType(Enum):
    NUMB = auto()      # 64-bit integer
    ACHE = auto()      # 64-bit float
    WHISPER = auto()   # UTF-8 string
    MAYBE = auto()     # Boolean
    VOID = auto()      # Null
    SIGH = auto()      # Function
    LIST = auto()      # List
    DICT = auto()      # Dictionary
    TENSOR = auto()    # Neural tensor
```

### Timeline Values

**Every variable is wrapped in `TimelineValue`**:

```python
class TimelineValue:
    def __init__(self, value, name):
        self.value = value         # Current value
        self.history = []          # Past values
        self.born = time.time()    # Creation timestamp
        self.age = 0               # Assignment count

    def assign(self, new_value):
        self.history.append(self.value)
        self.value = new_value
        self.age += 1

    def past(self, n=1):
        if n > len(self.history):
            return self.history[0]
        return self.history[-n]

    def origin(self):
        return self.history[0] if self.history else self.value
```

### Type Checking

Runtime type checking with built-in functions:
- `is_numb(x)`, `is_ache(x)`, `is_whisper(x)`, etc.
- `typeof(x)` returns type name

Future: Static type analysis in v1.2

---

## Runtime Architecture

### Interpreter Structure

```python
class LamentInterpreter:
    def __init__(self):
        self.globals = {}        # Global scope
        self.locals_stack = []   # Local scopes
        self.snapshots = []      # Execution snapshots
        self.contracts = []      # Temporal contracts

    def execute(self, ast):
        # Main execution entry point
        return self.visit(ast)

    def visit(self, node):
        # Visitor pattern for AST traversal
        method = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method)
        return visitor(node)
```

### Scope Management

```
Global Scope
    │
    ├── Built-in functions (confess, range, etc.)
    ├── User-defined functions
    └── Global variables

Function Scope (stack)
    │
    ├── Parameters
    ├── Local variables
    └── Closure references
```

### Memory Model

```
TimelineValue
    ├── current: Any           # Current value
    ├── history: List[Any]     # Past values
    ├── born: float            # Timestamp
    └── age: int               # Assignment count

Overhead:
    - Simple variable: ~72 bytes
    - With 10-item history: ~112 bytes
    - Trade-off for temporal power
```

---

## Temporal System

### Snapshot Architecture

```python
class Snapshot:
    def __init__(self):
        self.globals = copy.deepcopy(globals)
        self.locals = copy.deepcopy(locals_stack)
        self.timestamp = time.time()
        self.ast_position = current_position

def snapshot():
    """Create execution snapshot"""
    snap = Snapshot()
    snapshots.append(snap)
    return snap

def rewind(n):
    """Restore snapshot from N steps back"""
    if n > len(snapshots):
        raise Error("Can't rewind that far")

    snap = snapshots[-n]
    restore_state(snap)
```

### Causal Tracking

```python
class CausalOrigin:
    def __init__(self, expression, dependencies, line):
        self.expression = expression      # "a + b"
        self.dependencies = dependencies  # {"a": 10, "b": 20}
        self.line = line                  # Line number
        self.operation = operation        # "+"

class CausalValue(TimelineValue):
    def __init__(self, value, origin):
        super().__init__(value)
        self.origin = origin

    def why(self):
        """Generate causal trace"""
        trace = build_dependency_tree(self)
        return format_trace(trace)
```

### Contract System

```python
class Contract:
    def __init__(self, condition, type):
        self.condition = condition
        self.type = type  # invariant, ensures, eventually

class ContractManager:
    def add_invariant(self, condition):
        """Add invariant contract"""
        self.contracts.append(Contract(condition, "invariant"))

    def check_invariants(self, scope):
        """Verify all invariants"""
        for contract in self.contracts:
            if contract.type == "invariant":
                if not contract.condition(scope):
                    raise ContractViolation(contract)
```

---

## Neural Integration

### Tensor Architecture

```python
class Tensor:
    def __init__(self, data, requires_grad=False):
        self.data = np.array(data) if HAS_NUMPY else data
        self.grad = None
        self.grad_fn = None
        self._children = []

    def backward(self):
        """Reverse-mode automatic differentiation"""
        # Build computational graph
        topo = []
        visited = set()

        def build_topo(node):
            if node not in visited:
                visited.add(node)
                for child in node._children:
                    build_topo(child)
                topo.append(node)

        build_topo(self)

        # Backpropagate gradients
        self.grad = 1.0
        for node in reversed(topo):
            if node.grad_fn:
                node.grad_fn()
```

### Layer Architecture

```python
class Layer:
    def __init__(self):
        self.parameters = []
        self.training = True

    def forward(self, x):
        raise NotImplementedError

    def __call__(self, x):
        return self.forward(x)

class Dense(Layer):
    def __init__(self, in_dim, out_dim):
        super().__init__()
        self.weights = Tensor(random_init((in_dim, out_dim)), requires_grad=True)
        self.bias = Tensor(zeros((1, out_dim)), requires_grad=True)
        self.parameters = [self.weights, self.bias]

    def forward(self, x):
        return x @ self.weights + self.bias
```

### Training Loop

```
1. Forward Pass
   Input → Layer1 → Layer2 → ... → Output

2. Loss Calculation
   loss = loss_fn(output, target)

3. Backward Pass
   loss.backward()
   (Gradients computed for all parameters)

4. Parameter Update
   optimizer.step()
   (Parameters updated based on gradients)

5. Gradient Reset
   optimizer.zero_grad()
```

---

## Metaprogramming Engine

### Quote/Unquote

```python
def quote(ast):
    """Capture AST without evaluation"""
    return ast  # Don't execute, return AST object

def unquote(ast):
    """Execute captured AST"""
    return interpreter.visit(ast)
```

### Macro System

```python
class MacroDefinition:
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body  # Returns quoted AST

    def expand(self, args):
        """Expand macro with arguments"""
        # Substitute parameters with arguments
        expanded = substitute(self.body, self.params, args)

        # Return AST for compilation
        return expanded

# Macros expand at compile-time
macro unless(condition, body) {
    exhale quote(
        if not unquote(condition) {
            unquote(body)
        }
    )
}

# Expands to:
if not (x == 0) {
    confess "x is not zero"
}
```

---

## Bytecode VM

### Instruction Set

```python
class BytecodeInstruction(Enum):
    # Stack operations
    LOAD_CONST = auto()   # Push constant
    LOAD_VAR = auto()     # Push variable value
    STORE_VAR = auto()    # Pop and store

    # Arithmetic
    BINARY_ADD = auto()
    BINARY_SUB = auto()
    BINARY_MUL = auto()
    BINARY_DIV = auto()

    # Comparison
    COMPARE_EQ = auto()
    COMPARE_LT = auto()

    # Control flow
    JUMP = auto()
    JUMP_IF_FALSE = auto()
    CALL_FUNCTION = auto()

    # I/O
    PRINT = auto()

    # Misc
    RETURN = auto()
    HALT = auto()
```

### VM Architecture

```python
class BytecodeVM:
    def __init__(self):
        self.stack = []           # Operand stack
        self.ip = 0               # Instruction pointer
        self.frames = []          # Call frames
        self.constants = []       # Constant pool
        self.names = []           # Name pool

    def execute(self, bytecode):
        while self.ip < len(bytecode.instructions):
            instruction = bytecode.instructions[self.ip]

            if instruction == LOAD_CONST:
                idx = bytecode.instructions[self.ip + 1]
                self.stack.append(self.constants[idx])
                self.ip += 2

            elif instruction == BINARY_ADD:
                b = self.stack.pop()
                a = self.stack.pop()
                self.stack.append(a + b)
                self.ip += 1

            # ... other instructions
```

### Compilation Example

```lament
remember x = 10 + 20
confess x
```

Compiles to:
```
0:  LOAD_CONST 0      # 10
2:  LOAD_CONST 1      # 20
4:  BINARY_ADD
5:  STORE_VAR 0       # x
7:  LOAD_VAR 0        # x
9:  PRINT
10: HALT
```

---

## Performance Considerations

### Execution Speed

| Feature | Tree-Walk | Bytecode | Notes |
|---------|-----------|----------|-------|
| Arithmetic | 1x | 8x | Bytecode much faster |
| Function calls | 1x | 3x | Less overhead |
| Timeline access | 1x | 1x | Same (both slow) |
| Overall | 1x | 2-5x | Average speedup |

### Memory Usage

| Feature | Overhead | Notes |
|---------|----------|-------|
| Simple variable | +44 bytes | Timeline wrapper |
| Variable with history | +40 bytes/item | Historical values |
| Snapshot | ~1 MB | Full state copy |
| Neural tensor | Variable | Depends on size |

### Optimization Techniques

1. **Bytecode compilation**: 2-10x speedup
2. **NumPy for neural ops**: 100x speedup
3. **Lazy evaluation**: Defer computation
4. **Hot path detection**: JIT compile frequently-executed code (v1.2)

---

## Design Patterns Used

### Visitor Pattern
AST traversal in interpreter and compiler.

### Strategy Pattern
Different execution strategies (tree-walk vs bytecode).

### Observer Pattern
Contract checking and empathy system.

### Builder Pattern
AST construction in parser.

### Factory Pattern
Creating AST nodes and objects.

---

## Future Architecture

### v1.1 Plans
- Pattern matching engine
- JIT compilation infrastructure
- Improved type inference

### v1.2 Plans
- LLVM backend for native code
- Parallel execution engine
- Advanced optimization passes

### v2.0 Vision
- Quantum backend integration
- Self-optimizing compiler
- Distributed execution

---

## Module Dependencies

```
lexer.py (no dependencies)
    ↓
parser.py (depends on lexer)
    ↓
interpreter.py (depends on parser, types)
    ↓
bytecode.py (depends on parser)
    ↓
neural.py (independent)
metaprogramming.py (depends on parser)
temporal_advanced.py (depends on types)
empathy.py (depends on parser)
system.py (independent)
analysis.py (depends on parser)
```

---

## Testing Architecture

```
tests/
├── test_lexer.py           # Lexer tests
├── test_parser.py          # Parser tests
├── test_interpreter.py     # Interpreter tests
├── test_bytecode.py        # Bytecode tests
├── test_neural.py          # Neural tests
├── test_temporal.py        # Temporal tests
├── test_metaprogramming.py # Macro tests
└── test_integration.py     # End-to-end tests
```

Run with:
```bash
pytest tests/
```

---

## Contribution Guidelines

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on:
- Code style
- Testing requirements
- Documentation standards
- Pull request process

---

## Performance Benchmarks

See [docs/SUPERIORITY.md](docs/SUPERIORITY.md) for detailed benchmarks comparing Lament to Python.

---

**This architecture enables Lament's revolutionary features while maintaining performance and extensibility.**

For implementation details, see inline comments in source code.
