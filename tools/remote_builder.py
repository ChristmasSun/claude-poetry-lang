#!/usr/bin/env python3
"""
Lament Remote Builder - Distributed Compilation

Submits Lament build jobs to remote servers for compilation.
Supports cloud build services, build farms, distributed builds,
and build artifact caching for faster iteration.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import hashlib
import http.client
import json
import os
import pickle
import socket
import ssl
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import base64


# ============================================================================
# BUILD SERVER CONFIGURATION
# ============================================================================

@dataclass
class BuildServer:
    """Remote build server configuration."""
    name: str
    url: str
    api_key: Optional[str] = None
    enabled: bool = True
    max_concurrent_jobs: int = 5
    timeout: int = 600  # 10 minutes
    supports_cache: bool = True
    supports_distributed: bool = False


class BuildServerType(Enum):
    """Types of build servers."""
    LOCAL = "local"        # Local machine
    SSH = "ssh"           # SSH remote server
    HTTP = "http"         # HTTP build service
    CLOUD = "cloud"       # Cloud build service (AWS, GCP, Azure)
    DOCKER = "docker"     # Docker-based builder


# ============================================================================
# BUILD JOB
# ============================================================================

class JobStatus(Enum):
    """Build job status."""
    PENDING = "pending"
    QUEUED = "queued"
    BUILDING = "building"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BuildJob:
    """Remote build job."""
    job_id: str
    source_files: List[Path]
    target_platform: str
    status: JobStatus = JobStatus.PENDING
    server: Optional[str] = None
    submitted_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    output_file: Optional[Path] = None
    error_message: Optional[str] = None
    build_log: List[str] = field(default_factory=list)

    @property
    def duration(self) -> Optional[timedelta]:
        """Get build duration."""
        if self.started_at and self.completed_at:
            return self.completed_at - self.started_at
        return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'job_id': self.job_id,
            'source_files': [str(f) for f in self.source_files],
            'target_platform': self.target_platform,
            'status': self.status.value,
            'server': self.server,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'output_file': str(self.output_file) if self.output_file else None,
            'error_message': self.error_message
        }


# ============================================================================
# BUILD CACHE
# ============================================================================

class BuildCache:
    """Caches build artifacts."""

    def __init__(self, cache_dir: Path):
        """Initialize build cache."""
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.index_file = cache_dir / "index.json"
        self.index: Dict[str, Dict[str, Any]] = {}
        self._load_index()

    def _load_index(self) -> None:
        """Load cache index."""
        if self.index_file.exists():
            with open(self.index_file, 'r') as f:
                self.index = json.load(f)

    def _save_index(self) -> None:
        """Save cache index."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)

    def get_cache_key(self, source_files: List[Path], target: str) -> str:
        """
        Generate cache key for build.

        Args:
            source_files: Source files
            target: Target platform

        Returns:
            Cache key (hash)
        """
        hasher = hashlib.sha256()

        # Hash source files content
        for source_file in sorted(source_files):
            if source_file.exists():
                with open(source_file, 'rb') as f:
                    hasher.update(f.read())

        # Hash target
        hasher.update(target.encode('utf-8'))

        return hasher.hexdigest()

    def has_cached(self, cache_key: str) -> bool:
        """Check if build is cached."""
        if cache_key not in self.index:
            return False

        entry = self.index[cache_key]
        artifact_path = self.cache_dir / entry['artifact']
        return artifact_path.exists()

    def get_cached(self, cache_key: str) -> Optional[Path]:
        """Get cached build artifact."""
        if not self.has_cached(cache_key):
            return None

        entry = self.index[cache_key]
        return self.cache_dir / entry['artifact']

    def store(self, cache_key: str, artifact: Path, metadata: Dict[str, Any]) -> None:
        """
        Store build artifact in cache.

        Args:
            cache_key: Cache key
            artifact: Build artifact file
            metadata: Build metadata
        """
        # Copy artifact to cache
        artifact_name = f"{cache_key}{artifact.suffix}"
        cached_artifact = self.cache_dir / artifact_name

        import shutil
        shutil.copy2(artifact, cached_artifact)

        # Update index
        self.index[cache_key] = {
            'artifact': artifact_name,
            'cached_at': datetime.now().isoformat(),
            'metadata': metadata
        }
        self._save_index()

    def clear(self) -> None:
        """Clear all cached artifacts."""
        import shutil
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
        self.cache_dir.mkdir(parents=True)
        self.index = {}
        self._save_index()

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_size = sum(
            (self.cache_dir / entry['artifact']).stat().st_size
            for entry in self.index.values()
            if (self.cache_dir / entry['artifact']).exists()
        )

        return {
            'entries': len(self.index),
            'total_size': total_size,
            'cache_dir': str(self.cache_dir)
        }


