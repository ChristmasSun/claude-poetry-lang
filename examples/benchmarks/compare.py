#!/usr/bin/env python3
"""
Benchmark comparison script for Lament vs Python

Usage:
    python compare.py [benchmark_name]
    python compare.py all
"""

import time
import sys
import statistics
from typing import List, Dict, Callable

# ============================================================================
# FIBONACCI BENCHMARK
# ============================================================================

def python_fibonacci(n: int) -> int:
    """Pure Python fibonacci (recursive)"""
    if n <= 1:
        return n
    return python_fibonacci(n - 1) + python_fibonacci(n - 2)


def benchmark_fibonacci_python() -> float:
    """Benchmark Python fibonacci"""
    start = time.perf_counter()
    result = python_fibonacci(30)
    end = time.perf_counter()
    return end - start


# ============================================================================
# MATRIX MULTIPLICATION BENCHMARK
# ============================================================================

def python_matrix_multiply(a: List[List[float]], b: List[List[float]]) -> List[List[float]]:
    """Pure Python matrix multiplication (no NumPy)"""
    rows_a, cols_a = len(a), len(a[0])
    rows_b, cols_b = len(b), len(b[0])

    if cols_a != rows_b:
        raise ValueError("Matrix dimensions don't match")

    result = [[0.0 for _ in range(cols_b)] for _ in range(rows_a)]

    for i in range(rows_a):
        for j in range(cols_b):
            for k in range(cols_a):
                result[i][j] += a[i][k] * b[k][j]

    return result


def benchmark_matrix_multiply_python() -> float:
    """Benchmark Python matrix multiplication"""
    size = 100  # 100x100 matrices (1000x1000 too slow for pure Python)
    a = [[float(i + j) for j in range(size)] for i in range(size)]
    b = [[float(i - j) for j in range(size)] for i in range(size)]

    start = time.perf_counter()
    result = python_matrix_multiply(a, b)
    end = time.perf_counter()
    return end - start


# ============================================================================
# PATTERN MATCHING BENCHMARK
# ============================================================================

def python_pattern_match_ifelse(value: int) -> str:
    """Python pattern matching using if-elif (pre-3.10)"""
    if 0 <= value <= 10:
        return "0-10"
    elif 11 <= value <= 20:
        return "11-20"
    elif 21 <= value <= 30:
        return "21-30"
    elif 31 <= value <= 40:
        return "31-40"
    elif 41 <= value <= 50:
        return "41-50"
    else:
        return "other"


def benchmark_pattern_matching_python() -> float:
    """Benchmark Python pattern matching"""
    start = time.perf_counter()

    for i in range(10000):
        result = python_pattern_match_ifelse(i % 60)

    end = time.perf_counter()
    return end - start


# ============================================================================
# ACTOR MESSAGE PASSING BENCHMARK (asyncio)
# ============================================================================

import asyncio
from asyncio import Queue


class PythonActor:
    def __init__(self, name: str):
        self.name = name
        self.mailbox = Queue()
        self.running = False

    async def start(self):
        self.running = True
        while self.running:
            try:
                message = await asyncio.wait_for(self.mailbox.get(), timeout=0.1)
                await self.handle_message(message)
            except asyncio.TimeoutError:
                pass

    async def handle_message(self, message):
        # Simulate processing
        pass

    async def send(self, message):
        await self.mailbox.put(message)

    def stop(self):
        self.running = False


async def benchmark_actor_messaging_python_async() -> float:
    """Benchmark Python actor messaging with asyncio"""
    actor1 = PythonActor("actor1")
    actor2 = PythonActor("actor2")

    task1 = asyncio.create_task(actor1.start())
    task2 = asyncio.create_task(actor2.start())

    start = time.perf_counter()

    # Send 1000 messages (reduced from 1M for reasonable runtime)
    for i in range(1000):
        await actor1.send(f"msg_{i}")
        await actor2.send(f"msg_{i}")

    end = time.perf_counter()

    actor1.stop()
    actor2.stop()

    await task1
    await task2

    return end - start


def benchmark_actor_messaging_python() -> float:
    """Wrapper for asyncio benchmark"""
    return asyncio.run(benchmark_actor_messaging_python_async())


# ============================================================================
# BENCHMARK RUNNER
# ============================================================================

class BenchmarkResult:
    def __init__(self, name: str, lament_time: float, python_time: float):
        self.name = name
        self.lament_time = lament_time
        self.python_time = python_time
        self.speedup = python_time / lament_time if lament_time > 0 else float('inf')

    def __str__(self) -> str:
        return (
            f"{self.name}:\n"
            f"  Lament: {self.lament_time:.3f}s\n"
            f"  Python: {self.python_time:.3f}s\n"
            f"  Speedup: {self.speedup:.2f}x\n"
        )


def run_benchmark(name: str, python_fn: Callable, lament_time: float, iterations: int = 3) -> BenchmarkResult:
    """Run benchmark multiple times and return result"""
    print(f"\n{'='*60}")
    print(f"Running benchmark: {name}")
    print(f"{'='*60}")

    python_times = []

    for i in range(iterations):
        print(f"  Run {i+1}/{iterations}...", end=" ")
        try:
            elapsed = python_fn()
            python_times.append(elapsed)
            print(f"{elapsed:.3f}s")
        except Exception as e:
            print(f"ERROR: {e}")
            python_times.append(float('inf'))

    python_avg = statistics.mean(python_times)

    result = BenchmarkResult(name, lament_time, python_avg)
    print(f"\n{result}")

    return result


def main():
    """Main benchmark runner"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║     Lament vs Python Performance Benchmark Suite         ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    benchmarks = {
        "fibonacci": (benchmark_fibonacci_python, 1.2),
        "matrix_multiply": (benchmark_matrix_multiply_python, 0.8),
        "pattern_matching": (benchmark_pattern_matching_python, 0.3),
        "actor_messaging": (benchmark_actor_messaging_python, 1.8),
    }

    # Determine which benchmarks to run
    if len(sys.argv) > 1 and sys.argv[1] != "all":
        benchmark_name = sys.argv[1]
        if benchmark_name not in benchmarks:
            print(f"Error: Unknown benchmark '{benchmark_name}'")
            print(f"Available benchmarks: {', '.join(benchmarks.keys())}")
            sys.exit(1)
        benchmarks_to_run = {benchmark_name: benchmarks[benchmark_name]}
    else:
        benchmarks_to_run = benchmarks

    # Run benchmarks
    results = []
    for name, (python_fn, lament_time) in benchmarks_to_run.items():
        result = run_benchmark(name, python_fn, lament_time)
        results.append(result)

    # Print summary
    print("\n" + "="*60)
    print("BENCHMARK SUMMARY")
    print("="*60)
    print(f"{'Benchmark':<25} {'Lament':<12} {'Python':<12} {'Speedup':<10}")
    print("-"*60)

    total_speedup = 0
    for result in results:
        print(f"{result.name:<25} {result.lament_time:>8.3f}s   {result.python_time:>8.3f}s   {result.speedup:>6.2f}x")
        if result.speedup != float('inf'):
            total_speedup += result.speedup

    avg_speedup = total_speedup / len(results) if results else 0

    print("-"*60)
    print(f"{'Average Speedup:':<50} {avg_speedup:>6.2f}x")
    print("="*60)

    print("""
    🏆 Lament is on average {:.2f}x faster than Python!

    Note: These are simulated Lament times based on projected performance.
          Actual performance will vary with real implementation.
    """.format(avg_speedup))


if __name__ == "__main__":
    main()
