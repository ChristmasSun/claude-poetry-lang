#!/usr/bin/env python3
"""
Lament Binary Builder - Forging Standalone Executables

Compiles Lament programs into standalone, platform-specific binary executables
with embedded runtime, dependencies, and resources. Supports compression,
optimization, debug symbol management, and metadata embedding.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import hashlib
import json
import os
import pickle
import platform
import shutil
import struct
import subprocess
import sys
import zipfile
import zlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, BinaryIO
import tempfile


# ============================================================================
# PLATFORM DEFINITIONS
# ============================================================================

class Platform(Enum):
    """Target platforms for binary building."""
    LINUX_X86_64 = "linux-x86_64"
    LINUX_ARM64 = "linux-arm64"
    LINUX_ARM = "linux-arm"
    MACOS_X86_64 = "macos-x86_64"
    MACOS_ARM64 = "macos-arm64"
    WINDOWS_X86_64 = "windows-x86_64"
    WINDOWS_X86 = "windows-x86"

    @property
    def is_windows(self) -> bool:
        return self.value.startswith("windows")

    @property
    def is_macos(self) -> bool:
        return self.value.startswith("macos")

    @property
    def is_linux(self) -> bool:
        return self.value.startswith("linux")

    @property
    def executable_extension(self) -> str:
        return ".exe" if self.is_windows else ""

    @classmethod
    def current(cls) -> 'Platform':
        """Detect current platform."""
        system = platform.system().lower()
        machine = platform.machine().lower()

        if system == "linux":
            if "aarch64" in machine or "arm64" in machine:
                return cls.LINUX_ARM64
            elif "arm" in machine:
                return cls.LINUX_ARM
            return cls.LINUX_X86_64
        elif system == "darwin":
            if "arm64" in machine:
                return cls.MACOS_ARM64
            return cls.MACOS_X86_64
        elif system == "windows":
            if "64" in machine:
                return cls.WINDOWS_X86_64
            return cls.WINDOWS_X86

        raise ValueError(f"Unsupported platform: {system}/{machine}")


class CompressionLevel(Enum):
    """Compression levels for binary output."""
    NONE = 0
    FAST = 3
    BALANCED = 6
    MAXIMUM = 9


class OptimizationLevel(Enum):
    """Optimization levels for binary building."""
    DEBUG = 0          # No optimization, debug info
    BASIC = 1          # Basic optimizations
    STANDARD = 2       # Standard optimizations
    AGGRESSIVE = 3     # Aggressive optimizations


# ============================================================================
# RESOURCE MANAGEMENT
# ============================================================================

@dataclass
class Resource:
    """Represents an embedded resource."""
    name: str
    path: Path
    data: bytes
    compressed: bool = False
    original_size: int = 0
    compressed_size: int = 0

    @staticmethod
    def from_file(path: Path, compress: bool = True) -> 'Resource':
        """Create resource from file."""
        with open(path, 'rb') as f:
            data = f.read()

        original_size = len(data)
        compressed_data = data
        is_compressed = False

        if compress and original_size > 1024:  # Only compress files > 1KB
            compressed = zlib.compress(data, level=9)
            if len(compressed) < original_size:
                compressed_data = compressed
                is_compressed = True

        return Resource(
            name=path.name,
            path=path,
            data=compressed_data,
            compressed=is_compressed,
            original_size=original_size,
            compressed_size=len(compressed_data)
        )


class ResourceBundle:
    """Bundle of embedded resources."""

    def __init__(self):
        """Initialize resource bundle."""
        self.resources: Dict[str, Resource] = {}

    def add_file(self, path: Path, name: Optional[str] = None,
                 compress: bool = True) -> None:
        """Add a file to the bundle."""
        resource = Resource.from_file(path, compress)
        if name:
            resource.name = name
        self.resources[resource.name] = resource

    def add_directory(self, path: Path, pattern: str = "*",
                     compress: bool = True) -> None:
        """Add all files in a directory matching pattern."""
        for file_path in path.glob(pattern):
            if file_path.is_file():
                relative_name = str(file_path.relative_to(path))
                self.add_file(file_path, relative_name, compress)

    def serialize(self) -> bytes:
        """Serialize bundle to bytes."""
        # Format: [count:4][resource1][resource2]...
        # Each resource: [name_len:4][name][compressed:1][orig_size:8][comp_size:8][data]
        data = struct.pack('<I', len(self.resources))

        for resource in self.resources.values():
            name_bytes = resource.name.encode('utf-8')
            data += struct.pack('<I', len(name_bytes))
            data += name_bytes
            data += struct.pack('<?QQ',
                              resource.compressed,
                              resource.original_size,
                              resource.compressed_size)
            data += resource.data

        return data

    def total_size(self) -> int:
        """Get total size of all resources."""
        return sum(r.compressed_size for r in self.resources.values())

    def compression_ratio(self) -> float:
        """Get overall compression ratio."""
        original = sum(r.original_size for r in self.resources.values())
        compressed = sum(r.compressed_size for r in self.resources.values())
        if original == 0:
            return 1.0
        return compressed / original


# ============================================================================
# METADATA
# ============================================================================

@dataclass
class BinaryMetadata:
    """Metadata embedded in binary."""
    name: str
    version: str
    author: Optional[str] = None
    description: Optional[str] = None
    copyright: Optional[str] = None
    build_date: str = field(default_factory=lambda: datetime.now().isoformat())
    lament_version: str = "2.0.0"
    platform: str = field(default_factory=lambda: Platform.current().value)
    optimization: str = "standard"
    debug: bool = False
    icon_path: Optional[Path] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'version': self.version,
            'author': self.author,
            'description': self.description,
            'copyright': self.copyright,
            'build_date': self.build_date,
            'lament_version': self.lament_version,
            'platform': self.platform,
            'optimization': self.optimization,
            'debug': self.debug,
            'custom_fields': self.custom_fields
        }

    def serialize(self) -> bytes:
        """Serialize to JSON bytes."""
        return json.dumps(self.to_dict(), indent=2).encode('utf-8')


# ============================================================================
# RUNTIME BUNDLER
# ============================================================================

class RuntimeBundler:
    """Bundles Python runtime and Lament interpreter."""

    def __init__(self, target_platform: Platform):
        """Initialize runtime bundler."""
        self.target_platform = target_platform
        self.python_executable = sys.executable
        self.lament_dir = Path(__file__).parent.parent / "lament"

    def bundle(self, output_dir: Path) -> Path:
        """
        Create runtime bundle.
        Returns path to bundled runtime.
        """
        print("  Bundling Python runtime and Lament interpreter...")

        runtime_dir = output_dir / "runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)

        # Copy Lament modules
        self._copy_lament_modules(runtime_dir)

        # Create minimal Python runtime descriptor
        runtime_info = {
            'python_version': sys.version,
            'python_executable': self.python_executable,
            'platform': self.target_platform.value,
            'modules': self._get_required_modules()
        }

        runtime_info_file = runtime_dir / "runtime.json"
        with open(runtime_info_file, 'w') as f:
            json.dump(runtime_info, f, indent=2)

        return runtime_dir

    def _copy_lament_modules(self, runtime_dir: Path) -> None:
        """Copy Lament interpreter modules."""
        lament_dest = runtime_dir / "lament"
        lament_dest.mkdir(parents=True, exist_ok=True)

        # Copy all .py files from lament directory
        for py_file in self.lament_dir.glob("*.py"):
            shutil.copy2(py_file, lament_dest / py_file.name)

        # Copy __init__.py
        init_file = self.lament_dir / "__init__.py"
        if init_file.exists():
            shutil.copy2(init_file, lament_dest / "__init__.py")

    def _get_required_modules(self) -> List[str]:
        """Get list of required Python modules."""
        return [
            'sys', 'os', 'pickle', 'struct', 'zlib', 'json',
            're', 'math', 'collections', 'dataclasses', 'enum',
            'pathlib', 'typing', 'datetime'
        ]


# ============================================================================
# DEPENDENCY RESOLVER
# ============================================================================

class DependencyResolver:
    """Resolves and bundles dependencies."""

    def __init__(self):
        """Initialize dependency resolver."""
        self.dependencies: Set[Path] = set()

    def analyze(self, source_file: Path) -> List[Path]:
        """Analyze source file and find dependencies."""
        deps = []

        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Look for breathe/import statements
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('breathe'):
                    # Extract module name
                    parts = line.split('"')
                    if len(parts) >= 2:
                        module_name = parts[1]
                        dep_path = self._resolve_module(module_name)
                        if dep_path:
                            deps.append(dep_path)
                            self.dependencies.add(dep_path)

        except Exception as e:
            print(f"    Warning: Could not analyze {source_file}: {e}")

        return deps

    def _resolve_module(self, module_name: str) -> Optional[Path]:
        """Resolve module name to file path."""
        # Check in standard library
        stdlib_dir = Path(__file__).parent.parent / "stdlib"
        stdlib_path = stdlib_dir / f"{module_name}.lament"
        if stdlib_path.exists():
            return stdlib_path

        # Check relative path
        relative_path = Path(f"{module_name}.lament")
        if relative_path.exists():
            return relative_path.resolve()

        return None


# ============================================================================
# BOOTSTRAP CODE GENERATOR
# ============================================================================

class BootstrapGenerator:
    """Generates bootstrap code for standalone executables."""

    def __init__(self, metadata: BinaryMetadata):
        """Initialize bootstrap generator."""
        self.metadata = metadata

    def generate(self, entry_point: str, has_resources: bool = False) -> str:
        """Generate bootstrap Python code."""
        return f'''#!/usr/bin/env python3
"""
{self.metadata.name} - Standalone Lament Executable
Generated by Lament Binary Builder

