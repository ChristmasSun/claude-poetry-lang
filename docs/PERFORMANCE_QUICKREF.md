# Lament Performance Module - Quick Reference

## Import

```python
from lament.performance import (
    LLVMCompiler, OptimizationLevel,
    ParallelIterator,
    SIMDVector, VectorizedOps, VectorWidth,
    AbstractionOptimizer, inline,
    CompileTimeEvaluator, comptime,
    IncrementalCompiler,
    PerformanceProfiler, benchmark
)
```

## 1. JIT Compilation

### Basic Usage
```python
compiler = LLVMCompiler()

@compiler.jit_compile(threshold=100)
def my_function(x):
    return x ** 2
```

### Explicit Optimization
```python
optimized = compiler.optimize(my_function, OptimizationLevel.MAXIMUM)
hot_paths = compiler.get_hot_paths()
stats = compiler.get_compilation_stats()
```

## 2. Parallel Iterators

```python
data = range(1000000)
parallel = ParallelIterator(data, num_workers=4)

# Map
results = parallel.map(lambda x: x * 2)

# Filter
evens = parallel.filter(lambda x: x % 2 == 0)

# Reduce
total = parallel.reduce(lambda a, b: a + b, 0)

# Foreach
parallel.foreach(lambda x: process(x))
```

## 3. SIMD Operations

### Vector Operations
```python
vec1 = SIMDVector([1.0, 2.0, 3.0, 4.0], VectorWidth.AVX)
vec2 = SIMDVector([5.0, 6.0, 7.0, 8.0], VectorWidth.AVX)

result = vec1.add(vec2)
scaled = vec1.multiply_scalar(2.0)
dot = vec1.dot(vec2)
```

### High-Level Operations
```python
ops = VectorizedOps()
scaled = ops.scale_array([1, 2, 3], 2.0)
result = ops.add_arrays([1, 2], [3, 4])
normalized = ops.normalize([3, 4])
```

## 4. Zero-Cost Abstractions

```python
optimizer = AbstractionOptimizer()

@inline
def helper(x):
    return x * 2

optimized_code = optimizer.constant_fold("x = 2 + 3")
optimized_func = optimizer.optimize(func, OptimizationLevel.AGGRESSIVE)
```

## 5. Compile-Time Execution

### Expression Evaluation
```python
evaluator = CompileTimeEvaluator()
result = evaluator.evaluate("2 ** 10")  # 1024
```

### Compile-Time Functions
```python
@evaluator.comptime
def generate_table():
    return [i * i for i in range(100)]

table = generate_table()  # Computed at compile time
```

### Constants
```python
evaluator.const("MAX_SIZE", 1024)
size = evaluator.get_const("MAX_SIZE")
```

### Global Decorator
```python
@comptime
def compute_primes(n):
    # Executed once at compile time
    return [p for p in range(2, n) if is_prime(p)]
```

## 6. Incremental Compilation

```python
compiler = IncrementalCompiler()

# Add files
compiler.add_source_file(Path("main.py"))
compiler.add_source_file(Path("utils.py"))

# Compile
results = compiler.compile(parallel=True)

# Stats
stats = compiler.get_compilation_stats()
```

### Dependency Graph
```python
from lament.performance import DependencyGraph

graph = DependencyGraph()
graph.add_module("main", Path("main.py"))
graph.add_dependency("main", "utils")

compile_order = graph.topological_sort()
recompile_set = graph.get_recompilation_set({"utils"})
```

## 7. Performance Profiling

### Context Manager
```python
profiler = PerformanceProfiler()

with profiler.measure("operation"):
    expensive_operation()

stats = profiler.get_stats("operation")
profiler.print_stats()
```

### Benchmark Decorator
```python
@benchmark(iterations=1000)
def my_function(x):
    return x ** 2

result = my_function(10)  # Benchmarked
```

## Optimization Levels

```python
OptimizationLevel.NONE        # No optimization
OptimizationLevel.BASIC       # Constant folding, dead code elimination
OptimizationLevel.AGGRESSIVE  # Inlining, loop unrolling
OptimizationLevel.MAXIMUM     # All optimizations
```

## Vector Widths

```python
VectorWidth.SSE     # 128-bit (SSE/SSE2)
VectorWidth.AVX     # 256-bit (AVX/AVX2)
VectorWidth.AVX512  # 512-bit (AVX-512)
VectorWidth.AUTO    # Auto-detect
```

## Common Patterns

### Hot Path Optimization
```python
compiler = LLVMCompiler()

@compiler.jit_compile(threshold=50)
def hot_function(x):
    # Automatically compiled after 50 calls
    return compute(x)
```

### Parallel Data Processing
```python
data = load_large_dataset()
parallel = ParallelIterator(data, num_workers=8)
processed = parallel.map(process_item).filter(is_valid)
```

### Compile-Time Code Generation
```python
@comptime
def generate_constants():
    return {f"CONST_{i}": i*100 for i in range(10)}

constants = generate_constants()  # Generated once
```

### Performance Monitoring
```python
profiler = PerformanceProfiler()

with profiler.measure("parsing"):
    parse(code)

with profiler.measure("compilation"):
    compile(ast)

profiler.print_stats()  # Compare operations
```

## Best Practices

1. **JIT Compilation**: Use for hot loops and frequently called functions
2. **Parallel Iterators**: Best for CPU-bound operations on large datasets
3. **SIMD Operations**: Use for numerical computations on arrays
4. **Zero-Cost Abstractions**: Apply to hot paths after profiling
5. **Compile-Time Execution**: Use for expensive computations needed at startup
6. **Incremental Compilation**: Essential for large codebases
7. **Profiling**: Always measure before optimizing

## Performance Tips

- Start with profiling to identify bottlenecks
- Use JIT compilation for frequently executed code
- Parallelize independent operations
- Vectorize numerical computations
- Move constant computations to compile time
- Enable incremental compilation for fast iteration
- Monitor performance with the profiler

## Common Issues

### JIT Compilation
- Threshold too low: Unnecessary compilation overhead
- Threshold too high: Miss optimization opportunities
- **Solution**: Profile first, adjust threshold based on call frequency

### Parallel Iterators
- Small datasets: Overhead exceeds benefit
- **Solution**: Use parallelism only for datasets > 10,000 items

### SIMD Operations
- Non-numeric data: No benefit
- **Solution**: Use SIMD only for float/int arrays

### Compile-Time Execution
- Non-deterministic functions: Unexpected behavior
- **Solution**: Only use for pure functions with constant inputs

## Examples

See comprehensive examples in:
- `/home/user/claude-poetry-lang/demos/demo_performance.py`
- `/home/user/claude-poetry-lang/tests/test_performance.py`

## Documentation

Full documentation in:
- `/home/user/claude-poetry-lang/lament/performance.py` (inline docstrings)
- `/home/user/claude-poetry-lang/PERFORMANCE_SUMMARY.md` (detailed summary)
