# Lament Development Tools

Complete suite of development tools for the Lament programming language.

## Overview

This package provides six professional-grade development tools:

1. **Code Formatter** - Automatic code formatting
2. **Linter** - Static code analysis with 30+ rules
3. **Language Server Protocol** - IDE integration
4. **Interactive Debugger** - Step-through debugging with time-travel
5. **Profiler** - Performance profiling
6. **Documentation Generator** - Automatic docs from source

## Installation

All tools are included in the Lament distribution. No additional installation required.

## Tools

### 1. Code Formatter (`formatter.py`)

Automatically formats Lament code to maintain consistent style.

**Usage:**
```bash
python -m tools.formatter <file.lament>
lament-fmt <file.lament>
```

**Options:**
- `-i, --in-place` - Format file in place
- `-c, --check` - Check if file is formatted (exit 1 if not)
- `-o, --output FILE` - Write formatted code to FILE

**Features:**
- Configurable indentation (spaces/tabs)
- Consistent spacing around operators
- Proper alignment of blocks
- Multi-line list/dict formatting
- Preserves all semantic meaning

**Example:**
```bash
# Format and print to stdout
lament-fmt example.lament

# Format in place
lament-fmt -i example.lament

# Check if formatted
lament-fmt -c example.lament
```

### 2. Linter (`linter.py`)

Static code analysis with comprehensive lint rules.

**Usage:**
```bash
python -m tools.linter <file.lament>
lament-lint <file.lament>
```

**Options:**
- `--strict` - Treat warnings as errors
- `--json` - Output in JSON format

**Lint Rules (30+):**

**Errors:**
- undefined-variable - Variable used before declaration
- undefined-function - Function called but never defined
- division-by-zero - Literal division by zero
- return-outside-function - Return outside function
- duplicate-parameter - Duplicate function parameters
- negative-temporal-offset - Invalid temporal offset

**Warnings:**
- unused-variable - Variable declared but never used
- unused-function - Function defined but never called
- infinite-loop - Loop with constant true condition
- too-many-parameters - Function with >5 parameters
- complex-expression - Very complex expression
- large-temporal-offset - Temporal offset >100
- comparison-chain - Chained comparisons
- single-fork-branch - Reality fork with only one branch
- large-list-literal - List literal with >100 elements
- always-true-condition - If condition always true
- always-false-condition - If condition always false

**Style:**
- variable-naming - Variable naming conventions
- function-naming - Function naming conventions
- short-variable-name - Very short variable names
- double-underscore - Double underscore in names
- complex-confess - Complex confess statement
- zero-initialization - Unnecessary zero initialization

**Info:**
- missing-return - Function without explicit return
- no-collapse-observation - Reality fork without collapse
- temporal-on-non-timeline - Temporal op on non-timeline var

**Example:**
```bash
# Lint file
lament-lint program.lament

# Strict mode (warnings = errors)
lament-lint --strict program.lament

# JSON output
lament-lint --json program.lament
```

### 3. Language Server Protocol (`lsp_server.py`)

LSP server for IDE integration providing intelligent code assistance.

**Usage:**
```bash
python -m tools.lsp_server
```

**Features:**
- **Autocomplete** - Smart completion for:
  - Keywords (confess, remember, sigh, etc.)
  - Built-in functions
  - User-defined functions and variables
  - Temporal operators (@past, @origin, etc.)

- **Hover Information** - Documentation on hover:
  - Function signatures
  - Parameter lists
  - Built-in function docs
  - Variable info with temporal support

- **Go-to-Definition** - Jump to:
  - Variable declarations (remember statements)
  - Function definitions (sigh statements)

- **Real-time Diagnostics** - Live error checking:
  - Syntax errors
  - Lint warnings
  - Type errors

**IDE Integration:**

VS Code (settings.json):
```json
{
  "languageServer": {
    "lament": {
      "command": "python",
      "args": ["-m", "tools.lsp_server"],
      "filetypes": ["lament"]
    }
  }
}
```

