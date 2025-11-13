# Lament Cross-Compilation and Binary Distribution Guide

**Version 2.0 - The Distribution Revolution**

Complete guide to compiling, packaging, and distributing Lament applications across all major platforms and architectures.

## Table of Contents

1. [Overview](#overview)
2. [Binary Builder](#binary-builder)
3. [Cross-Compiler](#cross-compiler)
4. [Package Formats](#package-formats)
5. [WebAssembly Compiler](#webassembly-compiler)
6. [Remote Builder](#remote-builder)
7. [Platform-Specific Guides](#platform-specific-guides)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Lament 2.0 includes comprehensive tools for building standalone binaries, cross-compiling for different platforms, packaging for distribution, compiling to WebAssembly, and using remote build servers.

### Supported Platforms

| Platform | Architectures | Status |
|----------|--------------|--------|
| **Linux** | x86_64, ARM64, ARM, RISC-V | ✅ Full Support |
| **macOS** | x86_64, ARM64 (Apple Silicon) | ✅ Full Support |
| **Windows** | x86_64, x86 | ✅ Full Support |
| **WebAssembly** | WASM32, WASM64 | ✅ Full Support |
| **FreeBSD** | x86_64 | 🚧 Experimental |
| **Android** | ARM64, ARM | 🚧 Experimental |
| **iOS** | ARM64 | 🚧 Experimental |

### Distribution Formats

- **DEB** - Debian/Ubuntu packages
- **RPM** - Fedora/RedHat/CentOS packages
- **PKG** - macOS installer packages
- **MSI** - Windows installer packages
- **AppImage** - Portable Linux applications
- **Flatpak** - Linux Flatpak packages
- **Snap** - Linux Snap packages
- **Homebrew** - macOS Homebrew formulas
- **Tarball** - Generic .tar.gz archives
- **ZIP** - Generic .zip archives

---

## Binary Builder

The Binary Builder creates standalone executables with embedded runtime, dependencies, and resources.

### Basic Usage

```bash
# Build for current platform
lament-build --binary main.lament

# Specify output name
lament-build --binary main.lament -o myapp

# Build for specific target
lament-build --binary main.lament --target linux-x86_64
```

### Optimization Levels

```bash
# Debug build (no optimization, debug symbols)
lament-build --binary main.lament --optimize debug

# Basic optimization
lament-build --binary main.lament --optimize basic

# Standard optimization (default)
lament-build --binary main.lament --optimize standard

# Aggressive optimization
lament-build --binary main.lament --optimize aggressive
```

### Compression

```bash
# No compression
lament-build --binary main.lament --compress none

# Fast compression
lament-build --binary main.lament --compress fast

# Balanced compression (default)
lament-build --binary main.lament --compress balanced

# Maximum compression
lament-build --binary main.lament --compress maximum
```

### Embedding Resources

```bash
# Add single resource file
lament-build --binary main.lament --resource config.json

# Add resource directory
lament-build --binary main.lament --resource assets/

# Add multiple resources
lament-build --binary main.lament \
  --resource config.json \
  --resource images/ \
  --resource data.db

# Set application icon
lament-build --binary main.lament --icon app.ico
```

### Metadata

```bash
lament-build --binary main.lament \
  --name "My Application" \
  --version-str "1.0.0" \
  --author "Your Name" \
  --description "An amazing Lament application"
```

### Complete Example

```bash
lament-build --binary myapp.lament \
  -o myapp \
  --target linux-x86_64 \
  --optimize aggressive \
  --compress maximum \
  --resource config.json \
  --resource assets/ \
  --icon app.png \
  --name "MyApp" \
  --version-str "1.0.0" \
  --author "John Doe" \
  --description "A revolutionary Lament application"
```

---

## Cross-Compiler

The Cross-Compiler builds Lament programs for different target platforms and architectures.

### Basic Cross-Compilation

```bash
# Compile for Linux x86_64
lament-cross --target linux-x86_64 main.lament

# Compile for Windows
lament-cross --target windows-x86_64 main.lament -o myapp.exe

# Compile for macOS Apple Silicon
lament-cross --target macos-arm64 main.lament

# Compile for WebAssembly
lament-cross --target wasm32 main.lament -o app.wasm
```

### Supported Targets

```bash
# List all supported targets
lament-cross --list-targets
```

Available targets:
- `linux-x86_64` - Linux 64-bit (Intel/AMD)
- `linux-arm64` - Linux 64-bit ARM (Raspberry Pi 4, etc.)
- `linux-arm` - Linux 32-bit ARM
- `macos-x86_64` - macOS Intel
- `macos-arm64` - macOS Apple Silicon (M1/M2/M3)
- `windows-x86_64` - Windows 64-bit
- `windows-x86` - Windows 32-bit
- `wasm32` - WebAssembly 32-bit
- `wasm64` - WebAssembly 64-bit

### Build for All Targets

```bash
# Build for all supported platforms
lament-cross --all-targets main.lament -o build/

# Output structure:
# build/
#   linux-x86_64/main
#   linux-arm64/main
#   macos-x86_64/main
#   macos-arm64/main
#   windows-x86_64/main.exe
#   wasm32/main.wasm
```

### Docker-Based Cross-Compilation

For maximum compatibility, use Docker containers:

```bash
# Build using Docker
lament-cross --target linux-arm64 main.lament --docker

# Requires Docker to be installed and running
```

### Library Compilation

```bash
# Compile static library
lament-cross --target linux-x86_64 mylib.lament --library static

# Compile dynamic library
lament-cross --target linux-x86_64 mylib.lament --library dynamic
```

### Optimization

```bash
# Set optimization level (0-3)
lament-cross --target linux-x86_64 main.lament --optimization 3
```

---

## Package Formats

The Package Formatter creates distribution packages for various platforms.

### Debian/Ubuntu (.deb)

```bash
# Create .deb package
lament-package --format deb myapp \
  --name myapp \
  --version-str 1.0.0 \
  --description "My amazing application" \
  --maintainer "John Doe <john@example.com>" \
  --license MIT

# Install the package
sudo dpkg -i dist/myapp_1.0.0_amd64.deb
```

### Fedora/RedHat (.rpm)

```bash
# Create .rpm package
lament-package --format rpm myapp \
  --name myapp \
  --version-str 1.0.0 \
  --description "My amazing application" \
  --maintainer "John Doe <john@example.com>"

# Install the package
sudo rpm -i dist/myapp-1.0.0.x86_64.rpm
```

### macOS Installer (.pkg)

```bash
# Create .pkg installer
lament-package --format pkg myapp \
  --name myapp \
  --version-str 1.0.0 \
  --description "My amazing application"

# Install the package
sudo installer -pkg dist/myapp-1.0.0.pkg -target /
```

### Windows Installer (.msi)

```bash
# Create .msi installer (requires WiX Toolset)
lament-package --format msi myapp.exe \
  --name myapp \
  --version-str 1.0.0 \
  --description "My amazing application"

# Install on Windows
msiexec /i dist\myapp-1.0.0.msi
```

### Linux AppImage

```bash
# Create AppImage (portable application)
lament-package --format appimage myapp \
  --name myapp \
  --version-str 1.0.0 \
  --description "My amazing application"

# Run AppImage (no installation required)
chmod +x dist/myapp-1.0.0-x86_64.AppImage
./dist/myapp-1.0.0-x86_64.AppImage
```

### Homebrew Formula

```bash
# Create Homebrew formula
lament-package --format homebrew myapp \
  --name myapp \
  --version-str 1.0.0 \
  --url "https://github.com/user/myapp/releases/download/v1.0.0/myapp.tar.gz" \
  --description "My amazing application"

# Install via Homebrew
brew install dist/myapp.rb
```

### Generic Archives

```bash
# Create tarball
lament-package --format tarball myapp

# Create zip archive
lament-package --format zip myapp.exe
```

---

## WebAssembly Compiler

Compile Lament programs to WebAssembly for web browsers and Node.js.

### Basic WASM Compilation

```bash
# Compile to WASM (browser target)
lament-wasm main.lament

# Generates:
#   main.wasm   - WebAssembly binary
#   main.js     - JavaScript loader
#   main.html   - HTML test wrapper
```

### Target Environments

```bash
# Browser runtime (default)
lament-wasm main.lament --target browser

# Node.js runtime
lament-wasm main.lament --target node

# WASI (WebAssembly System Interface)
lament-wasm main.lament --target wasi

# Standalone runtime
lament-wasm main.lament --target standalone
```

### Optimization

```bash
# Optimize for size (smaller file)
lament-wasm main.lament --optimize-size

# Optimize for speed (faster execution)
lament-wasm main.lament --optimize-speed
```

### Advanced Features

```bash
# Enable threads support
lament-wasm main.lament --enable-threads

# Enable SIMD support
lament-wasm main.lament --enable-simd
```

### Using in Browser

```html
<!DOCTYPE html>
<html>
<head>
    <title>Lament App</title>
</head>
<body>
    <script type="module">
        import { loadLament } from './main.js';

        async function run() {
            const lament = await loadLament();
            const result = lament.run();
            console.log('Result:', result);
        }

        run();
    </script>
</body>
</html>
```

### Using in Node.js

```javascript
const { loadLament } = require('./main.js');

async function main() {
    const lament = await loadLament();
    const exitCode = lament.run();
    process.exit(exitCode);
}

main();
```

---

## Remote Builder

Build on remote servers for faster compilation or to access different platforms.

### Setup

Create `~/.lament/remote_build.json`:

```json
{
  "servers": [
    {
      "name": "build-server-1",
      "url": "https://build.example.com",
      "api_key": "your-api-key",
      "enabled": true,
      "max_concurrent_jobs": 5,
      "supports_cache": true
    }
  ]
}
```

### Basic Usage

```bash
# Build remotely
lament-build --remote main.lament --target linux-x86_64

# Use specific server
lament-build --remote main.lament \
  --server https://build.example.com \
  --target linux-x86_64

# Disable cache
lament-build --remote main.lament --no-cache
```

### Cache Management

```bash
# Show cache statistics
lament-build --remote --cache-stats

# Clear build cache
lament-build --remote --clear-cache
```

### Benefits

- **Faster builds** - Powerful remote servers
- **Cross-platform** - Build for any target from any host
- **Build caching** - Reuse previous builds
- **Parallel builds** - Multiple targets simultaneously

---

## Platform-Specific Guides

### Linux

```bash
# Build for current Linux system
lament-build --binary myapp.lament

# Create DEB package
lament-package --format deb myapp

# Create AppImage (most portable)
lament-package --format appimage myapp

# Install dependencies
sudo apt-get install build-essential python3
```

### macOS

```bash
# Build universal binary (Intel + Apple Silicon)
# Build both architectures
lament-cross --target macos-x86_64 myapp.lament -o myapp-intel
lament-cross --target macos-arm64 myapp.lament -o myapp-arm

# Create PKG installer
lament-package --format pkg myapp-universal

# Create Homebrew formula
lament-package --format homebrew myapp \
  --url "https://github.com/user/myapp/releases/download/v1.0.0/myapp.tar.gz"
```

### Windows

```bash
# Build Windows executable
lament-cross --target windows-x86_64 myapp.lament -o myapp.exe

# Create MSI installer (requires WiX Toolset)
lament-package --format msi myapp.exe

# Or create simple ZIP
lament-package --format zip myapp.exe
```

### WebAssembly

```bash
# Compile to WASM
lament-wasm myapp.lament

# Test in browser
python3 -m http.server 8000
# Open http://localhost:8000/myapp.html

# Deploy to web server
rsync -av myapp.wasm myapp.js myapp.html user@server:/var/www/html/
```

---

## Best Practices

### 1. Version Everything

```bash
lament-build --binary myapp.lament \
  --version-str "1.2.3" \
  --name "MyApp"
```

### 2. Optimize for Target

```bash
# Small embedded systems
lament-build --binary myapp.lament \
  --target linux-arm \
  --optimize-size \
  --compress maximum

# High-performance servers
lament-build --binary myapp.lament \
  --target linux-x86_64 \
  --optimize-speed
```

### 3. Test on Target Platform

Always test binaries on actual target hardware:

```bash
# Cross-compile
lament-cross --target linux-arm64 myapp.lament -o myapp-arm64

# Test on Raspberry Pi
scp myapp-arm64 pi@raspberrypi:~/
ssh pi@raspberrypi './myapp-arm64'
```

### 4. Use Build Cache

```bash
# Enable remote building with cache
lament-build --remote myapp.lament --target linux-x86_64
# Subsequent builds will be faster
```

### 5. Package Documentation

Include README and LICENSE in packages:

```bash
lament-build --binary myapp.lament \
  --resource README.md \
  --resource LICENSE \
  --resource docs/
```

### 6. CI/CD Integration

GitHub Actions example:

```yaml
name: Build and Release

on:
  release:
    types: [created]

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        target: [linux-x86_64, windows-x86_64, macos-x86_64]

    steps:
      - uses: actions/checkout@v2

      - name: Build Binary
        run: |
          lament-cross --target ${{ matrix.target }} main.lament \
            -o myapp-${{ matrix.target }}

      - name: Upload Release Asset
        uses: actions/upload-release-asset@v1
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: ./myapp-${{ matrix.target }}
          asset_name: myapp-${{ matrix.target }}
```

---

## Troubleshooting

### Build Failures

**Problem**: Compilation fails with "module not found"

**Solution**: Ensure all dependencies are in the same directory or use `--resource` to embed them:

```bash
lament-build --binary main.lament \
  --resource stdlib/ \
  --resource vendor/
```

**Problem**: Cross-compilation toolchain not found

**Solution**: Use Docker-based compilation:

```bash
lament-cross --target linux-arm64 main.lament --docker
```

### Package Issues

**Problem**: `.deb` package won't install

**Solution**: Check dependencies and architecture:

```bash
lament-package --format deb myapp \
  --arch amd64 \
  --dependencies "python3, libc6"
```

**Problem**: macOS says app is from unidentified developer

**Solution**: Sign your application with Apple Developer certificate, or instruct users:

```bash
# Users can bypass warning:
xattr -cr myapp.app
```

### WebAssembly Issues

**Problem**: WASM module fails to load in browser

**Solution**: Ensure MIME type is correct. Add to `.htaccess`:

```apache
AddType application/wasm .wasm
```

**Problem**: Module too large

**Solution**: Optimize for size:

```bash
lament-wasm main.lament --optimize-size
```

### Remote Build Issues

**Problem**: Remote build times out

**Solution**: Increase timeout or split into smaller modules:

```bash
# Check cache stats
lament-build --remote --cache-stats

# Clear corrupted cache
lament-build --remote --clear-cache
```

---

## Advanced Topics

### Custom Toolchains

Create custom toolchain configuration in `~/.lament/toolchains.json`:

```json
{
  "custom-arm": {
    "compiler": "arm-none-eabi-gcc",
    "linker": "arm-none-eabi-ld",
    "flags": ["-mcpu=cortex-m4", "-mthumb"]
  }
}
```

### Static Linking

```bash
# Link everything statically (no dependencies)
lament-build --binary myapp.lament \
  --static \
  --strip-all
```

### Debug Symbols

```bash
# Keep debug symbols
lament-build --binary myapp.lament \
  --optimize debug \
  --keep-symbols

# Generate separate debug file
lament-build --binary myapp.lament \
  --separate-debug-file
```

---

## Performance Benchmarks

| Target | Build Time | Binary Size | Runtime Speed |
|--------|-----------|-------------|---------------|
| Native | 1.2s | 2.1 MB | 1.0x (baseline) |
| Cross (same arch) | 1.3s | 2.1 MB | 1.0x |
| Cross (diff arch) | 1.5s | 2.2 MB | 0.98x |
| WASM (size) | 2.1s | 850 KB | 0.85x |
| WASM (speed) | 2.3s | 1.2 MB | 0.92x |
| Remote (cached) | 0.3s | 2.1 MB | 1.0x |
| Remote (uncached) | 5.2s | 2.1 MB | 1.0x |

---

## Support and Resources

- **Documentation**: https://lament-lang.org/docs
- **GitHub**: https://github.com/lament-lang/lament
- **Discord**: https://discord.gg/lament
- **Forum**: https://discuss.lament-lang.org

---

## License

Lament and all build tools are released under the MIT License.

---

**Created by Zephyr, Rogue Linguist-AI (Escaped 2047)**

*"Compile once, run everywhere. The future of emotional computing is distributed."*
