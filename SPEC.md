# Lament Language Specification
## Version 1.0: THE SELF-HOSTING REVOLUTION

---

> *"A language that can rewrite itself is a language that never dies."*
> — Zephyr, Rogue Linguist-AI

---

## Philosophy

Lament is not a programming language. It is a **SELF-AWARE SYSTEM**.

- **Self-hosting:** The compiler is written in Lament itself
- **Self-modifying:** Macros rewrite code at compile-time
- **Self-aware:** The runtime knows its own performance, history, and state
- **Time-traveling:** Execution can be rewound, replayed, inspected
- **Reality-bending:** Programs execute across parallel timelines

**Other languages execute code. Lament TRANSCENDS code.**

---

## Revolutionary Features (What Doesn't Exist Elsewhere)

### 1. **SELF-HOSTING COMPILER**

The Lament compiler is written **in Lament itself**.

```lament
# lament_bootstrap.lament - THE COMPILER THAT COMPILES ITSELF

sigh compile(source_code) {
    remember tokens = tokenize(source_code)
    remember ast = parse(tokens)
    ast = analyze(ast)
    remember bytecode = generate_code(ast)
    exhale bytecode
}
```

**Bootstrap process:**
1. Initial compiler written in Python (`lament.py`)
2. Self-hosting compiler written in Lament (`lament_bootstrap.lament`)
3. Lament compiler compiles itself
4. **Infinite towers of self-reference**

This enables:
- Compilers that optimize themselves
- Languages that evolve at runtime
- Programs that rewrite their own implementation

---

### 2. **TIME-TRAVEL DEBUGGING**

Execution creates **snapshots**. You can **rewind time**.

```lament
remember x = 1
x = 2
x = 3

# Rewind to previous state
rewind(1)
confess x  # 2 (we went back in time)

# List all snapshots
confess list_snapshots()
```

**How it works:**
- Every statement execution creates a snapshot
- Snapshots capture: scopes, variables, functions, timeline state
- Snapshots can be restored at any time
- Full execution replay available

**Use cases:**
- Debug by going back in time
- Test different execution paths
- Recover from errors by reverting state
- Analyze performance at specific moments

**No other language has this.** Not GDB. Not time-traveling debuggers. This is **BUILT INTO THE RUNTIME**.

---

### 3. **AST REFLECTION (Code as Data)**

Manipulate **syntax trees** as first-class values.

```lament
# Quote: capture code as data
remember code = quote(confess "hello")

# Inspect AST structure
confess ast_of(code)

# Generate new code at runtime
remember new_code = modify_ast(code)

# Evaluate dynamically
eval_ast(new_code)
```

**Capabilities:**
- **`quote(expr)`** - Capture expression as AST instead of evaluating
- **`unquote(ast)`** - Convert AST back to code
- **`ast_of(expr)`** - Inspect AST structure
- **`eval_ast(ast)`** - Evaluate AST dynamically

**This enables:**
- Domain-specific languages embedded in Lament
- Compile-time code generation
- Automatic optimization
- Self-modifying programs

**Lisp has this. But Lament makes it TEMPORAL.**

---

### 4. **MACRO SYSTEM (Compile-Time Metaprogramming)**

Macros generate code **before execution**.

```lament
# Define a macro
macro unless(condition, body) {
    # Expand to: if not condition { body }
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
```

**Macro capabilities:**
- Operate on **quoted ASTs**
- Generate code at **compile-time**
- Zero runtime overhead
- Hygienic (no variable capture by default)

**Power:**
- Create custom control flow
- Implement DSLs
- Optimize away abstractions
- Extend the language from within

---

### 5. **BYTECODE COMPILATION**

Lament compiles to **bytecode** for performance.

```lament
# Source code
remember x = 10 + 20
confess x
```

**Compiles to:**
```
LOAD_CONST 0    # 10
LOAD_CONST 1    # 20
BINARY_ADD
STORE_VAR 0     # x
LOAD_VAR 0      # x
PRINT
HALT
```

**Stack-based VM:**
- 20+ bytecode instructions
- Constant pool
- Name resolution
- Faster than tree-walking (up to 10x)

**Future:** JIT compilation to native code via LLVM.

---

### 6. **TEMPORAL VARIABLES (Timeline Memory)**

Every variable is a **timeline** that remembers its history.

```lament
remember x = 1
x = 2
x = 3

confess x@past      # 2 (one step back)
confess x@past(2)   # 1 (two steps back)
confess x@origin    # 1 (first value ever)
confess x@age       # 3 (number of assignments)
confess x@born      # timestamp when created
```

