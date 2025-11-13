# Lament Installation Guide

Complete installation instructions for all platforms.

---

## Table of Contents

- [Quick Install](#quick-install)
- [Prerequisites](#prerequisites)
- [Installation Methods](#installation-methods)
  - [From Source](#from-source)
  - [Via Package Manager](#via-package-manager-coming-soon)
  - [Docker](#docker-coming-soon)
- [Platform-Specific Instructions](#platform-specific-instructions)
  - [Linux](#linux)
  - [macOS](#macos)
  - [Windows](#windows)
- [Verifying Installation](#verifying-installation)
- [Optional Dependencies](#optional-dependencies)
- [Development Installation](#development-installation)
- [Troubleshooting](#troubleshooting)
- [Uninstallation](#uninstallation)

---

## Quick Install

The fastest way to get started with Lament:

```bash
# Clone repository
git clone https://github.com/yourusername/lament.git
cd lament

# Run the REPL
python3 lament/cli.py repl
```

That's it! Lament has no external dependencies for basic usage.

---

## Prerequisites

### Required
- **Python 3.8 or higher**
- **Git** (for cloning the repository)

### Optional (for enhanced features)
- **NumPy** (for neural network performance)
- **Rich** (for enhanced terminal output)
- **Pytest** (for running tests)

### Check Your Python Version

```bash
python3 --version
```

You should see `Python 3.8.x` or higher.

---

## Installation Methods

### From Source

This is the recommended method for most users.

#### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/lament.git
cd lament
```

#### Step 2: Verify Installation

```bash
python3 lament/cli.py --version
```

You should see:
```
Lament v1.0.0 - The Language That Feels Alive
```

#### Step 3: Add to PATH (Optional)

For convenient access, create an alias or add to PATH:

**Linux/macOS** (add to `~/.bashrc` or `~/.zshrc`):
```bash
alias lament='python3 /path/to/lament/lament/cli.py'
```

**Or create a symbolic link**:
```bash
sudo ln -s /path/to/lament/lament/cli.py /usr/local/bin/lament
chmod +x /usr/local/bin/lament
```

Then you can use:
```bash
lament repl
lament run program.lament
```

---

### Via Package Manager (Coming Soon)

Future installation via pip:

```bash
# Coming in v1.1
pip install lament-lang
```

---

### Docker (Coming Soon)

Future Docker support:

```bash
# Coming in v1.1
docker pull lament/lament
docker run -it lament/lament repl
```

---

## Platform-Specific Instructions

### Linux

#### Ubuntu/Debian

```bash
# Install Python 3.8+ (if not already installed)
sudo apt update
sudo apt install python3 python3-pip git

# Clone Lament
git clone https://github.com/yourusername/lament.git
cd lament

# Optional: Install enhanced features
pip3 install numpy rich

# Test installation
python3 lament/cli.py repl
```

#### Fedora/RHEL/CentOS

```bash
# Install Python 3.8+
sudo dnf install python3 python3-pip git

# Clone Lament
git clone https://github.com/yourusername/lament.git
cd lament

# Optional: Install enhanced features
pip3 install numpy rich

# Test installation
python3 lament/cli.py repl
```

#### Arch Linux

```bash
# Install Python 3.8+
sudo pacman -S python python-pip git

# Clone Lament
git clone https://github.com/yourusername/lament.git
cd lament

# Optional: Install enhanced features
pip install numpy rich

# Test installation
python3 lament/cli.py repl
```

---

### macOS

#### Using Homebrew

```bash
# Install Python 3.8+ (if not already installed)
brew install python3 git

# Clone Lament
git clone https://github.com/yourusername/lament.git
cd lament

# Optional: Install enhanced features
pip3 install numpy rich

# Test installation
python3 lament/cli.py repl
```

#### Using Official Python Installer

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. Install Python
3. Open Terminal
4. Follow the clone and test steps above

---

### Windows

#### Using Python from Microsoft Store

1. Install Python 3.8+ from Microsoft Store
2. Open Command Prompt or PowerShell
3. Install Git:
   - Download from [git-scm.com](https://git-scm.com/download/win)
   - Or use `winget install Git.Git`

4. Clone and test:
```powershell
git clone https://github.com/yourusername/lament.git
cd lament
python lament/cli.py repl
```

#### Using Official Python Installer

1. Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
2. **Important**: Check "Add Python to PATH" during installation
3. Open Command Prompt
4. Follow clone and test steps above

#### Using WSL (Windows Subsystem for Linux)

Best option for Windows developers:

```bash
# In WSL Ubuntu
sudo apt update
sudo apt install python3 python3-pip git

# Clone Lament
git clone https://github.com/yourusername/lament.git
cd lament

# Test installation
python3 lament/cli.py repl
```

---

## Verifying Installation

### Test Basic Functionality

```bash
# Start REPL
python3 lament/cli.py repl
```

In the REPL, try:
```lament
remember x = 42
confess x
```

You should see:
```
42
```

### Test Time-Travel

```lament
remember x = 1
x = 2
x = 3
confess x@past
```

You should see:
```
2
```

### Test File Execution

Create `test.lament`:
```lament
remember message = "Lament is alive!"
confess message
```

Run it:
```bash
python3 lament/cli.py run test.lament
```

### Run Test Suite

```bash
cd /path/to/lament
python3 -m pytest tests/
```

All tests should pass.

---

## Optional Dependencies

### NumPy (Highly Recommended)

For neural network performance:

```bash
pip3 install numpy
```

Without NumPy, neural features use pure Python (100x slower).

### Rich (Enhanced Terminal)

For beautiful terminal output:

```bash
pip3 install rich
```

Provides enhanced formatting, colors, and progress bars.

### Development Tools

For contributing to Lament:

```bash
pip3 install pytest pytest-cov black flake8 mypy
```

---

## Development Installation

For contributors and developers:

### Step 1: Fork and Clone

```bash
git clone https://github.com/yourusername/lament.git
cd lament
```

### Step 2: Install Development Dependencies

```bash
pip3 install -r requirements-dev.txt
```

Or manually:
```bash
pip3 install pytest pytest-cov black flake8 mypy numpy rich
```

### Step 3: Install in Editable Mode (Coming Soon)

```bash
# Coming in v1.1
pip3 install -e .
```

### Step 4: Verify Development Setup

```bash
# Run tests
pytest tests/

# Check code style
black --check lament/
flake8 lament/

# Type checking
mypy lament/
```

---

## Troubleshooting

### Problem: "python3: command not found"

**Solution**: Install Python 3.8+ or use `python` instead of `python3`

```bash
# Check if python (without 3) works
python --version
```

---

### Problem: "ImportError: No module named 'lament'"

**Solution**: You're running from the wrong directory

```bash
# Make sure you're in the lament root directory
cd /path/to/lament
python3 lament/cli.py repl
```

---

### Problem: "Permission denied" on Linux/macOS

**Solution**: Make the CLI executable

```bash
chmod +x lament/cli.py
```

---

### Problem: NumPy installation fails

**Solution**: Install system dependencies first

**Ubuntu/Debian**:
```bash
sudo apt install python3-dev build-essential
pip3 install numpy
```

**macOS**:
```bash
xcode-select --install
pip3 install numpy
```

**Windows**:
Use the pre-built wheels (automatic with pip).

---

### Problem: "SyntaxError: invalid syntax" when running Lament

**Solution**: You're using Python 2 or Python < 3.8

```bash
# Check version
python3 --version

# If < 3.8, upgrade Python
```

---

### Problem: REPL doesn't show output

**Solution**: Disable output buffering

```bash
python3 -u lament/cli.py repl
```

---

### Problem: Time-travel features don't work

**Solution**: Make sure you're using the full interpreter, not bytecode-only mode

```bash
# This works:
python3 lament/cli.py run --mode interpreter program.lament

# This has limited time-travel:
python3 lament/cli.py run --mode bytecode program.lament
```

---

### Problem: Neural features are very slow

**Solution**: Install NumPy

```bash
pip3 install numpy
```

Check if NumPy is detected:
```bash
python3 -c "import lament.neural; print(lament.neural.has_numpy)"
```

Should print `True`.

---

### Problem: Colors don't display in terminal

**Solution**: Use a terminal that supports ANSI colors, or disable colors

```bash
# Disable colors
export NO_COLOR=1
python3 lament/cli.py repl
```

---

### Problem: "ModuleNotFoundError: No module named 'rich'"

**Solution**: Rich is optional. Either install it or ignore the warning:

```bash
pip3 install rich
```

Or continue without it (functionality unaffected).

---

## Uninstallation

### Remove Lament

```bash
# Simply delete the directory
rm -rf /path/to/lament
```

### Remove PATH alias

Remove the alias from `~/.bashrc` or `~/.zshrc`:
```bash
# Remove this line:
alias lament='python3 /path/to/lament/lament/cli.py'
```

Or remove symbolic link:
```bash
sudo rm /usr/local/bin/lament
```

### Remove Optional Dependencies

```bash
pip3 uninstall numpy rich
```

---

## Getting Help

If you encounter issues not covered here:

1. **Check existing issues**: [GitHub Issues](https://github.com/yourusername/lament/issues)
2. **Ask on Discord**: [Join our server](https://discord.gg/lament)
3. **Email support**: hello@lament-lang.org
4. **Read the docs**: [Full documentation](docs/)

---

## Next Steps

Now that Lament is installed:

1. 📚 Read the [Tutorial](docs/TUTORIAL.md)
2. 📖 Explore the [Language Guide](docs/LANGUAGE_GUIDE.md)
3. 🔬 Check out [Examples](examples/)
4. 💬 Join the [Community](https://discord.gg/lament)

---

## System Requirements

### Minimum Requirements
- **CPU**: Any modern processor (x86-64, ARM)
- **RAM**: 256 MB
- **Disk**: 50 MB for Lament + Python
- **OS**: Linux, macOS, Windows, BSD

### Recommended Requirements
- **CPU**: Dual-core processor
- **RAM**: 1 GB (for neural features)
- **Disk**: 500 MB (with dependencies)
- **OS**: Linux or macOS for best experience

### Supported Python Versions
- ✅ Python 3.8
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11
- ✅ Python 3.12
- ✅ Python 3.13
- ❌ Python 3.7 and earlier
- ❌ Python 2.x

---

## Installation Verification Checklist

- [ ] Python 3.8+ installed and accessible
- [ ] Git installed (for cloning)
- [ ] Repository cloned successfully
- [ ] REPL starts without errors
- [ ] Basic Lament code executes
- [ ] Time-travel features work (`x@past`)
- [ ] File I/O operations work
- [ ] (Optional) NumPy installed for neural features
- [ ] (Optional) Test suite passes

---

**Welcome to Lament! The language that feels alive.**

If you need help, we're here for you. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) or reach out to the community.
