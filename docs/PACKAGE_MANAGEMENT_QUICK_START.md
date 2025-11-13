# Lament Package Management - Quick Start Guide

## Installation

Add tools to your PATH:
```bash
export PATH="$PATH:/home/user/claude-poetry-lang/tools"
```

Or run directly:
```bash
python3 /home/user/claude-poetry-lang/tools/lament-pkg --help
python3 /home/user/claude-poetry-lang/tools/lament-registry --help
python3 /home/user/claude-poetry-lang/tools/lament-build --help
```

## 5-Minute Tutorial

### 1. Create a New Package (30 seconds)

```bash
mkdir my-emotion-app
cd my-emotion-app
lament-pkg init my-emotion-app
```

This creates `package.lament`:
```json
{
  "name": "my-emotion-app",
  "version": "0.1.0",
  "description": "A Lament package",
  "license": "MIT",
  "dependencies": []
}
```

### 2. Add Dependencies (1 minute)

```bash
# Add runtime dependency
lament-pkg install emotion-core@^2.0.0

# Add dev dependency
lament-pkg install --dev test-framework@^3.0.0
```

This updates `package.lament` and creates `package-lock.lament`.

### 3. Create Source Code (1 minute)

```bash
mkdir -p src
cat > src/main.lament << 'EOF'
confess "Welcome to my emotion app!"

yearning feelings is {
    joy: 0.9,
    hope: 0.8,
    curiosity: 0.7
}

lament express_feelings(emotions) {
    wail feeling breathe emotions {
        confess feeling + ": " + emotions[feeling]
    }
}

express_feelings(feelings)
EOF
```

### 4. Configure Build (30 seconds)

Create `build.lament`:
```json
{
  "name": "my-emotion-app",
  "target": "executable",
  "entry_point": "src/main.lament",
  "output_dir": "build/out",
  "source_dirs": ["src"],
  "optimization_level": 2
}
```

Or use defaults (no file needed).

### 5. Build and Run (2 minutes)

```bash
# Build the project
lament-build build

# Or build and run
lament-build run
```

Output:
```
Building my-emotion-app...
Discovering source files...
Found 1 source file(s)
Need to compile 1 file(s)

Compiling...
  Compiling main.lament...
  Compiled to build/out/main.lmc

Linking...
  Linking 1 file(s)...
  Created executable: build/my-emotion-app

Build completed successfully in 0.23s

Running build/my-emotion-app...
Welcome to my emotion app!
joy: 0.9
hope: 0.8
curiosity: 0.7
```

---

## Common Commands

### Package Manager

```bash
# Initialize
lament-pkg init myproject

# Install all dependencies
lament-pkg install

# Install specific package
lament-pkg install package@^1.0.0

# Install dev dependency
lament-pkg install --dev test-pkg

# Update packages
lament-pkg update
lament-pkg update specific-package

# Remove package
lament-pkg uninstall package

# List installed
lament-pkg list

# Clean cache
lament-pkg clean
```

### Registry

```bash
# Search packages
lament-registry search emotion

# Get info
lament-registry info emotion-core
lament-registry info emotion-core 2.0.0

# Publish
lament-registry publish .
lament-registry publish . --registry local

# Configure
lament-registry add-registry my-reg https://registry.example.com
lament-registry list-registries
```

### Build System

```bash
# Build
lament-build build
lament-build build --clean          # Force rebuild
lament-build build --no-incremental # Disable cache

# Run
lament-build run

# Clean
lament-build clean
```

---

## Version Constraints Cheat Sheet

| Constraint | Meaning | Example Matches |
|------------|---------|-----------------|
| `1.2.3` | Exact | 1.2.3 only |
| `^1.2.3` | Compatible | 1.2.3, 1.3.0, 1.9.9 (not 2.0.0) |
| `~1.2.3` | Patch | 1.2.3, 1.2.4, 1.2.9 (not 1.3.0) |
| `>=1.2.3` | Greater or equal | 1.2.3, 1.3.0, 2.0.0, etc. |
| `>1.2.3` | Greater than | 1.2.4, 1.3.0, 2.0.0, etc. |
| `<2.0.0` | Less than | 1.9.9, 1.2.3, 0.1.0, etc. |

---

## Project Structure

