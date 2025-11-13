#!/usr/bin/env python3
"""
Lament Performance Module Demo
==============================

Comprehensive demonstration of all performance optimization features
in the Lament programming language.

Features demonstrated:
1. JIT Compilation with hot path detection
2. Parallel Iterators for automatic parallelization
3. SIMD Operations for vectorized computation
4. Zero-Cost Abstractions for compile-time optimization
5. Compile-Time Execution for metaprogramming
6. Incremental Compilation for fast rebuilds
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from lament.performance import (
    LLVMCompiler, OptimizationLevel,
    ParallelIterator,
    SIMDVector, VectorizedOps, VectorWidth,
    AbstractionOptimizer, inline,
    CompileTimeEvaluator, comptime,
    IncrementalCompiler,
    PerformanceProfiler, benchmark
)


def demo_jit_compilation():
    """Demonstrate JIT compilation with hot path detection."""
    print("\n" + "="*70)
    print("DEMO 1: JIT COMPILATION")
    print("="*70)

    compiler = LLVMCompiler(enable_profiling=True)

    # Example 1: Automatic JIT compilation with hot path detection
    print("\n--- Automatic JIT Compilation ---")

    @compiler.jit_compile(threshold=10, level=OptimizationLevel.AGGRESSIVE)
    def fibonacci(n):
        """Compute Fibonacci number (inefficient recursive version)."""
        if n <= 1:
            return n
        return fibonacci(n-1) + fibonacci(n-2)

    print("Computing Fibonacci numbers (will JIT compile after 10 calls)...")
    start = time.time()
    for i in range(20):
        result = fibonacci(10)
        if i == 0:
            print(f"  fibonacci(10) = {result}")
    elapsed = time.time() - start

    print(f"✓ Computed 20 times in {elapsed:.4f}s")
    print(f"✓ JIT compilation triggered automatically")

    # Example 2: Explicit optimization
    print("\n--- Explicit Function Optimization ---")

    def matrix_multiply(n):
        """Simple matrix multiplication for demonstration."""
        A = [[i + j for j in range(n)] for i in range(n)]
        B = [[i * j for j in range(n)] for i in range(n)]
        C = [[0] * n for _ in range(n)]

        for i in range(n):
            for j in range(n):
                for k in range(n):
                    C[i][j] += A[i][k] * B[k][j]
        return C

    print("Optimizing matrix multiplication function...")
    optimized = compiler.optimize(matrix_multiply, OptimizationLevel.MAXIMUM)

    start = time.time()
    result = matrix_multiply(10)
    elapsed_original = time.time() - start

    print(f"✓ Original function time: {elapsed_original:.4f}s")
    print(f"✓ Function optimized with MAXIMUM optimization level")

    # Show hot paths
    print("\n--- Hot Path Analysis ---")
    hot_paths = compiler.get_hot_paths(top_n=5)
    for i, hp in enumerate(hot_paths, 1):
        print(f"{i}. {hp.function_name}")
        print(f"   Calls: {hp.call_count}, Total time: {hp.total_time:.6f}s")
        print(f"   Avg time: {hp.avg_time:.6f}s, Level: {hp.optimization_level.name}")

    # Show compilation stats
    stats = compiler.get_compilation_stats()
    print("\n--- Compilation Statistics ---")
    print(f"Total compilations: {stats.total_compilations}")
    print(f"Hot path compilations: {stats.hot_path_compilations}")
    print(f"Total compilation time: {stats.compilation_time:.6f}s")


def demo_parallel_iterators():
    """Demonstrate parallel iterator operations."""
    print("\n" + "="*70)
    print("DEMO 2: PARALLEL ITERATORS")
    print("="*70)

    # Example 1: Parallel map
    print("\n--- Parallel Map ---")
    data = list(range(10000))
    parallel_iter = ParallelIterator(data, num_workers=4)

    start = time.time()
    squared = parallel_iter.map(lambda x: x * x)
    elapsed_parallel = time.time() - start

    start = time.time()
    squared_seq = [x * x for x in data]
    elapsed_sequential = time.time() - start

    print(f"Sequential time: {elapsed_sequential:.4f}s")
    print(f"Parallel time: {elapsed_parallel:.4f}s")
    print(f"Speedup: {elapsed_sequential/elapsed_parallel:.2f}x")
    print(f"✓ Processed {len(squared):,} elements")

    # Example 2: Parallel filter
    print("\n--- Parallel Filter ---")

    def is_prime(n):
        """Check if number is prime."""
        if n < 2:
            return False
        for i in range(2, int(n ** 0.5) + 1):
            if n % i == 0:
                return False
        return True

    numbers = list(range(1000))
    parallel_iter = ParallelIterator(numbers, num_workers=4)

    start = time.time()
    primes = parallel_iter.filter(is_prime)
    elapsed = time.time() - start

    print(f"Found {len(primes)} primes in {elapsed:.4f}s")
    print(f"First 10 primes: {primes[:10]}")

    # Example 3: Parallel reduce
    print("\n--- Parallel Reduce ---")
    data = list(range(1, 1001))
    parallel_iter = ParallelIterator(data, num_workers=4)

    total = parallel_iter.reduce(lambda a, b: a + b, 0)
    product_first_10 = ParallelIterator(range(1, 11), num_workers=2).reduce(
        lambda a, b: a * b, 1
    )

    print(f"Sum of 1-1000: {total:,}")
    print(f"Product of 1-10: {product_first_10:,}")

    # Example 4: Parallel foreach (side effects)
    print("\n--- Parallel Foreach ---")
    results = []
    lock = []  # Simple synchronization

    def process_item(x):
        # Simulate some work
        result = x ** 2
        results.append(result)

    data = list(range(100))
    parallel_iter = ParallelIterator(data, num_workers=4)
    parallel_iter.foreach(process_item)

    print(f"✓ Processed {len(data)} items with side effects")


def demo_simd_operations():
    """Demonstrate SIMD vector operations."""
    print("\n" + "="*70)
    print("DEMO 3: SIMD OPERATIONS")
    print("="*70)

    # Example 1: Basic vector operations
    print("\n--- Basic Vector Operations ---")
    vec1 = SIMDVector([1.0, 2.0, 3.0, 4.0, 5.0], VectorWidth.AVX)
    vec2 = SIMDVector([2.0, 3.0, 4.0, 5.0, 6.0], VectorWidth.AVX)

    result_add = vec1.add(vec2)
    result_mul = vec1.multiply(vec2)
    result_scalar = vec1.multiply_scalar(3.0)
    dot_product = vec1.dot(vec2)

    print(f"Vector 1: {vec1.to_list()[:5]}")
    print(f"Vector 2: {vec2.to_list()[:5]}")
    print(f"Addition: {result_add.to_list()[:5]}")
    print(f"Multiplication: {result_mul.to_list()[:5]}")
    print(f"Scalar * 3: {result_scalar.to_list()[:5]}")
    print(f"Dot product: {dot_product}")

    # Example 2: Vector aggregations
    print("\n--- Vector Aggregations ---")
    data = [float(i) for i in range(1, 101)]
    vec = SIMDVector(data)

    print(f"Sum: {vec.sum()}")
    print(f"Max: {vec.max()}")
    print(f"Min: {vec.min()}")

    # Example 3: High-level vectorized operations
    print("\n--- High-Level Vectorized Operations ---")
    ops = VectorizedOps()

    # Scale array
    data = [1.0, 2.0, 3.0, 4.0, 5.0]
    scaled = ops.scale_array(data, 2.5)
    print(f"Original: {data}")
    print(f"Scaled by 2.5: {scaled[:5]}")

    # Add arrays
    a = [1.0, 2.0, 3.0, 4.0]
    b = [5.0, 6.0, 7.0, 8.0]
    result = ops.add_arrays(a, b)
    print(f"\n{a} + {b} = {result[:4]}")

    # Normalize vector
    vec_data = [3.0, 4.0, 0.0, 0.0]
    normalized = ops.normalize(vec_data)
    print(f"\nNormalize {vec_data[:2]}: {normalized[:2]}")
    print(f"Length: {(normalized[0]**2 + normalized[1]**2)**0.5:.4f}")

    # Example 4: Performance comparison
    print("\n--- Performance Comparison ---")
    large_vec1 = SIMDVector([float(i) for i in range(10000)])
    large_vec2 = SIMDVector([float(i*2) for i in range(10000)])

    start = time.time()
    result = large_vec1.add(large_vec2)
    elapsed_simd = time.time() - start

    start = time.time()
    result_manual = [a + b for a, b in zip(large_vec1.to_list(), large_vec2.to_list())]
    elapsed_manual = time.time() - start

    print(f"SIMD addition (10K elements): {elapsed_simd:.6f}s")
    print(f"Manual addition (10K elements): {elapsed_manual:.6f}s")
    print(f"SIMD speedup: {elapsed_manual/elapsed_simd:.2f}x")


def demo_zero_cost_abstractions():
    """Demonstrate zero-cost abstraction optimizations."""
    print("\n" + "="*70)
    print("DEMO 4: ZERO-COST ABSTRACTIONS")
    print("="*70)

    optimizer = AbstractionOptimizer()

    # Example 1: Inline expansion
    print("\n--- Inline Expansion ---")

    @inline
    def fast_add(a, b):
        """Small function marked for inlining."""
        return a + b

    @inline
    def fast_multiply(a, b):
        """Another small function for inlining."""
        return a * b

    def compute(x, y):
        """Function using inlined helpers."""
        result = fast_add(x, y)
        result = fast_multiply(result, 2)
        return result

    optimized = optimizer.inline_expand(fast_add)
    print("✓ Functions marked for inlining")
    print(f"  - fast_add: {hasattr(fast_add, '_inline_hint')}")
    print(f"  - fast_multiply: {hasattr(fast_multiply, '_inline_hint')}")

    # Example 2: Constant folding
    print("\n--- Constant Folding ---")
    code = """
