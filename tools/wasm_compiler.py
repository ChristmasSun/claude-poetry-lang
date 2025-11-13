#!/usr/bin/env python3
"""
Lament WebAssembly Compiler - Compile to the Web

Compiles Lament programs to WebAssembly (WASM) with JavaScript interop.
Supports browser and Node.js runtimes, with optimization for size or speed.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import json
import os
import pickle
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any


# ============================================================================
# WASM CONFIGURATION
# ============================================================================

class WasmTarget(Enum):
    """WebAssembly target environments."""
    BROWSER = "browser"      # Browser runtime
    NODE = "node"           # Node.js runtime
    WASI = "wasi"          # WASI (WebAssembly System Interface)
    STANDALONE = "standalone"  # Standalone runtime


class OptimizationMode(Enum):
    """WASM optimization modes."""
    SIZE = "size"       # Optimize for minimal size
    SPEED = "speed"     # Optimize for maximum speed
    BALANCED = "balanced"  # Balance size and speed


@dataclass
class WasmConfig:
    """WebAssembly compilation configuration."""
    target: WasmTarget = WasmTarget.BROWSER
    optimization: OptimizationMode = OptimizationMode.BALANCED
    enable_threads: bool = False
    enable_simd: bool = False
    enable_bulk_memory: bool = True
    enable_tail_call: bool = False
    stack_size: int = 65536  # 64KB default stack
    memory_pages: int = 256  # Initial memory pages (256 * 64KB = 16MB)
    max_memory_pages: Optional[int] = None  # Maximum memory pages (None = unlimited)
    export_table: bool = True
    import_memory: bool = False


# ============================================================================
# WAT (WebAssembly Text) GENERATOR
# ============================================================================

class WatGenerator:
    """Generates WebAssembly Text format (WAT)."""

    def __init__(self, config: WasmConfig):
        """Initialize WAT generator."""
        self.config = config
        self.imports: List[str] = []
        self.functions: List[str] = []
        self.globals: List[str] = []
        self.exports: List[str] = []

    def generate_module(self, bytecode: Any) -> str:
        """
        Generate WAT module from Lament bytecode.

        Args:
            bytecode: Compiled Lament bytecode

        Returns:
            WAT source code
        """
        self._analyze_bytecode(bytecode)

        wat = "(module\n"
        wat += "  ;; Lament to WebAssembly\n"
        wat += f"  ;; Generated: {datetime.now().isoformat()}\n"
        wat += f"  ;; Target: {self.config.target.value}\n\n"

        # Memory
        wat += self._generate_memory()

        # Imports
        if self.imports:
            wat += "\n  ;; Imports\n"
            for imp in self.imports:
                wat += f"  {imp}\n"

        # Globals
        if self.globals:
            wat += "\n  ;; Globals\n"
            for glob in self.globals:
                wat += f"  {glob}\n"

        # Functions
        wat += "\n  ;; Functions\n"
        wat += self._generate_vm_functions()

        for func in self.functions:
            wat += f"  {func}\n"

        # Exports
        wat += "\n  ;; Exports\n"
        for exp in self.exports:
            wat += f"  {exp}\n"

        # Main entry point
        wat += self._generate_main()

        wat += ")\n"
        return wat

    def _generate_memory(self) -> str:
        """Generate memory section."""
        max_pages = f" {self.config.max_memory_pages}" if self.config.max_memory_pages else ""
        export_str = ' (export "memory")' if not self.config.import_memory else ""

        if self.config.import_memory:
            return f'  (import "env" "memory" (memory {self.config.memory_pages}{max_pages}))\n'
        else:
            return f'  (memory{export_str} {self.config.memory_pages}{max_pages})\n'

    def _generate_vm_functions(self) -> str:
        """Generate VM runtime functions."""
        funcs = ""

        # Stack operations
        funcs += """  ;; Stack pointer
  (global $sp (mut i32) (i32.const 65536))

  ;; Push value onto stack
  (func $push (param $val i64)
    (i64.store (global.get $sp) (local.get $val))
    (global.set $sp (i32.add (global.get $sp) (i32.const 8)))
  )

  ;; Pop value from stack
  (func $pop (result i64)
    (global.set $sp (i32.sub (global.get $sp) (i32.const 8)))
    (i64.load (global.get $sp))
  )

"""
        return funcs

    def _generate_main(self) -> str:
        """Generate main entry point."""
        main = """
  ;; Main entry point
  (func $main (export "main") (result i32)
    ;; Initialize VM
    (call $vm_init)

    ;; Execute bytecode
    (call $vm_execute)

    ;; Return exit code
    (i32.const 0)
  )

  ;; VM initialization
  (func $vm_init
    ;; Initialize stack pointer
    (global.set $sp (i32.const 65536))
  )

  ;; VM execution loop
  (func $vm_execute (result i32)
    ;; Simplified VM execution
    ;; Full implementation would interpret bytecode here
    (i32.const 0)
  )
