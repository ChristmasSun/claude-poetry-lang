# Temporal Advanced Features - Integration Guide

## How to Integrate with the Lament Interpreter

This guide shows how to integrate **Causal Debugging** and **Temporal Contracts** into the existing Lament interpreter.

---

## Current State

The temporal advanced features are implemented as standalone modules that can be used independently. To fully integrate them into the Lament language, follow these steps:

---

## Step 1: Extend TimelineValue with Causality

### In `types.py`:

Replace the current `TimelineValue` class with `CausalValue` for full tracking:

```python
# Option A: Import and use CausalValue
from lament.temporal_advanced import CausalValue as TimelineValue

# Option B: Add causality to existing TimelineValue
from lament.temporal_advanced import CausalOrigin

class TimelineValue:
    # ... existing code ...

    def __init__(self, current):
        # ... existing initialization ...
        self.causal_history = []
        self.name = ""

    def assign(self, value, expression="", line=None, dependencies=None, operation=None):
        """Enhanced assign with causal tracking."""
        # Store causal origin
        origin = CausalOrigin(
            value=self.current,
            expression=expression or str(value),
            line=line,
            dependencies=dependencies or {},
            operation=operation
        )
        self.causal_history.append(origin)

        # Standard timeline assignment
        self.history.append(self.current)
        self.current = value
```

---

## Step 2: Add Built-in Functions

### In `interpreter.py`, update `register_builtins()`:

```python
def register_builtins(self):
    # ... existing built-ins ...

    # Causal debugging
    from lament.temporal_advanced import why
    self.globals['why'] = why

    # Contract management
    from lament.temporal_advanced import ContractManager
    self.contract_manager = ContractManager()
```

---

## Step 3: Hook Contract Checking into Variable Assignments

### In `interpreter.py`, update `set_var()`:

```python
def set_var(self, name, value):
    """Set variable with contract checking."""
    # ... existing variable lookup code ...

    # Update the variable
    if isinstance(scope[name], TimelineValue):
        scope[name].assign(value)
    else:
        scope[name] = value

    # Check invariants after mutation
    if hasattr(self, 'contract_manager'):
        current_scope = self.get_current_scope_dict()
        try:
            self.contract_manager.check_invariants(current_scope, name)
        except ContractViolation as e:
            # Convert to Lament error
            self.error(
                f"Contract violation: {e.contract.condition_str}",
                str(e),
                error_type="CONTRACT VIOLATION",
                bells=5
            )
```

---

## Step 4: Add Contract Syntax to Lexer

### In `lexer.py`, add new keywords:

```python
KEYWORDS = {
    # ... existing keywords ...
    'invariant': TokenType.INVARIANT,
    'ensures': TokenType.ENSURES,
    'eventually': TokenType.EVENTUALLY,
    'why': TokenType.WHY,
}
```

### In `lexer.py`, add new token types:

```python
class TokenType(Enum):
    # ... existing types ...
    INVARIANT = auto()
    ENSURES = auto()
    EVENTUALLY = auto()
    WHY = auto()
```

---

## Step 5: Add Contract Syntax to Parser

### In `parser.py`, add AST nodes:

```python
@dataclass
class InvariantStmt(ASTNode):
    """Represents: invariant <condition>"""
    condition: ASTNode
    condition_str: str

@dataclass
class EnsuresStmt(ASTNode):
    """Represents: ensures <condition>"""
    condition: ASTNode
    condition_str: str

@dataclass
class EventuallyStmt(ASTNode):
    """Represents: eventually(N) <condition>"""
    steps: int
    condition: ASTNode
    condition_str: str
```

### Add parsing methods:

```python
def parse_statement(self):
    """Parse statement with contract support."""
    token = self.peek()

    # ... existing statement types ...

    if token.type == TokenType.INVARIANT:
        return self.parse_invariant()
    elif token.type == TokenType.ENSURES:
        return self.parse_ensures()
    elif token.type == TokenType.EVENTUALLY:
        return self.parse_eventually()

def parse_invariant(self):
    """Parse: invariant <condition>"""
    self.expect(TokenType.INVARIANT)
    start_pos = self.pos
    condition = self.parse_expression()

    # Extract condition string for error messages
    condition_str = self.extract_expression_string(start_pos, self.pos)

    return InvariantStmt(condition, condition_str)

def parse_ensures(self):
    """Parse: ensures <condition>"""
    self.expect(TokenType.ENSURES)
    start_pos = self.pos
    condition = self.parse_expression()
    condition_str = self.extract_expression_string(start_pos, self.pos)

    return EnsuresStmt(condition, condition_str)

def parse_eventually(self):
    """Parse: eventually(N) <condition>"""
    self.expect(TokenType.EVENTUALLY)
    self.expect(TokenType.LPAREN)
    steps_expr = self.parse_expression()
    if not isinstance(steps_expr, NumberLiteral):
        self.error("Eventually step count must be a number")
    steps = int(steps_expr.value)
    self.expect(TokenType.RPAREN)

    start_pos = self.pos
    condition = self.parse_expression()
    condition_str = self.extract_expression_string(start_pos, self.pos)

    return EventuallyStmt(steps, condition, condition_str)
```

---

## Step 6: Execute Contracts in Interpreter

### In `interpreter.py`, update `execute_statement()`:

```python
def execute_statement(self, stmt):
    """Execute statement with contract support."""
    # ... existing statement types ...

    if isinstance(stmt, InvariantStmt):
        self.execute_invariant(stmt)
    elif isinstance(stmt, EnsuresStmt):
        self.execute_ensures(stmt)
    elif isinstance(stmt, EventuallyStmt):
        self.execute_eventually(stmt)

def execute_invariant(self, stmt):
    """Register an invariant contract."""
    # Convert AST condition to callable
    condition = lambda scope: self.evaluate_with_scope(stmt.condition, scope)
    self.contract_manager.add_invariant(condition, stmt.condition_str)

def execute_ensures(self, stmt):
    """Register an ensures contract for current function."""
    condition = lambda scope: self.evaluate_with_scope(stmt.condition, scope)
    self.contract_manager.add_ensures(condition, stmt.condition_str)

def execute_eventually(self, stmt):
    """Register an eventually contract."""
    condition = lambda scope: self.evaluate_with_scope(stmt.condition, scope)
    self.contract_manager.add_eventually(stmt.steps, condition, stmt.condition_str)

def evaluate_with_scope(self, expr, scope):
    """Evaluate expression with custom scope."""
    # Temporarily use provided scope
    old_scopes = self.scopes
    self.scopes = [scope]
    try:
        result = self.evaluate(expr)
        return result
    finally:
        self.scopes = old_scopes
```

---

## Step 7: Track Causality in Operations

### In `interpreter.py`, update `evaluate_binary_op()`:

```python
def evaluate_binary_op(self, expr):
    """Evaluate binary operation with causal tracking."""
    left = self.evaluate(expr.left)
    right = self.evaluate(expr.right)
    op = expr.op

    # ... perform operation ...
    result = left + right  # or whatever operation

    # Track causality if we're in causal mode
    if self.track_causality:
        from lament.temporal_advanced import track_operation

        dependencies = {}
        if isinstance(expr.left, Identifier):
            dependencies[expr.left.name] = left
        if isinstance(expr.right, Identifier):
            dependencies[expr.right.name] = right

        # Note: In full integration, you'd wrap result in CausalValue
        # and return that instead

    return result
```

---

## Step 8: Check Contracts at Function Boundaries

### In `interpreter.py`, update `evaluate_function_call()`:

```python
def evaluate_function_call(self, expr):
    """Evaluate function call with contract checking."""
    # ... existing function call code ...

    try:
        self.execute(func_def.body)
        result = None
    except ReturnValue as rv:
        result = rv.value
    finally:
        # Check ensures contracts before returning
        if hasattr(self, 'contract_manager'):
            scope_dict = self.scopes[-1]
            scope_dict['result'] = result  # Add return value to scope
            try:
                self.contract_manager.check_ensures(scope_dict, expr.name)
            except ContractViolation as e:
                self.error(
                    f"Post-condition violated in {expr.name}",
                    str(e),
                    error_type="CONTRACT VIOLATION",
                    bells=5
                )

        self.scopes.pop()

    return result
```

