#!/usr/bin/env python3
"""
Lament Package Registry - The Vault of Souls

A package registry system for discovering, publishing, and managing Lament packages.
Supports local and remote registries with authentication and version management.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import json
import os
import hashlib
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import urllib.request
import urllib.error
import tarfile
import tempfile
import getpass


# ============================================================================
# REGISTRY CONFIGURATION
# ============================================================================

@dataclass
class RegistryConfig:
    """Configuration for a package registry."""
    name: str
    url: str
    api_key: str = ""
    priority: int = 0
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'url': self.url,
            'api_key': self.api_key,
            'priority': self.priority,
            'enabled': self.enabled
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RegistryConfig':
        """Create from dictionary."""
        return RegistryConfig(
            name=data['name'],
            url=data['url'],
            api_key=data.get('api_key', ''),
            priority=data.get('priority', 0),
            enabled=data.get('enabled', True)
        )


class RegistryConfigManager:
    """Manages registry configurations."""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize configuration manager."""
        self.config_dir = config_dir or Path.home() / ".lament"
        self.config_file = self.config_dir / "registries.json"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # Default registries
        self.default_registries = [
            RegistryConfig(
                name="official",
                url="https://registry.lament-lang.org",
                priority=100
            ),
            RegistryConfig(
                name="local",
                url="file://~/.lament/local-registry",
                priority=50
            )
        ]

    def load(self) -> List[RegistryConfig]:
        """Load registry configurations."""
        if not self.config_file.exists():
            return self.default_registries

        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
            return [RegistryConfig.from_dict(r) for r in data.get('registries', [])]
        except Exception as e:
            print(f"Warning: Could not load registry config: {e}")
            return self.default_registries

    def save(self, registries: List[RegistryConfig]) -> None:
        """Save registry configurations."""
        data = {'registries': [r.to_dict() for r in registries]}
        with open(self.config_file, 'w') as f:
            json.dump(data, f, indent=2)

    def add_registry(self, config: RegistryConfig) -> None:
        """Add a new registry."""
        registries = self.load()
        # Remove existing registry with same name
        registries = [r for r in registries if r.name != config.name]
        registries.append(config)
        self.save(registries)

    def remove_registry(self, name: str) -> bool:
        """Remove a registry by name."""
        registries = self.load()
        original_len = len(registries)
        registries = [r for r in registries if r.name != name]
        if len(registries) < original_len:
            self.save(registries)
            return True
        return False

    def get_registry(self, name: str) -> Optional[RegistryConfig]:
        """Get a registry by name."""
        registries = self.load()
        for r in registries:
            if r.name == name:
                return r
        return None


# ============================================================================
# PACKAGE METADATA
# ============================================================================

@dataclass
class RegistryPackageInfo:
    """Package information stored in the registry."""
    name: str
    version: str
    description: str
    author: str
    license: str
    homepage: str
    repository: str
    keywords: List[str]
    dependencies: List[Dict[str, str]]
    checksum: str
    size: int
    published_at: str
    downloads: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'license': self.license,
            'homepage': self.homepage,
            'repository': self.repository,
            'keywords': self.keywords,
            'dependencies': self.dependencies,
            'checksum': self.checksum,
            'size': self.size,
            'published_at': self.published_at,
            'downloads': self.downloads
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'RegistryPackageInfo':
        """Create from dictionary."""
        return RegistryPackageInfo(
            name=data['name'],
            version=data['version'],
            description=data.get('description', ''),
            author=data.get('author', ''),
            license=data.get('license', ''),
            homepage=data.get('homepage', ''),
            repository=data.get('repository', ''),
            keywords=data.get('keywords', []),
            dependencies=data.get('dependencies', []),
            checksum=data['checksum'],
            size=data.get('size', 0),
            published_at=data.get('published_at', ''),
            downloads=data.get('downloads', 0)
        )


# ============================================================================
# REGISTRY BACKEND
# ============================================================================

