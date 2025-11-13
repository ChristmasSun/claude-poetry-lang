#!/usr/bin/env python3
"""
Lament Build System - Forging Emotional Executables

A comprehensive build system for the Lament programming language.
Handles compilation, dependency linking, executable output, and incremental builds.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import json
import os
import hashlib
import shutil
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import pickle


# ============================================================================
# BUILD TARGETS
# ============================================================================

class BuildTarget(Enum):
    """Build target types."""
    EXECUTABLE = "executable"
    LIBRARY = "library"
    MODULE = "module"


@dataclass
class SourceFile:
    """Represents a source file in the build."""
    path: Path
    modified_time: float
    checksum: str
    dependencies: List[Path] = field(default_factory=list)

    def needs_rebuild(self, cache: 'BuildCache') -> bool:
        """Check if this file needs to be rebuilt."""
        if not cache.has_file(self.path):
            return True

        cached = cache.get_file(self.path)
        if cached.checksum != self.checksum:
            return True

        # Check if any dependency was modified
        for dep in self.dependencies:
            if cache.has_file(dep):
                dep_cached = cache.get_file(dep)
                dep_current = SourceFile.from_path(dep)
                if dep_current.checksum != dep_cached.checksum:
                    return True

        return False

    @staticmethod
    def from_path(path: Path) -> 'SourceFile':
        """Create SourceFile from a path."""
        if not path.exists():
            raise FileNotFoundError(f"Source file not found: {path}")

        with open(path, 'rb') as f:
            content = f.read()

        checksum = hashlib.sha256(content).hexdigest()
        modified_time = path.stat().st_mtime

        return SourceFile(
            path=path,
            modified_time=modified_time,
            checksum=checksum
        )


# ============================================================================
# BUILD CONFIGURATION
# ============================================================================

@dataclass
class BuildConfig:
    """Configuration for a build."""
    name: str
    target: BuildTarget
    entry_point: Path
    output_dir: Path
    source_dirs: List[Path] = field(default_factory=list)
    include_patterns: List[str] = field(default_factory=lambda: ["**/*.lament"])
    exclude_patterns: List[str] = field(default_factory=lambda: ["tests/**", "**/test_*.lament"])
    dependencies: List[str] = field(default_factory=list)
    optimization_level: int = 0
    debug: bool = False
    warnings_as_errors: bool = False
    custom_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'target': self.target.value,
            'entry_point': str(self.entry_point),
            'output_dir': str(self.output_dir),
            'source_dirs': [str(d) for d in self.source_dirs],
            'include_patterns': self.include_patterns,
            'exclude_patterns': self.exclude_patterns,
            'dependencies': self.dependencies,
            'optimization_level': self.optimization_level,
            'debug': self.debug,
            'warnings_as_errors': self.warnings_as_errors,
            'custom_flags': self.custom_flags
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BuildConfig':
        """Create from dictionary."""
        return BuildConfig(
            name=data['name'],
            target=BuildTarget(data['target']),
            entry_point=Path(data['entry_point']),
            output_dir=Path(data['output_dir']),
            source_dirs=[Path(d) for d in data.get('source_dirs', [])],
            include_patterns=data.get('include_patterns', ["**/*.lament"]),
            exclude_patterns=data.get('exclude_patterns', ["tests/**"]),
            dependencies=data.get('dependencies', []),
            optimization_level=data.get('optimization_level', 0),
            debug=data.get('debug', False),
            warnings_as_errors=data.get('warnings_as_errors', False),
            custom_flags=data.get('custom_flags', [])
        )

    @staticmethod
    def from_file(filepath: Path) -> 'BuildConfig':
        """Load build configuration from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return BuildConfig.from_dict(data)

    def to_file(self, filepath: Path) -> None:
        """Save build configuration to file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# ============================================================================
# BUILD CACHE
# ============================================================================

class BuildCache:
    """Manages incremental build cache."""

    def __init__(self, cache_file: Path):
        """Initialize build cache."""
        self.cache_file = cache_file
        self.files: Dict[Path, SourceFile] = {}
        self.load()

    def load(self) -> None:
        """Load cache from disk."""
        if not self.cache_file.exists():
            return

        try:
            with open(self.cache_file, 'rb') as f:
                self.files = pickle.load(f)
        except Exception as e:
            print(f"Warning: Could not load build cache: {e}")
            self.files = {}

    def save(self) -> None:
        """Save cache to disk."""
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_file, 'wb') as f:
            pickle.dump(self.files, f)

    def has_file(self, path: Path) -> bool:
        """Check if file is in cache."""
        return path in self.files

    def get_file(self, path: Path) -> Optional[SourceFile]:
        """Get cached file info."""
        return self.files.get(path)

    def update_file(self, source_file: SourceFile) -> None:
        """Update cache with file info."""
        self.files[source_file.path] = source_file

    def clear(self) -> None:
        """Clear the cache."""
        self.files = {}
        if self.cache_file.exists():
            self.cache_file.unlink()


# ============================================================================
# DEPENDENCY ANALYZER
# ============================================================================

class DependencyAnalyzer:
    """Analyzes source file dependencies."""

    def __init__(self, source_dirs: List[Path]):
        """Initialize dependency analyzer."""
        self.source_dirs = source_dirs

    def analyze(self, source_file: Path) -> List[Path]:
        """
        Analyze a source file and return its dependencies.
        Looks for 'import' statements in Lament code.
        """
        dependencies = []

        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Simple regex-like parsing for import statements
            # Format: breathe "module_name"
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('breathe'):
                    # Extract module name
                    parts = line.split('"')
                    if len(parts) >= 2:
                        module_name = parts[1]
                        dep_path = self._resolve_import(module_name)
                        if dep_path:
                            dependencies.append(dep_path)

        except Exception as e:
            print(f"Warning: Could not analyze {source_file}: {e}")

        return dependencies

    def _resolve_import(self, module_name: str) -> Optional[Path]:
        """Resolve an import to a file path."""
        # Try as relative import
        possible_names = [
            f"{module_name}.lament",
            f"{module_name}/main.lament",
            module_name
        ]

        for source_dir in self.source_dirs:
            for name in possible_names:
                path = source_dir / name
                if path.exists():
                    return path

        return None


# ============================================================================
# COMPILER INTERFACE
# ============================================================================

class LamentCompiler:
    """Interface to the Lament compiler."""

    def __init__(self, config: BuildConfig):
        """Initialize compiler."""
        self.config = config

    def compile_file(self, source_file: Path, output_dir: Path) -> Tuple[bool, str]:
        """
        Compile a single source file.
        Returns (success, output_message).
        """
        print(f"  Compiling {source_file.name}...")

        try:
            # Import Lament modules
            sys.path.insert(0, str(Path(__file__).parent.parent))
            from lament.lexer import Lexer
            from lament.parser import Parser
            from lament.bytecode import BytecodeCompiler

            # Read source
            with open(source_file, 'r', encoding='utf-8') as f:
                source = f.read()

            # Lex
            lexer = Lexer(source)
            tokens = lexer.tokenize()

            # Parse
            parser = Parser(tokens)
            ast = parser.parse()

            # Compile to bytecode
            compiler = BytecodeCompiler()
            bytecode = compiler.compile(ast)

            # Save bytecode
            output_file = output_dir / f"{source_file.stem}.lmc"
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'wb') as f:
                pickle.dump(bytecode, f)

            return True, f"Compiled to {output_file}"

        except Exception as e:
            return False, f"Compilation failed: {e}"

    def compile_project(self, source_files: List[SourceFile],
                       output_dir: Path) -> Tuple[bool, List[str]]:
        """
        Compile multiple source files.
        Returns (success, messages).
        """
        messages = []
        success = True

        for source_file in source_files:
            file_success, message = self.compile_file(source_file.path, output_dir)
            messages.append(message)
            if not file_success:
                success = False
                if self.config.warnings_as_errors:
                    break

        return success, messages


# ============================================================================
# LINKER
# ============================================================================

class Linker:
    """Links compiled modules into an executable."""

    def __init__(self, config: BuildConfig):
        """Initialize linker."""
        self.config = config

    def link(self, compiled_files: List[Path], output_file: Path) -> Tuple[bool, str]:
        """
        Link compiled bytecode files into an executable.
        Returns (success, message).
        """
        print(f"  Linking {len(compiled_files)} file(s)...")

        try:
            # Load all bytecode modules
            modules = {}
            for compiled_file in compiled_files:
                with open(compiled_file, 'rb') as f:
                    bytecode = pickle.load(f)
                module_name = compiled_file.stem
                modules[module_name] = bytecode

            # Create executable wrapper
            wrapper = self._create_executable_wrapper(modules)

            # Write executable
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                f.write(wrapper)

            # Make executable on Unix-like systems
            if sys.platform != 'win32':
                os.chmod(output_file, 0o755)

            return True, f"Created executable: {output_file}"

        except Exception as e:
            return False, f"Linking failed: {e}"

    def _create_executable_wrapper(self, modules: Dict[str, Any]) -> str:
        """Create a Python wrapper script for the executable."""
        wrapper = f'''#!/usr/bin/env python3
"""
Lament Executable
Generated by Lament Build System
Build time: {datetime.now().isoformat()}
"""

import sys
import pickle
from pathlib import Path

# Add Lament to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main entry point."""
    try:
        from lament.bytecode import BytecodeVM

        # Load entry module
        entry_module = "{self.config.entry_point.stem}"

        # Embedded modules
        modules = pickle.loads({pickle.dumps(modules)!r})

        if entry_module not in modules:
            print(f"Error: Entry module '{{entry_module}}' not found")
            sys.exit(1)

        # Create VM and execute
        vm = BytecodeVM()
        bytecode = modules[entry_module]
        result = vm.execute(bytecode)

        return 0

    except Exception as e:
        print(f"Runtime error: {{e}}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
'''
        return wrapper


# ============================================================================
# BUILD SYSTEM
# ============================================================================

class BuildSystem:
    """Main build system orchestrator."""

    def __init__(self, project_dir: Optional[Path] = None):
        """Initialize build system."""
        self.project_dir = project_dir or Path.cwd()
        self.build_dir = self.project_dir / "build"
        self.cache_file = self.build_dir / ".build_cache"

        # Load configuration
        self.config_file = self.project_dir / "build.lament"
        self.config = self._load_config()

        # Initialize components
        self.cache = BuildCache(self.cache_file)
        self.analyzer = DependencyAnalyzer(self.config.source_dirs)
        self.compiler = LamentCompiler(self.config)
        self.linker = Linker(self.config)

    def _load_config(self) -> BuildConfig:
        """Load or create build configuration."""
        if self.config_file.exists():
            return BuildConfig.from_file(self.config_file)

        # Create default config
        return BuildConfig(
            name=self.project_dir.name,
            target=BuildTarget.EXECUTABLE,
            entry_point=Path("main.lament"),
            output_dir=self.build_dir / "out",
            source_dirs=[self.project_dir / "src", self.project_dir]
        )

    def discover_sources(self) -> List[SourceFile]:
        """Discover all source files in the project."""
        source_files = []

        for source_dir in self.config.source_dirs:
            if not source_dir.exists():
                continue

            for pattern in self.config.include_patterns:
                for path in source_dir.glob(pattern):
                    if path.is_file() and not self._is_excluded(path):
                        source_file = SourceFile.from_path(path)
                        # Analyze dependencies
                        source_file.dependencies = self.analyzer.analyze(path)
                        source_files.append(source_file)

        return source_files

    def _is_excluded(self, path: Path) -> bool:
        """Check if a path should be excluded."""
        for pattern in self.config.exclude_patterns:
            if path.match(pattern):
                return True
        return False

    def build(self, incremental: bool = True, clean: bool = False) -> bool:
        """
        Build the project.

        Args:
            incremental: Use incremental builds
            clean: Clean before building

        Returns:
            True if build succeeded
        """
        print(f"Building {self.config.name}...")
        start_time = time.time()

        # Clean if requested
        if clean:
            self.clean()

        # Create output directory
        self.config.output_dir.mkdir(parents=True, exist_ok=True)

        # Discover sources
        print("\nDiscovering source files...")
        source_files = self.discover_sources()
        print(f"Found {len(source_files)} source file(s)")

        # Determine which files need compilation
        if incremental:
            files_to_compile = [
                sf for sf in source_files
                if sf.needs_rebuild(self.cache)
            ]
            print(f"Need to compile {len(files_to_compile)} file(s)")
        else:
            files_to_compile = source_files

        if not files_to_compile and incremental:
            print("Nothing to compile (use --clean to force rebuild)")
            return True

        # Compile
        print("\nCompiling...")
        success, messages = self.compiler.compile_project(
            files_to_compile,
            self.config.output_dir
        )

        for msg in messages:
            print(f"  {msg}")

        if not success:
            print("\nBuild failed!")
            return False

        # Update cache
        for source_file in files_to_compile:
            self.cache.update_file(source_file)
        self.cache.save()

        # Link if building executable
        if self.config.target == BuildTarget.EXECUTABLE:
            print("\nLinking...")
            compiled_files = list(self.config.output_dir.glob("*.lmc"))
            output_file = self.build_dir / self.config.name

            link_success, link_message = self.linker.link(
                compiled_files,
                output_file
            )

            print(f"  {link_message}")

            if not link_success:
                print("\nBuild failed!")
                return False

        # Build summary
        elapsed = time.time() - start_time
        print(f"\nBuild completed successfully in {elapsed:.2f}s")
        return True

    def clean(self) -> None:
        """Clean build artifacts."""
        print("Cleaning build artifacts...")

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
            print(f"Removed {self.build_dir}")

        self.cache.clear()
        print("Build cache cleared")

    def run(self) -> int:
        """Build and run the executable."""
        if self.config.target != BuildTarget.EXECUTABLE:
            print("Cannot run non-executable target")
            return 1

        # Build first
        if not self.build():
            return 1

        # Run
        executable = self.build_dir / self.config.name
        if not executable.exists():
            print(f"Executable not found: {executable}")
            return 1

        print(f"\nRunning {executable}...")
        print("=" * 60)

        try:
            result = subprocess.run([str(executable)], check=False)
            return result.returncode
        except Exception as e:
            print(f"Error running executable: {e}")
            return 1


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Build System - Forging Emotional Executables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-build build                 Build the project
  lament-build build --clean         Clean and build
  lament-build build --no-incremental  Full rebuild
  lament-build run                   Build and run
  lament-build clean                 Clean build artifacts
        """
    )

    parser.add_argument('--version', action='version', version='lament-build 1.0.0')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Build command
    build_parser = subparsers.add_parser('build', help='Build the project')
    build_parser.add_argument('--clean', action='store_true', help='Clean before building')
    build_parser.add_argument('--no-incremental', action='store_true',
                             help='Disable incremental builds')

    # Run command
    subparsers.add_parser('run', help='Build and run the project')

    # Clean command
    subparsers.add_parser('clean', help='Clean build artifacts')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create build system
    build_system = BuildSystem()

    # Execute command
    if args.command == 'build':
        success = build_system.build(
            incremental=not args.no_incremental,
            clean=args.clean
        )
        sys.exit(0 if success else 1)

    elif args.command == 'run':
        sys.exit(build_system.run())

    elif args.command == 'clean':
        build_system.clean()


if __name__ == '__main__':
    main()