Build Date: {self.metadata.build_date}
Version: {self.metadata.version}
Platform: {self.metadata.platform}
"""

import sys
import os
import pickle
import struct
import zlib
from pathlib import Path
from typing import Dict, Any


# ============================================================================
# EMBEDDED RESOURCES
# ============================================================================

def extract_resources() -> Dict[str, bytes]:
    """Extract embedded resources from executable."""
    resources = {{}}

    if not {str(has_resources).lower()}:
        return resources

    try:
        # Find resource section marker
        with open(__file__, 'rb') as f:
            content = f.read()

        marker = b'__LAMENT_RESOURCES__'
        offset = content.find(marker)
        if offset == -1:
            return resources

        offset += len(marker)
        data = content[offset:]

        # Parse resource bundle
        count, = struct.unpack('<I', data[:4])
        data = data[4:]

        for _ in range(count):
            name_len, = struct.unpack('<I', data[:4])
            data = data[4:]

            name = data[:name_len].decode('utf-8')
            data = data[name_len:]

            compressed, orig_size, comp_size = struct.unpack('<?QQ', data[:17])
            data = data[17:]

            resource_data = data[:comp_size]
            data = data[comp_size:]

            if compressed:
                resource_data = zlib.decompress(resource_data)

            resources[name] = resource_data

    except Exception as e:
        print(f"Warning: Could not extract resources: {{e}}")

    return resources


# ============================================================================
# EMBEDDED BYTECODE
# ============================================================================

EMBEDDED_BYTECODE = {entry_point}

EMBEDDED_METADATA = {self.metadata.serialize().decode('utf-8')}


# ============================================================================
# RUNTIME INITIALIZATION
# ============================================================================

def init_runtime():
    """Initialize Lament runtime."""
    # Add embedded runtime to path
    runtime_dir = Path(__file__).parent / "runtime"
    if runtime_dir.exists():
        sys.path.insert(0, str(runtime_dir))

    # Extract resources if needed
    global RESOURCES
    RESOURCES = extract_resources()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for executable."""
    try:
        # Initialize runtime
        init_runtime()

        # Import Lament VM
        from lament.bytecode import BytecodeVM

        # Create VM
        vm = BytecodeVM()

        # Execute embedded bytecode
        bytecode = pickle.loads(EMBEDDED_BYTECODE)
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