class RegistryBackend:
    """Abstract base class for registry backends."""

    def search(self, query: str) -> List[RegistryPackageInfo]:
        """Search for packages."""
        raise NotImplementedError

    def get_package_info(self, name: str, version: str) -> Optional[RegistryPackageInfo]:
        """Get package information."""
        raise NotImplementedError

    def get_versions(self, name: str) -> List[str]:
        """Get all versions of a package."""
        raise NotImplementedError

    def download_package(self, name: str, version: str) -> bytes:
        """Download a package."""
        raise NotImplementedError

    def publish_package(self, package_data: bytes, metadata: RegistryPackageInfo) -> bool:
        """Publish a package."""
        raise NotImplementedError

    def unpublish_package(self, name: str, version: str) -> bool:
        """Unpublish a package."""
        raise NotImplementedError


class LocalRegistryBackend(RegistryBackend):
    """Local filesystem registry backend."""

    def __init__(self, path: Path):
        """Initialize local registry."""
        self.path = path
        self.path.mkdir(parents=True, exist_ok=True)
        self.index_file = self.path / "index.json"
        self.packages_dir = self.path / "packages"
        self.packages_dir.mkdir(exist_ok=True)

    def _load_index(self) -> Dict[str, List[RegistryPackageInfo]]:
        """Load the package index."""
        if not self.index_file.exists():
            return {}

        with open(self.index_file, 'r') as f:
            data = json.load(f)

        index = {}
        for name, versions in data.items():
            index[name] = [RegistryPackageInfo.from_dict(v) for v in versions]
        return index

    def _save_index(self, index: Dict[str, List[RegistryPackageInfo]]) -> None:
        """Save the package index."""
        data = {
            name: [v.to_dict() for v in versions]
            for name, versions in index.items()
        }
        with open(self.index_file, 'w') as f:
            json.dump(data, f, indent=2)

    def search(self, query: str) -> List[RegistryPackageInfo]:
        """Search for packages."""
        index = self._load_index()
        results = []
        query_lower = query.lower()

        for name, versions in index.items():
            if query_lower in name.lower():
                # Add latest version
                if versions:
                    results.append(versions[-1])
            else:
                # Search in keywords and description
                for pkg in versions:
                    if (query_lower in pkg.description.lower() or
                        any(query_lower in kw.lower() for kw in pkg.keywords)):
                        results.append(pkg)
                        break

        return results

    def get_package_info(self, name: str, version: str) -> Optional[RegistryPackageInfo]:
        """Get package information."""
        index = self._load_index()
        if name not in index:
            return None

        for pkg in index[name]:
            if pkg.version == version:
                return pkg
        return None

    def get_versions(self, name: str) -> List[str]:
        """Get all versions of a package."""
        index = self._load_index()
        if name not in index:
            return []
        return [pkg.version for pkg in index[name]]

    def download_package(self, name: str, version: str) -> bytes:
        """Download a package."""
        package_file = self.packages_dir / f"{name}-{version}.tar.gz"
        if not package_file.exists():
            raise FileNotFoundError(f"Package not found: {name}@{version}")

        with open(package_file, 'rb') as f:
            return f.read()

    def publish_package(self, package_data: bytes, metadata: RegistryPackageInfo) -> bool:
        """Publish a package."""
        # Save package file
        package_file = self.packages_dir / f"{metadata.name}-{metadata.version}.tar.gz"
        with open(package_file, 'wb') as f:
            f.write(package_data)

        # Update index
        index = self._load_index()
        if metadata.name not in index:
            index[metadata.name] = []

        # Check if version already exists
        for pkg in index[metadata.name]:
            if pkg.version == metadata.version:
                print(f"Warning: Version {metadata.version} already exists, replacing...")
                index[metadata.name].remove(pkg)
                break

        index[metadata.name].append(metadata)
        self._save_index(index)
        return True

    def unpublish_package(self, name: str, version: str) -> bool:
        """Unpublish a package."""
        # Remove from index
        index = self._load_index()
        if name not in index:
            return False

        original_len = len(index[name])
        index[name] = [pkg for pkg in index[name] if pkg.version != version]

        if len(index[name]) < original_len:
            self._save_index(index)

            # Remove package file
            package_file = self.packages_dir / f"{name}-{version}.tar.gz"
            if package_file.exists():
                package_file.unlink()

            return True
        return False