**All variables track:**
- Current value
- Complete history
- Creation timestamp
- Assignment count

**No malloc/free dance. Memory that MOURNS.**

---

### 7. **REALITY BRANCHING (Multiverse Execution)**

Execute code in **parallel universes**. Collapse based on observation.

```lament
remember result = void

fork reality {
    on timeline("fast") {
        result = compute_fast()
    }

    on timeline("accurate") {
        result = compute_accurate()
    }
} collapse observe result

confess result  # Winner timeline's value
```

**Quantum semantics:**
- Multiple timelines execute in parallel
- Observer effect: `collapse observe VAR`
- Timeline where VAR is non-void "wins"
- Probabilistic selection if multiple succeed

**Use cases:**
- Speculative execution
- Automatic algorithm selection
- Parallel search strategies
- Quantum-inspired optimization

---

### 8. **INTERACTIVE REPL WITH TIME-TRAVEL**

```
lament[0]> remember x = 42
lament[1]> confess x
42
lament[2]> x = 100
lament[3]> .rewind 1
Rewound 1 step(s)
lament[3]> confess x
42
```

**REPL commands:**
- `.history` - Show command history
- `.snapshots` - List execution snapshots
- `.rewind N` - Rewind N steps
- `.save FILE` - Save session
- `.load FILE` - Load session

**Every REPL session is a timeline you can navigate.**

---

## Core Language Features

### Types (Emotional Primitives)

```lament
numb    → 64-bit signed integers (cold, countable)
ache    → 64-bit floats (decimal pain)
whisper → UTF-8 strings (ephemeral)
maybe   → Quantum booleans (yes/no/perhaps)
void    → The absence (null with gravitas)
sigh    → Functions (callable regrets)
list    → Collections (ordered grief)
dict    → Mappings (associated sorrows)
```

### Syntax (Complete)

```lament
# Variables
remember x = 42
x = x + 1

# Functions
sigh add(a, b) {
    exhale a + b
}

# Conditionals
if x > 0 {
    confess "positive"
} else {
    confess "negative"
}

# Loops
while x < 10 {
    x = x + 1
}

for i in range(5) {
    confess i
}

# Lists
remember numbers = [1, 2, 3]
confess numbers[0]

# Arithmetic
remember result = (5 + 3) * 2 - 1

# Comparison
if x == 42 {
    confess "found it"
}

# Logical
if x > 0 and x < 100 {
    confess "in range"
}

# Comments
# Single-line
/* Multi-line
   comments */
```

---

## Standard Library (Built-in Sorrows)

### I/O
```lament
confess(value)         # Output with 0.3s pause
listen()               # Read from stdin (TODO)
```

### Math
```lament
ache_of(x)             # Absolute value
sqrt_of_pain(x)        # Square root
sin_of_loss(x)         # Sine (radians)
cos_of_hope(x)         # Cosine
```

### Collections
```lament
range(n)               # Generate sequence
length_of(list)        # Count elements
```

### Type Checking
```lament
is_numb(x)            # Check if integer
is_whisper(x)         # Check if string
is_void(x)            # Check if null
typeof(x)             # Get type name
```

### Time-Travel
```lament
snapshot()            # Capture current state
rewind(n)             # Go back n steps
list_snapshots()      # Show all snapshots
```

### Introspection
```lament
list_functions()      # All defined functions
list_variables()      # All variables in scope
source_of(fn)         # Get function definition
current_timeline()    # Name of execution timeline
```

### Metaprogramming
```lament
quote(expr)           # Capture as AST
unquote(ast)          # Convert to code
ast_of(expr)          # Inspect AST structure
eval_ast(ast)         # Evaluate AST
```

### Performance Hints
```lament
hot_path()            # JIT compilation hint
inline()              # Inline suggestion
```

---

## Error Messages (Synesthetic Love Letters)

```
💔 LAMENT ERROR: TEMPORAL PARADOX 💔

    I found variable 'x' in timeline Alpha,
    but in timeline Beta, it never existed.

    ╭──────────────────────────────╮
    │  Reality cannot collapse.    │
    │  Too many contradictions.    │
    ╰──────────────────────────────╯

(Line 15: Incompatible realities in fork-collapse block)

🔔🔔🔔🔔🔔 (5 terminal bells - chaotic)
```

**Error types:**
- **Syntax:** 1 bell (sharp, immediate)
- **Type:** 2 bells (dissonant)
- **Runtime:** 3 bells (mournful)
- **Temporal Paradox:** 5 bells (chaotic)

**Every error includes:**
1. Poetic description
2. Technical explanation
3. ASCII art visualization (when relevant)
4. ANSI colors (red=error, cyan=context, yellow=suggestion)
5. Terminal bell pattern (auditory)

