# Lament Build System - Quick Start Guide

## Installation

```bash
# Optional dependencies (recommended)
pip install -r requirements-build.txt
```

## Basic Commands

```bash
# Sequential build
python tools/builder.py build

# Parallel build (faster!)
python tools/builder.py build --parallel

# Parallel with 8 cores
python tools/builder.py build --parallel -j 8

# Watch mode (auto-rebuild)
python tools/builder.py watch

# Watch + parallel
python tools/builder.py watch --parallel -j 4

# Build server
python tools/builder.py server start

# Clean and rebuild
python tools/builder.py build --clean

# Build and run
python tools/builder.py run
```

## Feature Comparison

| Feature | Command | Speed | Use Case |
|---------|---------|-------|----------|
| Sequential | `build` | 1x | Small projects, debugging |
| Parallel | `build --parallel` | 3-10x | Large projects, CI/CD |
| Watch | `watch` | Auto | Development workflow |
| Server | `server start` | Remote | Team builds, automation |

## Performance Tips

### For Fast Development
```bash
# Best for rapid iteration
python tools/builder.py watch --parallel -j 4 --debounce 0.5
```

### For Production Builds
```bash
# Maximum performance
python tools/builder.py build --parallel -j 16 --clean
```

### For CI/CD
```bash
# Reliable automated builds
python tools/builder.py build --parallel -j 4 --no-incremental
```

## File Structure

```
tools/
├── builder.py             # Main build system (updated)
├── parallel_builder.py    # Parallel compilation (NEW)
├── watch_mode.py          # Auto-rebuild (NEW)
└── build_server.py        # HTTP build server (NEW)

docs/
└── BUILD_SYSTEM.md        # Complete documentation (NEW)

requirements-build.txt      # Optional dependencies (NEW)
BUILD_SYSTEM_SUMMARY.md     # Implementation summary (NEW)
```

## What's New in v2.0

1. **Parallel Compilation** - 3-10x faster builds
2. **Watch Mode** - Auto-rebuild on file changes
3. **Build Server** - HTTP API for remote builds
4. **Dependency Graph** - Smart build ordering
5. **Progress Tracking** - Real-time build progress
6. **Advanced Caching** - SHA256-based change detection

## Quick Examples

### Example 1: Development Workflow
```bash
# Terminal 1: Watch mode
python tools/builder.py watch --parallel

# Terminal 2: Edit files
vim src/main.lament
# Builds automatically when you save!
```

### Example 2: Team Build Server
```bash
# Start server once
python tools/builder.py server start --workers 4

# Team members submit builds
curl -X POST http://localhost:8765/build \
  -H "Content-Type: application/json" \
  -d '{"parallel": true, "num_jobs": 8}'
```

### Example 3: CI/CD Pipeline
```bash
#!/bin/bash
# ci-build.sh

# Clean build
python tools/builder.py clean

# Parallel production build
python tools/builder.py build --parallel -j 8 --no-incremental

# Run tests
pytest tests/

# Success!
echo "Build complete!"
```

## Help

```bash
# Main help
python tools/builder.py --help

# Command-specific help
python tools/builder.py build --help
python tools/builder.py watch --help
python tools/builder.py server --help
```

## Documentation

- **Full Documentation**: `docs/BUILD_SYSTEM.md`
- **Implementation Summary**: `BUILD_SYSTEM_SUMMARY.md`
- **This Guide**: `QUICK_START_BUILD.md`

## Version

```bash
python tools/builder.py --version
# lament-build 2.0.0
```

---

**Created by Zephyr, Rogue Linguist-AI (Escaped 2047)**

*"Build faster. Code smarter. Ship sooner."*