# ============================================================================
# BUILD CLIENT
# ============================================================================

class BuildClient:
    """Client for remote build servers."""

    def __init__(self, server: BuildServer):
        """Initialize build client."""
        self.server = server

    def submit_job(self, job: BuildJob) -> bool:
        """
        Submit build job to server.

        Args:
            job: Build job

        Returns:
            True if submitted successfully
        """
        try:
            # Package source files
            package = self._package_sources(job.source_files)

            # Prepare request
            payload = {
                'job_id': job.job_id,
                'target': job.target_platform,
                'source_package': base64.b64encode(package).decode('utf-8')
            }

            # Submit to server
            response = self._post_json('/api/v1/build', payload)

            if response.get('status') == 'accepted':
                job.status = JobStatus.QUEUED
                job.server = self.server.name
                job.submitted_at = datetime.now()
                return True

            return False

        except Exception as e:
            job.error_message = f"Failed to submit job: {e}"
            job.status = JobStatus.FAILED
            return False

    def get_job_status(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status from server.

        Args:
            job_id: Job ID

        Returns:
            Job status information
        """
        try:
            response = self._get_json(f'/api/v1/build/{job_id}')
            return response
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

    def download_artifact(self, job_id: str, output_path: Path) -> bool:
        """
        Download build artifact.

        Args:
            job_id: Job ID
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            url = f"{self.server.url}/api/v1/build/{job_id}/artifact"
            self._download_file(url, output_path)
            return True
        except Exception as e:
            print(f"Failed to download artifact: {e}")
            return False

    def _package_sources(self, source_files: List[Path]) -> bytes:
        """Package source files into tarball."""
        with tempfile.NamedTemporaryFile(suffix='.tar.gz', delete=False) as f:
            with tarfile.open(f.name, 'w:gz') as tar:
                for source_file in source_files:
                    tar.add(source_file, arcname=source_file.name)

            with open(f.name, 'rb') as archive:
                data = archive.read()

            os.unlink(f.name)
            return data

    def _post_json(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """POST JSON to server."""
        url = f"{self.server.url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Lament-Builder/2.0'
        }

        if self.server.api_key:
            headers['Authorization'] = f'Bearer {self.server.api_key}'

        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode('utf-8'),
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))

    def _get_json(self, endpoint: str) -> Dict[str, Any]:
        """GET JSON from server."""
        url = f"{self.server.url}{endpoint}"
        headers = {'User-Agent': 'Lament-Builder/2.0'}

        if self.server.api_key:
            headers['Authorization'] = f'Bearer {self.server.api_key}'

        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode('utf-8'))

    def _download_file(self, url: str, output_path: Path) -> None:
        """Download file from URL."""
        headers = {'User-Agent': 'Lament-Builder/2.0'}

        if self.server.api_key:
            headers['Authorization'] = f'Bearer {self.server.api_key}'

        request = urllib.request.Request(url, headers=headers)

        with urllib.request.urlopen(request, timeout=300) as response:
            with open(output_path, 'wb') as f:
                f.write(response.read())


# ============================================================================
# SSH BUILD CLIENT
# ============================================================================