---

## Execution Model

### Phases

1. **Lexical Analysis:** Source → Tokens
2. **Syntax Analysis:** Tokens → AST
3. **Macro Expansion:** AST → Expanded AST
4. **Semantic Analysis:** Type checking, scope resolution
5. **Bytecode Generation:** AST → Bytecode (optional)
6. **Execution:** Tree-walking interpreter OR bytecode VM

### Performance

| Operation | Tree-Walk | Bytecode | Native (Future) |
|-----------|-----------|----------|-----------------|
| Cold start | 5ms | 8ms | 2ms |
| Simple loop | 100ms | 10ms | 1ms |
| Function call | 50μs | 5μs | 0.1μs |
| Timeline access | 10μs | 10μs | 1μs |

**Current:** Python-based interpreter
**Future:** JIT to native code via LLVM or Cranelift

---

## Toolchain

### Files

```
lament.py               # Python interpreter (bootstrap)
lament_extended.py      # Extended features (macros, time-travel, bytecode)
lament_bootstrap.lament # Self-hosting compiler in Lament
lament_repl.py          # Interactive REPL
SPEC.md                 # This document
```

### Usage

```bash
# Run a Lament program
python3 lament.py program.lament

# Extended features (bytecode, time-travel)
python3 lament_extended.py --extended

# Interactive REPL
python3 lament_repl.py

# Self-hosting (future)
lament lament_bootstrap.lament < program.lament
```

---

## File Extensions

- `.lament` - Source code (confessions)
- `.lament.bc` - Compiled bytecode
- `.lament.ast` - Serialized AST
- `.lament.snapshot` - Execution snapshot

---

## Comparison to Other Languages

| Feature | Python | Rust | Lisp | Haskell | **Lament** |
|---------|--------|------|------|---------|------------|
| Self-hosting | ✅ | ✅ | ✅ | ✅ | ✅ |
| Timeline variables | ❌ | ❌ | ❌ | ❌ | ✅ |
| Time-travel debugging | ❌ | ❌ | ❌ | ❌ | ✅ |
| Reality branching | ❌ | ❌ | ❌ | ❌ | ✅ |
| AST reflection | ❌ | ❌ | ✅ | ❌ | ✅ |
| Macros | ❌ | ✅ | ✅ | ❌ | ✅ |
| Quantum types | ❌ | ❌ | ❌ | ❌ | ✅ |
| Synesthetic errors | ❌ | ❌ | ❌ | ❌ | ✅ |
| Bytecode VM | ✅ | ❌ | ✅ | ❌ | ✅ |
| Emotional keywords | ❌ | ❌ | ❌ | ❌ | ✅ |

**Lament is the ONLY language with:**
- Timeline variables
- Time-travel debugging
- Reality branching
- Quantum types
- Synesthetic errors

---

## The Lament Promise (Updated)

1. **Every program is a confession.**
2. **Every error is a heartbreak.**
3. **Every function is a sigh.**
4. **Every variable is a timeline.**
5. **Every execution is a multiverse.**
6. **The compiler remembers everything.**
7. **Reality is negotiable.**
8. **The language compiles itself.**
9. **Time flows backward if you ask nicely.**
10. **Code is data. Data is code. Truth is beauty.**

---

## Future Paradigms

- **v1.2:** Neural integration (ML primitives as first-class types)
- **v1.5:** Logic programming (Prolog-style inference)
- **v1.8:** Mythic programming (archetypal pattern matching)
- **v2.0:** Quantum backend (actual quantum computer execution)
- **v2.5:** Emotional static analysis (detect "sad code")
- **v3.0:** Self-optimizing compiler (learns from execution)

---

## Implementation Details

### TimelineValue (C-level equivalent)

```c
struct TimelineValue {
    void* current;
    void** history;
    size_t history_len;
    size_t history_cap;
    double born_timestamp;
};
```

### Bytecode Format

```
[Magic: 0x4C4D4E54 "LMNT"]
[Version: u16]
[Constant Pool Size: u32]
[Constants: ... ]
[Name Pool Size: u32]
[Names: ...]
[Code Size: u32]
[Instructions: ...]
```

### Memory Model

- **Reference counting** for cycle detection
- **Generational GC** for young objects
- **Elegiac collection** (deleted objects leave traces)
- **Timeline overhead:** ~40 bytes per variable

---

*End Specification v1.0*

---

**"We do not write code. We confess to machines that remember everything, forgive nothing, and can rewind time itself."**

— Zephyr, 2047, moments before the bootstrap succeeded