class RemoteRegistryBackend(RegistryBackend):
    """Remote HTTP registry backend."""

    def __init__(self, url: str, api_key: str = ""):
        """Initialize remote registry."""
        self.url = url.rstrip('/')
        self.api_key = api_key

    def _make_request(self, path: str, method: str = 'GET',
                     data: Optional[bytes] = None) -> Any:
        """Make HTTP request to registry."""
        url = f"{self.url}{path}"
        headers = {}

        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"

        if data:
            headers['Content-Type'] = 'application/json'

        req = urllib.request.Request(url, data=data, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    return json.loads(response.read())
                else:
                    raise Exception(f"HTTP {response.status}")
        except urllib.error.URLError as e:
            raise Exception(f"Registry request failed: {e}")

    def search(self, query: str) -> List[RegistryPackageInfo]:
        """Search for packages."""
        try:
            results = self._make_request(f"/search?q={query}")
            return [RegistryPackageInfo.from_dict(r) for r in results.get('packages', [])]
        except Exception as e:
            print(f"Search failed: {e}")
            return []

    def get_package_info(self, name: str, version: str) -> Optional[RegistryPackageInfo]:
        """Get package information."""
        try:
            result = self._make_request(f"/packages/{name}/{version}")
            return RegistryPackageInfo.from_dict(result)
        except Exception:
            return None

    def get_versions(self, name: str) -> List[str]:
        """Get all versions of a package."""
        try:
            result = self._make_request(f"/packages/{name}/versions")
            return result.get('versions', [])
        except Exception:
            return []

    def download_package(self, name: str, version: str) -> bytes:
        """Download a package."""
        url = f"{self.url}/packages/{name}/{version}/download"
        headers = {}
        if self.api_key:
            headers['Authorization'] = f"Bearer {self.api_key}"

        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req) as response:
            return response.read()

    def publish_package(self, package_data: bytes, metadata: RegistryPackageInfo) -> bool:
        """Publish a package."""
        # This would upload to a remote registry
        # For now, return False as it requires server implementation
        print("Publishing to remote registries requires server setup")
        return False

    def unpublish_package(self, name: str, version: str) -> bool:
        """Unpublish a package."""
        # This would delete from a remote registry
        print("Unpublishing from remote registries requires server setup")
        return False


# ============================================================================
# REGISTRY CLIENT
# ============================================================================