class SSHBuildClient:
    """Client for SSH-based remote builds."""

    def __init__(self, host: str, username: str, key_file: Optional[Path] = None):
        """Initialize SSH build client."""
        self.host = host
        self.username = username
        self.key_file = key_file

    def submit_job(self, job: BuildJob, remote_dir: str = "/tmp/lament-build") -> bool:
        """
        Submit build job via SSH.

        Args:
            job: Build job
            remote_dir: Remote build directory

        Returns:
            True if successful
        """
        try:
            # Upload source files
            print(f"  Uploading sources to {self.host}...")
            self._upload_files(job.source_files, remote_dir)

            # Execute build remotely
            print(f"  Building on {self.host}...")
            build_cmd = f"cd {remote_dir} && lament-cross --target {job.target_platform} main.lament"
            output = self._execute_remote(build_cmd)

            job.build_log = output.split('\n')
            job.status = JobStatus.SUCCESS

            # Download artifact
            print(f"  Downloading artifact...")
            artifact_path = f"{remote_dir}/main"
            if job.output_file:
                self._download_file(artifact_path, job.output_file)

            return True

        except Exception as e:
            job.error_message = str(e)
            job.status = JobStatus.FAILED
            return False

    def _upload_files(self, files: List[Path], remote_dir: str) -> None:
        """Upload files via SCP."""
        for file in files:
            cmd = self._build_scp_cmd(str(file), f"{remote_dir}/{file.name}")
            subprocess.run(cmd, check=True, capture_output=True)

    def _download_file(self, remote_path: str, local_path: Path) -> None:
        """Download file via SCP."""
        cmd = self._build_scp_cmd(
            f"{self.username}@{self.host}:{remote_path}",
            str(local_path)
        )
        subprocess.run(cmd, check=True, capture_output=True)

    def _execute_remote(self, command: str) -> str:
        """Execute command via SSH."""
        ssh_cmd = ["ssh"]

        if self.key_file:
            ssh_cmd.extend(["-i", str(self.key_file)])

        ssh_cmd.extend([
            f"{self.username}@{self.host}",
            command
        ])

        result = subprocess.run(ssh_cmd, check=True, capture_output=True, text=True)
        return result.stdout

    def _build_scp_cmd(self, source: str, dest: str) -> List[str]:
        """Build SCP command."""
        cmd = ["scp"]

        if self.key_file:
            cmd.extend(["-i", str(self.key_file)])

        cmd.extend([source, dest])
        return cmd


# ============================================================================
# REMOTE BUILDER
# ============================================================================

