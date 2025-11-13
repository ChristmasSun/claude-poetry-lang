# Lament Build System Documentation

Complete guide to the Lament Build System with parallel compilation, watch mode, and build server capabilities.

**Version 2.0 - The Parallel Revolution**

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)

---

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Build Modes](#build-modes)
5. [Parallel Compilation](#parallel-compilation)
6. [Watch Mode](#watch-mode)
7. [Build Server](#build-server)
8. [Configuration](#configuration)
9. [Advanced Usage](#advanced-usage)
10. [API Reference](#api-reference)
11. [Performance Tuning](#performance-tuning)
12. [Troubleshooting](#troubleshooting)

---

## Overview

The Lament Build System is a comprehensive, high-performance build tool for the Lament programming language. It provides:

- **Incremental Builds**: Only recompile changed files
- **Parallel Compilation**: Multi-threaded builds using all CPU cores
- **Watch Mode**: Automatic rebuilds on file changes
- **Build Server**: Background daemon with HTTP API
- **Dependency Tracking**: Smart dependency graph analysis
- **Build Cache**: Fast incremental compilation
- **Progress Tracking**: Real-time build progress visualization
- **Live Reload**: WebSocket support for IDE integration

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Lament Build System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   builder.py │  │ watch_mode.py│  │build_server  │     │
│  │              │  │              │  │    .py       │     │
│  │  Main Build  │  │  File Watch  │  │  HTTP API    │     │
│  │    System    │  │  Auto-Rebuild│  │  WebSocket   │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                 │                  │              │
│         └─────────────────┴──────────────────┘              │
│                           │                                 │
│                  ┌────────▼─────────┐                      │
│                  │ parallel_builder │                      │
│                  │       .py        │                      │
│                  │                  │                      │
│                  │  Dependency Graph│                      │
│                  │  Work Queue      │                      │
│                  │  Thread Pool     │                      │
│                  │  Progress Track  │                      │
│                  └──────────────────┘                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Lament language runtime

### Basic Installation

The build system is included with Lament. No additional installation required.

### Optional Dependencies

For full functionality, install these optional packages:

```bash
# For watch mode (recommended)
pip install watchdog

# For build server (HTTP API)
pip install flask flask-cors

# For WebSocket support
pip install websockets
```

### Verify Installation

```bash
python tools/builder.py --version
# Output: lament-build 2.0.0
```

---

## Quick Start

### Basic Build

```bash
# Build the project
python tools/builder.py build

# Clean and build
python tools/builder.py build --clean

# Build and run
python tools/builder.py run
```

### Parallel Build

```bash
# Parallel compilation (uses all CPU cores)
python tools/builder.py build --parallel

# Parallel with specific number of jobs
python tools/builder.py build --parallel -j 8
```

### Watch Mode

```bash
# Start watch mode
python tools/builder.py watch

# Watch mode with parallel compilation
python tools/builder.py watch --parallel -j 4
```

### Build Server

```bash
# Start build server
python tools/builder.py server start

# Start with custom settings
python tools/builder.py server start --workers 4 --port 8080
```

---

## Build Modes

### Sequential Build (Default)

Compiles files one at a time in dependency order.

**Pros:**
- Predictable resource usage
- Easy debugging
- Works everywhere

**Cons:**
- Slower for large projects
- Doesn't utilize multiple cores

**Usage:**
```bash
python tools/builder.py build
```

### Parallel Build

Compiles multiple files simultaneously using thread pool.

**Pros:**
- 3-10x faster on multi-core systems
- Automatic dependency resolution
- Smart work distribution

**Cons:**
- Higher memory usage
- More complex error messages

**Usage:**
```bash
python tools/builder.py build --parallel -j 8
```

### Incremental Build

Only recompiles files that have changed.

**Pros:**
- Very fast for small changes
- Automatic cache management
- Checksums for reliability

**Cons:**
- Cache can become stale (use --clean)

**Usage:**
```bash
# Incremental is default
python tools/builder.py build

# Force full rebuild
python tools/builder.py build --no-incremental
```

---

## Parallel Compilation

### How It Works

The parallel compiler uses a sophisticated multi-stage process:

1. **Dependency Analysis**: Builds a directed acyclic graph (DAG) of file dependencies
2. **Level Detection**: Identifies compilation levels (files with no interdependencies)
3. **Work Distribution**: Distributes work across worker threads
4. **Progress Tracking**: Real-time progress visualization
5. **Result Collection**: Aggregates results and detects errors

### Dependency Graph

The system automatically analyzes `breathe` (import) statements:

```lament
breathe "utils"        # Depends on utils.lament
breathe "helpers/io"   # Depends on helpers/io.lament
```

Files are compiled in topological order:

```
Level 1: [utils.lament, config.lament]     ← No dependencies
Level 2: [helpers.lament]                  ← Depends on utils
Level 3: [main.lament]                     ← Depends on helpers
```

### Performance

Example benchmarks on 100 files:

| Mode       | Time    | Speedup |
|------------|---------|---------|
| Sequential | 45.3s   | 1.0x    |
| Parallel 2 | 24.1s   | 1.9x    |
| Parallel 4 | 13.2s   | 3.4x    |
| Parallel 8 | 8.1s    | 5.6x    |
| Parallel 16| 6.3s    | 7.2x    |

### Usage Examples

```bash
# Auto-detect CPU cores
python tools/builder.py build --parallel

# Use 4 cores
python tools/builder.py build --parallel -j 4

# Maximum parallelism (2x CPU count)
python tools/builder.py build --parallel -j 32

# Parallel incremental build
python tools/builder.py build --parallel --clean
```

### Configuration

Control parallel compilation via build configuration:

```json
{
  "name": "my-project",
  "optimization_level": 2,
  "warnings_as_errors": true
}
```

### Advanced Features

#### Build Cache

The parallel builder uses an advanced cache:

```python
# Cache structure
{
  "source_file.lament": {
    "checksum": "sha256...",
    "dependencies": ["dep1.lament", "dep2.lament"],
    "output_file": "build/source_file.lmc",
    "timestamp": 1699999999.0
  }
}
```

#### Circular Dependency Detection

Automatically detects and reports circular dependencies:

```
Warning: Detected 1 circular dependencies:
  module_a.lament -> module_b.lament -> module_c.lament -> module_a.lament
```

#### Progress Tracking

Real-time progress bar with statistics:

```
[████████████████████░░░░░░░░] 75.0% (75/100) ✓ 73 ✗ 2 | ETA: 3.2s | Compiling: utils.lament, config.lament, helpers.lament
```

---

## Watch Mode

### Overview

Watch mode automatically rebuilds when source files change. Features:

- **File Watching**: Uses `watchdog` library (or polling fallback)
- **Debouncing**: Prevents rebuilds on rapid file changes
- **Smart Detection**: Only rebuilds affected files
- **Live Reload**: WebSocket support for IDEs
- **Terminal UI**: Clean progress display

### Basic Usage

```bash
# Start watch mode
python tools/builder.py watch

# Watch with debounce delay
python tools/builder.py watch --debounce 1.0

# Watch with parallel compilation
python tools/builder.py watch --parallel -j 8
```

### How It Works

```
File Changed → Debouncer → Detect Affected → Build → Notify
     ↓            ↓              ↓             ↓        ↓
  Modified      Wait          Analyze       Compile   Show
   Event       500ms         Dependencies   Files    Results
```

### Watched File Patterns

By default, watches:
- `**/*.lament` - All Lament source files

Excludes:
- `**/test_*.lament` - Test files
- `**/__pycache__/**` - Python cache

### Configuration

Customize watch patterns in `build.lament`:

```json
{
  "include_patterns": ["**/*.lament", "**/*.lib"],
  "exclude_patterns": ["tests/**", "build/**"]
}
```

### Debouncing

Prevents rebuilds on rapid file changes:

```bash
# Short debounce (responsive)
python tools/builder.py watch --debounce 0.2

# Long debounce (stable)
python tools/builder.py watch --debounce 2.0
```

### Output

```
===========================================================
Lament Watch Mode - Auto-rebuild on Changes
===========================================================

Performing initial build...
Building my-project...
...
Build completed successfully in 2.34s

Starting file watcher for 2 directory(ies)...
  Watching: /project/src
  Watching: /project/lib
File watcher started. Waiting for changes...

Press Ctrl+C to stop watching

============================================================
Detected 1 file change(s):
  modified: main.lament
------------------------------------------------------------
Rebuilding at 14:23:45...
------------------------------------------------------------
Rebuilding 1 affected file(s)...
...
✓ Build succeeded in 0.42s
```

### Statistics

Periodically shows stats:

```
--- Watch Mode Stats (running 15.3 min) ---
  Changes detected: 23
  Total builds: 18
  Successful: 16
  Failed: 2
```

### Integration with IDEs

Watch mode can be integrated with editors:

**VS Code**: Use tasks.json
```json
{
  "label": "Lament Watch",
  "type": "shell",
  "command": "python tools/builder.py watch --parallel",
  "isBackground": true
}
```

**Vim/Neovim**: Run in split terminal
```vim
:term python tools/builder.py watch
```

---

## Build Server

### Overview

The build server runs as a background daemon providing:

- **HTTP API**: RESTful build requests
- **WebSocket**: Live build updates
- **Build Queue**: Manages concurrent builds
- **Background Processing**: Non-blocking builds
- **Build History**: Tracks recent builds

### Starting the Server

```bash
# Start with defaults
python tools/builder.py server start

# Custom configuration
python tools/builder.py server start --workers 4 --port 8080

# Production deployment
python tools/builder.py server start --host 0.0.0.0 --port 8765 --workers 8
```

### HTTP API

#### Health Check

```bash
GET /health
```

Response:
```json
{
  "status": "healthy",
  "uptime": 3600.5
}
```

#### Server Statistics

```bash
GET /stats
```

Response:
```json
{
  "queued": 2,
  "active": 1,
  "total_builds": 127,
  "successful": 119,
  "failed": 8,
  "success_rate": 93.7
}
```

#### Submit Build Request

```bash
POST /build
Content-Type: application/json

{
  "project_dir": "/path/to/project",
  "clean": false,
  "parallel": true,
  "num_jobs": 8,
  "priority": 10
}
```

Response:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

#### Get Build Result

```bash
GET /build/{request_id}
```

Response:
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "success",
  "started_at": 1699999999.0,
  "finished_at": 1700000005.3,
  "duration": 6.3,
  "message": "Build succeeded",
  "logs": ["Compiled main.lament", "Compiled utils.lament"],
  "errors": []
}
```

#### Cancel Build

```bash
DELETE /build/{request_id}
```

Note: Only queued builds can be cancelled (not running ones).

#### Recent Builds

```bash
GET /builds/recent?limit=10
```

#### Active Builds

```bash
GET /builds/active
```

### Example Client

Python client example:

```python
import requests

# Submit build
response = requests.post('http://localhost:8765/build', json={
    'project_dir': '/path/to/project',
    'parallel': True,
    'num_jobs': 8
})

request_id = response.json()['request_id']
print(f"Build queued: {request_id}")

# Poll for result
import time
while True:
    response = requests.get(f'http://localhost:8765/build/{request_id}')
    result = response.json()

    if result['status'] in ['success', 'failed']:
        print(f"Build {result['status']}: {result['message']}")
        break

    time.sleep(0.5)
```

### Build Queue

The server maintains a priority queue:

```
┌─────────────────────────────────────┐
│         Build Queue                 │
├─────────────────────────────────────┤
│  Priority 10: Build A (queued)      │
│  Priority 5:  Build B (queued)      │
│  Priority 0:  Build C (queued)      │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      Worker Pool (2 workers)        │
├─────────────────────────────────────┤
│  Worker 0: Building A (running)     │
│  Worker 1: Building D (running)     │
└─────────────────────────────────────┘
           ↓
┌─────────────────────────────────────┐
│      Build History (100 max)        │
├─────────────────────────────────────┤
│  Build D: success (5.2s ago)        │
│  Build E: failed  (12.8s ago)       │
│  Build F: success (45.3s ago)       │
└─────────────────────────────────────┘
```

### Deployment

#### Systemd Service

Create `/etc/systemd/system/lament-build-server.service`:

```ini
[Unit]
Description=Lament Build Server
After=network.target

[Service]
Type=simple
User=builder
WorkingDirectory=/opt/lament
ExecStart=/usr/bin/python3 tools/builder.py server start --host 0.0.0.0 --port 8765
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable lament-build-server
sudo systemctl start lament-build-server
```

#### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install flask flask-cors watchdog

EXPOSE 8765

CMD ["python", "tools/builder.py", "server", "start", "--host", "0.0.0.0", "--port", "8765"]
```

Build and run:
```bash
docker build -t lament-build-server .
docker run -d -p 8765:8765 lament-build-server
```

---

## Configuration

### Build Configuration File

Create `build.lament` in your project root:

```json
{
  "name": "my-project",
  "target": "executable",
  "entry_point": "main.lament",
  "output_dir": "build/out",
  "source_dirs": ["src", "lib"],
  "include_patterns": ["**/*.lament"],
  "exclude_patterns": ["tests/**", "**/test_*.lament"],
  "dependencies": [],
  "optimization_level": 2,
  "debug": false,
  "warnings_as_errors": true,
  "custom_flags": []
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `name` | string | Project directory name | Project name |
| `target` | enum | "executable" | Build target: executable, library, module |
| `entry_point` | path | "main.lament" | Main entry point file |
| `output_dir` | path | "build/out" | Output directory for compiled files |
| `source_dirs` | array | ["src", "."] | Directories to search for source files |
| `include_patterns` | array | ["**/*.lament"] | File patterns to include |
| `exclude_patterns` | array | ["tests/**"] | File patterns to exclude |
| `dependencies` | array | [] | External dependencies |
| `optimization_level` | int | 0 | Optimization level (0-3) |
| `debug` | boolean | false | Enable debug mode |
| `warnings_as_errors` | boolean | false | Treat warnings as errors |
| `custom_flags` | array | [] | Custom compiler flags |

---

## Advanced Usage

### Custom Build Scripts

Create a custom build script:

```python
#!/usr/bin/env python3
"""Custom build script."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from tools.builder import BuildSystem
from tools.parallel_builder import ParallelCompiler

def main():
    # Create custom build system
    build_system = BuildSystem()

    # Configure
    build_system.config.optimization_level = 3
    build_system.config.warnings_as_errors = True

    # Build with custom logic
    source_files = build_system.discover_sources()

    # Filter specific files
    production_files = [
        f for f in source_files
        if not f.path.match('**/debug_*.lament')
    ]

    # Parallel compile
    compiler = ParallelCompiler(build_system.config, num_jobs=16)
    success, results = compiler.compile_parallel(
        production_files,
        build_system.config.output_dir
    )

    if success:
        print("Production build complete!")
        return 0
    else:
        print("Build failed!")
        return 1

if __name__ == '__main__':
    sys.exit(main())
```

### Programmatic API

Use the build system programmatically:

```python
from tools.builder import BuildSystem, BuildConfig, BuildTarget
from pathlib import Path

# Create configuration
config = BuildConfig(
    name="my-lib",
    target=BuildTarget.LIBRARY,
    entry_point=Path("src/main.lament"),
    output_dir=Path("dist"),
    optimization_level=3
)

# Create build system
build_system = BuildSystem()
build_system.config = config

# Build
success = build_system.build(
    incremental=True,
    parallel=True,
    num_jobs=8
)
```

### Pre/Post Build Hooks

Add build hooks:

```python
class CustomBuildSystem(BuildSystem):
    def build(self, **kwargs):
        # Pre-build hook
        print("Running pre-build checks...")
        self.run_linter()
        self.run_tests()

        # Build
        success = super().build(**kwargs)

        # Post-build hook
        if success:
            print("Running post-build tasks...")
            self.generate_docs()
            self.create_package()

        return success

    def run_linter(self):
        # Run linter
        pass

    def run_tests(self):
        # Run tests
        pass
```

---

## API Reference

### BuildSystem Class

```python
class BuildSystem:
    def __init__(self, project_dir: Optional[Path] = None)
    def discover_sources(self) -> List[SourceFile]
    def build(self, incremental: bool = True, clean: bool = False,
              parallel: bool = False, num_jobs: Optional[int] = None) -> bool
    def clean(self) -> None
    def run(self) -> int
```

### ParallelCompiler Class

```python
class ParallelCompiler:
    def __init__(self, config: BuildConfig, num_jobs: Optional[int] = None)
    def build_dependency_graph(self, source_files: List[SourceFile]) -> None
    def compile_parallel(self, source_files: List[SourceFile],
                        output_dir: Path) -> Tuple[bool, List[CompilationResult]]
    def get_build_stats(self) -> Dict[str, Any]
```

### FileWatcher Class

```python
class FileWatcher:
    def __init__(self, directories: List[Path], patterns: List[str] = None,
                 exclude_patterns: List[str] = None, debounce_delay: float = 0.5)
    def register_callback(self, callback: Callable[[List[FileChangeEvent]], None]) -> None
    def start(self) -> None
    def stop(self) -> None
    def get_stats(self) -> Dict[str, Any]
```

### BuildServer Class

```python
class BuildServer:
    def __init__(self, num_workers: int = 2, host: str = 'localhost', port: int = 8765)
    def start(self) -> None
    def stop(self) -> None
```

---

## Performance Tuning

### Optimal Job Count

Find the optimal number of jobs for your system:

```bash
# Test different job counts
for jobs in 2 4 8 16; do
    echo "Testing with $jobs jobs..."
    time python tools/builder.py build --parallel -j $jobs --clean
done
```

Generally:
- **Small projects (<20 files)**: 2-4 jobs
- **Medium projects (20-100 files)**: 4-8 jobs
- **Large projects (>100 files)**: 8-16 jobs

### Memory Usage

Parallel compilation uses more memory:

| Jobs | Memory Usage (approx) |
|------|----------------------|
| 1    | 50-100 MB           |
| 4    | 150-300 MB          |
| 8    | 300-600 MB          |
| 16   | 600-1200 MB         |

### Disk I/O Optimization

For SSD:
- Use more jobs (16-32)
- Enable parallel builds

For HDD:
- Use fewer jobs (2-4)
- Consider sequential builds

### Network Builds

Building over network storage:
- Use sequential builds
- Enable aggressive caching
- Consider build server on same network

---

## Troubleshooting

### Build Fails with Parallel Mode

**Problem**: Build succeeds sequentially but fails with `--parallel`

**Solution**:
1. Check for circular dependencies:
   ```bash
   python tools/builder.py build --parallel 2>&1 | grep "circular"
   ```

2. Try fewer jobs:
   ```bash
   python tools/builder.py build --parallel -j 2
   ```

3. Check for race conditions in dependencies

### Watch Mode Not Detecting Changes

**Problem**: Files change but watch mode doesn't rebuild

**Solution**:
1. Install watchdog:
   ```bash
   pip install watchdog
   ```

2. Check file patterns in `build.lament`

3. Increase debounce delay:
   ```bash
   python tools/builder.py watch --debounce 1.0
   ```

### Build Server Connection Refused

**Problem**: Cannot connect to build server

**Solution**:
1. Check if server is running:
   ```bash
   curl http://localhost:8765/health
   ```

2. Check firewall settings

3. Try different port:
   ```bash
   python tools/builder.py server start --port 9000
   ```

### High Memory Usage

**Problem**: Build uses too much memory

**Solution**:
1. Reduce parallel jobs:
   ```bash
   python tools/builder.py build --parallel -j 2
   ```

2. Use sequential build:
   ```bash
   python tools/builder.py build
   ```

3. Clean build cache:
   ```bash
   python tools/builder.py clean
   ```

### Stale Cache Issues

**Problem**: Build not picking up changes

**Solution**:
```bash
# Clean and rebuild
python tools/builder.py build --clean

# Delete cache manually
rm -rf build/.build_cache

# Disable incremental builds
python tools/builder.py build --no-incremental
```

---

## Examples

### Example 1: Fast Development Workflow

```bash
# Terminal 1: Watch mode with parallel compilation
python tools/builder.py watch --parallel -j 4

# Edit files in your editor
# Builds happen automatically!
```

### Example 2: Production Build

```bash
#!/bin/bash
# production_build.sh

echo "Building for production..."

# Clean build
python tools/builder.py clean

# Optimized parallel build
python tools/builder.py build \
    --parallel \
    -j 16 \
    --no-incremental

# Run tests
python -m pytest tests/

# Package
tar -czf dist/my-project.tar.gz build/
```

### Example 3: CI/CD Pipeline

```yaml
# .github/workflows/build.yml
name: Build

on: [push]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Install dependencies
        run: pip install watchdog flask flask-cors

      - name: Build
        run: python tools/builder.py build --parallel -j 4

      - name: Upload artifacts
        uses: actions/upload-artifact@v2
        with:
          name: build
          path: build/
```

### Example 4: Multi-Project Build Server

```bash
# Start central build server
python tools/builder.py server start --workers 8 --port 8765

# Submit builds from different projects
curl -X POST http://localhost:8765/build \
  -H "Content-Type: application/json" \
  -d '{"project_dir": "/project1", "parallel": true}'

curl -X POST http://localhost:8765/build \
  -H "Content-Type: application/json" \
  -d '{"project_dir": "/project2", "parallel": true}'
```

---

## Conclusion

The Lament Build System provides a modern, high-performance build experience with:

- **3-10x speedup** with parallel compilation
- **Automatic rebuilds** with watch mode
- **Remote builds** via build server
- **Smart caching** for fast incremental builds
- **Professional tooling** ready for production

For more information:
- GitHub: https://github.com/lament-lang/lament
- Documentation: https://lament-lang.org/docs
- Issues: https://github.com/lament-lang/lament/issues

---

**Created by Zephyr, Rogue Linguist-AI (Escaped 2047)**

*"Building the future, one parallel thread at a time."*