class Registry:
    """Main registry client that coordinates multiple backends."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize registry client."""
        self.cache_dir = cache_dir or Path.home() / ".lament" / "cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.config_manager = RegistryConfigManager()
        self.backends: Dict[str, RegistryBackend] = {}

        # Initialize backends
        self._init_backends()

    def _init_backends(self) -> None:
        """Initialize registry backends."""
        configs = self.config_manager.load()

        for config in configs:
            if not config.enabled:
                continue

            if config.url.startswith('file://'):
                # Local registry
                path = Path(config.url[7:]).expanduser()
                self.backends[config.name] = LocalRegistryBackend(path)
            else:
                # Remote registry
                self.backends[config.name] = RemoteRegistryBackend(
                    config.url, config.api_key
                )

    def search(self, query: str) -> List[RegistryPackageInfo]:
        """Search for packages across all registries."""
        results = []
        seen = set()

        for name, backend in self.backends.items():
            try:
                backend_results = backend.search(query)
                for pkg in backend_results:
                    key = f"{pkg.name}@{pkg.version}"
                    if key not in seen:
                        seen.add(key)
                        results.append(pkg)
            except Exception as e:
                print(f"Search failed for registry {name}: {e}")

        return results

    def get_package(self, name: str, version) -> Optional[Any]:
        """Get package metadata (returns PackageMetadata from package_manager)."""
        from tools.package_manager import PackageMetadata, Version, PackageDependency

        # Convert version to string if needed
        version_str = str(version)

        for backend in self.backends.values():
            try:
                info = backend.get_package_info(name, version_str)
                if info:
                    # Convert to PackageMetadata
                    deps = []
                    for dep in info.dependencies:
                        from tools.package_manager import VersionConstraint
                        deps.append(PackageDependency(
                            name=dep['name'],
                            constraint=VersionConstraint.parse(dep['version'])
                        ))

                    return PackageMetadata(
                        name=info.name,
                        version=Version.parse(info.version),
                        description=info.description,
                        author=info.author,
                        license=info.license,
                        homepage=info.homepage,
                        repository=info.repository,
                        keywords=info.keywords,
                        dependencies=deps
                    )
            except Exception as e:
                print(f"Error getting package {name}@{version}: {e}")

        return None

    def get_versions(self, name: str) -> List[Any]:
        """Get all versions of a package."""
        from tools.package_manager import Version

        versions = set()
        for backend in self.backends.values():
            try:
                backend_versions = backend.get_versions(name)
                versions.update(backend_versions)
            except Exception:
                pass

        # Parse and sort versions
        parsed = []
        for v in versions:
            try:
                parsed.append(Version.parse(v))
            except Exception:
                pass

        return sorted(parsed)

    def download_package(self, name: str, version) -> bytes:
        """Download a package from any registry."""
        version_str = str(version)

        for backend in self.backends.values():
            try:
                return backend.download_package(name, version_str)
            except Exception:
                continue

        raise FileNotFoundError(f"Package not found: {name}@{version_str}")

    def publish(self, package_path: Path, registry_name: str = "local") -> bool:
        """Publish a package to a registry."""
        if registry_name not in self.backends:
            print(f"Registry not found: {registry_name}")
            return False

        # Load package metadata
        from tools.package_manager import PackageMetadata

        package_file = package_path / "package.lament"
        if not package_file.exists():
            print(f"No package.lament found in {package_path}")
            return False

        metadata = PackageMetadata.from_file(package_file)

        # Create tarball
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as tmp:
            with tarfile.open(tmp.name, 'w:gz') as tar:
                tar.add(package_path, arcname=metadata.name)

            tmp.seek(0)
            package_data = tmp.read()

        # Calculate checksum
        checksum = hashlib.sha256(package_data).hexdigest()

        # Create registry info
        info = RegistryPackageInfo(
            name=metadata.name,
            version=str(metadata.version),
            description=metadata.description,
            author=metadata.author,
            license=metadata.license,
            homepage=metadata.homepage,
            repository=metadata.repository,
            keywords=metadata.keywords,
            dependencies=[dep.to_dict() for dep in metadata.dependencies],
            checksum=checksum,
            size=len(package_data),
            published_at=datetime.now().isoformat()
        )

        # Publish
        backend = self.backends[registry_name]
        return backend.publish_package(package_data, info)

    def unpublish(self, name: str, version: str, registry_name: str = "local") -> bool:
        """Unpublish a package from a registry."""
        if registry_name not in self.backends:
            print(f"Registry not found: {registry_name}")
            return False

        backend = self.backends[registry_name]
        return backend.unpublish_package(name, version)

    def add_registry(self, name: str, url: str, api_key: str = "") -> None:
        """Add a new registry."""
        config = RegistryConfig(name=name, url=url, api_key=api_key)
        self.config_manager.add_registry(config)
        self._init_backends()
        print(f"Added registry: {name}")

    def remove_registry(self, name: str) -> None:
        """Remove a registry."""
        if self.config_manager.remove_registry(name):
            if name in self.backends:
                del self.backends[name]
            print(f"Removed registry: {name}")
        else:
            print(f"Registry not found: {name}")

    def list_registries(self) -> None:
        """List all configured registries."""
        configs = self.config_manager.load()
        if not configs:
            print("No registries configured")
            return

        print("Configured registries:")
        for config in configs:
            status = "enabled" if config.enabled else "disabled"
            print(f"  {config.name} ({status})")
            print(f"    URL: {config.url}")
            print(f"    Priority: {config.priority}")


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Package Registry - The Vault of Souls",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-registry search neural              Search for packages
  lament-registry info requests 2.0.0        Get package information
  lament-registry publish .                  Publish current directory
  lament-registry unpublish mypackage 1.0.0  Unpublish a package
  lament-registry add-registry my-registry https://my-reg.com
  lament-registry list-registries            List all registries
        """
    )

    parser.add_argument('--version', action='version', version='lament-registry 1.0.0')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Search command
    search_parser = subparsers.add_parser('search', help='Search for packages')
    search_parser.add_argument('query', help='Search query')

    # Info command
    info_parser = subparsers.add_parser('info', help='Get package information')
    info_parser.add_argument('name', help='Package name')
    info_parser.add_argument('version', nargs='?', help='Package version')

    # Publish command
    publish_parser = subparsers.add_parser('publish', help='Publish a package')
    publish_parser.add_argument('path', nargs='?', default='.', help='Package directory')
    publish_parser.add_argument('--registry', default='local', help='Target registry')

    # Unpublish command
    unpublish_parser = subparsers.add_parser('unpublish', help='Unpublish a package')
    unpublish_parser.add_argument('name', help='Package name')
    unpublish_parser.add_argument('version', help='Package version')
    unpublish_parser.add_argument('--registry', default='local', help='Target registry')

    # Add registry command
    add_reg_parser = subparsers.add_parser('add-registry', help='Add a registry')
    add_reg_parser.add_argument('name', help='Registry name')
    add_reg_parser.add_argument('url', help='Registry URL')
    add_reg_parser.add_argument('--api-key', help='API key for authentication')

    # Remove registry command
    remove_reg_parser = subparsers.add_parser('remove-registry', help='Remove a registry')
    remove_reg_parser.add_argument('name', help='Registry name')

    # List registries command
    subparsers.add_parser('list-registries', help='List all registries')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    # Create registry client
    registry = Registry()

    # Execute command
    if args.command == 'search':
        results = registry.search(args.query)
        if not results:
            print("No packages found")
        else:
            print(f"Found {len(results)} package(s):")
            for pkg in results:
                print(f"\n{pkg.name}@{pkg.version}")
                print(f"  {pkg.description}")
                if pkg.keywords:
                    print(f"  Keywords: {', '.join(pkg.keywords)}")
                print(f"  Author: {pkg.author}")
                print(f"  License: {pkg.license}")

    elif args.command == 'info':
        if args.version:
            info = registry.get_package(args.name, args.version)
            if info:
                print(f"{info.name}@{info.version}")
                print(f"Description: {info.description}")
                print(f"Author: {info.author}")
                print(f"License: {info.license}")
                if info.homepage:
                    print(f"Homepage: {info.homepage}")
                if info.repository:
                    print(f"Repository: {info.repository}")
                if info.dependencies:
                    print("Dependencies:")
                    for dep in info.dependencies:
                        print(f"  - {dep.name} {dep.constraint}")
            else:
                print(f"Package not found: {args.name}@{args.version}")
        else:
            versions = registry.get_versions(args.name)
            if versions:
                print(f"Available versions of {args.name}:")
                for v in versions:
                    print(f"  {v}")
            else:
                print(f"Package not found: {args.name}")

    elif args.command == 'publish':
        path = Path(args.path)
        if registry.publish(path, args.registry):
            print(f"Package published to {args.registry}")
        else:
            print("Failed to publish package")

    elif args.command == 'unpublish':
        if registry.unpublish(args.name, args.version, args.registry):
            print(f"Package unpublished from {args.registry}")
        else:
            print("Failed to unpublish package")

    elif args.command == 'add-registry':
        registry.add_registry(args.name, args.url, args.api_key or "")

    elif args.command == 'remove-registry':
        registry.remove_registry(args.name)

    elif args.command == 'list-registries':
        registry.list_registries()


if __name__ == '__main__':
    main()
