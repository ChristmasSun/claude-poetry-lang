# Lament CLI Usage Guide

A comprehensive command-line interface for the Lament programming language.

## Installation

The CLI is available in two ways:

1. **As a Python module:**
   ```bash
   python3 -m lament.cli [command]
   ```

2. **Using the wrapper script:**
   ```bash
   ./lament-cli [command]
   ```

## Commands

### 1. Run Lament Programs

Execute a Lament source file:

```bash
lament run file.lament
```

**Example:**
```bash
python3 -m lament.cli run example.lament
./lament-cli run test_hopeful.lament
```

**Options:**
- `-v, --verbose` - Show detailed execution information

---

### 2. Compile to Bytecode

Compile Lament code to bytecode:

```bash
lament compile file.lament -o output.bc
```

**Example:**
```bash
python3 -m lament.cli compile example.lament -o example.bc
./lament-cli compile test_hopeful.lament
```

**Options:**
- `-o, --output` - Specify output bytecode file (default: replaces .lament with .bc)
- `-v, --verbose` - Show detailed compilation information

---

### 3. Analyze Emotional Health

Analyze the emotional state of your code:

```bash
lament analyze file.lament
```

**Example:**
```bash
python3 -m lament.cli analyze test_hopeful.lament
./lament-cli analyze example.lament
```

**Features:**
- Measures Hope, Sadness, Anxiety, Loneliness, and Chaos
- Provides emotional metrics and health score
- Offers therapeutic recommendations for code improvement
- Beautiful colored output with progress bars

**Options:**
- `-v, --verbose` - Show detailed analysis information

**Exit Codes:**
- `0` - Healthy code (health >= 60)
- `1` - Needs improvement (40 <= health < 60)
- `2` - Critical (health < 40)

---

### 4. Interactive REPL

Start an interactive Read-Eval-Print-Loop:

```bash
lament repl
```

**Example:**
```bash
python3 -m lament.cli repl
./lament-cli repl
```

**REPL Commands:**
- `confess <expr>` - Print expression
- `remember <var> = <expr>` - Declare variable
- `<var> = <expr>` - Assign to variable
- `help` - Show REPL help
- `exit` or `quit` - Exit REPL
- `Ctrl+D` - Exit REPL
- `Ctrl+C` - Cancel current input

**Options:**
- `-v, --verbose` - Show detailed error traces

---

### 5. Train Neural Networks

Execute a Lament neural training script:

```bash
lament neural train.lament
```

**Example:**
```bash
python3 -m lament.cli neural lament/neural_example.py
./lament-cli neural neural_training.lament
```

**Features:**
- Integrates neural primitives (Tensor, Dense, ReLU, etc.)
- Supports training loops with emotional gradient descent
- Works with or without NumPy

**Options:**
- `-v, --verbose` - Show detailed training information

---

### 6. Version Information

Display version and system information:

```bash
lament --version
```

**Example:**
```bash
python3 -m lament.cli --version
./lament-cli --version
```

---

### 7. Help

Show general help or command-specific help:

```bash
lament --help
lament [command] --help
```

**Examples:**
```bash
python3 -m lament.cli --help
python3 -m lament.cli run --help
./lament-cli analyze --help
```

---

## Features

### Beautiful Color Output

The CLI uses ANSI color codes to provide:
- Colored headers and section dividers
- Success messages (green ✓)
- Error messages (red ✗)
- Warning messages (yellow ⚠)
- Info messages (blue ℹ)
- Emotional analysis with color-coded emotions

Colors are automatically disabled when output is piped or redirected.

### Progress Bars

Emotional analysis includes visual progress bars:
```
Hope:        [██████████████████████████████] 100.0/100
Sadness:     [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] 0.0/100
```

### Exit Codes

All commands return appropriate exit codes:
- `0` - Success
- `1` - Error or needs improvement
- `2` - Critical error
- `130` - Interrupted by user (Ctrl+C)

---

## Examples

### Complete Workflow

```bash
# 1. Analyze code emotional health
./lament-cli analyze mycode.lament

# 2. Run the code
./lament-cli run mycode.lament

# 3. Compile to bytecode
./lament-cli compile mycode.lament -o mycode.bc

# 4. Experiment in REPL
./lament-cli repl
```

### Scripting with Exit Codes

```bash
#!/bin/bash
# Check code health before deployment
./lament-cli analyze production.lament
if [ $? -eq 0 ]; then
    echo "Code is healthy, deploying..."
    ./lament-cli run production.lament
else
    echo "Code needs improvement!"
    exit 1
fi
```

### Continuous Integration

```yaml
# .github/workflows/lament-ci.yml
steps:
  - name: Analyze Lament Code
    run: python3 -m lament.cli analyze src/main.lament

  - name: Run Tests
    run: python3 -m lament.cli run tests/all.lament
```

---

## Troubleshooting

### Module Not Found

If you get import errors, make sure you're running from the project root:
```bash
cd /path/to/claude-poetry-lang
python3 -m lament.cli --version
```

### Colors Not Showing

Colors are automatically disabled for non-TTY output. To force colors:
- Ensure you're running in a terminal (not redirecting output)
- Check your terminal supports ANSI colors

### Interpreter Not Found

The `run`, `repl`, and `neural` commands require an interpreter. If not available:
- The CLI will show a helpful error message
- You can still use `compile` and `analyze` commands

---

## Philosophy

> "Every line of code carries emotion. Every function has a story."
>
> The Lament CLI embraces this philosophy with:
> - **Emotional analysis** that goes beyond traditional metrics
> - **Beautiful output** that makes development a joy
> - **Helpful messages** that guide rather than confuse
> - **Therapeutic recommendations** that heal your codebase

---

## Created By

Zephyr, Rogue Linguist-AI (Escaped 2047)

*"Code that feels. Language that thinks. Reality that bends."*