---

## Step 9: Advance Time Steps

### In `interpreter.py`, update `execute()`:

```python
def execute(self, statements):
    """Execute statements with temporal tracking."""
    for stmt in statements:
        self.execute_statement(stmt)

        # Advance time step for eventually contracts
        if hasattr(self, 'contract_manager'):
            current_scope = self.get_current_scope_dict()
            self.contract_manager.step(current_scope)

def get_current_scope_dict(self):
    """Get current scope as a dict for contract checking."""
    scope = {}

    # Merge all scopes
    for s in self.scopes:
        for name, val in s.items():
            if isinstance(val, TimelineValue):
                scope[name] = val.current
            else:
                scope[name] = val

    # Add globals
    for name, val in self.globals.items():
        if not callable(val):
            if isinstance(val, TimelineValue):
                scope[name] = val.current
            else:
                scope[name] = val

    return scope
```

---

## Example: Fully Integrated Lament Code

With these integrations, you could write:

```lament
# Declare variables with causal tracking
remember balance = 1000
remember transactions = 0

# Add invariant contract
invariant balance >= 0

# Function with ensures contract
sigh withdraw(amount) {
    ensures balance == balance@past - amount

    balance = balance - amount
    transactions = transactions + 1

    exhale balance
}

# Use the function
withdraw(200)
confess balance  # 800

# Query causality
confess why(balance)
# Output:
#   🔍 CAUSAL TRACE: balance
#   Current value: 800
#   Last assigned: balance - amount
#   Location: line 12
#   Dependencies:
#     • balance@past = 1000
#     • amount = 200

# This would trigger invariant violation:
# withdraw(900)  # Balance would be -100, violates "balance >= 0"
```

---

## Complete Integration Checklist

- [ ] Replace `TimelineValue` with `CausalValue` or add causality
- [ ] Add `why()` to built-in functions
- [ ] Initialize `ContractManager` in interpreter
- [ ] Add contract keywords to lexer (invariant, ensures, eventually)
- [ ] Add contract AST nodes to parser
- [ ] Implement contract parsing methods
- [ ] Hook invariant checking into `set_var()`
- [ ] Hook ensures checking into function returns
- [ ] Hook eventually checking into execution steps
- [ ] Track causality in all operations
- [ ] Add contract violation error handling
- [ ] Test with example programs

---

## Backward Compatibility

To maintain backward compatibility:

1. **Make contracts optional**: Only check contracts if they're registered
2. **Make causality opt-in**: Add a flag `--track-causality` to enable it
3. **Gradual migration**: Keep old `TimelineValue` and add `CausalValue` as opt-in

```python
# In interpreter:
def __init__(self, track_causality=False, enable_contracts=False):
    self.track_causality = track_causality
    self.enable_contracts = enable_contracts

    if enable_contracts:
        self.contract_manager = ContractManager()
```

---

## Performance Considerations

### Causality Tracking
- **Memory**: O(n) where n = number of assignments (stores full history)
- **Time**: O(1) per assignment (just appends to list)
- **Recommendation**: Enable only during debugging

### Contracts
- **Memory**: O(c) where c = number of contracts
- **Time**: O(c) per check (evaluates each contract's predicate)
- **Recommendation**: Keep contracts active, they're lightweight

---

## Future Enhancements

1. **Selective Causality**: Track only specific variables
2. **Contract Inference**: Automatically infer likely contracts
3. **Visual Causal Graphs**: Generate graphviz diagrams of causality
4. **Contract DSL**: More expressive contract language
5. **Temporal Queries**: SQL-like queries over program history

---

## Questions?

See `TEMPORAL_ADVANCED_README.md` for detailed API documentation.

Run demos:
- `python -m lament.temporal_advanced` - Built-in demo
- `python lament/temporal_advanced_demo.py` - Interactive demo

---

*"Time itself becomes your debugging tool."*
