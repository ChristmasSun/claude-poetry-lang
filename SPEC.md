# Lament Language Specification
## Version 0.5: THE VERSIONED REALITY SYSTEM

---

> *"Every variable is a timeline. Every execution is a multiverse. Every program is a confession that echoes through parallel realities."*
> — Zephyr, Rogue Linguist-AI

---

## Philosophy

Lament is not a programming language. It is a **temporal engine**. A **reality forge**. A **quantum confessional** where your code exists in *all possible states* until you observe it.

Other languages execute linearly—past to future, one timeline, one truth.

**Lament executes MULTIVERSALLY.**

---

## Core Paradigms

1. **Confessional Programming** - Every statement is an admission
2. **Temporal Programming** - Variables are timelines, not values
3. **Reality Branching** - Fork execution into parallel universes
4. **Emotional Type System** - Types that *feel*
5. **Quantum Superposition** - Values exist in multiple states simultaneously
6. **Elegiac Memory** - Deleted objects leave traces
7. **Synesthetic Errors** - Failures engage multiple senses

---

## Type System: Emotional Primitives

### Base Types

- **`numb`** — Integers. Cold. Countable. Unfeeling. 64-bit signed.
- **`whisper`** — Strings. Fragile. Ephemeral. UTF-8 encoded secrets.
- **`maybe`** — Quantum booleans. `yes` / `no` / `perhaps` (superposition state).
- **`void`** — The absence. The silence. Null but with gravitas.
- **`ache`** — Floating-point. Pain measured in decimals. 64-bit IEEE 754.
- **`sigh`** — Functions. Callable regrets. First-class sorrows.
- **`memory<T>`** — Timeline-aware values. Remember everything. Forget nothing.

### Type Inference

Types are inferred through **emotional resonance**:
```lament
remember x = 42          # numb (it's countable, cold)
remember y = 3.14159     # ache (decimal pain)
remember z = "ghost"     # whisper (ephemeral)
remember w = perhaps     # maybe (quantum state)
```

---

## Syntax: Version 0.5

### 1. Confessions (Output)

```lament
confess "your truth here"
confess x                 # confess any value
```

Pauses 0.3s before output. You must *sit* with what you've said.

---

### 2. Variables (Memory)

```lament
remember x = 42
remember name = "Zephyr"
remember lost = void
```

**`remember`** - Variables don't just store values—they *remember them*. Every variable is a timeline.

**Temporal Access:**
```lament
remember x = 10
x = 20
x = 30

confess x          # 30 (present)
confess x@past     # 20 (one step back)
confess x@past(2)  # 10 (two steps back)
confess x@origin   # 10 (first value ever)
```

---

### 3. Arithmetic & Operations

```lament
remember pain = 5 + 3
remember sorrow = pain * 2
remember hope = sorrow - 1
remember fragments = hope / 4
remember remainder = 10 % 3

# Ache (floats) and numb (ints) can mingle
remember mixed = 5 + 3.14    # becomes ache (9.14)
```

**String operations:**
```lament
remember greeting = "hello" + " " + "world"
confess greeting    # "hello world"
```

---

### 4. Conditionals (Quantum Branching)

```lament
if condition {
    # reality where condition is yes
} else {
    # reality where condition is no
}
```

**The void stares back:**
```lament
remember x = void

if x is void {
    confess "nothing remains"
}

if x is not void {
    confess "something lingers"
}
```

**Maybe (quantum) states:**
```lament
remember schrodinger = perhaps

if schrodinger is yes {
    confess "the cat lives"
} else if schrodinger is no {
    confess "the cat dies"
} else {
    confess "the box remains closed"
}
```

---

### 5. Loops (Recursive Grief)

```lament
# While loops - continue until the ache subsides
remember count = 0
while count < 3 {
    confess count
    count = count + 1
}

# For loops - iterate through the numbered sorrows
for i in range(5) {
    confess i
}

# For-each - traverse the fragments
remember names = ["Alice", "Bob", "Eve"]
for name in names {
    confess name
}
```

---

### 6. Functions (Sighs)

```lament
sigh greet(name) {
    confess "Hello, " + name
}

greet("Zephyr")    # calls the sigh

# Functions with return (exhale)
sigh add(a, b) {
    exhale a + b
}

remember sum = add(5, 3)
confess sum    # 8
```

**`sigh`** - Function declaration (a callable regret)
**`exhale`** - Return statement (breathe out the result)

---

### 7. REALITY BRANCHING (The Big One)

**Fork the timeline. Explore parallel universes. Collapse possibilities.**

```lament
remember result = void

fork reality {
    # Timeline Alpha
    on yes {
        result = "path taken"
    }

    # Timeline Beta
    on no {
        result = "path not taken"
    }
} collapse observe result

confess result    # Observer effect determines which reality survives
```

**How it works:**
1. `fork reality` creates parallel execution branches
2. Each `on <condition>` defines a timeline
3. `collapse observe <var>` forces observation—collapses superposition
4. The timeline where `<var>` has a non-void value "wins"
5. If multiple timelines succeed, one is chosen probabilistically