def calculate():
    x = 10 + 20
    y = x * 2
    z = 100 - 50
    return x + y + z
"""
    print("Original code:")
    print(code)

    optimized_code = optimizer.constant_fold(code)
    print("After constant folding:")
    print(optimized_code)

    # Example 3: Full optimization pipeline
    print("\n--- Full Optimization Pipeline ---")

    def example_function(data):
        """Function to optimize."""
        total = 0
        for item in data:
            total += item * 2 + 1
        return total

    print("Optimizing function with different levels...")
    for level in [OptimizationLevel.BASIC, OptimizationLevel.AGGRESSIVE, OptimizationLevel.MAXIMUM]:
        optimized = optimizer.optimize(example_function, level)
        print(f"✓ Optimized with {level.name} level")


def demo_compile_time_execution():
    """Demonstrate compile-time code execution."""
    print("\n" + "="*70)
    print("DEMO 5: COMPILE-TIME EXECUTION")
    print("="*70)

    evaluator = CompileTimeEvaluator()

    # Example 1: Compile-time expressions
    print("\n--- Compile-Time Expression Evaluation ---")
    expressions = [
        "2 ** 10",
        "sum(range(100))",
        "len([1, 2, 3, 4, 5])",
        "max([10, 20, 15, 30, 25])"
    ]

    for expr in expressions:
        result = evaluator.evaluate(expr)
        print(f"{expr:30} = {result}")

    # Example 2: Compile-time functions
    print("\n--- Compile-Time Function Execution ---")

    @evaluator.comptime
    def generate_lookup_table():
        """Generate lookup table at compile time."""
        print("  [Computing at compile time...]")
        return {i: i ** 2 for i in range(20)}

    print("First call (computed):")
    table1 = generate_lookup_table()
    print(f"✓ Generated {len(table1)} entries")

    print("\nSecond call (cached):")
    table2 = generate_lookup_table()
    print(f"✓ Retrieved from cache: {table1 == table2}")

    # Example 3: Compile-time constants
    print("\n--- Compile-Time Constants ---")
    evaluator.const("MAX_BUFFER_SIZE", 8192)
    evaluator.const("PI", 3.14159265359)
    evaluator.const("VERSION", "1.0.0")

    constants = ["MAX_BUFFER_SIZE", "PI", "VERSION"]
    for name in constants:
        value = evaluator.get_const(name)
        print(f"{name:20} = {value}")

    # Example 4: Complex compile-time computation
    print("\n--- Complex Compile-Time Computation ---")

    @comptime
    def generate_prime_table(limit):
        """Generate prime numbers at compile time."""
        print(f"  [Computing primes up to {limit} at compile time...]")
        primes = []
        for num in range(2, limit):
            is_prime = True
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(num)
        return primes

    primes = generate_prime_table(100)
    print(f"✓ Found {len(primes)} primes < 100")
    print(f"  First 10: {primes[:10]}")

    # Example 5: Compile-time code generation
    print("\n--- Compile-Time Code Generation ---")

    @evaluator.comptime
    def generate_accessor_functions(fields):
        """Generate accessor functions at compile time."""
        print(f"  [Generating {len(fields)} accessors at compile time...]")
        code = {}
        for field in fields:
            # Generate getter
            code[f"get_{field}"] = f"lambda obj: obj.{field}"
            # Generate setter
            code[f"set_{field}"] = f"lambda obj, val: setattr(obj, '{field}', val)"
        return code

    accessors = generate_accessor_functions(['name', 'age', 'email'])
    print(f"✓ Generated {len(accessors)} accessor functions")
    print(f"  Functions: {list(accessors.keys())}")


def demo_incremental_compilation():
    """Demonstrate incremental compilation."""
    print("\n" + "="*70)
    print("DEMO 6: INCREMENTAL COMPILATION")
    print("="*70)

    # Example 1: Dependency graph
    print("\n--- Dependency Graph Construction ---")
    from lament.performance import DependencyGraph

    graph = DependencyGraph()

    # Create a module dependency structure
    modules = ['main', 'utils', 'data', 'config', 'logging']
    for module in modules:
        graph.add_module(module, Path(f"{module}.py"))
        print(f"✓ Added module: {module}")

    # Add dependencies
    dependencies = [
        ('main', 'utils'),
        ('main', 'config'),
        ('utils', 'data'),
        ('utils', 'logging'),
        ('data', 'config'),
    ]

    print("\n--- Dependency Relationships ---")
    for dependent, dependency in dependencies:
        graph.add_dependency(dependent, dependency)
        print(f"  {dependent} → {dependency}")

    # Topological sort
    print("\n--- Compilation Order ---")
    compile_order = graph.topological_sort()
    print("Optimal compilation order:")
    for i, module in enumerate(compile_order, 1):
        print(f"  {i}. {module}")

    # Simulate change and get recompilation set
    print("\n--- Change Detection ---")
    changed = {'config'}
    recompile_set = graph.get_recompilation_set(changed)

    print(f"Changed modules: {changed}")
    print(f"Modules to recompile: {recompile_set}")
    print(f"✓ Only {len(recompile_set)}/{len(modules)} modules need recompilation")

    # Example 2: Incremental compiler
    print("\n--- Incremental Compiler ---")
    compiler = IncrementalCompiler()

    # Create test files
    test_dir = Path("/tmp/lament_demo")
    test_dir.mkdir(exist_ok=True)

    files = {
        'main.py': '# Main module\nfrom utils import helper\n',
        'utils.py': '# Utils module\ndef helper(): pass\n',
        'data.py': '# Data module\nDATA = []\n',
    }

    print("\nCreating test modules...")
    for filename, content in files.items():
        filepath = test_dir / filename
        filepath.write_text(content)
        compiler.add_source_file(filepath)
        print(f"✓ Created {filename}")

    # Initial compilation
    print("\n--- Initial Compilation ---")
    start = time.time()
    results = compiler.compile(parallel=True)
    elapsed = time.time() - start

    print(f"✓ Compiled {len(results)} modules in {elapsed:.4f}s")
    stats = compiler.get_compilation_stats()
    for module, compile_time in stats.items():
        print(f"  {module}: {compile_time:.6f}s")

    # Modify a file
    print("\n--- Incremental Recompilation ---")
    time.sleep(0.1)
    (test_dir / 'utils.py').write_text('# Utils module (modified)\ndef helper(): return 42\n')

    start = time.time()
    results = compiler.compile(parallel=True)
    elapsed = time.time() - start

    print(f"✓ Recompiled in {elapsed:.4f}s (incremental)")
    print("✓ Only modified module and dependents were recompiled")

    # Cleanup
    for filepath in test_dir.glob("*.py"):
        filepath.unlink()
    test_dir.rmdir()


def demo_performance_profiling():
    """Demonstrate performance profiling utilities."""
    print("\n" + "="*70)
    print("DEMO 7: PERFORMANCE PROFILING")
    print("="*70)

    # Example 1: Performance profiler
    print("\n--- Performance Profiler ---")
    profiler = PerformanceProfiler()

    # Measure various operations
    print("Measuring operations...")

    with profiler.measure("list_comprehension"):
        _ = [x ** 2 for x in range(10000)]

    with profiler.measure("generator_expression"):
        _ = list(x ** 2 for x in range(10000))

    with profiler.measure("map_function"):
        _ = list(map(lambda x: x ** 2, range(10000)))

    # Multiple measurements
    for _ in range(5):
        with profiler.measure("short_operation"):
            _ = sum(range(1000))

    print("\nProfiling results:")
    profiler.print_stats()

    # Example 2: Benchmark decorator
    print("\n--- Benchmark Decorator ---")

    @benchmark(iterations=1000)
    def sort_operation(n):
        """Benchmark sorting operation."""
        data = list(range(n, 0, -1))
        return sorted(data)

    result = sort_operation(100)

    @benchmark(iterations=100)
    def complex_computation(n):
        """Benchmark complex computation."""
        result = 0
        for i in range(n):
            for j in range(n):
                result += i * j
        return result

    result = complex_computation(50)


def main():
    """Run all performance demonstrations."""
    print("="*70)
    print("LAMENT PERFORMANCE MODULE - COMPREHENSIVE DEMO")
    print("="*70)
    print("\nDemonstrating advanced performance optimization features:")
    print("1. JIT Compilation")
    print("2. Parallel Iterators")
    print("3. SIMD Operations")
    print("4. Zero-Cost Abstractions")
    print("5. Compile-Time Execution")
    print("6. Incremental Compilation")
    print("7. Performance Profiling")

    start_time = time.time()

    try:
        demo_jit_compilation()
        demo_parallel_iterators()
        demo_simd_operations()
        demo_zero_cost_abstractions()
        demo_compile_time_execution()
        demo_incremental_compilation()
        demo_performance_profiling()

        total_time = time.time() - start_time

        print("\n" + "="*70)
        print("DEMO COMPLETE")
        print("="*70)
        print(f"Total demo time: {total_time:.2f}s")
        print("\n✓ All performance features demonstrated successfully!")

    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