Vim/Neovim (with coc.nvim):
```vim
{
  "languageserver": {
    "lament": {
      "command": "python",
      "args": ["-m", "tools.lsp_server"],
      "filetypes": ["lament"]
    }
  }
}
```

### 4. Interactive Debugger (`debugger.py`)

Step-through debugger with time-travel capabilities.

**Usage:**
```bash
python -m tools.debugger <file.lament>
lament-debug <file.lament>
```

**Commands:**
- `break <line>` - Set breakpoint at line
- `delete <line>` - Remove breakpoint
- `continue` (c) - Continue execution
- `step` (s) - Step to next statement
- `next` (n) - Step over function calls
- `vars` - Show all variables
- `print <expr>` (p) - Evaluate expression
- `timeline <var>` - Show variable timeline
- `rewind [steps]` - Rewind execution (time-travel!)
- `replay` - Replay execution from start
- `stack` - Show call stack
- `list` (l) - Show source code
- `quit` (q) - Exit debugger

**Features:**
- Line-based breakpoints
- Conditional breakpoints
- Variable inspection
- Timeline navigation (view variable history)
- Time-travel debugging (rewind/replay)
- Call stack visualization
- Expression evaluation

**Example Session:**
```
$ lament-debug program.lament
Lament Debugger. Type 'help' or '?' for commands.

(lament-debug) break 10
Breakpoint set at line 10

(lament-debug) continue
Breakpoint hit at statement 10

>>> 10 | remember x = 42

(lament-debug) step
>>> 11 | confess x

(lament-debug) print x
42

(lament-debug) timeline x
=== Timeline for 'x' ===
Current value: 42
Origin value: 42
Age: 0
Born: 1699000000

(lament-debug) continue
42
Program finished
```

### 5. Profiler (`profiler.py`)

Performance profiling for time and memory analysis.

**Usage:**
```bash
python -m tools.profiler <file.lament> [options]
lament-profile <file.lament>
```

**Options:**
- `--time` - Time profiling (default)
- `--memory` - Enable memory profiling
- `--flamegraph` - Generate flamegraph data
- `--output FILE` - Export to file (.json or .html)

**Features:**
- **Time Profiling:**
  - Total execution time
  - Per-function timing
  - Per-statement timing
  - Call counts
  - Average call time

- **Memory Profiling:**
  - Memory usage tracking
  - Per-function memory delta
  - Memory snapshots

- **Hotspot Detection:**
  - Automatically identifies slow code
  - Shows top 10 performance bottlenecks
  - Percentage of total time

- **Export Formats:**
  - JSON (for programmatic analysis)
  - HTML (beautiful interactive reports)
  - Flamegraph (for visualization)

**Example:**
```bash
# Basic time profiling
lament-profile program.lament

# With memory profiling
lament-profile --memory program.lament

# Export HTML report
lament-profile --output report.html program.lament

# Generate flamegraph
lament-profile --flamegraph program.lament
```

**Output Example:**
```
======================================================================
LAMENT PROFILER REPORT
======================================================================

Total execution time: 0.123456s
Total memory delta: 45600 bytes

----------------------------------------------------------------------
FUNCTION PROFILES
----------------------------------------------------------------------
Function                       Calls   Total Time     Avg Time
----------------------------------------------------------------------
fibonacci                        100    0.100000s    0.001000s
calculate                         10    0.020000s    0.002000s

----------------------------------------------------------------------
PERFORMANCE HOTSPOTS
----------------------------------------------------------------------
Location                                           Time  % of Total
----------------------------------------------------------------------
function fibonacci                           0.100000s      81.0%
line 25: x = x + fibonacci(x - 1)           0.015000s      12.2%
```

### 6. Documentation Generator (`docgen.py`)

Automatic documentation generation from source code.

**Usage:**
```bash
python -m tools.docgen <file.lament> [options]
lament-doc <file.lament>
```

