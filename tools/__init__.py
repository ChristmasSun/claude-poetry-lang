"""
Lament Language Development Tools & Package Management System
==============================================================

This package provides development tools and package management for Lament:

Development Tools:
- Code Formatter
- Linter
- Language Server Protocol
- Interactive Debugger
- Profiler
- Documentation Generator

Package Management System:
- Package Manager (lament-pkg): Install, uninstall, update packages
- Package Registry (lament-registry): Search, publish, manage packages
- Build System (lament-build): Compile, link, create executables

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

__version__ = "1.0.0"

# Package Management System Exports
from tools.package_manager import (
    PackageManager,
    Version,
    VersionConstraint,
    PackageMetadata,
    PackageDependency,
    LockFile,
    LockedPackage,
    DependencyResolver
)

from tools.registry import (
    Registry,
    RegistryConfig,
    RegistryPackageInfo,
    LocalRegistryBackend,
    RemoteRegistryBackend
)

from tools.builder import (
    BuildSystem,
    BuildConfig,
    BuildTarget,
    SourceFile,
    BuildCache,
    DependencyAnalyzer,
    LamentCompiler,
    Linker
)

__all__ = [
    # Package Manager
    'PackageManager',
    'Version',
    'VersionConstraint',
    'PackageMetadata',
    'PackageDependency',
    'LockFile',
    'LockedPackage',
    'DependencyResolver',

    # Registry
    'Registry',
    'RegistryConfig',
    'RegistryPackageInfo',
    'LocalRegistryBackend',
    'RemoteRegistryBackend',

    # Builder
    'BuildSystem',
    'BuildConfig',
    'BuildTarget',
    'SourceFile',
    'BuildCache',
    'DependencyAnalyzer',
    'LamentCompiler',
    'Linker',
]
