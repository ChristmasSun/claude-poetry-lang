# Lament Temporal Advanced Features

## Two Revolutionary Features That Make Time Your Debugging Tool

This module introduces two groundbreaking capabilities to the Lament programming language:

1. **CAUSAL DEBUGGING** - Trace the WHY of every computation
2. **TEMPORAL CONTRACTS** - Enforce invariants across time

---

## 🔍 Feature 1: Causal Debugging

### What Is It?

Traditional debugging shows you *what* a variable's value is. Causal debugging shows you **WHY** it has that value - the complete computational lineage from initial value through every transformation.

### Key Concepts

- **CausalValue**: An enhanced timeline variable that tracks not just history, but the *reason* for each change
- **CausalOrigin**: Records for each assignment:
  - The expression that created the value
  - Line number in source code
  - Dependencies (which variables contributed)
  - Operation performed
- **why()**: The main query function - ask WHY any variable is what it is

### Example Usage

```python
from lament.temporal_advanced import create_causal_variable, why

# Create variables with causal tracking
price = create_causal_variable("price", 100, "price = 100", line=1)
quantity = create_causal_variable("quantity", 5, "quantity = 5", line=2)

# Perform computation
subtotal_value = price.current * quantity.current
subtotal = create_causal_variable("subtotal", subtotal_value,
                                 "subtotal = price * quantity", line=3)

# Track the causality
subtotal.causal_history.append(CausalOrigin(
    value=subtotal_value,
    expression="price * quantity",
    line=3,
    dependencies={"price": price, "quantity": quantity},
    operation="*"
))

# Ask WHY
print(why(subtotal))
```

### Output

```
╔══════════════════════════════════════════════════════════╗
║  🔍 CAUSAL TRACE: subtotal                               ║
╚══════════════════════════════════════════════════════════╝

Current value: 500
Last assigned: price * quantity
Location: line 3
Operation: *
Dependencies:
  • price = 100
  • quantity = 5

Historical assignments (1 total):
  1. price * quantity → 500
```

### Benefits

- **Deep Understanding**: See the complete chain of reasoning
- **Bug Hunting**: Trace errors back to their source
- **Learning**: Understand how complex computations evolve
- **Debugging Recursion**: Track dependencies through multiple levels

---

## 📜 Feature 2: Temporal Contracts

### What Is It?

Temporal contracts are promises about your program's behavior across time. They automatically verify conditions and produce beautiful, informative error messages when violated.

### Three Types of Contracts

#### 1. Invariant

**What**: A condition that must ALWAYS be true
**When Checked**: On every variable mutation
**Use Case**: Fundamental truths that should never break

```python
from lament.temporal_advanced import ContractManager

manager = ContractManager()

# Balance must never be negative
manager.add_invariant(
    lambda s: s.get('balance', 0) >= 0,
    "balance >= 0",
    "non-negative balance"
)

scope = {'balance': 100}
manager.check_invariants(scope)  # ✓ OK

scope['balance'] = -50
manager.check_invariants(scope)  # ✗ Violation!
```

**Violation Output**:
```
═══════════════════════════════════════════════════════════
║  💔 TEMPORAL CONTRACT VIOLATED 💔                      ║
═══════════════════════════════════════════════════════════

Contract Type: Invariant
Condition: balance >= 0

The universe promised this would always be true,
but time has betrayed us. The invariant shattered.

Context:
  violated_by: balance
  scope: {'balance': -50}
```

#### 2. Ensures (Post-conditions)

**What**: A condition that must be true after a function returns
**When Checked**: When function exits
**Use Case**: Verify function correctness

```python
manager.add_ensures(
    lambda s: s.get('result', 0) > 0,
    "result > 0",
    "positive result"
)

# After function execution
scope = {'a': 10, 'b': 20, 'result': 30}
manager.check_ensures(scope, 'my_function')  # ✓ OK
```

**Violation Output**:
```
Contract Type: Ensures
Condition: result > 0

The function promised to ensure this condition,
but it returned without keeping its word.
```

#### 3. Eventually

**What**: A condition that must become true within N steps
**When Checked**: Each execution step
**Use Case**: Convergence, timeouts, eventual consistency

```python
manager.add_eventually(
    10,  # Must become true within 10 steps
    lambda s: s.get('temperature', 0) <= 20,
    "temperature <= 20",
    "cooling system reaches target"
)

scope = {'temperature': 100}
for step in range(15):
    scope['temperature'] -= 10
    manager.step(scope)  # Will violate if not met in 10 steps
```

**Violation Output**:
```
Contract Type: Eventually
Condition: temperature <= 20

We waited for 10 steps,
but the future never arrived. Time ran out.

Recent History:
  1. Step 1: False
  2. Step 2: False
  ...
  10. Step 10: False
```

---

## 🚀 The Power Combo: Causality + Contracts

The true power emerges when you combine both features:

