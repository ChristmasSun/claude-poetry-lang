#!/usr/bin/env python3
"""
Lament Workspace Manager - Organizing Multiple Sorrows into One

A comprehensive workspace and monorepo management system for Lament.
Supports multiple packages in a single repository with shared configuration,
cross-package dependencies, and workspace-wide operations.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import json
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import concurrent.futures
import shutil

# Import package manager components
from tools.package_manager import PackageMetadata, Version, PackageDependency


# ============================================================================
# WORKSPACE CONFIGURATION
# ============================================================================

@dataclass
class WorkspacePackage:
    """Represents a package within a workspace."""
    name: str
    path: Path
    metadata: Optional[PackageMetadata] = None

    def load_metadata(self) -> None:
        """Load package metadata."""
        package_file = self.path / "package.lament"
        if package_file.exists():
            self.metadata = PackageMetadata.from_file(package_file)
        else:
            raise FileNotFoundError(f"No package.lament found in {self.path}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'path': str(self.path.relative_to(self.path.parent.parent))
        }

    @staticmethod
    def from_dict(data: Dict[str, Any], workspace_root: Path) -> 'WorkspacePackage':
        """Create from dictionary."""
        path = workspace_root / data['path']
        return WorkspacePackage(
            name=data['name'],
            path=path
        )


@dataclass
class WorkspaceConfig:
    """Configuration for a Lament workspace."""
    name: str
    packages: List[WorkspacePackage] = field(default_factory=list)
    shared_dependencies: List[PackageDependency] = field(default_factory=list)
    shared_dev_dependencies: List[PackageDependency] = field(default_factory=list)
    build_config: Dict[str, Any] = field(default_factory=dict)
    scripts: Dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'packages': [pkg.to_dict() for pkg in self.packages],
            'shared_dependencies': [dep.to_dict() for dep in self.shared_dependencies],
            'shared_dev_dependencies': [dep.to_dict() for dep in self.shared_dev_dependencies],
            'build_config': self.build_config,
            'scripts': self.scripts
        }

    @staticmethod
    def from_dict(data: Dict[str, Any], workspace_root: Path) -> 'WorkspaceConfig':
        """Create from dictionary."""
        packages = [
            WorkspacePackage.from_dict(pkg, workspace_root)
            for pkg in data.get('packages', [])
        ]

        shared_deps = [
            PackageDependency.from_dict(dep)
            for dep in data.get('shared_dependencies', [])
        ]

        shared_dev_deps = [
            PackageDependency.from_dict(dep)
            for dep in data.get('shared_dev_dependencies', [])
        ]

        return WorkspaceConfig(
            name=data['name'],
            packages=packages,
            shared_dependencies=shared_deps,
            shared_dev_dependencies=shared_dev_deps,
            build_config=data.get('build_config', {}),
            scripts=data.get('scripts', {})
        )

    def to_file(self, filepath: Path) -> None:
        """Save workspace configuration to file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def from_file(filepath: Path) -> 'WorkspaceConfig':
        """Load workspace configuration from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        workspace_root = filepath.parent
        return WorkspaceConfig.from_dict(data, workspace_root)


# ============================================================================
# DEPENDENCY GRAPH
# ============================================================================

class WorkspaceDependencyGraph:
    """Manages dependency relationships between workspace packages."""

    def __init__(self, packages: List[WorkspacePackage]):
        """Initialize dependency graph."""
        self.packages = {pkg.name: pkg for pkg in packages}
        self.graph: Dict[str, Set[str]] = defaultdict(set)
        self._build_graph()

    def _build_graph(self) -> None:
        """Build dependency graph from package metadata."""
        for pkg in self.packages.values():
            if pkg.metadata:
                for dep in pkg.metadata.dependencies:
                    if dep.name in self.packages:
                        # Internal workspace dependency
                        self.graph[pkg.name].add(dep.name)

    def get_build_order(self) -> List[str]:
        """
        Get packages in build order (topological sort).
        Returns list of package names.
        """
        # Kahn's algorithm for topological sort
        in_degree = {pkg: 0 for pkg in self.packages}

        for pkg, deps in self.graph.items():
            for dep in deps:
                in_degree[dep] += 1

        queue = [pkg for pkg, degree in in_degree.items() if degree == 0]
        result = []

        while queue:
            # Sort for deterministic order
            queue.sort()
            node = queue.pop(0)
            result.append(node)

            for neighbor in sorted(self.graph[node]):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(self.packages):
            # Circular dependency detected
            raise ValueError("Circular dependency detected in workspace")

        # Reverse to get correct build order (dependencies first)
        return list(reversed(result))

    def get_dependents(self, package_name: str) -> Set[str]:
        """Get packages that depend on the given package."""
        dependents = set()
        for pkg, deps in self.graph.items():
            if package_name in deps:
                dependents.add(pkg)
        return dependents

    def get_dependencies(self, package_name: str) -> Set[str]:
        """Get packages that the given package depends on."""
        return self.graph.get(package_name, set())


# ============================================================================
# WORKSPACE MANAGER
# ============================================================================

class WorkspaceManager:
    """Main workspace management system."""

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize workspace manager.

        Args:
            workspace_root: Root directory of workspace (defaults to cwd)
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.config_file = self.workspace_root / "workspace.lament"
        self.config: Optional[WorkspaceConfig] = None

        if self.config_file.exists():
            self.load_config()

    def load_config(self) -> None:
        """Load workspace configuration."""
        self.config = WorkspaceConfig.from_file(self.config_file)

        # Load package metadata
        for pkg in self.config.packages:
            try:
                pkg.load_metadata()
            except FileNotFoundError as e:
                print(f"Warning: {e}")

    def save_config(self) -> None:
        """Save workspace configuration."""
        if self.config:
            self.config.to_file(self.config_file)

    def init(self, name: str) -> None:
        """
        Initialize a new workspace.

        Args:
            name: Workspace name
        """
        if self.config_file.exists():
            print(f"Workspace already initialized: {self.config_file}")
            return

        self.config = WorkspaceConfig(
            name=name,
            packages=[],
            build_config={
                'parallel_builds': True,
                'max_workers': 4,
                'build_dir': 'build',
                'cache_dir': '.lament/cache'
            },
            scripts={}
        )

        # Create packages directory
        packages_dir = self.workspace_root / "packages"
        packages_dir.mkdir(exist_ok=True)

        self.save_config()
        print(f"Initialized workspace: {name}")
        print(f"Created: {self.config_file}")
        print(f"Created: {packages_dir}")

    def add_package(self, package_path: Path, name: Optional[str] = None) -> None:
        """
        Add a package to the workspace.

        Args:
            package_path: Path to package (relative to workspace root)
            name: Package name (auto-detected if not provided)
        """
        if not self.config:
            print("No workspace initialized. Run 'lament-workspace init' first.")
            return

        full_path = self.workspace_root / package_path

        # Check if package exists
        if not full_path.exists():
            print(f"Error: Package path does not exist: {full_path}")
            return

        package_file = full_path / "package.lament"
        if not package_file.exists():
            print(f"Error: No package.lament found in {full_path}")
            return

        # Load metadata to get name
        metadata = PackageMetadata.from_file(package_file)
        pkg_name = name or metadata.name

        # Check if already added
        if any(pkg.name == pkg_name for pkg in self.config.packages):
            print(f"Package {pkg_name} already in workspace")
            return

        # Create workspace package
        workspace_pkg = WorkspacePackage(
            name=pkg_name,
            path=full_path,
            metadata=metadata
        )

        self.config.packages.append(workspace_pkg)
        self.save_config()

        print(f"Added package: {pkg_name} ({package_path})")

    def create_package(self, name: str, template: str = "library") -> None:
        """
        Create a new package in the workspace.

        Args:
            name: Package name
            template: Template type to use
        """
        if not self.config:
            print("No workspace initialized. Run 'lament-workspace init' first.")
            return

        # Import scaffolder
        from tools.scaffolder import ProjectScaffolder, ProjectConfig

        # Create package in workspace packages directory
        package_path = self.workspace_root / "packages" / name

        if package_path.exists():
            print(f"Error: Package directory already exists: {package_path}")
            return

        # Create config
        config = ProjectConfig(
            name=name,
            description=f"A Lament {template} package",
            author="",
            email="",
            license="MIT",
            use_git=False,  # Workspace manages git
            use_ci=False,   # Workspace manages CI
            template_type=template
        )

        # Scaffold package
        scaffolder = ProjectScaffolder()
        scaffolder.scaffold(
            template=template,
            name=name,
            output_dir=package_path,
            config=config,
            interactive=False
        )

        # Add to workspace
        self.add_package(package_path.relative_to(self.workspace_root), name)

    def remove_package(self, name: str, delete: bool = False) -> None:
        """
        Remove a package from the workspace.

        Args:
            name: Package name
            delete: Whether to delete package directory
        """
        if not self.config:
            print("No workspace initialized.")
            return

        # Find package
        pkg = next((p for p in self.config.packages if p.name == name), None)
        if not pkg:
            print(f"Package not found: {name}")
            return

        # Remove from config
        self.config.packages = [p for p in self.config.packages if p.name != name]
        self.save_config()

        print(f"Removed package: {name}")

        # Delete directory if requested
        if delete and pkg.path.exists():
            shutil.rmtree(pkg.path)
            print(f"Deleted: {pkg.path}")

    def list_packages(self) -> None:
        """List all packages in the workspace."""
        if not self.config:
            print("No workspace initialized.")
            return

        if not self.config.packages:
            print("No packages in workspace.")
            return

        print(f"Workspace: {self.config.name}")
        print(f"Packages ({len(self.config.packages)}):")
        print()

        for pkg in sorted(self.config.packages, key=lambda p: p.name):
            if pkg.metadata:
                print(f"  {pkg.name} v{pkg.metadata.version}")
                print(f"    Path: {pkg.path.relative_to(self.workspace_root)}")
                if pkg.metadata.description:
                    print(f"    Description: {pkg.metadata.description}")

                # Show workspace dependencies
                workspace_deps = [
                    d.name for d in pkg.metadata.dependencies
                    if any(p.name == d.name for p in self.config.packages)
                ]
                if workspace_deps:
                    print(f"    Workspace deps: {', '.join(workspace_deps)}")
            else:
                print(f"  {pkg.name}")
                print(f"    Path: {pkg.path.relative_to(self.workspace_root)}")
            print()

    def build_all(self, parallel: bool = True, verbose: bool = False) -> None:
        """
        Build all packages in the workspace.

        Args:
            parallel: Build packages in parallel
            verbose: Show verbose output
        """
        if not self.config:
            print("No workspace initialized.")
            return

        print(f"Building workspace: {self.config.name}")
        print()

        # Get build order
        graph = WorkspaceDependencyGraph(self.config.packages)
        try:
            build_order = graph.get_build_order()
        except ValueError as e:
            print(f"Error: {e}")
            return

        # Build packages
        if parallel and self.config.build_config.get('parallel_builds', True):
            self._build_parallel(build_order, verbose)
        else:
            self._build_sequential(build_order, verbose)

    def _build_sequential(self, build_order: List[str], verbose: bool) -> None:
        """Build packages sequentially."""
        packages = {pkg.name: pkg for pkg in self.config.packages}

        for pkg_name in build_order:
            pkg = packages[pkg_name]
            print(f"Building {pkg_name}...")

            result = self._build_package(pkg, verbose)

            if result.returncode == 0:
                print(f"✓ {pkg_name} built successfully")
            else:
                print(f"✗ {pkg_name} build failed")
                if verbose:
                    print(result.stderr)
                break

    def _build_parallel(self, build_order: List[str], verbose: bool) -> None:
        """Build packages in parallel (respecting dependencies)."""
        packages = {pkg.name: pkg for pkg in self.config.packages}
        graph = WorkspaceDependencyGraph(self.config.packages)

        # Group packages by dependency level
        levels: List[List[str]] = []
        remaining = set(build_order)
        built = set()

        while remaining:
            # Find packages with all dependencies built
            level = []
            for pkg_name in remaining:
                deps = graph.get_dependencies(pkg_name)
                if deps.issubset(built):
                    level.append(pkg_name)

            if not level:
                print("Error: Cannot resolve build order")
                break

            levels.append(level)
            remaining -= set(level)
            built.update(level)

        # Build each level in parallel
        max_workers = self.config.build_config.get('max_workers', 4)

        for level in levels:
            if len(level) == 1:
                # Single package, build directly
                pkg = packages[level[0]]
                print(f"Building {pkg.name}...")
                result = self._build_package(pkg, verbose)
                if result.returncode == 0:
                    print(f"✓ {pkg.name} built successfully")
                else:
                    print(f"✗ {pkg.name} build failed")
                    if verbose:
                        print(result.stderr)
                    return
            else:
                # Multiple packages, build in parallel
                print(f"Building {len(level)} packages in parallel...")
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = {
                        executor.submit(self._build_package, packages[name], verbose): name
                        for name in level
                    }

                    for future in concurrent.futures.as_completed(futures):
                        pkg_name = futures[future]
                        result = future.result()

                        if result.returncode == 0:
                            print(f"✓ {pkg_name} built successfully")
                        else:
                            print(f"✗ {pkg_name} build failed")
                            if verbose:
                                print(result.stderr)

    def _build_package(self, pkg: WorkspacePackage, verbose: bool) -> subprocess.CompletedProcess:
        """Build a single package."""
        try:
            result = subprocess.run(
                ['lament-build', 'build'],
                cwd=pkg.path,
                capture_output=True,
                text=True
            )
            return result
        except Exception as e:
            print(f"Error building {pkg.name}: {e}")
            return subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr=str(e)
            )

    def test_all(self, parallel: bool = True, verbose: bool = False) -> None:
        """
        Run tests for all packages in the workspace.

        Args:
            parallel: Run tests in parallel
            verbose: Show verbose output
        """
        if not self.config:
            print("No workspace initialized.")
            return

        print(f"Testing workspace: {self.config.name}")
        print()

        packages = self.config.packages

        if parallel:
            self._test_parallel(packages, verbose)
        else:
            self._test_sequential(packages, verbose)

    def _test_sequential(self, packages: List[WorkspacePackage], verbose: bool) -> None:
        """Run tests sequentially."""
        for pkg in packages:
            print(f"Testing {pkg.name}...")

            result = self._test_package(pkg, verbose)

            if result.returncode == 0:
                print(f"✓ {pkg.name} tests passed")
            else:
                print(f"✗ {pkg.name} tests failed")
                if verbose:
                    print(result.stderr)

    def _test_parallel(self, packages: List[WorkspacePackage], verbose: bool) -> None:
        """Run tests in parallel."""
        max_workers = self.config.build_config.get('max_workers', 4)

        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(self._test_package, pkg, verbose): pkg.name
                for pkg in packages
            }

            for future in concurrent.futures.as_completed(futures):
                pkg_name = futures[future]
                result = future.result()

                if result.returncode == 0:
                    print(f"✓ {pkg_name} tests passed")
                else:
                    print(f"✗ {pkg_name} tests failed")
                    if verbose:
                        print(result.stderr)

    def _test_package(self, pkg: WorkspacePackage, verbose: bool) -> subprocess.CompletedProcess:
        """Test a single package."""
        try:
            result = subprocess.run(
                ['lament-build', 'test'],
                cwd=pkg.path,
                capture_output=True,
                text=True
            )
            return result
        except Exception as e:
            print(f"Error testing {pkg.name}: {e}")
            return subprocess.CompletedProcess(
                args=[],
                returncode=1,
                stdout="",
                stderr=str(e)
            )

    def run_script(self, script_name: str) -> None:
        """
        Run a workspace script.

        Args:
            script_name: Name of script to run
        """
        if not self.config:
            print("No workspace initialized.")
            return

        if script_name not in self.config.scripts:
            print(f"Script not found: {script_name}")
            print("Available scripts:")
            for name in self.config.scripts:
                print(f"  - {name}")
            return

        script = self.config.scripts[script_name]
        print(f"Running script: {script_name}")
        print(f"Command: {script}")
        print()

        try:
            result = subprocess.run(
                script,
                shell=True,
                cwd=self.workspace_root
            )
            sys.exit(result.returncode)
        except Exception as e:
            print(f"Error running script: {e}")
            sys.exit(1)


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Workspace Manager - Organizing Multiple Sorrows into One",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-workspace init my-workspace          Initialize new workspace
  lament-workspace add packages/my-lib        Add existing package
  lament-workspace create my-lib library      Create new library package
  lament-workspace list                       List all packages
  lament-workspace build                      Build all packages
  lament-workspace test                       Test all packages
  lament-workspace remove my-lib              Remove package from workspace
        """
    )

    parser.add_argument('--version', action='version', version='lament-workspace 1.0.0')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize a new workspace')
    init_parser.add_argument('name', help='Workspace name')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add existing package to workspace')
    add_parser.add_argument('path', type=Path, help='Path to package (relative to workspace root)')
    add_parser.add_argument('--name', help='Package name (auto-detected if not provided)')

    # Create command
    create_parser = subparsers.add_parser('create', help='Create new package in workspace')
    create_parser.add_argument('name', help='Package name')
    create_parser.add_argument(
        'template',
        nargs='?',
        default='library',
        choices=['library', 'application', 'web-server', 'cli-tool', 'ml-model'],
        help='Package template (default: library)'
    )

    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove package from workspace')
    remove_parser.add_argument('name', help='Package name')
    remove_parser.add_argument('--delete', action='store_true', help='Delete package directory')

    # List command
    subparsers.add_parser('list', help='List all packages in workspace')

    # Build command
    build_parser = subparsers.add_parser('build', help='Build all packages')
    build_parser.add_argument('--sequential', action='store_true', help='Build sequentially')
    build_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Test command
    test_parser = subparsers.add_parser('test', help='Test all packages')
    test_parser.add_argument('--sequential', action='store_true', help='Test sequentially')
    test_parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run workspace script')
    run_parser.add_argument('script', help='Script name')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create workspace manager
    wm = WorkspaceManager()

    # Execute command
    if args.command == 'init':
        wm.init(args.name)
    elif args.command == 'add':
        wm.add_package(args.path, args.name)
    elif args.command == 'create':
        wm.create_package(args.name, args.template)
    elif args.command == 'remove':
        wm.remove_package(args.name, args.delete)
    elif args.command == 'list':
        wm.list_packages()
    elif args.command == 'build':
        wm.build_all(parallel=not args.sequential, verbose=args.verbose)
    elif args.command == 'test':
        wm.test_all(parallel=not args.sequential, verbose=args.verbose)
    elif args.command == 'run':
        wm.run_script(args.script)


if __name__ == '__main__':
    main()
