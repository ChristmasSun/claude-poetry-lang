#!/usr/bin/env python3
"""
Storage Backend for Lament Registry Server

Handles package file storage with multiple backend support:
- Filesystem storage
- S3/Object storage
- Package upload/download
- Deduplication
- Garbage collection
- Backup/restore

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import asyncio
import hashlib
import shutil
import tarfile
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any, BinaryIO

# Try to import optional dependencies
try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


# ============================================================================
# STORAGE BACKEND INTERFACE
# ============================================================================

class StorageBackend(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def store_package(self, name: str, version: str, data: bytes) -> str:
        """
        Store a package file.

        Args:
            name: Package name
            version: Package version
            data: Package file data

        Returns:
            Storage path/key
        """
        pass

    @abstractmethod
    async def get_package(self, name: str, version: str) -> Optional[Path]:
        """
        Get a package file path.

        Args:
            name: Package name
            version: Package version

        Returns:
            Path to package file, or None if not found
        """
        pass

    @abstractmethod
    async def delete_package(self, name: str, version: str) -> bool:
        """
        Delete a package file.

        Args:
            name: Package name
            version: Package version

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def list_packages(self) -> List[Dict[str, Any]]:
        """
        List all stored packages.

        Returns:
            List of package info dicts
        """
        pass

    @abstractmethod
    async def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.

        Returns:
            Dict with storage stats
        """
        pass

    @abstractmethod
    async def cleanup_orphaned_files(self) -> int:
        """
        Clean up orphaned files not referenced in database.

        Returns:
            Number of files cleaned up
        """
        pass


# ============================================================================
# FILESYSTEM STORAGE
# ============================================================================

class FilesystemStorage(StorageBackend):
    """Filesystem-based storage backend."""

    def __init__(self, base_path: Path):
        """
        Initialize filesystem storage.

        Args:
            base_path: Base directory for package storage
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Create subdirectories for organization
        self.packages_dir = self.base_path / "packages"
        self.temp_dir = self.base_path / "temp"
        self.backup_dir = self.base_path / "backups"

        self.packages_dir.mkdir(exist_ok=True)
        self.temp_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)

    def _get_package_path(self, name: str, version: str) -> Path:
        """Get path for a package file."""
        # Use first letter for directory organization (like npm)
        first_letter = name[0].lower()
        package_dir = self.packages_dir / first_letter / name
        package_dir.mkdir(parents=True, exist_ok=True)
        return package_dir / f"{name}-{version}.tar.gz"

    async def store_package(self, name: str, version: str, data: bytes) -> str:
        """Store a package file."""
        package_path = self._get_package_path(name, version)

        # Write file
        if AIOFILES_AVAILABLE:
            async with aiofiles.open(package_path, 'wb') as f:
                await f.write(data)
        else:
            # Fallback to synchronous I/O
            with open(package_path, 'wb') as f:
                f.write(data)

        return str(package_path)

    async def get_package(self, name: str, version: str) -> Optional[Path]:
        """Get a package file path."""
        package_path = self._get_package_path(name, version)

        if package_path.exists():
            return package_path

        return None

    async def delete_package(self, name: str, version: str) -> bool:
        """Delete a package file."""
        package_path = self._get_package_path(name, version)

        if package_path.exists():
            package_path.unlink()
            return True

        return False

    async def list_packages(self) -> List[Dict[str, Any]]:
        """List all stored packages."""
        packages = []

        for package_file in self.packages_dir.rglob("*.tar.gz"):
            stat = package_file.stat()
            packages.append({
                'path': str(package_file),
                'size': stat.st_size,
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
            })

        return packages

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        total_size = 0
        file_count = 0

        for package_file in self.packages_dir.rglob("*.tar.gz"):
            total_size += package_file.stat().st_size
            file_count += 1

        return {
            'total_size': total_size,
            'file_count': file_count,
            'backend': 'filesystem',
            'base_path': str(self.base_path)
        }

    async def cleanup_orphaned_files(self) -> int:
        """Clean up orphaned files."""
        # This would require database integration to check which files are orphaned
        # For now, just clean up temp directory
        cleaned = 0

        for temp_file in self.temp_dir.iterdir():
            # Delete files older than 1 hour
            if temp_file.is_file():
                age = datetime.now().timestamp() - temp_file.stat().st_mtime
                if age > 3600:  # 1 hour
                    temp_file.unlink()
                    cleaned += 1

        return cleaned

    async def create_backup(self, backup_name: Optional[str] = None) -> Path:
        """
        Create a backup of all packages.

        Args:
            backup_name: Optional backup name (defaults to timestamp)

        Returns:
            Path to backup file
        """
        if not backup_name:
            backup_name = f"backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        backup_file = self.backup_dir / f"{backup_name}.tar.gz"

        # Create tarball of packages directory
        with tarfile.open(backup_file, 'w:gz') as tar:
            tar.add(self.packages_dir, arcname='packages')

        return backup_file

    async def restore_backup(self, backup_file: Path) -> bool:
        """
        Restore packages from a backup.

        Args:
            backup_file: Path to backup file

        Returns:
            True if successful
        """
        if not backup_file.exists():
            return False

        try:
            # Extract backup
            with tarfile.open(backup_file, 'r:gz') as tar:
                tar.extractall(self.base_path)

            return True
        except Exception:
            return False

    async def deduplicate(self) -> Dict[str, Any]:
        """
        Deduplicate packages by checksum.

        Returns:
            Stats about deduplication
        """
        checksums: Dict[str, List[Path]] = {}

        # Calculate checksums for all packages
        for package_file in self.packages_dir.rglob("*.tar.gz"):
            with open(package_file, 'rb') as f:
                checksum = hashlib.sha256(f.read()).hexdigest()

            if checksum not in checksums:
                checksums[checksum] = []
            checksums[checksum].append(package_file)

        # Find duplicates
        duplicates = {k: v for k, v in checksums.items() if len(v) > 1}
        space_saved = 0
        files_removed = 0

        # For each duplicate set, keep one and remove others
        for checksum, files in duplicates.items():
            # Keep the first file, remove others
            files_to_remove = files[1:]

            for file_path in files_to_remove:
                size = file_path.stat().st_size
                file_path.unlink()
                space_saved += size
                files_removed += 1

        return {
            'duplicates_found': len(duplicates),
            'files_removed': files_removed,
            'space_saved': space_saved
        }


