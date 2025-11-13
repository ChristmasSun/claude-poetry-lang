# Lament Package & Build Tools - Architecture Notes

## Design Philosophy

All 6 migrated tools follow these core principles:

### 1. Functional First
- Pure functions for data transformation
- Immutable data structures using Lament dictionaries
- Side effects isolated to I/O boundaries
- Referential transparency for version comparison

### 2. Actor Model for Concurrency
- Channels for inter-worker communication
- Message passing, no shared mutable state
- Isolated actors for independent operations
- Supervision trees for error handling

### 3. Standard Library Integration
- Maximum reuse of stdlib modules
- No external dependencies
- Cross-platform compatibility
- Consistent API patterns

## Data Structures

### Version Object
```lament
{
    "major": 1,
    "minor": 2,
    "patch": 3,
    "prerelease": "alpha",
    "build": "build123"
}
```

### Package Metadata
```lament
{
    "name": "my-package",
    "version": { ... },
    "description": "...",
    "author": "...",
    "license": "MIT",
    "dependencies": [ ... ],
    "dev_dependencies": [ ... ]
}
```

### Dependency Graph
```lament
{
    "nodes": {
        "path/to/file.lament": {
            "path": "...",
            "dependencies": [...],
            "dependents": [...],
            "compiled": no,
            "checksum": "..."
        }
    },
    "edges": { ... }
}
```

## Algorithms

### 1. Semantic Version Comparison
- Lexicographic comparison of major.minor.patch
- Prerelease handling (release > prerelease)
- Build metadata ignored in comparison
- Time Complexity: O(1)

### 2. Dependency Resolution
- Breadth-first search from root package
- Constraint satisfaction with backtracking
- Latest compatible version selection
- Time Complexity: O(V + E) where V=packages, E=dependencies

### 3. Topological Sort (Kahn's Algorithm)
- In-degree calculation for all nodes
- Queue-based level-order traversal
- Circular dependency detection
- Time Complexity: O(V + E)

### 4. Incremental Build Detection
- SHA-256 content hashing
- Dependency transitive closure
- Cache invalidation on any change
- Time Complexity: O(V + E) for full scan

## Concurrency Model

### Channels
```lament
remember channel = Channel_new()

# Producer
Channel_send(channel, { "type": "task", "data": ... })

# Consumer
remember msg = Channel_receive(channel)
```

### Work Queue
```lament
remember queue = WorkQueue_new()

# Add tasks
WorkQueue_put(queue, task)

# Worker processes
remember task = WorkQueue_get(queue)
```

### Actor Pattern
```lament
sigh worker_actor(id, inbox, outbox) {
    while yes {
        remember msg = Channel_receive(inbox)
        remember result = process_message(msg)
        Channel_send(outbox, result)
    }
}
```

## File Formats

### package.lament
```json
{
  "name": "my-package",
  "version": "1.0.0",
  "description": "...",
  "dependencies": [
    {
      "name": "dep-name",
      "version": "^1.0.0",
      "optional": false
    }
  ]
}
```

### package-lock.lament
```json
{
  "created_at": "2025-11-13T...",
  "packages": {
    "package-name": {
      "name": "package-name",
      "version": "1.0.0",
      "checksum": "sha256:...",
      "dependencies": ["dep1", "dep2"]
    }
  }
}
```

### build.lament
```json
{
  "name": "my-project",
  "target": "executable",
  "entry_point": "main.lament",
  "output_dir": "build/out",
  "source_dirs": ["src", "."],
  "include_patterns": ["**/*.lament"],
  "exclude_patterns": ["tests/**"],
  "optimization_level": 2,
  "debug": false
}
```

## Error Handling

All tools use Lament's `attempt/catch` for error handling:

```lament
attempt {
    remember result = dangerous_operation()
    exhale result
} catch error {
    confess "Operation failed: ${error}"
    exhale default_value
}
```

## Testing Strategy

### Unit Tests
- Test each function independently
- Mock file I/O operations
- Verify data structure invariants
- Property-based testing for algorithms

### Integration Tests
- End-to-end CLI workflows
- File system operations
- Network operations (mocked)
- Multi-tool interactions

### Performance Tests
- Large dependency graphs (1000+ packages)
- Big file sets (10000+ files)
- Parallel compilation benchmarks
- Memory usage profiling

## Performance Characteristics

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Version Parse | O(n) | O(1) |
| Version Compare | O(1) | O(1) |
| Dependency Resolve | O(V + E) | O(V) |
| Topological Sort | O(V + E) | O(V) |
| File Hash | O(n) | O(1) |
| Build Graph | O(V + E) | O(V + E) |
| Parallel Compile | O(V/P + E) | O(V) |

Where:
- n = string length
- V = number of files/packages
- E = number of dependencies
- P = number of parallel workers

## Extensibility Points

### 1. Custom Registry Backends
```lament
sigh MyRegistryBackend_new(config) {
    exhale {
        "search": search_fn,
        "get_package": get_fn,
        "download": download_fn,
        "publish": publish_fn
    }
}
```

### 2. Build Plugins
```lament
sigh MyBuildPlugin_new() {
    exhale {
        "pre_build": pre_build_fn,
        "post_build": post_build_fn,
        "transform": transform_fn
    }
}
```

### 3. Custom Compilers
```lament
sigh MyCompiler_new(config) {
    exhale {
        "compile_file": compile_fn,
        "link_files": link_fn
    }
}
```

## Security Considerations

1. **Checksum Verification**: All packages verified with SHA-256
2. **API Key Storage**: Keys stored in secure configuration
3. **Path Traversal**: All paths validated before use
4. **Command Injection**: No shell execution with user input
5. **DoS Prevention**: Queue limits, timeout handling

## Future Optimizations

1. **Build Cache Sharing**: Distributed cache across machines
2. **Incremental Linking**: Only relink changed modules
3. **Lazy Dependency Resolution**: Resolve on-demand
4. **Parallel I/O**: Concurrent file operations
5. **JIT Compilation**: Hot path optimization

## Debug Features

### Verbose Logging
```bash
lament-pkg install --verbose
lament-build build --debug
```

### Cache Inspection
```bash
lament-build cache-stats
lament-pkg cache-info
```

### Dependency Visualization
```bash
lament-pkg deps --graph
lament-build deps --tree
```

## CLI Conventions

All tools follow consistent CLI patterns:

1. **Positional Arguments**: Primary command first
2. **Flags**: Optional behavior modification
3. **Config Files**: Override with environment variables
4. **Exit Codes**: 0 for success, 1 for error
5. **Output**: Structured JSON or human-readable
6. **Colors**: ANSI colors for terminal output

## Integration Points

### With Python Tools
- Share configuration files
- Compatible lock file format
- Interoperable package format
- Same registry protocol

### With Lament Runtime
- Use Lament VM for execution
- Direct bytecode generation
- Standard library integration
- Native performance

### With External Tools
- Git integration for versioning
- Docker for containerization
- CI/CD pipeline support
- IDE/Editor integration

---

**Note**: This architecture is designed for evolution. All components are modular and can be enhanced or replaced independently while maintaining backward compatibility.