**Options:**
- `--output DIR` - Output directory (default: ./docs)
- `--format FORMAT` - Output format: html, markdown (default: html)
- `--title TITLE` - Documentation title

**Features:**
- **Extraction:**
  - Function docstrings (from comments)
  - Parameter lists
  - Return value documentation
  - Example code blocks
  - Variable documentation

- **HTML Output:**
  - Beautiful themed documentation
  - Syntax highlighting
  - Cross-reference links
  - Symbol index
  - Mobile-responsive

- **Markdown Output:**
  - Clean, readable markdown
  - GitHub-compatible
  - Easy to edit

**Documentation Format:**

Functions should be documented with preceding comments:
```lament
# Calculate the Fibonacci number at position n.
#
# This function uses recursive descent into mathematical sorrow.
#
# Parameters:
#   n - The position in the sequence (must be non-negative)
#
# Returns: The Fibonacci number at position n
#
# Example:
#   remember result = fib(10)
#   confess result  # Outputs: 55
sigh fib(n) {
  if n <= 1 {
    exhale n
  }
  exhale fib(n - 1) + fib(n - 2)
}
```

**Example:**
```bash
# Generate HTML docs
lament-doc program.lament

# Generate Markdown
lament-doc --format markdown program.lament

# Custom output directory
lament-doc --output ./documentation program.lament

# Custom title
lament-doc --title "My Amazing Project" program.lament
```

## Creating Command Aliases

Add these to your shell configuration (`.bashrc`, `.zshrc`, etc.):

```bash
# Lament development tools
alias lament-fmt='python -m tools.formatter'
alias lament-lint='python -m tools.linter'
alias lament-debug='python -m tools.debugger'
alias lament-profile='python -m tools.profiler'
alias lament-doc='python -m tools.docgen'
```

## Tool Integration Workflow

Recommended workflow for developing Lament programs:

1. **Write Code** - Create your `.lament` file
2. **Format** - `lament-fmt -i program.lament`
3. **Lint** - `lament-lint program.lament`
4. **Debug** - `lament-debug program.lament` (if issues)
5. **Profile** - `lament-profile program.lament` (optimize)
6. **Document** - `lament-doc program.lament`

## Code Statistics

### Formatter (`formatter.py`)
- **Lines**: ~430
- **Classes**: 2 (LamentFormatter, FormatterConfig)
- **Features**: AST formatting, configurable styles, multi-line support

### Linter (`linter.py`)
- **Lines**: ~630
- **Classes**: 4 (LamentLinter, LintIssue, LintRule, Severity)
- **Rules**: 30+ comprehensive lint rules

### LSP Server (`lsp_server.py`)
- **Lines**: ~550
- **Classes**: 2 (LamentLSP, plus data classes)
- **Features**: Autocomplete, hover, definition, diagnostics

### Debugger (`debugger.py`)
- **Lines**: ~450
- **Classes**: 3 (LamentDebugger, DebuggerShell, ExecutionSnapshot)
- **Features**: Breakpoints, time-travel, timeline inspection

### Profiler (`profiler.py`)
- **Lines**: ~470
- **Classes**: 3 (LamentProfiler, ProfileEntry, ProfilingResult)
- **Features**: Time/memory profiling, hotspot detection, export

### Documentation Generator (`docgen.py`)
- **Lines**: ~520
- **Classes**: 2 (DocGenerator, plus data classes)
- **Features**: HTML/Markdown generation, cross-references

**Total**: ~3,050 lines of production code

## Development

All tools are built on the Lament AST and can be extended:

- **formatter.py** - Modify `FormatterConfig` for custom styles
- **linter.py** - Add rules by extending `LamentLinter`
- **lsp_server.py** - Add LSP features to `LamentLSP`
- **debugger.py** - Extend `DebuggerShell` for new commands
- **profiler.py** - Add metrics to `LamentProfiler`
- **docgen.py** - Customize HTML/CSS in `DocGenerator`

## License

Part of the Lament programming language.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
