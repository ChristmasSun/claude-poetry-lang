# Revolutionary Features - Quick Reference

## Security as Type (Taint Tracking)

### Creating Tainted Values
```python
# Untrusted data (from user input)
user_data = untrusted("user input")

# Trusted data (from literals)
safe_data = trusted("safe literal")
```

### Sanitization
```python
# Convert untrusted → trusted
clean_data = sanitize(user_data)
```

### SQL Safety Check
```python
# This will raise SecurityError if query contains untrusted data
check_sql_safety(query)
execute_sql(query)
```

### Taint Propagation Rules
```python
trusted + trusted = trusted
trusted + untrusted = untrusted  # Conservative!
untrusted + anything = untrusted
```

## Persistent Memory

### Declaring Persistent Variables
```python
# Create persistent store
store = PersistentStore(".memory_file.json")

# Set/get values
store.set('counter', 0)
value = store.get('counter')

# Check existence
if store.has('variable'):
    # ...
```

### Transactions
```python
# Begin transaction
store.begin_transaction()

# Make changes
store.set('a', 100)
store.set('b', 200)

# Commit or rollback
store.commit()     # Save changes
# OR
store.rollback()   # Discard changes
```

## Probability Distributions

### Creating Distributions
```python
# Uniform distribution [a, b]
u = uniform(0, 10)

# Normal (Gaussian) distribution
n = normal(mean=100, std=15)

# Bernoulli (coin flip)
b = bernoulli(p=0.5)

# Empirical (from samples)
e = empirical_from_samples([1, 2, 3, 4, 5])
```

### Sampling and Queries
```python
# Draw sample
value = dist.sample()

# Expected value (mean)
mean = dist.expected_value()

# Probability query (Monte Carlo)
p = dist.probability(lambda x: x > 100)
```

### Monte Carlo Simulation (Conceptual)
```python
samples = []
for _ in range(1000):
    result = simulate_something()
    samples.append(result)

dist = empirical_from_samples(samples)
mean = dist.expected_value()
```

## Complete Example

```python
from lament.revolutionary import (
    TaintedValue, TaintLevel, sanitize, check_sql_safety,
    PersistentStore, uniform, normal, bernoulli
)

# 1. SECURITY: Prevent SQL injection
user_input = TaintedValue("admin' OR '1'='1", TaintLevel.UNTRUSTED, source="form")
clean_input = sanitize(user_input)
query = TaintedValue(f"SELECT * FROM users WHERE name = '{clean_input.value}'",
                    TaintLevel.TRUSTED)
check_sql_safety(query)  # ✓ Safe

# 2. PERSISTENCE: Save state
store = PersistentStore()
store.set('visits', 0)
visits = store.get('visits') + 1
store.set('visits', visits)  # Persists!

# 3. PROBABILITY: Risk analysis
login_time = normal(13, 3)  # 1pm ± 3 hours
p_night = login_time.probability(lambda x: x < 6 or x > 22)
print(f"P(suspicious login) = {p_night:.3f}")

# All three features working together!
```

## Common Patterns

### Secure User Input Processing
```python
def process_input(user_data):
    # Mark as untrusted
    tainted = TaintedValue(user_data, TaintLevel.UNTRUSTED, source="user")

    # Sanitize
    clean = sanitize(tainted)

    # Use safely
    query = build_query(clean)
    check_sql_safety(query)
    return execute_sql(query)
```

### Persistent Configuration
```python
def load_config():
    store = PersistentStore(".config.memory")

    if not store.has('theme'):
        store.set('theme', 'dark')
        store.set('language', 'en')

    return {
        'theme': store.get('theme'),
        'language': store.get('language')
    }
```

### Risk Assessment
```python
def assess_risk(failure_rate):
    normal_behavior = bernoulli(0.05)  # 5% normal failures
    expected = normal_behavior.expected_value()

    if failure_rate > expected * 10:
        return "HIGH_RISK"
    return "NORMAL"
```

## Error Handling

### Security Errors
```python
try:
    check_sql_safety(query)
except SecurityError as e:
    print(f"Security violation: {e}")
    # Log, alert, block request
```

### Persistence Errors
```python
try:
    store.begin_transaction()
    # ... operations ...
    store.commit()
except Exception as e:
    store.rollback()
    print(f"Transaction failed: {e}")
```

### Distribution Errors
```python
try:
    dist = bernoulli(1.5)  # Invalid: p must be in [0, 1]
except ValueError as e:
    print(f"Invalid distribution: {e}")
```

## Best Practices

### Security
1. **Always sanitize user input** before use
2. **Never trust external data** - mark as untrusted
3. **Let the type system enforce safety** - don't bypass checks
4. **Sanitize at the boundary** - as early as possible

### Persistence
1. **Use transactions for related updates** - atomicity matters
2. **Commit frequently** - don't hold transactions open
3. **Handle rollback gracefully** - expect failures
4. **Choose meaningful filenames** - `.memory` extension

### Probability
1. **Choose appropriate distributions** - match your domain
2. **Use enough samples** - 10,000+ for Monte Carlo
3. **Validate parameters** - ensure they're valid
4. **Consider performance** - sampling can be expensive

## Testing Patterns

### Test Security
```python
def test_sql_injection_prevention():
    attack = TaintedValue("' OR '1'='1", TaintLevel.UNTRUSTED)
    query = build_query(attack)

    with pytest.raises(SecurityError):
        check_sql_safety(query)
```

### Test Persistence
```python
def test_persistence():
    store = PersistentStore(".test.memory")
    store.set('key', 'value')

    # Simulate restart
    new_store = PersistentStore(".test.memory")
    assert new_store.get('key') == 'value'
```

### Test Distributions
```python
def test_distribution():
    dist = uniform(0, 10)

    # Test sampling
    samples = [dist.sample() for _ in range(100)]
    assert all(0 <= s <= 10 for s in samples)

    # Test expected value
    assert abs(dist.expected_value() - 5.0) < 0.01
```

## Performance Tips

### Security
- Sanitization is O(n) in string length
- Cache sanitized values when possible
- Taint checking is O(1)

### Persistence
- Batch updates in transactions
- Use in-memory caching
- Avoid frequent commits

### Probability
- Reuse distributions (don't recreate)
- Sample in batches
- Consider caching probability queries

## Integration with Lament

These features extend Lament's existing capabilities:

```lament
# Lament syntax (conceptual - requires parser integration)

# Security as Type
remember user_input = untrusted("admin' OR '1'='1")
remember clean = sanitize(user_input)
remember query = "SELECT * FROM users WHERE name = '" + clean + "'"
execute_sql(query)  # Type-safe!

# Persistent Memory
persistent remember counter = 0
counter = counter + 1  # Survives restarts!

# Probability Distributions
remember iq = normal(100, 15)
remember sample = sample(iq)
confess "IQ sample: " + sample
```

---

**Quick, practical reference for revolutionary features.**
**Keep secure, keep state, keep probabilistic! 🎯**