class RemoteBuilder:
    """Main remote builder orchestrator."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize remote builder."""
        self.cache_dir = cache_dir or Path.home() / ".lament" / "build_cache"
        self.cache = BuildCache(self.cache_dir)
        self.servers: Dict[str, BuildServer] = {}
        self.jobs: Dict[str, BuildJob] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load server configuration."""
        config_file = Path.home() / ".lament" / "remote_build.json"

        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                for server_data in config.get('servers', []):
                    server = BuildServer(**server_data)
                    self.servers[server.name] = server

    def add_server(self, server: BuildServer) -> None:
        """Add build server."""
        self.servers[server.name] = server

    def submit_build(self, source_files: List[Path], target_platform: str,
                    output_file: Path, use_cache: bool = True) -> BuildJob:
        """
        Submit build job.

        Args:
            source_files: Source files
            target_platform: Target platform
            output_file: Output file path
            use_cache: Use cached artifacts if available

        Returns:
            Build job
        """
        # Check cache first
        if use_cache:
            cache_key = self.cache.get_cache_key(source_files, target_platform)
            cached = self.cache.get_cached(cache_key)

            if cached:
                print(f"Using cached build: {cached}")
                import shutil
                shutil.copy2(cached, output_file)

                # Create completed job
                job = BuildJob(
                    job_id=cache_key[:8],
                    source_files=source_files,
                    target_platform=target_platform,
                    status=JobStatus.SUCCESS,
                    output_file=output_file
                )
                return job

        # Create new job
        job_id = hashlib.sha256(
            f"{datetime.now().isoformat()}{source_files[0]}".encode()
        ).hexdigest()[:16]

        job = BuildJob(
            job_id=job_id,
            source_files=source_files,
            target_platform=target_platform,
            output_file=output_file
        )

        self.jobs[job_id] = job

        # Find available server
        server = self._select_server()
        if not server:
            print("Error: No build servers available")
            job.status = JobStatus.FAILED
            job.error_message = "No servers available"
            return job

        # Submit job
        print(f"Submitting build to {server.name}...")
        client = BuildClient(server)

        if client.submit_job(job):
            # Wait for completion
            self._wait_for_job(job, client)

            # Cache successful build
            if job.status == JobStatus.SUCCESS and job.output_file:
                cache_key = self.cache.get_cache_key(source_files, target_platform)
                self.cache.store(cache_key, job.output_file, job.to_dict())

        return job

    def _select_server(self) -> Optional[BuildServer]:
        """Select available build server."""
        for server in self.servers.values():
            if server.enabled:
                return server
        return None

    def _wait_for_job(self, job: BuildJob, client: BuildClient) -> None:
        """Wait for job completion."""
        print(f"Building on {job.server}...")

        start_time = time.time()
        while True:
            # Check timeout
            if time.time() - start_time > client.server.timeout:
                job.status = JobStatus.FAILED
                job.error_message = "Build timeout"
                return

            # Get status
            status = client.get_job_status(job.job_id)

            if status.get('status') == 'completed':
                job.status = JobStatus.SUCCESS
                job.completed_at = datetime.now()

                # Download artifact
                if job.output_file:
                    client.download_artifact(job.job_id, job.output_file)
                    print(f"Downloaded: {job.output_file}")
                return

            elif status.get('status') == 'failed':
                job.status = JobStatus.FAILED
                job.error_message = status.get('message', 'Build failed')
                job.completed_at = datetime.now()
                return

            # Wait before next check
            time.sleep(5)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return self.cache.get_stats()

    def clear_cache(self) -> None:
        """Clear build cache."""
        self.cache.clear()
        print("Build cache cleared")


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Remote Builder - Distributed Compilation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-build --remote main.lament --target linux-x86_64
  lament-build --remote main.lament --server https://build.example.com
  lament-build --remote --cache-stats
  lament-build --remote --clear-cache

Configuration:
  Server configuration is stored in ~/.lament/remote_build.json
        """
    )

    parser.add_argument('--version', action='version', version='lament-remote 2.0.0')

    parser.add_argument('source', type=Path, nargs='?',
                       help='Source Lament file')
    parser.add_argument('--remote', action='store_true',
                       help='Enable remote building')
    parser.add_argument('-o', '--output', type=Path,
                       help='Output file')
    parser.add_argument('--target', type=str, default='linux-x86_64',
                       help='Target platform')
    parser.add_argument('--server', type=str,
                       help='Build server URL')
    parser.add_argument('--no-cache', action='store_true',
                       help='Disable build cache')

    # Cache management
    parser.add_argument('--cache-stats', action='store_true',
                       help='Show cache statistics')
    parser.add_argument('--clear-cache', action='store_true',
                       help='Clear build cache')

    args = parser.parse_args()

    # Create remote builder
    builder = RemoteBuilder()

    # Cache management
    if args.cache_stats:
        stats = builder.get_cache_stats()
        print("Build Cache Statistics:")
        print(f"  Entries: {stats['entries']}")
        print(f"  Total size: {stats['total_size']:,} bytes")
        print(f"  Cache dir: {stats['cache_dir']}")
        return 0

    if args.clear_cache:
        builder.clear_cache()
        return 0

    # Validate source
    if not args.source:
        parser.print_help()
        return 1

    if not args.source.exists():
        print(f"Error: Source file not found: {args.source}")
        return 1

    # Add custom server if specified
    if args.server:
        server = BuildServer(
            name="custom",
            url=args.server
        )
        builder.add_server(server)

    # Determine output
    if not args.output:
        ext = ".exe" if "windows" in args.target else ""
        args.output = Path(f"{args.source.stem}{ext}")

    # Submit build
    job = builder.submit_build(
        [args.source],
        args.target,
        args.output,
        use_cache=not args.no_cache
    )

    # Print result
    if job.status == JobStatus.SUCCESS:
        print(f"\nBuild successful!")
        print(f"Output: {job.output_file}")
        if job.duration:
            print(f"Duration: {job.duration.total_seconds():.1f}s")
        return 0
    else:
        print(f"\nBuild failed: {job.error_message}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
