#!/usr/bin/env python3
"""
Lament Package Manager - Poetry for the Soul

A comprehensive package management system for the Lament programming language.
Handles installation, dependency resolution, versioning, and lock files.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import json
import os
import hashlib
import shutil
import sys
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from collections import defaultdict
import urllib.request
import urllib.error


# ============================================================================
# SEMANTIC VERSIONING
# ============================================================================

@dataclass
class Version:
    """Represents a semantic version number."""
    major: int
    minor: int
    patch: int
    prerelease: str = ""
    build: str = ""

    @staticmethod
    def parse(version_str: str) -> 'Version':
        """Parse a semantic version string like '1.2.3-alpha+build'."""
        # Remove 'v' prefix if present
        if version_str.startswith('v'):
            version_str = version_str[1:]

        # Split on '+' for build metadata
        if '+' in version_str:
            version_str, build = version_str.split('+', 1)
        else:
            build = ""

        # Split on '-' for prerelease
        if '-' in version_str:
            version_str, prerelease = version_str.split('-', 1)
        else:
            prerelease = ""

        # Parse major.minor.patch
        parts = version_str.split('.')
        if len(parts) != 3:
            raise ValueError(f"Invalid version string: {version_str}")

        major, minor, patch = map(int, parts)
        return Version(major, minor, patch, prerelease, build)

    def __str__(self) -> str:
        """Convert to string representation."""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version

    def __lt__(self, other: 'Version') -> bool:
        """Compare versions for sorting."""
        if self.major != other.major:
            return self.major < other.major
        if self.minor != other.minor:
            return self.minor < other.minor
        if self.patch != other.patch:
            return self.patch < other.patch

        # Versions without prerelease are greater than those with
        if not self.prerelease and other.prerelease:
            return False
        if self.prerelease and not other.prerelease:
            return True

        return self.prerelease < other.prerelease

    def __eq__(self, other: object) -> bool:
        """Check version equality."""
        if not isinstance(other, Version):
            return False
        return (self.major == other.major and
                self.minor == other.minor and
                self.patch == other.patch and
                self.prerelease == other.prerelease)

    def __le__(self, other: 'Version') -> bool:
        return self < other or self == other

    def __gt__(self, other: 'Version') -> bool:
        return not self <= other

    def __ge__(self, other: 'Version') -> bool:
        return not self < other


@dataclass
class VersionConstraint:
    """Represents a version constraint like '^1.2.3' or '>=1.0.0'."""
    operator: str
    version: Version

    @staticmethod
    def parse(constraint_str: str) -> 'VersionConstraint':
        """Parse a version constraint string."""
        constraint_str = constraint_str.strip()

        # Handle special operators
        if constraint_str.startswith('^'):
            return VersionConstraint('^', Version.parse(constraint_str[1:]))
        elif constraint_str.startswith('~'):
            return VersionConstraint('~', Version.parse(constraint_str[1:]))
        elif constraint_str.startswith('>='):
            return VersionConstraint('>=', Version.parse(constraint_str[2:]))
        elif constraint_str.startswith('<='):
            return VersionConstraint('<=', Version.parse(constraint_str[2:]))
        elif constraint_str.startswith('>'):
            return VersionConstraint('>', Version.parse(constraint_str[1:]))
        elif constraint_str.startswith('<'):
            return VersionConstraint('<', Version.parse(constraint_str[1:]))
        elif constraint_str.startswith('='):
            return VersionConstraint('=', Version.parse(constraint_str[1:]))
        else:
            # Exact version
            return VersionConstraint('=', Version.parse(constraint_str))

    def satisfies(self, version: Version) -> bool:
        """Check if a version satisfies this constraint."""
        if self.operator == '=':
            return version == self.version
        elif self.operator == '>':
            return version > self.version
        elif self.operator == '<':
            return version < self.version
        elif self.operator == '>=':
            return version >= self.version
        elif self.operator == '<=':
            return version <= self.version
        elif self.operator == '^':
            # Compatible with version (same major for 1.x.x, same minor for 0.x.x)
            if self.version.major > 0:
                return (version.major == self.version.major and
                       version >= self.version)
            else:
                return (version.major == 0 and
                       version.minor == self.version.minor and
                       version >= self.version)
        elif self.operator == '~':
            # Approximately equivalent (same major and minor)
            return (version.major == self.version.major and
                   version.minor == self.version.minor and
                   version >= self.version)
        return False

    def __str__(self) -> str:
        """Convert to string representation."""
        return f"{self.operator}{self.version}"


# ============================================================================
# PACKAGE METADATA
# ============================================================================

@dataclass
class PackageDependency:
    """Represents a package dependency."""
    name: str
    constraint: VersionConstraint
    optional: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'version': str(self.constraint),
            'optional': self.optional
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PackageDependency':
        """Create from dictionary."""
        return PackageDependency(
            name=data['name'],
            constraint=VersionConstraint.parse(data['version']),
            optional=data.get('optional', False)
        )


@dataclass
class PackageMetadata:
    """Metadata for a Lament package."""
    name: str
    version: Version
    description: str = ""
    author: str = ""
    license: str = ""
    homepage: str = ""
    repository: str = ""
    keywords: List[str] = field(default_factory=list)
    dependencies: List[PackageDependency] = field(default_factory=list)
    dev_dependencies: List[PackageDependency] = field(default_factory=list)
    entry_point: str = ""
    include: List[str] = field(default_factory=lambda: ["**/*.lament"])
    exclude: List[str] = field(default_factory=lambda: ["tests/**", "examples/**"])
    build_script: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'version': str(self.version),
            'description': self.description,
            'author': self.author,
            'license': self.license,
            'homepage': self.homepage,
            'repository': self.repository,
            'keywords': self.keywords,
            'dependencies': [dep.to_dict() for dep in self.dependencies],
            'dev_dependencies': [dep.to_dict() for dep in self.dev_dependencies],
            'entry_point': self.entry_point,
            'include': self.include,
            'exclude': self.exclude,
            'build_script': self.build_script
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PackageMetadata':
        """Create from dictionary."""
        return PackageMetadata(
            name=data['name'],
            version=Version.parse(data['version']),
            description=data.get('description', ''),
            author=data.get('author', ''),
            license=data.get('license', ''),
            homepage=data.get('homepage', ''),
            repository=data.get('repository', ''),
            keywords=data.get('keywords', []),
            dependencies=[PackageDependency.from_dict(d) for d in data.get('dependencies', [])],
            dev_dependencies=[PackageDependency.from_dict(d) for d in data.get('dev_dependencies', [])],
            entry_point=data.get('entry_point', ''),
            include=data.get('include', ["**/*.lament"]),
            exclude=data.get('exclude', ["tests/**", "examples/**"]),
            build_script=data.get('build_script', '')
        )

    @staticmethod
    def from_file(filepath: Path) -> 'PackageMetadata':
        """Load package metadata from a file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return PackageMetadata.from_dict(data)

    def to_file(self, filepath: Path) -> None:
        """Save package metadata to a file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# ============================================================================
# LOCK FILE
# ============================================================================

@dataclass
class LockedPackage:
    """Represents a locked package version."""
    name: str
    version: Version
    checksum: str
    dependencies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'version': str(self.version),
            'checksum': self.checksum,
            'dependencies': self.dependencies
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LockedPackage':
        """Create from dictionary."""
        return LockedPackage(
            name=data['name'],
            version=Version.parse(data['version']),
            checksum=data['checksum'],
            dependencies=data.get('dependencies', [])
        )


@dataclass
class LockFile:
    """Represents a lock file with exact package versions."""
    packages: Dict[str, LockedPackage] = field(default_factory=dict)
    created_at: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'created_at': self.created_at,
            'packages': {name: pkg.to_dict() for name, pkg in self.packages.items()}
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LockFile':
        """Create from dictionary."""
        packages = {name: LockedPackage.from_dict(pkg)
                   for name, pkg in data.get('packages', {}).items()}
        return LockFile(
            packages=packages,
            created_at=data.get('created_at', '')
        )

    @staticmethod
    def from_file(filepath: Path) -> 'LockFile':
        """Load lock file."""
        if not filepath.exists():
            return LockFile()
        with open(filepath, 'r') as f:
            data = json.load(f)
        return LockFile.from_dict(data)

    def to_file(self, filepath: Path) -> None:
        """Save lock file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