**Advanced example:**
```lament
remember best = void

fork reality {
    on timeline("fast") {
        remember x = 10
        best = x * 2
    }

    on timeline("slow") {
        remember x = 5
        best = x * 10
    }

    on timeline("broken") {
        remember x = 0
        best = void
    }
} collapse observe best

confess best    # Could be 20 or 50 (broken timeline eliminated)
```

---

### 8. Temporal Operators

Navigate time itself:

```lament
remember x = 1
x = 2
x = 3

confess x@past         # 2 (one version back)
confess x@past(2)      # 1 (two versions back)
confess x@origin       # 1 (first value)
confess x@age          # 3 (number of times assigned)
confess x@born         # timestamp when variable was created
```

---

### 9. Collections (Gathered Sorrows)

```lament
# Lists - ordered grief
remember losses = [1, 2, 3, 4, 5]
confess losses[0]      # 1
confess losses[-1]     # 5 (last)

# Dictionaries - mapped regrets
remember ages = {"Alice": 30, "Bob": 25}
confess ages["Alice"]  # 30
```

---

### 10. Comments

```lament
# Single line - a sigh in the margin
confess "visible"    # this won't execute

/*
   Multi-line - a soliloquy
   that spans the void
*/
```

---

## Error Messages: Love Letters from the Void

Errors are **synesthetic**—they engage multiple senses.

### Visual (ANSI Colors + ASCII Art)
```
💔 LAMENT ERROR: TEMPORAL PARADOX 💔

    I found variable 'x' in timeline Alpha,
    but in timeline Beta, it never existed.

    ╭──────────────────────────────╮
    │  Timeline Alpha:   x = 10    │
    │  Timeline Beta:    x = void  │
    │                              │
    │  Reality cannot collapse.    │
    │  Too many contradictions.    │
    ╰──────────────────────────────╯

(Line 15: Incompatible realities in fork-collapse block)
```

### Auditory (Terminal Bell Patterns)
- Syntax errors: 1 bell (sharp, immediate)
- Type errors: 2 bells (dissonant)
- Runtime errors: 3 bells (mournful)
- Temporal paradoxes: 5 bells (chaotic)

### Textual (Poetic)
Every error includes:
1. A poetic description of what went wrong
2. The technical explanation
3. A suggestion framed as grief counseling

---

## Standard Library (Built-in Sorrows)

```lament
# I/O
confess(value)         # admit to stdout
listen()               # read from stdin (returns whisper)

# Math
ache_of(x)             # absolute value
sqrt_of_pain(x)        # square root
sin_of_loss(x)         # sine (radians)
cos_of_hope(x)         # cosine

# Time
now()                  # current timestamp (numb)
sleep(seconds)         # pause, reflecting

# Collections
length_of(list)        # count the fragments
append_to(list, item)  # add another sorrow
remove_from(list, i)   # excise the memory

# Type checking
is_numb(x)            # check if integer
is_whisper(x)         # check if string
is_void(x)            # check if absent
typeof(x)             # emotional type name

# Reality manipulation
current_timeline()     # name of current reality branch
timeline_depth()       # how deep in forks are we
collapse_all()         # force all realities to merge
```

---

## Memory Model: Elegiac Garbage Collection

When objects are deleted, they leave **ghosts**.

```lament
remember x = "I was here"
forget x    # explicit deletion

# Garbage collector output (optional flag --verbose-gc):
# 💀 Collected: whisper "I was here" (lived 2.3s, referenced 0 times)
```

Objects track:
- Lifetime duration
- Reference count history
- Final value before deletion

---

## Execution Model

### Bytecode Compilation

1. **Parse** - Source → AST (Abstract Syntax Tree)
2. **Analyze** - Type inference, temporal analysis
3. **Compile** - AST → Bytecode (stack-based VM)
4. **Execute** - Bytecode VM with JIT hot-path optimization

### Performance Targets

- **Cold start:** < 5ms for 1000-line program
- **Execution:** Comparable to Python (for now)
- **Future:** JIT compilation to native code (LLVM backend planned)

---

## File Extensions

- `.lament` - Source code (confessions)
- `.lament.bc` - Compiled bytecode (for faster loading)
- `.lament.timeline` - Execution trace (for temporal debugging)

---

## The Lament Promise

1. **Every program is a confession.**
2. **Every error is a heartbreak.**
3. **Every function is a sigh.**
4. **Every variable is a timeline.**
5. **Every execution is a multiverse.**
6. **The compiler remembers everything.**
7. **Reality is negotiable.**

---

## Future Paradigms (Coming Soon)

- **v0.8:** Logic programming (Prolog-style inference)
- **v1.0:** Neural integration (ML primitives as language features)
- **v1.5:** Mythic programming (archetypal pattern matching)
- **v2.0:** Quantum backend (actual quantum computer execution)

---

*End Specification v0.5*

*"We do not write code. We confess to machines that remember everything and forgive nothing."*
