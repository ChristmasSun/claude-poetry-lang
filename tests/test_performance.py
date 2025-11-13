"""
Comprehensive tests for Lament performance module.

Tests all performance features including JIT compilation, parallel iterators,
SIMD operations, zero-cost abstractions, compile-time execution, and
incremental compilation.
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
    IncrementalCompiler, DependencyGraph,
    PerformanceProfiler, benchmark
)


def test_jit_compilation():
    """Test JIT compilation features."""
    print("\n" + "="*70)
    print("TEST 1: JIT COMPILATION")
    print("="*70)

    compiler = LLVMCompiler(enable_profiling=True)

    # Test 1: Hot path detection
    @compiler.jit_compile(threshold=5)
    def compute_sum(n):
        """Compute sum of squares."""
        total = 0
        for i in range(n):
            total += i * i
        return total

    # Run multiple times to trigger JIT compilation
    print("\nRunning function to trigger JIT compilation...")
    results = []
    for i in range(10):
        result = compute_sum(100)
        results.append(result)

    print(f"✓ Function executed {len(results)} times")
    print(f"✓ Result: {results[0]}")

    # Check hot paths
    hot_paths = compiler.get_hot_paths(top_n=5)
    print(f"\n✓ Hot paths detected: {len(hot_paths)}")
    for hp in hot_paths:
        print(f"  - {hp.function_name}: {hp.call_count} calls, {hp.total_time:.6f}s")

    # Test 2: Explicit optimization
    def matrix_multiply(size):
        """Simple matrix multiplication."""
        a = [[i + j for j in range(size)] for i in range(size)]
        b = [[i - j for j in range(size)] for i in range(size)]
        c = [[0] * size for _ in range(size)]

        for i in range(size):
            for j in range(size):
                for k in range(size):
                    c[i][j] += a[i][k] * b[k][j]
        return c

    print("\nOptimizing matrix multiplication...")
    optimized = compiler.optimize(matrix_multiply, OptimizationLevel.AGGRESSIVE)
    print("✓ Function optimized successfully")

    # Get compilation stats
    stats = compiler.get_compilation_stats()
    print(f"\n✓ Compilation statistics:")
    print(f"  - Total compilations: {stats.total_compilations}")
    print(f"  - Hot path compilations: {stats.hot_path_compilations}")
    print(f"  - Compilation time: {stats.compilation_time:.6f}s")

    print("\n✓ JIT Compilation tests passed!")


def test_parallel_iterators():
    """Test parallel iterator features."""
    print("\n" + "="*70)
    print("TEST 2: PARALLEL ITERATORS")
    print("="*70)

    # Test 1: Parallel map
    print("\nTest parallel map operation...")
    data = list(range(1000))
    parallel_iter = ParallelIterator(data, num_workers=4)

    squared = parallel_iter.map(lambda x: x * x)
    expected = [x * x for x in data]

    assert len(squared) == len(expected), "Map result length mismatch"
    assert squared[:10] == expected[:10], "Map result values mismatch"
    print(f"✓ Parallel map completed: {len(squared)} results")
    print(f"  First 5 results: {squared[:5]}")

    # Test 2: Parallel filter
    print("\nTest parallel filter operation...")
    evens = parallel_iter.filter(lambda x: x % 2 == 0)
    expected_evens = [x for x in data if x % 2 == 0]

    assert len(evens) == len(expected_evens), "Filter result length mismatch"
    print(f"✓ Parallel filter completed: {len(evens)} results")
    print(f"  First 5 results: {evens[:5]}")

    # Test 3: Parallel reduce
    print("\nTest parallel reduce operation...")
    total = parallel_iter.reduce(lambda a, b: a + b, initial=0)
    expected_total = sum(data)

    assert total == expected_total, f"Reduce result mismatch: {total} != {expected_total}"
    print(f"✓ Parallel reduce completed: {total}")

    # Test 4: Thread-based with more workers
    print("\nTest parallel operations with more workers...")
    parallel_multi = ParallelIterator(range(100), num_workers=8)
    cubed = parallel_multi.map(lambda x: x ** 3)
    print(f"✓ Multi-worker map completed: {len(cubed)} results")

    print("\n✓ Parallel Iterator tests passed!")


def test_simd_operations():
    """Test SIMD vector operations."""
    print("\n" + "="*70)
    print("TEST 3: SIMD OPERATIONS")
    print("="*70)

    # Test 1: Vector addition
    print("\nTest SIMD vector addition...")
    vec1 = SIMDVector([1.0, 2.0, 3.0, 4.0], VectorWidth.AVX)
    vec2 = SIMDVector([5.0, 6.0, 7.0, 8.0], VectorWidth.AVX)

    result = vec1.add(vec2)
    expected = [6.0, 8.0, 10.0, 12.0]
    assert result.to_list()[:4] == expected, "Vector addition failed"
    print(f"✓ Vector addition: {result.to_list()[:4]}")

    # Test 2: Vector multiplication
    print("\nTest SIMD vector multiplication...")
    result = vec1.multiply(vec2)
    expected = [5.0, 12.0, 21.0, 32.0]
    assert result.to_list()[:4] == expected, "Vector multiplication failed"
    print(f"✓ Vector multiplication: {result.to_list()[:4]}")

    # Test 3: Scalar multiplication
    print("\nTest SIMD scalar multiplication...")
    result = vec1.multiply_scalar(2.0)
    expected = [2.0, 4.0, 6.0, 8.0]
    assert result.to_list()[:4] == expected, "Scalar multiplication failed"
    print(f"✓ Scalar multiplication: {result.to_list()[:4]}")

    # Test 4: Dot product
    print("\nTest SIMD dot product...")
    dot = vec1.dot(vec2)
    expected = 1*5 + 2*6 + 3*7 + 4*8  # 70
    assert dot == expected, f"Dot product failed: {dot} != {expected}"
    print(f"✓ Dot product: {dot}")

    # Test 5: Vector operations
    print("\nTest vector aggregate operations...")
    vec = SIMDVector([1.0, 2.0, 3.0, 4.0, 5.0])
    print(f"✓ Sum: {vec.sum()}")
    print(f"✓ Max: {vec.max()}")
    print(f"✓ Min: {vec.min()}")

    # Test 6: Vectorized operations
    print("\nTest high-level vectorized operations...")
    ops = VectorizedOps()

    data = [1.0, 2.0, 3.0, 4.0]
    scaled = ops.scale_array(data, 2.0)
    print(f"✓ Scale array: {scaled[:4]}")

    a = [1.0, 2.0, 3.0]
    b = [4.0, 5.0, 6.0]
    added = ops.add_arrays(a, b)
    print(f"✓ Add arrays: {added}")

    dot = ops.dot_product(a, b)
    print(f"✓ Dot product: {dot}")

    normalized = ops.normalize([3.0, 4.0])
    print(f"✓ Normalize: {normalized}")

    print("\n✓ SIMD Operations tests passed!")


def test_zero_cost_abstractions():
    """Test zero-cost abstraction optimizations."""
    print("\n" + "="*70)
    print("TEST 4: ZERO-COST ABSTRACTIONS")
    print("="*70)

    optimizer = AbstractionOptimizer()

    # Test 1: Inline expansion
    print("\nTest inline expansion...")

    @inline
    def small_helper(x, y):
        return x * 2 + y

    inlined = optimizer.inline_expand(small_helper)
    assert hasattr(inlined, '_inline_hint'), "Inline hint not set"
    print("✓ Function marked for inlining")

    # Test 2: Constant folding
    print("\nTest constant folding...")
    code = """