# ============================================================================
# S3 STORAGE
# ============================================================================

class S3Storage(StorageBackend):
    """S3-based storage backend."""

    def __init__(
        self,
        bucket_name: str,
        region: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        endpoint_url: Optional[str] = None
    ):
        """
        Initialize S3 storage.

        Args:
            bucket_name: S3 bucket name
            region: AWS region
            aws_access_key_id: AWS access key (uses default credentials if not provided)
            aws_secret_access_key: AWS secret key
            endpoint_url: Custom endpoint URL (for S3-compatible services)
        """
        if not BOTO3_AVAILABLE:
            raise RuntimeError("boto3 is required for S3 storage")

        self.bucket_name = bucket_name
        self.region = region

        # Initialize S3 client
        session_kwargs = {}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs['aws_access_key_id'] = aws_access_key_id
            session_kwargs['aws_secret_access_key'] = aws_secret_access_key

        client_kwargs = {'region_name': region}
        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url

        self.s3_client = boto3.client('s3', **{**session_kwargs, **client_kwargs})

        # Ensure bucket exists
        self._ensure_bucket()

    def _ensure_bucket(self):
        """Ensure S3 bucket exists."""
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                # Bucket doesn't exist, create it
                try:
                    if self.region == 'us-east-1':
                        self.s3_client.create_bucket(Bucket=self.bucket_name)
                    else:
                        self.s3_client.create_bucket(
                            Bucket=self.bucket_name,
                            CreateBucketConfiguration={'LocationConstraint': self.region}
                        )
                except ClientError:
                    pass

    def _get_package_key(self, name: str, version: str) -> str:
        """Get S3 key for a package."""
        first_letter = name[0].lower()
        return f"packages/{first_letter}/{name}/{name}-{version}.tar.gz"

    async def store_package(self, name: str, version: str, data: bytes) -> str:
        """Store a package file in S3."""
        key = self._get_package_key(name, version)

        # Upload to S3
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=data,
                ContentType='application/gzip'
            )
        )

        return key

    async def get_package(self, name: str, version: str) -> Optional[Path]:
        """
        Get a package file from S3.

        Downloads to a temporary file and returns the path.
        """
        key = self._get_package_key(name, version)

        try:
            # Download to temporary file
            temp_file = Path(tempfile.mktemp(suffix='.tar.gz'))

            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.download_file(
                    self.bucket_name,
                    key,
                    str(temp_file)
                )
            )

            return temp_file
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                return None
            raise

    async def delete_package(self, name: str, version: str) -> bool:
        """Delete a package file from S3."""
        key = self._get_package_key(name, version)

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.delete_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
            )
            return True
        except ClientError:
            return False

    async def list_packages(self) -> List[Dict[str, Any]]:
        """List all packages in S3."""
        packages = []

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.s3_client.list_objects_v2(
                    Bucket=self.bucket_name,
                    Prefix='packages/'
                )
            )

            for obj in response.get('Contents', []):
                packages.append({
                    'key': obj['Key'],
                    'size': obj['Size'],
                    'modified': obj['LastModified'].isoformat()
                })

        except ClientError:
            pass

        return packages

    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics."""
        packages = await self.list_packages()

        total_size = sum(p['size'] for p in packages)
        file_count = len(packages)

        return {
            'total_size': total_size,
            'file_count': file_count,
            'backend': 's3',
            'bucket': self.bucket_name,
            'region': self.region
        }

    async def cleanup_orphaned_files(self) -> int:
        """Clean up orphaned files in S3."""
        # This would require database integration
        # For now, return 0
        return 0

    async def enable_versioning(self) -> bool:
        """Enable versioning on the S3 bucket."""
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.put_bucket_versioning(
                    Bucket=self.bucket_name,
                    VersioningConfiguration={'Status': 'Enabled'}
                )
            )
            return True
        except ClientError:
            return False

    async def set_lifecycle_policy(self, days_to_glacier: int = 90, days_to_delete: int = 365):
        """
        Set lifecycle policy for the bucket.

        Args:
            days_to_glacier: Days before moving to Glacier
            days_to_delete: Days before deleting old versions
        """
        lifecycle_policy = {
            'Rules': [
                {
                    'Id': 'Archive old versions',
                    'Status': 'Enabled',
                    'Transitions': [
                        {
                            'Days': days_to_glacier,
                            'StorageClass': 'GLACIER'
                        }
                    ],
                    'NoncurrentVersionExpiration': {
                        'NoncurrentDays': days_to_delete
                    }
                }
            ]
        }

        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.s3_client.put_bucket_lifecycle_configuration(
                    Bucket=self.bucket_name,
                    LifecycleConfiguration=lifecycle_policy
                )
            )
            return True
        except ClientError:
            return False


# ============================================================================
# STORAGE UTILITIES
# ============================================================================

def calculate_checksum(file_path: Path) -> str:
    """
    Calculate SHA256 checksum of a file.

    Args:
        file_path: Path to file

    Returns:
        Hex digest of checksum
    """
    sha256 = hashlib.sha256()

    with open(file_path, 'rb') as f:
        while chunk := f.read(8192):
            sha256.update(chunk)

    return sha256.hexdigest()


def validate_package_archive(file_path: Path) -> bool:
    """
    Validate that a file is a valid tar.gz archive.

    Args:
        file_path: Path to archive

    Returns:
        True if valid, False otherwise
    """
    try:
        with tarfile.open(file_path, 'r:gz') as tar:
            # Try to list members
            tar.getmembers()
        return True
    except Exception:
        return False


def extract_package_metadata(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Extract metadata from a package archive.

    Args:
        file_path: Path to package archive

    Returns:
        Metadata dict if found, None otherwise
    """
    try:
        with tarfile.open(file_path, 'r:gz') as tar:
            # Look for package.lament file
            for member in tar.getmembers():
                if member.name.endswith('package.lament'):
                    f = tar.extractfile(member)
                    if f:
                        import json
                        metadata = json.load(f)
                        return metadata

        return None
    except Exception:
        return None


def format_size(size_bytes: int) -> str:
    """
    Format bytes to human-readable size.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0

    return f"{size_bytes:.2f} PB"
