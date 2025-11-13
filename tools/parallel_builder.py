#!/usr/bin/env python3
"""
Lament Parallel Build System - Multi-threaded Compilation

A parallel compilation system that distributes build work across multiple CPU cores.
Features dependency graph analysis, work distribution, progress tracking, and build cache.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import os
import sys
import time
import pickle
import hashlib
import threading
import multiprocessing
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from collections import deque, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue, Empty
from enum import Enum
import json


# ============================================================================
# DEPENDENCY GRAPH
# ============================================================================

class DependencyNode:
    """Represents a node in the dependency graph."""

    def __init__(self, path: Path):
        """Initialize dependency node."""
        self.path = path
        self.dependencies: Set[Path] = set()
        self.dependents: Set[Path] = set()
        self.compiled = False
        self.compiling = False
        self.failed = False
        self.checksum: Optional[str] = None

    def add_dependency(self, dep: Path) -> None:
        """Add a dependency."""
        self.dependencies.add(dep)

    def add_dependent(self, dep: Path) -> None:
        """Add a dependent."""
        self.dependents.add(dep)

    def is_ready(self) -> bool:
        """Check if node is ready to compile (all dependencies compiled)."""
        if self.compiled or self.compiling or self.failed:
            return False
        return True

    def can_compile(self, graph: 'DependencyGraph') -> bool:
        """Check if all dependencies are satisfied."""
        for dep in self.dependencies:
            node = graph.get_node(dep)
            if node and not node.compiled:
                return False
        return True


class DependencyGraph:
    """Manages the dependency graph for parallel compilation."""

    def __init__(self):
        """Initialize dependency graph."""
        self.nodes: Dict[Path, DependencyNode] = {}
        self.lock = threading.Lock()

    def add_node(self, path: Path) -> DependencyNode:
        """Add a node to the graph."""
        with self.lock:
            if path not in self.nodes:
                self.nodes[path] = DependencyNode(path)
            return self.nodes[path]

    def get_node(self, path: Path) -> Optional[DependencyNode]:
        """Get a node from the graph."""
        with self.lock:
            return self.nodes.get(path)

    def add_edge(self, from_path: Path, to_path: Path) -> None:
        """Add an edge (dependency) between two nodes."""
        with self.lock:
            from_node = self.add_node(from_path)
            to_node = self.add_node(to_path)
            from_node.add_dependency(to_path)
            to_node.add_dependent(from_path)

    def get_ready_nodes(self) -> List[DependencyNode]:
        """Get all nodes that are ready to compile."""
        with self.lock:
            ready = []
            for node in self.nodes.values():
                if node.is_ready() and node.can_compile(self):
                    ready.append(node)
            return ready

    def mark_compiling(self, path: Path) -> None:
        """Mark a node as currently compiling."""
        with self.lock:
            if path in self.nodes:
                self.nodes[path].compiling = True

    def mark_compiled(self, path: Path, success: bool = True) -> None:
        """Mark a node as compiled."""
        with self.lock:
            if path in self.nodes:
                self.nodes[path].compiling = False
                if success:
                    self.nodes[path].compiled = True
                else:
                    self.nodes[path].failed = True

    def get_compilation_order(self) -> List[List[Path]]:
        """
        Get compilation order as levels (each level can be compiled in parallel).
        Returns a list of lists, where each inner list contains files that can
        be compiled in parallel.
        """
        levels = []
        compiled = set()

        while len(compiled) < len(self.nodes):
            # Find nodes with all dependencies compiled
            current_level = []
            for path, node in self.nodes.items():
                if path in compiled or node.failed:
                    continue
                # Check if all dependencies are compiled
                if all(dep in compiled for dep in node.dependencies):
                    current_level.append(path)

            if not current_level:
                # Circular dependency or isolated nodes
                remaining = set(self.nodes.keys()) - compiled
                if remaining:
                    # Add remaining nodes (breaking circular deps)
                    current_level = list(remaining)
                else:
                    break

            levels.append(current_level)
            compiled.update(current_level)

        return levels

    def detect_cycles(self) -> List[List[Path]]:
        """Detect circular dependencies in the graph."""
        cycles = []
        visited = set()
        rec_stack = set()

        def dfs(node: DependencyNode, path: List[Path]) -> None:
            visited.add(node.path)
            rec_stack.add(node.path)
            path.append(node.path)

            for dep in node.dependencies:
                dep_node = self.nodes.get(dep)
                if not dep_node:
                    continue

                if dep not in visited:
                    dfs(dep_node, path.copy())
                elif dep in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(dep)
                    cycles.append(path[cycle_start:] + [dep])

            rec_stack.remove(node.path)

        for node in self.nodes.values():
            if node.path not in visited:
                dfs(node, [])

        return cycles

    def get_stats(self) -> Dict[str, int]:
        """Get graph statistics."""
        stats = {
            'total': len(self.nodes),
            'compiled': sum(1 for n in self.nodes.values() if n.compiled),
            'compiling': sum(1 for n in self.nodes.values() if n.compiling),
            'failed': sum(1 for n in self.nodes.values() if n.failed),
            'pending': sum(1 for n in self.nodes.values()
                          if not (n.compiled or n.compiling or n.failed))
        }
        return stats


# ============================================================================
# COMPILATION TASK
# ============================================================================

@dataclass
class CompilationTask:
    """Represents a compilation task."""
    source_file: Path
    output_dir: Path
    config: Any  # BuildConfig
    dependencies: List[Path] = field(default_factory=list)
    priority: int = 0  # Higher priority = compile first

    def __lt__(self, other):
        """Compare tasks by priority."""
        return self.priority > other.priority


@dataclass
class CompilationResult:
    """Result of a compilation task."""
    source_file: Path
    success: bool
    message: str
    output_file: Optional[Path] = None
    duration: float = 0.0
    error: Optional[Exception] = None


# ============================================================================
# WORK QUEUE
# ============================================================================

class WorkQueue:
    """Thread-safe work queue for compilation tasks."""

    def __init__(self):
        """Initialize work queue."""
        self.queue: deque = deque()
        self.lock = threading.Lock()
        self.not_empty = threading.Condition(self.lock)
        self.completed = 0
        self.failed = 0

    def put(self, task: CompilationTask) -> None:
        """Add a task to the queue."""
        with self.not_empty:
            # Insert based on priority
            inserted = False
            for i, existing in enumerate(self.queue):
                if task.priority > existing.priority:
                    self.queue.insert(i, task)
                    inserted = True
                    break
            if not inserted:
                self.queue.append(task)
            self.not_empty.notify()

    def get(self, timeout: Optional[float] = None) -> Optional[CompilationTask]:
        """Get a task from the queue."""
        with self.not_empty:
            while not self.queue:
                if timeout:
                    self.not_empty.wait(timeout)
                    if not self.queue:
                        return None
                else:
                    self.not_empty.wait()
            return self.queue.popleft()

    def size(self) -> int:
        """Get queue size."""
        with self.lock:
            return len(self.queue)

    def mark_completed(self, success: bool = True) -> None:
        """Mark a task as completed."""
        with self.lock:
            if success:
                self.completed += 1
            else:
                self.failed += 1

    def get_stats(self) -> Dict[str, int]:
        """Get queue statistics."""
        with self.lock:
            return {
                'pending': len(self.queue),
                'completed': self.completed,
                'failed': self.failed,
                'total': len(self.queue) + self.completed + self.failed
            }


# ============================================================================
# PROGRESS TRACKER
# ============================================================================

class ProgressTracker:
    """Tracks and displays build progress."""

    def __init__(self, total_files: int, show_progress: bool = True):
        """Initialize progress tracker."""
        self.total_files = total_files
        self.compiled = 0
        self.failed = 0
        self.current_files: Dict[str, str] = {}  # thread_id -> filename
        self.lock = threading.Lock()
        self.show_progress = show_progress
        self.start_time = time.time()

    def start_file(self, thread_id: str, filename: str) -> None:
        """Mark a file as started."""
        with self.lock:
            self.current_files[thread_id] = filename
            if self.show_progress:
                self._display_progress()

    def complete_file(self, thread_id: str, success: bool = True) -> None:
        """Mark a file as completed."""
        with self.lock:
            if thread_id in self.current_files:
                del self.current_files[thread_id]
            if success:
                self.compiled += 1
            else:
                self.failed += 1
            if self.show_progress:
                self._display_progress()

    def _display_progress(self) -> None:
        """Display current progress."""
        total_done = self.compiled + self.failed
        percent = (total_done / self.total_files * 100) if self.total_files > 0 else 0
        elapsed = time.time() - self.start_time

        # Calculate ETA
        if total_done > 0:
            rate = total_done / elapsed
            remaining = self.total_files - total_done
            eta = remaining / rate if rate > 0 else 0
            eta_str = f"ETA: {eta:.1f}s"
        else:
            eta_str = "ETA: --"

        # Progress bar
        bar_width = 40
        filled = int(bar_width * total_done / self.total_files) if self.total_files > 0 else 0
        bar = '█' * filled + '░' * (bar_width - filled)

        # Status line
        status = f"\r[{bar}] {percent:.1f}% ({total_done}/{self.total_files}) "
        status += f"✓ {self.compiled} ✗ {self.failed} | {eta_str}"

        # Currently compiling
        if self.current_files:
            current = list(self.current_files.values())[:3]  # Show max 3
            current_str = ", ".join(f.name if isinstance(f, Path) else f for f in current)
            if len(self.current_files) > 3:
                current_str += f" +{len(self.current_files) - 3} more"
            status += f" | Compiling: {current_str}"

        print(status, end='', flush=True)

    def finish(self) -> None:
        """Finish progress tracking."""
        if self.show_progress:
            print()  # New line after progress bar

    def get_summary(self) -> str:
        """Get build summary."""
        elapsed = time.time() - self.start_time
        rate = self.compiled / elapsed if elapsed > 0 else 0

        summary = f"\nBuild Summary:\n"
        summary += f"  Total files: {self.total_files}\n"
        summary += f"  Compiled: {self.compiled}\n"
        summary += f"  Failed: {self.failed}\n"
        summary += f"  Time: {elapsed:.2f}s\n"
        summary += f"  Rate: {rate:.1f} files/s\n"

        return summary


# ============================================================================
# PARALLEL COMPILER
# ============================================================================

class ParallelCompiler:
    """Multi-threaded parallel compiler for Lament."""

    def __init__(self, config: Any, num_jobs: Optional[int] = None):
        """
        Initialize parallel compiler.

        Args:
            config: Build configuration
            num_jobs: Number of parallel jobs (default: CPU count)
        """
        self.config = config
        self.num_jobs = num_jobs or multiprocessing.cpu_count()
        self.graph = DependencyGraph()
        self.work_queue = WorkQueue()
        self.results: List[CompilationResult] = []
        self.results_lock = threading.Lock()
        self.stop_on_error = config.warnings_as_errors
        self.should_stop = threading.Event()

    def build_dependency_graph(self, source_files: List[Any]) -> None:
        """
        Build dependency graph from source files.

        Args:
            source_files: List of SourceFile objects
        """
        print(f"Building dependency graph...")

        # Add all nodes
        for source_file in source_files:
            node = self.graph.add_node(source_file.path)
            node.checksum = source_file.checksum

            # Add dependencies
            for dep in source_file.dependencies:
                self.graph.add_edge(source_file.path, dep)

        # Check for circular dependencies
        cycles = self.graph.detect_cycles()
        if cycles:
            print(f"Warning: Detected {len(cycles)} circular dependencies:")
            for cycle in cycles[:3]:  # Show first 3
                cycle_str = " -> ".join(str(p.name) for p in cycle)
                print(f"  {cycle_str}")

        # Show compilation levels
        levels = self.graph.get_compilation_order()
        print(f"Dependency analysis complete: {len(levels)} compilation levels")
        max_parallelism = max(len(level) for level in levels) if levels else 0
        print(f"Maximum parallelism: {max_parallelism} files")

    def _compile_file_worker(self, task: CompilationTask) -> CompilationResult:
        """
        Worker function to compile a single file.

        Args:
            task: Compilation task

        Returns:
            Compilation result
        """
        start_time = time.time()

        try:
            # Import Lament modules
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from lament.lexer import Lexer
            from lament.parser import Parser
            from lament.bytecode import BytecodeCompiler

            # Read source
            with open(task.source_file, 'r', encoding='utf-8') as f:
                source = f.read()

            # Lex
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            # Parse
            parser = Parser(tokens)
            ast = parser.parse()

            # Compile to bytecode
            compiler = BytecodeCompiler()
            bytecode = compiler.compile(ast)

            # Save bytecode
            output_file = task.output_dir / f"{task.source_file.stem}.lmc"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                pickle.dump(bytecode, f)

            duration = time.time() - start_time

            return CompilationResult(
                source_file=task.source_file,
                success=True,
                message=f"Compiled {task.source_file.name}",
                output_file=output_file,
                duration=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            return CompilationResult(
                source_file=task.source_file,
                success=False,
                message=f"Failed to compile {task.source_file.name}: {e}",
                duration=duration,
                error=e
            )

    def _worker_thread(self, thread_id: int, progress: ProgressTracker) -> None:
        """
        Worker thread that processes compilation tasks.

        Args:
            thread_id: Thread identifier
            progress: Progress tracker
        """
        thread_name = f"worker-{thread_id}"

        while not self.should_stop.is_set():
            # Get next task
            task = self.work_queue.get(timeout=0.5)
            if task is None:
                continue

            # Mark as compiling
            self.graph.mark_compiling(task.source_file)
            progress.start_file(thread_name, task.source_file.name)

            # Compile
            result = self._compile_file_worker(task)

            # Store result
            with self.results_lock:
                self.results.append(result)

            # Update graph
            self.graph.mark_compiled(task.source_file, result.success)
            progress.complete_file(thread_name, result.success)
            self.work_queue.mark_completed(result.success)

            # Stop on error if configured
            if not result.success and self.stop_on_error:
                self.should_stop.set()
                break

            # Schedule ready dependents
            node = self.graph.get_node(task.source_file)
            if node and result.success:
                for dependent in node.dependents:
                    dep_node = self.graph.get_node(dependent)
                    if dep_node and dep_node.can_compile(self.graph):
                        # Create task for dependent
                        dep_task = CompilationTask(
                            source_file=dependent,
                            output_dir=task.output_dir,
                            config=task.config,
                            dependencies=list(dep_node.dependencies)
                        )
                        self.work_queue.put(dep_task)

    def compile_parallel(self, source_files: List[Any],
                        output_dir: Path) -> Tuple[bool, List[CompilationResult]]:
        """
        Compile multiple files in parallel.

        Args:
            source_files: List of SourceFile objects
            output_dir: Output directory for compiled files

        Returns:
            Tuple of (success, results)
        """
        if not source_files:
            return True, []

        print(f"\nParallel compilation with {self.num_jobs} workers")

        # Build dependency graph
        self.build_dependency_graph(source_files)

        # Create progress tracker
        progress = ProgressTracker(len(source_files))

        # Get initial ready tasks
        ready_nodes = self.graph.get_ready_nodes()
        print(f"Scheduling {len(ready_nodes)} initial tasks...")

        for node in ready_nodes:
            task = CompilationTask(
                source_file=node.path,
                output_dir=output_dir,
                config=self.config,
                dependencies=list(node.dependencies)
            )
            self.work_queue.put(task)

        # Start worker threads
        threads = []
        for i in range(self.num_jobs):
            thread = threading.Thread(
                target=self._worker_thread,
                args=(i, progress),
                daemon=True
            )
            thread.start()
            threads.append(thread)

        # Wait for completion
        while True:
            stats = self.graph.get_stats()
            if stats['compiled'] + stats['failed'] >= stats['total']:
                break
            if self.should_stop.is_set():
                break
            time.sleep(0.1)

        # Stop workers
        self.should_stop.set()
        for thread in threads:
            thread.join(timeout=1.0)

        # Finish progress
        progress.finish()
        print(progress.get_summary())

        # Check results
        success = all(r.success for r in self.results)

        if not success:
            failed = [r for r in self.results if not r.success]
            print(f"\n{len(failed)} file(s) failed to compile:")
            for result in failed[:10]:  # Show first 10
                print(f"  - {result.source_file.name}: {result.message}")

        return success, self.results

    def get_build_stats(self) -> Dict[str, Any]:
        """Get detailed build statistics."""
        if not self.results:
            return {}

        total_time = sum(r.duration for r in self.results)
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]

        stats = {
            'total_files': len(self.results),
            'successful': len(successful),
            'failed': len(failed),
            'total_time': total_time,
            'avg_time': total_time / len(self.results) if self.results else 0,
            'parallelism': self.num_jobs,
            'speedup': total_time / max(r.duration for r in self.results) if self.results else 0
        }

        return stats


# ============================================================================
# INCREMENTAL BUILD CACHE
# ============================================================================

class IncrementalCache:
    """Advanced incremental build cache with checksums."""

    def __init__(self, cache_file: Path):
        """Initialize incremental cache."""
        self.cache_file = cache_file
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.load()

    def load(self) -> None:
        """Load cache from disk."""
        if not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load incremental cache: {e}")
            self.cache = {}

    def save(self) -> None:
        """Save cache to disk."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

    def needs_rebuild(self, source_file: Path, checksum: str,
                     dependencies: List[Path]) -> bool:
        """Check if a file needs to be rebuilt."""
        key = str(source_file)

        if key not in self.cache:
            return True

        cached = self.cache[key]

        # Check checksum
        if cached.get('checksum') != checksum:
            return True

        # Check dependencies
        cached_deps = set(cached.get('dependencies', []))
        current_deps = set(str(d) for d in dependencies)
        if cached_deps != current_deps:
            return True

        return False

    def update(self, source_file: Path, checksum: str,
              dependencies: List[Path], output_file: Path) -> None:
        """Update cache entry."""
        self.cache[str(source_file)] = {
            'checksum': checksum,
            'dependencies': [str(d) for d in dependencies],
            'output_file': str(output_file),
            'timestamp': time.time()
        }

    def clear(self) -> None:
        """Clear the cache."""
        self.cache = {}
        if self.cache_file.exists():
            self.cache_file.unlink()


# ============================================================================
# CLI
# ============================================================================

def main():
    """CLI entry point for parallel builder."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Lament Parallel Build System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--jobs', '-j', type=int, default=None,
                       help='Number of parallel jobs (default: CPU count)')
    parser.add_argument('--output', '-o', type=Path, default=Path('build/out'),
                       help='Output directory')
    parser.add_argument('sources', nargs='+', type=Path,
                       help='Source files to compile')

    args = parser.parse_args()

    print(f"Lament Parallel Compiler - {args.jobs or 'auto'} jobs")

    # This is a standalone CLI for testing
    # Normal usage is through the main builder.py

    print("Note: Use 'lament-build --parallel' for full build system integration")


if __name__ == '__main__':
    main()