# ============================================================================
# DEPENDENCY RESOLUTION
# ============================================================================

class DependencyResolver:
    """Resolves package dependencies using a topological sort algorithm."""

    def __init__(self, registry):
        """Initialize resolver with a registry."""
        self.registry = registry

    def resolve(self, root_package: PackageMetadata) -> Dict[str, Version]:
        """
        Resolve all dependencies for a package.
        Returns a dictionary mapping package names to resolved versions.
        """
        # Build dependency graph
        graph = defaultdict(list)
        in_degree = defaultdict(int)
        versions = {}

        # Queue of packages to process
        queue = [(root_package.name, root_package.version, root_package.dependencies)]
        visited = set()

        while queue:
            pkg_name, pkg_version, dependencies = queue.pop(0)

            if pkg_name in visited:
                continue
            visited.add(pkg_name)

            versions[pkg_name] = pkg_version

            for dep in dependencies:
                if dep.optional:
                    continue

                # Find a version that satisfies the constraint
                available_versions = self.registry.get_versions(dep.name)
                if not available_versions:
                    raise ValueError(f"Package not found: {dep.name}")

                # Filter versions that satisfy the constraint
                compatible = [v for v in available_versions if dep.constraint.satisfies(v)]
                if not compatible:
                    raise ValueError(
                        f"No version of {dep.name} satisfies {dep.constraint}"
                    )

                # Choose the latest compatible version
                chosen_version = max(compatible)

                # Add edge to graph
                graph[pkg_name].append(dep.name)
                in_degree[dep.name] += 1

                # Get metadata for this dependency
                dep_metadata = self.registry.get_package(dep.name, chosen_version)
                if dep_metadata:
                    queue.append((dep.name, chosen_version, dep_metadata.dependencies))

        return versions

    def topological_sort(self, versions: Dict[str, Version]) -> List[str]:
        """
        Perform topological sort on resolved dependencies.
        Returns installation order.
        """
        # Build graph from resolved versions
        graph = defaultdict(list)
        in_degree = defaultdict(int)

        for pkg_name in versions:
            in_degree[pkg_name] = 0

        # Build edges
        for pkg_name, version in versions.items():
            metadata = self.registry.get_package(pkg_name, version)
            if metadata:
                for dep in metadata.dependencies:
                    if not dep.optional and dep.name in versions:
                        graph[dep.name].append(pkg_name)
                        in_degree[pkg_name] += 1

        # Kahn's algorithm
        queue = [pkg for pkg in versions if in_degree[pkg] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            for neighbor in graph[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(versions):
            raise ValueError("Circular dependency detected")

        return result


# ============================================================================
# PACKAGE MANAGER
# ============================================================================

class PackageManager:
    """Main package manager for Lament."""

    def __init__(self, base_dir: Optional[Path] = None,
                 verify_signatures: bool = True,
                 skip_security: bool = False):
        """Initialize package manager."""
        self.base_dir = base_dir or Path.cwd()
        self.packages_dir = self.base_dir / ".lament" / "packages"
        self.cache_dir = self.base_dir / ".lament" / "cache"
        self.package_file = self.base_dir / "package.lament"
        self.lock_file = self.base_dir / "package-lock.lament"
        self.verify_signatures = verify_signatures
        self.skip_security = skip_security

        # Create directories
        self.packages_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Import registry here to avoid circular dependency
        from tools.registry import Registry
        self.registry = Registry(cache_dir=self.cache_dir)
        self.resolver = DependencyResolver(self.registry)

    def init(self, name: str, version: str = "0.1.0") -> None:
        """Initialize a new package."""
        if self.package_file.exists():
            print(f"Package already initialized: {self.package_file}")
            return

        metadata = PackageMetadata(
            name=name,
            version=Version.parse(version),
            description="A Lament package",
            author="",
            license="MIT",
            dependencies=[],
            dev_dependencies=[]
        )

        metadata.to_file(self.package_file)
        print(f"Initialized package: {name} v{version}")
        print(f"Created: {self.package_file}")

    def install(self, package_spec: Optional[str] = None, dev: bool = False) -> None:
        """
        Install a package and its dependencies.

        Args:
            package_spec: Package specification like 'package@^1.0.0' or None for all deps
            dev: Whether to install as dev dependency
        """
        # Run security scan if not skipped
        if not self.skip_security and self.package_file.exists():
            print("\nRunning security scan...")
            try:
                from tools.security import SecurityScanner
                scanner = SecurityScanner(self.base_dir)
                report = scanner.scan(check_code=False)

                # Warn about critical/high issues
                if report.summary['critical'] > 0 or report.summary['high'] > 0:
                    print(f"\nWARNING: Found {report.summary['critical']} critical and "
                          f"{report.summary['high']} high severity security issues!")
                    print("Run 'lament-audit' for details")

                    if not self._confirm("Continue with installation?"):
                        print("Installation cancelled")
                        return
            except ImportError:
                print("Security scanner not available")

        # Load package metadata
        if not self.package_file.exists():
            print("No package.lament found. Run 'lament-pkg init' first.")
            return

        metadata = PackageMetadata.from_file(self.package_file)

        if package_spec:
            # Install specific package
            if '@' in package_spec:
                name, version_str = package_spec.split('@', 1)
                constraint = VersionConstraint.parse(version_str)
            else:
                name = package_spec
                constraint = VersionConstraint.parse('^1.0.0')

            dep = PackageDependency(name=name, constraint=constraint)

            # Add to metadata
            if dev:
                metadata.dev_dependencies.append(dep)
            else:
                metadata.dependencies.append(dep)

            metadata.to_file(self.package_file)
            print(f"Added {name} {constraint} to {'dev ' if dev else ''}dependencies")

        # Resolve all dependencies
        print("\nResolving dependencies...")
        try:
            resolved = self.resolver.resolve(metadata)
            install_order = self.resolver.topological_sort(resolved)
        except ValueError as e:
            print(f"Error resolving dependencies: {e}")
            return

        # Install packages
        lock_file = LockFile(created_at=datetime.now().isoformat())

        for pkg_name in install_order:
            if pkg_name == metadata.name:
                continue

            version = resolved[pkg_name]
            print(f"Installing {pkg_name}@{version}...")

            try:
                checksum = self._install_package(pkg_name, version)

                # Get dependencies for lock file
                pkg_metadata = self.registry.get_package(pkg_name, version)
                dep_names = [d.name for d in pkg_metadata.dependencies if not d.optional]

                lock_file.packages[pkg_name] = LockedPackage(
                    name=pkg_name,
                    version=version,
                    checksum=checksum,
                    dependencies=dep_names
                )

                print(f"✓ Installed {pkg_name}@{version}")
            except Exception as e:
                print(f"✗ Failed to install {pkg_name}@{version}: {e}")

        # Save lock file
        lock_file.to_file(self.lock_file)
        print(f"\nLock file saved: {self.lock_file}")
        print(f"Installed {len(lock_file.packages)} packages")

    def _install_package(self, name: str, version: Version) -> str:
        """Install a single package and return its checksum."""
        # Download package
        package_data = self.registry.download_package(name, version)

        # Calculate checksum
        checksum = hashlib.sha256(package_data).hexdigest()

        # Extract to packages directory
        pkg_dir = self.packages_dir / f"{name}-{version}"
        pkg_dir.mkdir(parents=True, exist_ok=True)

        # Save package data
        package_file = pkg_dir / "package.tar.gz"
        with open(package_file, 'wb') as f:
            f.write(package_data)

        # Verify signature if enabled
        if self.verify_signatures:
            if not self._verify_package_signature(package_file, name, version):
                if not self._confirm(f"\nSignature verification failed for {name}@{version}. Continue?"):
                    raise Exception("Package signature verification failed")
                else:
                    print(f"WARNING: Installing unverified package {name}@{version}")

        # TODO: Extract tarball
        # For now, just create a marker file
        (pkg_dir / "installed").touch()

        return checksum

    def _verify_package_signature(self, package_file: Path, name: str, version: Version) -> bool:
        """Verify package signature."""
        try:
            from tools.signing import PackageSigner
            signer = PackageSigner()

            # Try to download signature
            sig_file = package_file.with_suffix('.tar.gz.sig')

            if not sig_file.exists():
                print(f"  No signature found for {name}@{version}")
                return False

            result = signer.verify_package(package_file, sig_file)
            if result:
                print(f"  ✓ Signature verified for {name}@{version}")
            else:
                print(f"  ✗ Signature verification failed for {name}@{version}")

            return result
        except ImportError:
            print("  Signature verification not available (cryptography library missing)")
            return False
        except Exception as e:
            print(f"  Signature verification error: {e}")
            return False

    def _confirm(self, message: str) -> bool:
        """Ask user for confirmation."""
        try:
            response = input(f"{message} [y/N]: ").strip().lower()
            return response in ['y', 'yes']
        except (EOFError, KeyboardInterrupt):
            return False

    def uninstall(self, package_name: str) -> None:
        """Uninstall a package."""
        # Load metadata
        if not self.package_file.exists():
            print("No package.lament found.")
            return

        metadata = PackageMetadata.from_file(self.package_file)

        # Remove from dependencies
        metadata.dependencies = [d for d in metadata.dependencies if d.name != package_name]
        metadata.dev_dependencies = [d for d in metadata.dev_dependencies if d.name != package_name]
        metadata.to_file(self.package_file)

        # Remove from lock file
        lock_file = LockFile.from_file(self.lock_file)
        if package_name in lock_file.packages:
            del lock_file.packages[package_name]
            lock_file.to_file(self.lock_file)

        # Remove package directory
        for pkg_dir in self.packages_dir.glob(f"{package_name}-*"):
            shutil.rmtree(pkg_dir)
            print(f"Removed {pkg_dir.name}")

        print(f"Uninstalled {package_name}")

    def update(self, package_name: Optional[str] = None) -> None:
        """Update packages to their latest compatible versions."""
        if not self.package_file.exists():
            print("No package.lament found.")
            return

        metadata = PackageMetadata.from_file(self.package_file)

        if package_name:
            # Update specific package
            print(f"Updating {package_name}...")
            # Find in dependencies
            for dep in metadata.dependencies + metadata.dev_dependencies:
                if dep.name == package_name:
                    available = self.registry.get_versions(package_name)
                    compatible = [v for v in available if dep.constraint.satisfies(v)]
                    if compatible:
                        latest = max(compatible)
                        print(f"Latest compatible version: {latest}")
                        self._install_package(package_name, latest)
                    break
        else:
            # Update all packages
            print("Updating all packages...")
            self.install()

    def list_installed(self) -> None:
        """List all installed packages."""
        if not self.lock_file.exists():
            print("No packages installed.")
            return

        lock_file = LockFile.from_file(self.lock_file)

        if not lock_file.packages:
            print("No packages installed.")
            return

        print("Installed packages:")
        for name, pkg in sorted(lock_file.packages.items()):
            print(f"  {name}@{pkg.version}")
            if pkg.dependencies:
                print(f"    └─ dependencies: {', '.join(pkg.dependencies)}")

    def clean(self) -> None:
        """Clean package cache."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            print("Cache cleaned")


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Package Manager - Poetry for the Soul",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-pkg init myproject              Initialize a new package
  lament-pkg install                     Install all dependencies
  lament-pkg install requests@^2.0.0     Install a specific package
  lament-pkg install --dev pytest        Install dev dependency
  lament-pkg uninstall requests          Uninstall a package
  lament-pkg update                      Update all packages
  lament-pkg update requests             Update specific package
  lament-pkg list                        List installed packages
  lament-pkg clean                       Clean package cache
        """
    )

    parser.add_argument('--version', action='version', version='lament-pkg 1.0.0')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new package')
    init_parser.add_argument('name', help='Package name')
    init_parser.add_argument('--version', default='0.1.0', help='Initial version')

    # Install command
    install_parser = subparsers.add_parser('install', help='Install packages')
    install_parser.add_argument('package', nargs='?', help='Package to install')
    install_parser.add_argument('--dev', action='store_true', help='Install as dev dependency')
    install_parser.add_argument('--verify-signature', action='store_true', default=True,
                              help='Verify package signatures (default: enabled)')
    install_parser.add_argument('--skip-verification', action='store_true',
                              help='Skip signature verification (NOT RECOMMENDED)')
    install_parser.add_argument('--skip-security', action='store_true',
                              help='Skip security scanning')

    # Uninstall command
    uninstall_parser = subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package', help='Package to uninstall')

    # Update command
    update_parser = subparsers.add_parser('update', help='Update packages')
    update_parser.add_argument('package', nargs='?', help='Package to update')

    # List command
    subparsers.add_parser('list', help='List installed packages')

    # Clean command
    subparsers.add_parser('clean', help='Clean package cache')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create package manager
    verify_sigs = True
    skip_security = False

    if args.command == 'install':
        verify_sigs = not args.skip_verification
        skip_security = args.skip_security

        if args.skip_verification:
            print("WARNING: Signature verification disabled. This is NOT RECOMMENDED!")

    pm = PackageManager(verify_signatures=verify_sigs, skip_security=skip_security)

    # Execute command
    if args.command == 'init':
        pm.init(args.name, args.version)
    elif args.command == 'install':
        pm.install(args.package, dev=args.dev)
    elif args.command == 'uninstall':
        pm.uninstall(args.package)
    elif args.command == 'update':
        pm.update(args.package)
    elif args.command == 'list':
        pm.list_installed()
    elif args.command == 'clean':
        pm.clean()


if __name__ == '__main__':
    main()