```python
from lament.temporal_advanced import (
    create_causal_variable, why, ContractManager
)

# Track causality
velocity = create_causal_variable("velocity", 0, "velocity = 0")

# Enforce contract
manager = ContractManager()
manager.add_invariant(
    lambda s: s.get('velocity', 0) <= 100,
    "velocity <= 100",
    "speed limit"
)

# Simulate acceleration
for i in range(10):
    old_v = velocity.current
    velocity.assign_with_cause(
        old_v + 15,
        f"velocity += 15 [iteration {i}]",
        line=100 + i,
        dependencies={"velocity@past": old_v, "acceleration": 15},
        operation="+"
    )

    try:
        manager.check_invariants({'velocity': velocity.current}, 'velocity')
    except ContractViolation as e:
        print(e)
        print("\nCausal trace:")
        print(why(velocity))
        break
```

**Result**: When the contract is violated, you get:
1. **WHAT** went wrong (contract violation)
2. **WHY** it happened (causal trace)
3. **WHEN** it occurred (step history)
4. **HOW** to fix it (complete context)

---

## 📦 API Reference

### Causal Debugging

#### `create_causal_variable(name, initial_value, expression="", line=None)`
Create a new variable with causal tracking.

#### `CausalValue.assign_with_cause(value, expression="", line=None, dependencies=None, operation=None)`
Assign a new value with full causal metadata.

#### `why(variable)`
Generate a causal explanation for any variable's current value.

#### `CausalValue.get_causal_chain()`
Get the complete list of CausalOrigin objects.

### Temporal Contracts

#### `ContractManager()`
Central manager for all contracts.

#### `manager.add_invariant(condition, condition_str, name="")`
Register an invariant that must always be true.

#### `manager.add_ensures(condition, condition_str, name="")`
Register a post-condition for functions.

#### `manager.add_eventually(steps, condition, condition_str, name="")`
Register a condition that must become true within N steps.

#### `manager.check_invariants(scope, changed_var=None)`
Check all active invariants.

#### `manager.check_ensures(scope, function_name=None)`
Check all active ensures contracts.

#### `manager.step(scope)`
Advance one execution step and check eventually contracts.

---

## 🎯 Running the Demos

### Built-in Demo (Non-interactive)

```bash
python -m lament.temporal_advanced
```

### Comprehensive Interactive Demo

```bash
python lament/temporal_advanced_demo.py
```

The interactive demo includes:
1. Basic causal debugging
2. Complex multi-variable causal chains
3. Fibonacci with causal tracking
4. Invariant contracts (success and violation)
5. Eventually contracts (success and timeout)
6. Ensures contracts (post-conditions)
7. Combined features (causality + contracts)

---

## 🎨 Design Philosophy

### Synesthetic Error Messages

All contract violations produce **synesthetic** error messages that engage multiple senses:

- **Visual**: ANSI colors, borders, formatting
- **Linguistic**: Poetic descriptions that make errors memorable
- **Structural**: Clear hierarchy showing what, why, when, where

### Time as a First-Class Concept

In Lament, time isn't just a dimension - it's a tool:
- Variables remember their past
- Contracts enforce promises across time
- Causality links present to past
- Eventually contracts reach into the future

### Beautiful Failures

When things go wrong, you should *feel* it - but also understand it completely. Error messages are:
- **Poetic**: "The universe promised this would always be true, but time has betrayed us"
- **Informative**: Complete context, history, and dependencies
- **Actionable**: Clear indication of what violated and where

---

## 🔮 Future Integration

These features are designed to integrate with the Lament interpreter:

1. **Lexer/Parser**: Add syntax for `why()`, `invariant`, `ensures`, `eventually`
2. **Interpreter**: Hook contract checking into variable assignments
3. **Built-ins**: Register `why()` as a built-in function
4. **Timeline Variables**: Replace `TimelineValue` with `CausalValue` for full tracking

### Proposed Syntax

```lament
# Causal debugging
remember x = 10
x = x + 5
confess why(x)  # Shows causal chain

# Contracts
remember balance = 1000
invariant balance >= 0  # Always enforced

sigh transfer(amount) {
    ensures balance@past - amount == balance
    balance = balance - amount
    exhale balance
}

# Eventually
remember converged = no
eventually(10) converged == yes  # Must happen in 10 steps
```

---

## 📊 Performance Considerations

- **Causal Tracking**: Adds memory overhead (stores full history)
- **Contracts**: Minimal runtime overhead (simple predicate evaluation)
- **Eventually**: Linear space in number of steps tracked

**Recommendation**: Use causal tracking during development/debugging, disable in production if needed.

---

## 🌟 Why This Matters

Traditional debugging tools show you **snapshots** - the state of your program at specific moments. These features give you **movies** - the complete evolution of your program through time.

When combined with Lament's existing temporal operators (`@past`, `@origin`, `@age`, `@born`), you get unprecedented insight into program behavior.

**Time itself becomes your debugging tool.**

---

## 📝 Examples Gallery

See `examples/temporal_advanced_example.lament` for conceptual syntax examples showing how these features could be used in actual Lament code.

---

## 🙏 Credits

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)

*"In the void of time, we find not just the past, but the reasons why."*

---

## 📄 License

Part of the Lament programming language project.
