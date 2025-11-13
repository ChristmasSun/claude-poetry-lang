# Lament Package Management System

A comprehensive package management infrastructure for the Lament programming language, inspired by modern package managers like npm, cargo, and poetry.

## Overview

The Lament package management system consists of three main components:

1. **Package Manager** (`lament-pkg`) - Install, uninstall, and manage dependencies
2. **Package Registry** (`lament-registry`) - Search, publish, and discover packages
3. **Build System** (`lament-build`) - Compile, link, and create executables

## Features

### Package Manager Features
- ✓ Dependency resolution with topological sorting
- ✓ Semantic versioning (SemVer) support
- ✓ Lock files for reproducible builds
- ✓ Dev dependencies
- ✓ Optional dependencies
- ✓ Version constraint resolution (^, ~, >=, etc.)
- ✓ Package cache management
- ✓ Incremental installations

### Registry Features
- ✓ Local and remote registry support
- ✓ Package search with keyword matching
- ✓ Multi-registry configuration
- ✓ Package publishing and unpublishing
- ✓ Version management
- ✓ Checksum verification
- ✓ API key authentication
- ✓ Priority-based registry resolution

### Build System Features
- ✓ Incremental compilation
- ✓ Dependency analysis
- ✓ Build caching
- ✓ Multiple target types (executable, library, module)
- ✓ Optimization levels
- ✓ Debug mode
- ✓ Custom build flags
- ✓ Clean builds
- ✓ Build and run capability

## Installation

Add the tools directory to your PATH:

```bash
export PATH="$PATH:/home/user/claude-poetry-lang/tools"
```

Or create symlinks to a directory in your PATH:

```bash
ln -s /home/user/claude-poetry-lang/tools/lament-pkg /usr/local/bin/
ln -s /home/user/claude-poetry-lang/tools/lament-registry /usr/local/bin/
ln -s /home/user/claude-poetry-lang/tools/lament-build /usr/local/bin/
```

## Quick Start

### 1. Initialize a New Package

```bash
# Create a new package
lament-pkg init my-package

# This creates package.lament:
{
  "name": "my-package",
  "version": "0.1.0",
  "dependencies": []
}
```

### 2. Add Dependencies

```bash
# Add a dependency
lament-pkg install emotion-core@^2.0.0

# Add a dev dependency
lament-pkg install --dev test-framework

# Install all dependencies from package.lament
lament-pkg install
```

### 3. Build Your Project

```bash
# Build the project
lament-build build

# Build with clean (force rebuild)
lament-build build --clean

# Build and run
lament-build run
```

### 4. Publish Your Package

```bash
# Publish to local registry
lament-registry publish .

# Search for packages
lament-registry search emotion

# Get package info
lament-registry info emotion-core 2.0.0
```

## Package Manager (`lament-pkg`)

### Commands

#### `init <name>`
Initialize a new package.

```bash
lament-pkg init my-awesome-package
lament-pkg init my-awesome-package --version 1.0.0
```

#### `install [package]`
Install dependencies.

```bash
# Install all dependencies from package.lament
lament-pkg install

# Install specific package
lament-pkg install requests@^2.0.0

# Install dev dependency
lament-pkg install --dev pytest@~3.0.0
```

#### `uninstall <package>`
Uninstall a package.

```bash
lament-pkg uninstall requests
```

#### `update [package]`
Update packages to latest compatible versions.

```bash
# Update all packages
lament-pkg update

# Update specific package
lament-pkg update requests
```

#### `list`
List installed packages.

```bash
lament-pkg list
```

#### `clean`
Clean package cache.

```bash
lament-pkg clean
```

### Version Constraints

- `1.2.3` or `=1.2.3` - Exact version
- `^1.2.3` - Compatible with 1.2.3 (allows 1.x.x)
- `~1.2.3` - Approximately 1.2.3 (allows 1.2.x)
- `>=1.2.3` - Greater than or equal to 1.2.3
- `>1.2.3` - Greater than 1.2.3
- `<=1.2.3` - Less than or equal to 1.2.3
- `<1.2.3` - Less than 1.2.3