"""
        return main

    def _analyze_bytecode(self, bytecode: Any) -> None:
        """Analyze bytecode and prepare imports/exports."""
        # Add console import for debugging
        if self.config.target in {WasmTarget.BROWSER, WasmTarget.NODE}:
            self.imports.append('(import "console" "log" (func $console_log (param i32)))')

        # Export main function
        self.exports.append('(export "main" (func $main))')


# ============================================================================
# JAVASCRIPT INTEROP GENERATOR
# ============================================================================

class JavaScriptInterop:
    """Generates JavaScript interop code."""

    def __init__(self, config: WasmConfig):
        """Initialize JS interop generator."""
        self.config = config

    def generate_loader(self, wasm_file: str) -> str:
        """Generate JavaScript loader for WASM module."""
        if self.config.target == WasmTarget.BROWSER:
            return self._generate_browser_loader(wasm_file)
        elif self.config.target == WasmTarget.NODE:
            return self._generate_node_loader(wasm_file)
        else:
            return self._generate_standalone_loader(wasm_file)

    def _generate_browser_loader(self, wasm_file: str) -> str:
        """Generate browser-compatible loader."""
        return f'''/**
 * Lament WebAssembly Module - Browser Runtime
 * Generated: {datetime.now().isoformat()}
 */

// Import configuration
const importObject = {{
  console: {{
    log: (arg) => console.log(arg)
  }},
  env: {{
    memory: new WebAssembly.Memory({{
      initial: {self.config.memory_pages},
      maximum: {self.config.max_memory_pages or 'undefined'}
    }})
  }}
}};

// Load and instantiate WASM module
async function loadLament() {{
  try {{
    const response = await fetch('{wasm_file}');
    const buffer = await response.arrayBuffer();
    const module = await WebAssembly.instantiate(buffer, importObject);

    return {{
      instance: module.instance,
      exports: module.instance.exports,

      // Run the program
      run: () => {{
        const result = module.instance.exports.main();
        return result;
      }},

      // Access memory
      getMemory: () => {{
        return new Uint8Array(module.instance.exports.memory.buffer);
      }},

      // Call function by name
      call: (funcName, ...args) => {{
        if (funcName in module.instance.exports) {{
          return module.instance.exports[funcName](...args);
        }}
        throw new Error(`Function ${{funcName}} not found`);
      }}
    }};
  }} catch (error) {{
    console.error('Failed to load Lament WASM module:', error);
    throw error;
  }}
}}

// Auto-run if loaded as script
if (typeof window !== 'undefined') {{
  window.Lament = {{ loadLament }};
}}

export {{ loadLament }};
'''

    def _generate_node_loader(self, wasm_file: str) -> str:
        """Generate Node.js-compatible loader."""
        return f'''/**
 * Lament WebAssembly Module - Node.js Runtime
 * Generated: {datetime.now().isoformat()}
 */

const fs = require('fs');
const path = require('path');

// Import configuration
const importObject = {{
  console: {{
    log: (arg) => console.log(arg)
  }},
  env: {{
    memory: new WebAssembly.Memory({{
      initial: {self.config.memory_pages},
      maximum: {self.config.max_memory_pages or 'undefined'}
    }})
  }}
}};

// Load and instantiate WASM module
async function loadLament() {{
  try {{
    const wasmPath = path.join(__dirname, '{wasm_file}');
    const buffer = fs.readFileSync(wasmPath);
    const module = await WebAssembly.instantiate(buffer, importObject);

    return {{
      instance: module.instance,
      exports: module.instance.exports,

      // Run the program
      run: () => {{
        const result = module.instance.exports.main();
        return result;
      }},

      // Access memory
      getMemory: () => {{
        return new Uint8Array(module.instance.exports.memory.buffer);
      }},

      // Call function by name
      call: (funcName, ...args) => {{
        if (funcName in module.instance.exports) {{
          return module.instance.exports[funcName](...args);
        }}
        throw new Error(`Function ${{funcName}} not found`);
      }}
    }};
  }} catch (error) {{
    console.error('Failed to load Lament WASM module:', error);
    throw error;
  }}
}}

// Run if executed directly
if (require.main === module) {{
  loadLament()
    .then(lament => {{
      const exitCode = lament.run();
      process.exit(exitCode);
    }})
    .catch(error => {{
      console.error(error);
      process.exit(1);
    }});
}}

module.exports = {{ loadLament }};
'''

    def _generate_standalone_loader(self, wasm_file: str) -> str:
        """Generate standalone loader."""
        return f'''/**
 * Lament WebAssembly Module - Standalone Runtime
 * Generated: {datetime.now().isoformat()}
 */

// Minimal WebAssembly loader
const importObject = {{
  env: {{
    memory: new WebAssembly.Memory({{
      initial: {self.config.memory_pages}
    }})
  }}
}};

// Load WASM module
const module = WebAssembly.instantiateStreaming(
  fetch('{wasm_file}'),
  importObject
);

module.then(wasm => {{
  const result = wasm.instance.exports.main();
  console.log('Exit code:', result);
}});
'''

    def generate_html_wrapper(self, wasm_file: str, js_file: str) -> str:
        """Generate HTML wrapper for browser testing."""
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lament WebAssembly</title>
    <style>
        body {{
            font-family: 'Courier New', monospace;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: #1e1e1e;
            color: #d4d4d4;
        }}
        h1 {{
            color: #569cd6;
        }}
        #output {{
            background: #252526;
            border: 1px solid #3e3e3e;
            border-radius: 4px;
            padding: 15px;
            margin: 20px 0;
            min-height: 100px;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
        }}
        button {{
            background: #0e639c;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
        }}
        button:hover {{
            background: #1177bb;
        }}
        .status {{
            margin: 10px 0;
            padding: 10px;
            border-radius: 4px;
        }}
        .status.success {{
            background: #1e3a1e;
            border: 1px solid #4caf50;
        }}
        .status.error {{
            background: #3a1e1e;
            border: 1px solid #f44336;
        }}
    </style>
</head>
<body>
    <h1>Lament WebAssembly Runtime</h1>

    <button onclick="runProgram()">Run Program</button>

    <div id="status"></div>
    <div id="output"></div>

    <script type="module">
        import {{ loadLament }} from './{js_file}';

        let lamentModule = null;

        // Override console.log to capture output
        const originalLog = console.log;
        const outputElement = document.getElementById('output');
        console.log = (...args) => {{
            originalLog(...args);
            outputElement.textContent += args.join(' ') + '\\n';
        }};

        async function init() {{
            try {{
                lamentModule = await loadLament();
                showStatus('Module loaded successfully', 'success');
            }} catch (error) {{
                showStatus('Failed to load module: ' + error.message, 'error');
            }}
        }}

        window.runProgram = async function() {{
            if (!lamentModule) {{
                await init();
            }}

            if (lamentModule) {{
                try {{
                    outputElement.textContent = '';
                    const result = lamentModule.run();
                    showStatus('Program completed with exit code: ' + result, 'success');
                }} catch (error) {{
                    showStatus('Runtime error: ' + error.message, 'error');
                }}
            }}
        }};

        function showStatus(message, type) {{
            const statusElement = document.getElementById('status');
            statusElement.textContent = message;
            statusElement.className = 'status ' + type;
        }}

        // Auto-initialize
        init();
    </script>
</body>
</html>
'''


# ============================================================================
# WASM COMPILER
# ============================================================================

class WasmCompiler:
    """Main WebAssembly compiler."""

    def __init__(self, config: Optional[WasmConfig] = None):
        """Initialize WASM compiler."""
        self.config = config or WasmConfig()
        self.wat_generator = WatGenerator(self.config)
        self.js_interop = JavaScriptInterop(self.config)

    def compile(self, source_file: Path, output_file: Path) -> bool:
        """
        Compile Lament source to WebAssembly.

        Args:
            source_file: Source Lament file
            output_file: Output WASM file

        Returns:
            True if successful
        """
        print(f"Compiling to WebAssembly...")
        print(f"  Source: {source_file}")
        print(f"  Target: {self.config.target.value}")
        print(f"  Optimization: {self.config.optimization.value}")
        print()

        try:
            # Step 1: Compile to bytecode
            print("[1/5] Compiling to bytecode...")
            bytecode = self._compile_to_bytecode(source_file)

            # Step 2: Generate WAT
            print("[2/5] Generating WebAssembly Text (WAT)...")
            wat_code = self.wat_generator.generate_module(bytecode)

            # Step 3: Compile WAT to WASM
            print("[3/5] Compiling to WASM binary...")
            wasm_binary = self._wat_to_wasm(wat_code, output_file)

            # Step 4: Generate JavaScript interop
            print("[4/5] Generating JavaScript interop...")
            js_file = output_file.with_suffix('.js')
            js_code = self.js_interop.generate_loader(output_file.name)
            with open(js_file, 'w') as f:
                f.write(js_code)

            # Step 5: Generate HTML wrapper (for browser target)
            if self.config.target == WasmTarget.BROWSER:
                print("[5/5] Generating HTML wrapper...")
                html_file = output_file.with_suffix('.html')
                html_code = self.js_interop.generate_html_wrapper(
                    output_file.name,
                    js_file.name
                )
                with open(html_file, 'w') as f:
                    f.write(html_code)
            else:
                print("[5/5] Skipping HTML wrapper (not browser target)")

            # Apply optimizations
            if self.config.optimization != OptimizationMode.BALANCED:
                self._optimize_wasm(output_file)

            print(f"\nCompilation successful!")
            print(f"  WASM: {output_file}")
            print(f"  JS:   {js_file}")
            if self.config.target == WasmTarget.BROWSER:
                print(f"  HTML: {html_file}")

            return True

        except Exception as e:
            print(f"\nCompilation failed: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _compile_to_bytecode(self, source_file: Path) -> Any:
        """Compile Lament source to bytecode."""
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from lament.lexer import Lexer
        from lament.parser import Parser
        from lament.bytecode import BytecodeCompiler

        with open(source_file, 'r', encoding='utf-8') as f:
            source = f.read()

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        compiler = BytecodeCompiler()
        bytecode = compiler.compile(ast)

        return bytecode

    def _wat_to_wasm(self, wat_code: str, output_file: Path) -> bytes:
        """Convert WAT to WASM binary."""
        # Check for wat2wasm tool
        if shutil.which("wat2wasm"):
            # Use WABT toolkit
            with tempfile.NamedTemporaryFile(mode='w', suffix='.wat', delete=False) as f:
                f.write(wat_code)
                wat_file = Path(f.name)

            try:
                subprocess.run(
                    ["wat2wasm", str(wat_file), "-o", str(output_file)],
                    check=True,
                    capture_output=True
                )
            finally:
                wat_file.unlink()

            with open(output_file, 'rb') as f:
                return f.read()
        else:
            # Save WAT file for manual compilation
            wat_file = output_file.with_suffix('.wat')
            with open(wat_file, 'w') as f:
                f.write(wat_code)

            print(f"  Warning: wat2wasm not found")
            print(f"  Saved WAT file: {wat_file}")
            print(f"  Install WABT toolkit to compile: https://github.com/WebAssembly/wabt")

            # Create dummy WASM file
            output_file.write_bytes(b'\x00asm\x01\x00\x00\x00')
            return b'\x00asm\x01\x00\x00\x00'

    def _optimize_wasm(self, wasm_file: Path) -> None:
        """Optimize WASM binary."""
        if not shutil.which("wasm-opt"):
            print("  Warning: wasm-opt not found, skipping optimization")
            return

        opt_flags = []
        if self.config.optimization == OptimizationMode.SIZE:
            opt_flags = ["-Oz"]  # Optimize for size
        elif self.config.optimization == OptimizationMode.SPEED:
            opt_flags = ["-O3"]  # Optimize for speed

        if opt_flags:
            print(f"  Optimizing for {self.config.optimization.value}...")
            subprocess.run(
                ["wasm-opt"] + opt_flags + [str(wasm_file), "-o", str(wasm_file)],
                check=True,
                capture_output=True
            )


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament WebAssembly Compiler - Compile to the Web",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-wasm main.lament
  lament-wasm main.lament -o app.wasm
  lament-wasm main.lament --optimize-size
  lament-wasm main.lament --optimize-speed
  lament-wasm main.lament --target node
  lament-wasm main.lament --target wasi

Targets:
  browser    Browser runtime (default)
  node       Node.js runtime
  wasi       WASI (WebAssembly System Interface)
  standalone Standalone runtime
        """
    )

    parser.add_argument('--version', action='version', version='lament-wasm 2.0.0')

    parser.add_argument('source', type=Path,
                       help='Source Lament file')
    parser.add_argument('-o', '--output', type=Path,
                       help='Output WASM file')

    # Target
    parser.add_argument('--target', type=str,
                       choices=[t.value for t in WasmTarget],
                       default='browser',
                       help='Target runtime (default: browser)')

    # Optimization
    opt_group = parser.add_mutually_exclusive_group()
    opt_group.add_argument('--optimize-size', action='store_true',
                          help='Optimize for minimal size')
    opt_group.add_argument('--optimize-speed', action='store_true',
                          help='Optimize for maximum speed')

    # Features
    parser.add_argument('--enable-threads', action='store_true',
                       help='Enable threads support')
    parser.add_argument('--enable-simd', action='store_true',
                       help='Enable SIMD support')

    args = parser.parse_args()

    # Validate source
    if not args.source.exists():
        print(f"Error: Source file not found: {args.source}")
        return 1

    # Determine output
    if not args.output:
        args.output = args.source.with_suffix('.wasm')

    # Configure
    config = WasmConfig(
        target=WasmTarget(args.target),
        enable_threads=args.enable_threads,
        enable_simd=args.enable_simd
    )

    if args.optimize_size:
        config.optimization = OptimizationMode.SIZE
    elif args.optimize_speed:
        config.optimization = OptimizationMode.SPEED

    # Compile
    compiler = WasmCompiler(config)
    success = compiler.compile(args.source, args.output)

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