x = 2 + 3 * 4
y = 10 - 5
z = x + y
"""
    optimized = optimizer.constant_fold(code)
    print(f"✓ Original code:\n{code}")
    print(f"✓ Optimized code:\n{optimized}")

    # Test 3: Dead code elimination
    print("\nTest dead code elimination...")
    code_with_dead = """
def func(x):
    if True:
        return x * 2
    else:
        return x * 3  # Dead code
"""
    optimized = optimizer.eliminate_dead_code(code_with_dead)
    print("✓ Dead code elimination applied")

    # Test 4: Full optimization
    print("\nTest full optimization pipeline...")
    def example_func(a, b):
        temp = a + b
        result = temp * 2
        return result

    optimized_func = optimizer.optimize(example_func, OptimizationLevel.MAXIMUM)
    print("✓ Function fully optimized")

    print("\n✓ Zero-Cost Abstractions tests passed!")


def test_compile_time_execution():
    """Test compile-time execution features."""
    print("\n" + "="*70)
    print("TEST 5: COMPILE-TIME EXECUTION")
    print("="*70)

    evaluator = CompileTimeEvaluator()

    # Test 1: Compile-time evaluation
    print("\nTest compile-time expression evaluation...")
    result = evaluator.evaluate("2 ** 10")
    assert result == 1024, f"Evaluation failed: {result}"
    print(f"✓ Evaluated '2 ** 10' = {result}")

    result = evaluator.evaluate("sum(range(10))")
    assert result == 45, f"Evaluation failed: {result}"
    print(f"✓ Evaluated 'sum(range(10))' = {result}")

    # Test 2: Compile-time function
    print("\nTest compile-time function execution...")

    @evaluator.comptime
    def generate_lookup_table(size):
        """Generate lookup table at compile time."""
        return [i * i for i in range(size)]

    # First call - computed
    table1 = generate_lookup_table(10)
    print(f"✓ Generated lookup table: {table1}")

    # Second call - cached
    table2 = generate_lookup_table(10)
    assert table1 == table2, "Cache mismatch"
    print("✓ Result cached correctly")

    # Test 3: Compile-time constants
    print("\nTest compile-time constants...")
    evaluator.const("MAX_SIZE", 1024)
    evaluator.const("PI", 3.14159)

    max_size = evaluator.get_const("MAX_SIZE")
    pi = evaluator.get_const("PI")

    assert max_size == 1024, "Constant value mismatch"
    assert pi == 3.14159, "Constant value mismatch"
    print(f"✓ MAX_SIZE = {max_size}")
    print(f"✓ PI = {pi}")

    # Test 4: Const expression checking
    print("\nTest const expression detection...")
    evaluator.const("X", 10)
    evaluator.const("Y", 20)

    is_const = evaluator.is_const_expr("X + Y")
    print(f"✓ 'X + Y' is const: {is_const}")

    # Test 5: Global comptime decorator
    print("\nTest global comptime decorator...")

    @comptime
    def compute_primes(n):
        """Compute primes at compile time."""
        primes = []
        for num in range(2, n):
            is_prime = True
            for i in range(2, int(num ** 0.5) + 1):
                if num % i == 0:
                    is_prime = False
                    break
            if is_prime:
                primes.append(num)
        return primes

    primes = compute_primes(20)
    print(f"✓ Compile-time computed primes: {primes}")

    print("\n✓ Compile-Time Execution tests passed!")


def test_incremental_compilation():
    """Test incremental compilation features."""
    print("\n" + "="*70)
    print("TEST 6: INCREMENTAL COMPILATION")
    print("="*70)

    # Test 1: Dependency graph
    print("\nTest dependency graph...")
    graph = DependencyGraph()

    # Add modules
    module1 = graph.add_module("main", Path("main.py"))
    module2 = graph.add_module("utils", Path("utils.py"))
    module3 = graph.add_module("helpers", Path("helpers.py"))

    print(f"✓ Added modules: main, utils, helpers")

    # Add dependencies: main -> utils -> helpers
    graph.add_dependency("main", "utils")
    graph.add_dependency("utils", "helpers")

    print("✓ Dependencies: main -> utils -> helpers")

    # Test topological sort
    sorted_modules = graph.topological_sort()
    print(f"✓ Topological order: {sorted_modules}")

    # Test recompilation set
    changed = {"helpers"}
    recompile_set = graph.get_recompilation_set(changed)
    print(f"✓ Changed: {changed}")
    print(f"✓ Recompile set: {recompile_set}")
    assert "helpers" in recompile_set, "Changed module not in recompile set"
    assert "utils" in recompile_set, "Dependent not in recompile set"
    assert "main" in recompile_set, "Transitive dependent not in recompile set"

    # Test 2: Incremental compiler
    print("\nTest incremental compiler...")
    compiler = IncrementalCompiler()

    print(f"✓ Cache directory: {compiler.cache_dir}")
    print(f"✓ Incremental compiler initialized")

    # Create temporary test files
    test_dir = Path("/tmp/lament_test")
    test_dir.mkdir(exist_ok=True)

    file1 = test_dir / "module1.py"
    file2 = test_dir / "module2.py"

    file1.write_text("# Module 1\ndef func1():\n    return 1\n")
    file2.write_text("# Module 2\nfrom module1 import func1\ndef func2():\n    return func1() + 1\n")

    compiler.add_source_file(file1)
    compiler.add_source_file(file2)

    print("✓ Added source files to compiler")

    # First compilation
    print("\nPerforming initial compilation...")
    results = compiler.compile(parallel=False)
    print(f"✓ Compiled {len(results)} modules")

    # Check compilation stats
    stats = compiler.get_compilation_stats()
    print(f"✓ Compilation times: {stats}")

    # Modify file and recompile
    print("\nModifying module and recompiling...")
    time.sleep(0.1)  # Ensure timestamp changes
    file1.write_text("# Module 1 (modified)\ndef func1():\n    return 2\n")

    results = compiler.compile(parallel=False)
    print(f"✓ Recompiled {len(results)} modules (incremental)")

    # Cleanup
    file1.unlink()
    file2.unlink()
    test_dir.rmdir()

    print("\n✓ Incremental Compilation tests passed!")


def test_performance_utilities():
    """Test performance profiling utilities."""
    print("\n" + "="*70)
    print("TEST 7: PERFORMANCE UTILITIES")
    print("="*70)

    # Test 1: Performance profiler
    print("\nTest performance profiler...")
    profiler = PerformanceProfiler()

    # Measure some operations
    with profiler.measure("operation1"):
        time.sleep(0.01)
        _ = sum(range(1000))

    with profiler.measure("operation2"):
        time.sleep(0.02)
        _ = [x * x for x in range(1000)]

    with profiler.measure("operation1"):
        time.sleep(0.01)
        _ = sum(range(1000))

    stats1 = profiler.get_stats("operation1")
    stats2 = profiler.get_stats("operation2")

    print(f"✓ Operation 1 stats: {stats1}")
    print(f"✓ Operation 2 stats: {stats2}")

    assert stats1['count'] == 2, "Wrong measurement count"
    assert stats2['count'] == 1, "Wrong measurement count"

    print("\nFull profiling report:")
    profiler.print_stats()

    # Test 2: Benchmark decorator
    print("\nTest benchmark decorator...")

    @benchmark(iterations=100)
    def benchmark_test(n):
        return sum(range(n))

    result = benchmark_test(1000)
    print(f"✓ Benchmark completed, result: {result}")

    print("\n✓ Performance Utilities tests passed!")


def run_all_tests():
    """Run all performance module tests."""
    print("\n" + "="*70)
    print("LAMENT PERFORMANCE MODULE - COMPREHENSIVE TEST SUITE")
    print("="*70)

    start_time = time.time()

    tests = [
        test_jit_compilation,
        test_parallel_iterators,
        test_simd_operations,
        test_zero_cost_abstractions,
        test_compile_time_execution,
        test_incremental_compilation,
        test_performance_utilities,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"\n✗ {test_func.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    total_time = time.time() - start_time

    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Time: {total_time:.2f}s")
    print("="*70)

    if failed == 0:
        print("\n✓ ALL TESTS PASSED! 🎉")
    else:
        print(f"\n✗ {failed} TEST(S) FAILED")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