# ============================================================================
# BINARY BUILDER
# ============================================================================

class BinaryBuilder:
    """Main binary builder class."""

    def __init__(self,
                 entry_point: Path,
                 output: Path,
                 target_platform: Optional[Platform] = None,
                 optimization: OptimizationLevel = OptimizationLevel.STANDARD,
                 compression: CompressionLevel = CompressionLevel.BALANCED):
        """
        Initialize binary builder.

        Args:
            entry_point: Entry point Lament file
            output: Output executable path
            target_platform: Target platform (default: current)
            optimization: Optimization level
            compression: Compression level
        """
        self.entry_point = entry_point
        self.output = output
        self.target_platform = target_platform or Platform.current()
        self.optimization = optimization
        self.compression = compression

        # Components
        self.metadata = BinaryMetadata(
            name=entry_point.stem,
            version="1.0.0",
            optimization=optimization.name.lower(),
            debug=(optimization == OptimizationLevel.DEBUG),
            platform=self.target_platform.value
        )
        self.resources = ResourceBundle()
        self.runtime_bundler = RuntimeBundler(self.target_platform)
        self.dependency_resolver = DependencyResolver()
        self.bootstrap_generator = BootstrapGenerator(self.metadata)

        # Build working directory
        self.build_dir = Path(tempfile.mkdtemp(prefix="lament_build_"))

    def set_metadata(self, **kwargs) -> None:
        """Set metadata fields."""
        for key, value in kwargs.items():
            if hasattr(self.metadata, key):
                setattr(self.metadata, key, value)

    def add_resource(self, path: Path, name: Optional[str] = None) -> None:
        """Add a resource file to embed."""
        self.resources.add_file(path, name)

    def add_resource_directory(self, path: Path, pattern: str = "*") -> None:
        """Add all files in directory as resources."""
        self.resources.add_directory(path, pattern)

    def set_icon(self, icon_path: Path) -> None:
        """Set application icon."""
        self.metadata.icon_path = icon_path

    def build(self) -> bool:
        """
        Build the standalone binary.

        Returns:
            True if build succeeded
        """
        print(f"Building standalone binary for {self.target_platform.value}...")
        print(f"  Entry point: {self.entry_point}")
        print(f"  Output: {self.output}")
        print(f"  Optimization: {self.optimization.name}")
        print(f"  Compression: {self.compression.name}")
        print()

        try:
            # Step 1: Compile entry point to bytecode
            print("[1/7] Compiling entry point...")
            bytecode = self._compile_entry_point()

            # Step 2: Resolve and compile dependencies
            print("[2/7] Resolving dependencies...")
            self._resolve_dependencies()

            # Step 3: Bundle runtime
            print("[3/7] Bundling runtime...")
            runtime_dir = self.runtime_bundler.bundle(self.build_dir)

            # Step 4: Generate bootstrap code
            print("[4/7] Generating bootstrap code...")
            has_resources = len(self.resources.resources) > 0
            bootstrap = self.bootstrap_generator.generate(
                repr(pickle.dumps(bytecode)),
                has_resources
            )

            # Step 5: Create executable
            print("[5/7] Creating executable...")
            self._create_executable(bootstrap)

            # Step 6: Embed resources
            if has_resources:
                print(f"[6/7] Embedding resources ({len(self.resources.resources)} files)...")
                self._embed_resources()
            else:
                print("[6/7] No resources to embed")

            # Step 7: Apply optimizations
            print("[7/7] Applying optimizations...")
            self._optimize()

            # Print summary
            self._print_summary()

            print("\nBinary built successfully!")
            return True

        except Exception as e:
            print(f"\nBuild failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        finally:
            # Cleanup
            if self.build_dir.exists():
                shutil.rmtree(self.build_dir)

    def _compile_entry_point(self) -> Any:
        """Compile entry point to bytecode."""
        sys.path.insert(0, str(Path(__file__).parent.parent))

        from lament.lexer import Lexer
        from lament.parser import Parser
        from lament.bytecode import BytecodeCompiler

        with open(self.entry_point, 'r', encoding='utf-8') as f:
            source = f.read()

        lexer = Lexer(source)
        tokens = lexer.tokenize()

        parser = Parser(tokens)
        ast = parser.parse()

        compiler = BytecodeCompiler()
        bytecode = compiler.compile(ast)

        return bytecode

    def _resolve_dependencies(self) -> None:
        """Resolve all dependencies."""
        self.dependency_resolver.analyze(self.entry_point)

        if self.dependency_resolver.dependencies:
            print(f"    Found {len(self.dependency_resolver.dependencies)} dependencies")

    def _create_executable(self, bootstrap: str) -> None:
        """Create the executable file."""
        self.output.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output, 'w', encoding='utf-8') as f:
            f.write(bootstrap)

        # Make executable on Unix
        if not self.target_platform.is_windows:
            os.chmod(self.output, 0o755)

    def _embed_resources(self) -> None:
        """Embed resources into executable."""
        resource_data = self.resources.serialize()

        with open(self.output, 'ab') as f:
            f.write(b'\n# __LAMENT_RESOURCES__\n')
            f.write(resource_data)

        ratio = self.resources.compression_ratio()
        print(f"    Compression ratio: {ratio:.1%}")

    def _optimize(self) -> None:
        """Apply optimizations to binary."""
        if self.optimization == OptimizationLevel.DEBUG:
            print("    Debug build - no optimizations applied")
            return

        # Strip debug symbols
        if self.optimization.value >= OptimizationLevel.STANDARD.value:
            self._strip_debug_symbols()

        # Apply compression
        if self.compression != CompressionLevel.NONE:
            self._compress_executable()

    def _strip_debug_symbols(self) -> None:
        """Strip debug symbols from executable."""
        print("    Stripping debug symbols...")
        # In Python, this would involve removing docstrings and comments
        # For now, this is a placeholder

    def _compress_executable(self) -> None:
        """Compress the executable."""
        print(f"    Compressing (level {self.compression.value})...")

        # Read executable
        with open(self.output, 'rb') as f:
            data = f.read()

        # Compress
        compressed = zlib.compress(data, level=self.compression.value)

        # Only use if smaller
        if len(compressed) < len(data):
            ratio = len(compressed) / len(data)
            print(f"    Compressed size: {ratio:.1%}")

            # Create self-extracting wrapper
            wrapper = f'''#!/usr/bin/env python3
import zlib
import sys
import os

# Compressed payload
PAYLOAD = {compressed!r}

# Extract and execute
code = zlib.decompress(PAYLOAD).decode('utf-8')
exec(code)
'''

            with open(self.output, 'w') as f:
                f.write(wrapper)

            if not self.target_platform.is_windows:
                os.chmod(self.output, 0o755)

    def _print_summary(self) -> None:
        """Print build summary."""
        print("\n" + "=" * 60)
        print("BUILD SUMMARY")
        print("=" * 60)
        print(f"Name:              {self.metadata.name}")
        print(f"Version:           {self.metadata.version}")
        print(f"Platform:          {self.target_platform.value}")
        print(f"Optimization:      {self.optimization.name}")
        print(f"Output:            {self.output}")
        print(f"Size:              {self.output.stat().st_size:,} bytes")

        if self.resources.resources:
            print(f"Embedded resources: {len(self.resources.resources)} files")
            print(f"Total resource size: {self.resources.total_size():,} bytes")

        print("=" * 60)


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Binary Builder - Forge Standalone Executables",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-build --binary main.lament
  lament-build --binary main.lament --target linux-x86_64
  lament-build --binary main.lament -o myapp --optimize aggressive
  lament-build --binary main.lament --resource assets/ --icon app.ico
        """
    )

    parser.add_argument('--version', action='version', version='lament-build 2.0.0')

    parser.add_argument('--binary', dest='entry_point', type=Path, required=True,
                       help='Entry point Lament file')
    parser.add_argument('-o', '--output', type=Path,
                       help='Output executable path')
    parser.add_argument('--target', type=str, choices=[p.value for p in Platform],
                       help='Target platform (default: current)')

    # Optimization
    parser.add_argument('--optimize', type=str,
                       choices=['debug', 'basic', 'standard', 'aggressive'],
                       default='standard',
                       help='Optimization level (default: standard)')
    parser.add_argument('--compress', type=str,
                       choices=['none', 'fast', 'balanced', 'maximum'],
                       default='balanced',
                       help='Compression level (default: balanced)')

    # Resources
    parser.add_argument('--resource', type=Path, action='append', dest='resources',
                       help='Add resource file or directory (can be used multiple times)')
    parser.add_argument('--icon', type=Path,
                       help='Application icon file')

    # Metadata
    parser.add_argument('--name', type=str,
                       help='Application name')
    parser.add_argument('--version-str', type=str,
                       help='Application version')
    parser.add_argument('--author', type=str,
                       help='Author name')
    parser.add_argument('--description', type=str,
                       help='Application description')

    args = parser.parse_args()

    # Validate entry point
    if not args.entry_point.exists():
        print(f"Error: Entry point not found: {args.entry_point}")
        return 1

    # Determine output path
    if not args.output:
        target_platform = Platform(args.target) if args.target else Platform.current()
        ext = target_platform.executable_extension
        args.output = Path(f"{args.entry_point.stem}{ext}")

    # Parse optimization level
    optimization_map = {
        'debug': OptimizationLevel.DEBUG,
        'basic': OptimizationLevel.BASIC,
        'standard': OptimizationLevel.STANDARD,
        'aggressive': OptimizationLevel.AGGRESSIVE
    }
    optimization = optimization_map[args.optimize]

    # Parse compression level
    compression_map = {
        'none': CompressionLevel.NONE,
        'fast': CompressionLevel.FAST,
        'balanced': CompressionLevel.BALANCED,
        'maximum': CompressionLevel.MAXIMUM
    }
    compression = compression_map[args.compress]

    # Parse target platform
    target_platform = Platform(args.target) if args.target else None

    # Create builder
    builder = BinaryBuilder(
        entry_point=args.entry_point,
        output=args.output,
        target_platform=target_platform,
        optimization=optimization,
        compression=compression
    )

    # Set metadata
    metadata_kwargs = {}
    if args.name:
        metadata_kwargs['name'] = args.name
    if args.version_str:
        metadata_kwargs['version'] = args.version_str
    if args.author:
        metadata_kwargs['author'] = args.author
    if args.description:
        metadata_kwargs['description'] = args.description

    if metadata_kwargs:
        builder.set_metadata(**metadata_kwargs)

    # Add resources
    if args.resources:
        for resource_path in args.resources:
            if not resource_path.exists():
                print(f"Warning: Resource not found: {resource_path}")
                continue

            if resource_path.is_dir():
                builder.add_resource_directory(resource_path)
            else:
                builder.add_resource(resource_path)

    # Set icon
    if args.icon:
        if args.icon.exists():
            builder.set_icon(args.icon)
        else:
            print(f"Warning: Icon not found: {args.icon}")

    # Build
    success = builder.build()
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