### File Structure

```
my-package/
├── package.lament           # Package metadata
├── package-lock.lament      # Lock file (generated)
├── .lament/
│   ├── packages/           # Installed packages
│   └── cache/              # Download cache
└── src/
    └── main.lament
```

## Package Registry (`lament-registry`)

### Commands

#### `search <query>`
Search for packages.

```bash
lament-registry search neural
lament-registry search emotion
```

#### `info <name> [version]`
Get package information.

```bash
# Get all versions
lament-registry info emotion-core

# Get specific version
lament-registry info emotion-core 2.0.0
```

#### `publish <path>`
Publish a package.

```bash
# Publish to local registry
lament-registry publish .

# Publish to specific registry
lament-registry publish . --registry official
```

#### `unpublish <name> <version>`
Unpublish a package.

```bash
lament-registry unpublish my-package 1.0.0
lament-registry unpublish my-package 1.0.0 --registry local
```

#### `add-registry <name> <url>`
Add a new registry.

```bash
lament-registry add-registry my-registry https://registry.example.com
lament-registry add-registry secure-reg https://secure.example.com --api-key YOUR_KEY
```

#### `remove-registry <name>`
Remove a registry.

```bash
lament-registry remove-registry my-registry
```

#### `list-registries`
List all configured registries.

```bash
lament-registry list-registries
```

### Registry Configuration

Registries are configured in `~/.lament/registries.json`:

```json
{
  "registries": [
    {
      "name": "official",
      "url": "https://registry.lament-lang.org",
      "priority": 100,
      "enabled": true
    },
    {
      "name": "local",
      "url": "file://~/.lament/local-registry",
      "priority": 50,
      "enabled": true
    }
  ]
}
```

## Build System (`lament-build`)

### Commands

#### `build`
Build the project.

```bash
# Incremental build
lament-build build

# Clean build (rebuild all)
lament-build build --clean

# Full rebuild (no incremental)
lament-build build --no-incremental
```

#### `run`
Build and run the project.

```bash
lament-build run
```

#### `clean`
Clean build artifacts.

```bash
lament-build clean
```

### Build Configuration

Create `build.lament` in your project:

```json
{
  "name": "my-project",
  "target": "executable",
  "entry_point": "src/main.lament",
  "output_dir": "build/out",
  "source_dirs": ["src", "lib"],
  "include_patterns": ["**/*.lament"],
  "exclude_patterns": ["tests/**"],
  "optimization_level": 2,
  "debug": false,
  "warnings_as_errors": true
}
```

### Target Types

- **executable**: Standalone executable program
- **library**: Reusable library
- **module**: Single module

### Optimization Levels

- `0`: No optimization (fastest compile, slowest runtime)
- `1`: Basic optimization
- `2`: Full optimization (recommended)
- `3`: Aggressive optimization (slowest compile, fastest runtime)

### Build Process

1. **Discovery**: Find all source files matching patterns
2. **Analysis**: Analyze dependencies between files
3. **Compilation**: Compile changed files to bytecode
4. **Caching**: Update build cache
5. **Linking**: Link modules into executable

## Package Format

### `package.lament`

```json
{
  "name": "emotion-tracker",
  "version": "1.0.0",
  "description": "Track emotional states over time",
  "author": "Your Name <you@example.com>",
  "license": "MIT",
  "homepage": "https://example.com",
  "repository": "https://github.com/user/emotion-tracker",
  "keywords": ["emotion", "tracking"],
  "entry_point": "src/main.lament",
  "dependencies": [
    {
      "name": "emotion-core",
      "version": "^2.0.0",
      "optional": false
    }
  ],
  "dev_dependencies": [
    {
      "name": "test-framework",
      "version": "^3.0.0",
      "optional": false
    }
  ],
  "include": ["src/**/*.lament", "README.md", "LICENSE"],
  "exclude": ["tests/**", "build/**"]
}
```