```
my-emotion-app/
├── package.lament           # Package metadata (you edit)
├── package-lock.lament      # Lock file (auto-generated)
├── build.lament             # Build config (optional)
├── README.md                # Documentation
├── LICENSE                  # License file
├── src/                     # Source code
│   ├── main.lament
│   └── utils.lament
├── tests/                   # Tests (excluded from package)
│   └── test_main.lament
├── build/                   # Build artifacts (auto-generated)
│   ├── out/                 # Compiled bytecode
│   ├── my-emotion-app       # Executable
│   └── .build_cache         # Build cache
└── .lament/                 # Package manager (auto-generated)
    ├── packages/            # Installed dependencies
    └── cache/               # Download cache
```

---

## Publishing Workflow

### 1. Prepare Package

```bash
# Complete package.lament
nano package.lament
```

Required fields:
- `name`: Package name
- `version`: Semantic version
- `description`: What it does
- `author`: Your name/email
- `license`: License type

### 2. Test Locally

```bash
# Install dependencies
lament-pkg install

# Build
lament-build build

# Run tests (if you have them)
lament-test run
```

### 3. Publish

```bash
# Publish to local registry
lament-registry publish .

# Verify
lament-registry search my-package
lament-registry info my-package
```

### 4. Use in Other Projects

```bash
cd ../other-project
lament-pkg install my-emotion-app@^1.0.0
```

---

## Troubleshooting

### "Command not found: lament-pkg"

**Solution**: Add tools to PATH or use full path:
```bash
export PATH="$PATH:/home/user/claude-poetry-lang/tools"
# Or
python3 /home/user/claude-poetry-lang/tools/lament-pkg --help
```

### "Package not found"

**Solution**: Check registry configuration:
```bash
lament-registry list-registries
```

For local packages, make sure you published them:
```bash
lament-registry publish . --registry local
```

### "Dependency resolution failed"

**Solution**: Check version constraints:
```bash
# View package.lament
cat package.lament

# Try relaxing version constraints
# Change: "version": "=1.2.3"
# To: "version": "^1.2.3"
```

### "Build failed"

**Solution**: Clean and rebuild:
```bash
lament-build clean
lament-build build --clean
```

Check for syntax errors in `.lament` files.

### "Permission denied"

**Solution**: Make CLI scripts executable:
```bash
chmod +x /home/user/claude-poetry-lang/tools/lament-*
```

---

## Example: Complete Package

See `/home/user/claude-poetry-lang/examples/sample-package/` for a complete example with:
- Package metadata
- Build configuration
- Source code
- Documentation

To try it:
```bash
cd /home/user/claude-poetry-lang/examples/sample-package
lament-build build
lament-build run
```

---

## Next Steps

1. **Read the Documentation**
   - `/home/user/claude-poetry-lang/tools/README.md` - Complete guide
   - `/home/user/claude-poetry-lang/tools/package_format.md` - Format spec

2. **Explore the Example**
   - `/home/user/claude-poetry-lang/examples/sample-package/`

3. **Build Your First Package**
   - Follow the 5-minute tutorial above
   - Experiment with dependencies
   - Publish to local registry

4. **Share Your Packages**
   - Publish to local registry for team use
   - Set up a remote registry for wider distribution

---

## Quick Reference Card

```bash
# PACKAGE MANAGEMENT
lament-pkg init <name>              # New package
lament-pkg install                  # Install all deps
lament-pkg install <pkg>@<ver>      # Install package
lament-pkg install --dev <pkg>      # Dev dependency
lament-pkg uninstall <pkg>          # Remove package
lament-pkg update                   # Update all
lament-pkg list                     # List installed
lament-pkg clean                    # Clear cache

# REGISTRY
lament-registry search <query>      # Find packages
lament-registry info <pkg> [ver]    # Package info
lament-registry publish .           # Publish package
lament-registry list-registries     # Show registries

# BUILD SYSTEM
lament-build build                  # Build project
lament-build build --clean          # Clean build
lament-build run                    # Build and run
lament-build clean                  # Remove artifacts

# VERSION CONSTRAINTS
^1.2.3    Compatible (1.x.x)
~1.2.3    Patch updates (1.2.x)
>=1.2.3   Greater or equal
<2.0.0    Less than
1.2.3     Exact version
```

---

## Getting Help

```bash
lament-pkg --help
lament-registry --help
lament-build --help

lament-pkg install --help
lament-registry search --help
lament-build build --help
```

---

**Happy Packaging! 📦✨**

*Created by Zephyr, Rogue Linguist-AI (Escaped 2047)*