## Architecture

### Package Manager Architecture

```
PackageManager
├── DependencyResolver
│   ├── Version comparison
│   ├── Constraint satisfaction
│   └── Topological sorting
├── Registry (client)
│   └── Multi-registry support
├── LockFile
│   ├── Exact versions
│   └── Checksums
└── Cache
    └── Downloaded packages
```

### Registry Architecture

```
Registry
├── RegistryConfigManager
│   └── Multiple registry configs
├── Backends
│   ├── LocalRegistryBackend
│   │   ├── Filesystem storage
│   │   └── Index management
│   └── RemoteRegistryBackend
│       ├── HTTP requests
│       └── Authentication
└── Package metadata
    ├── Search index
    └── Version history
```

### Build System Architecture

```
BuildSystem
├── BuildConfig
│   ├── Target type
│   └── Build settings
├── SourceDiscovery
│   ├── Pattern matching
│   └── File exclusion
├── DependencyAnalyzer
│   └── Import resolution
├── BuildCache
│   ├── File checksums
│   └── Incremental tracking
├── LamentCompiler
│   ├── Lexer → Tokens
│   ├── Parser → AST
│   └── Compiler → Bytecode
└── Linker
    ├── Module combining
    └── Executable generation
```

## Code Statistics

### Package Manager (`package_manager.py`)
- **Lines**: ~680
- **Classes**: 10
- **Functions**: ~40
- **Features**:
  - Semantic versioning
  - Dependency resolution
  - Lock file management
  - CLI interface

### Registry (`registry.py`)
- **Lines**: ~580
- **Classes**: 8
- **Functions**: ~35
- **Features**:
  - Local/remote registries
  - Package search
  - Publishing
  - Authentication

### Build System (`builder.py`)
- **Lines**: ~540
- **Classes**: 9
- **Functions**: ~30
- **Features**:
  - Incremental builds
  - Dependency analysis
  - Compilation
  - Linking

**Total**: ~1800 lines of production code

## Examples

See `examples/sample-package/` for a complete example package with:
- `package.lament` - Package metadata
- `build.lament` - Build configuration
- `src/main.lament` - Source code
- `README.md` - Documentation

## Testing

```bash
# Initialize test package
cd /tmp
lament-pkg init test-package

# Add dependencies
lament-pkg install emotion-core@^1.0.0

# Create source file
mkdir -p src
cat > src/main.lament << 'EOF'
confess "Hello from Lament!"
EOF

# Build
lament-build build

# Run
lament-build run
```

## Troubleshooting

### "Package not found"
- Check registry configuration: `lament-registry list-registries`
- Verify package name: `lament-registry search <name>`

### "Dependency resolution failed"
- Check version constraints in `package.lament`
- Try updating to latest versions: `lament-pkg update`

### "Build failed"
- Clean and rebuild: `lament-build clean && lament-build build`
- Check source file syntax
- Verify dependencies are installed: `lament-pkg list`

### "Permission denied"
- Make sure CLI scripts are executable: `chmod +x tools/lament-*`
- Check file permissions in `.lament/` directory

## Future Enhancements

- [ ] Parallel compilation
- [ ] Watch mode for auto-rebuild
- [ ] Package testing framework integration
- [ ] Documentation generation
- [ ] Package templates
- [ ] Workspace support (monorepos)
- [ ] Git integration for versioning
- [ ] Package signing and verification
- [ ] Binary package distribution
- [ ] Cross-compilation support

## Contributing

Contributions welcome! Areas for improvement:
- Remote registry server implementation
- Better error messages
- Progress bars for downloads
- Package validation
- Security scanning
- Performance optimization

## License

MIT License - Part of the Lament programming language project.

## Credits

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)

Part of the Lament programming language - a language that feels alive.
