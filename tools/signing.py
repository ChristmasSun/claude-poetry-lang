#!/usr/bin/env python3
"""
Lament Package Signing - Cryptographic Security for the Soul

Comprehensive package signing and verification system supporting GPG/PGP,
Ed25519, key management, trust chains, and timestamping.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import base64
import hashlib
import json
import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
import urllib.request
import urllib.error


# ============================================================================
# CRYPTOGRAPHIC PRIMITIVES
# ============================================================================

class CryptoError(Exception):
    """Cryptography operation error."""
    pass


# Check if cryptography is available
CRYPTO_AVAILABLE = False
ed25519 = None
serialization = None
InvalidSignature = Exception
hashes = None
rsa = None
padding = None

def _try_import_crypto():
    """Attempt to import cryptography library."""
    global CRYPTO_AVAILABLE, ed25519, serialization, InvalidSignature, hashes, rsa, padding
    try:
        from cryptography.hazmat.primitives import hashes as _hashes, serialization as _serialization
        from cryptography.hazmat.primitives.asymmetric import ed25519 as _ed25519, padding as _padding, rsa as _rsa
        from cryptography.hazmat.backends import default_backend as _default_backend
        from cryptography.exceptions import InvalidSignature as _InvalidSignature

        # If we get here, imports succeeded
        CRYPTO_AVAILABLE = True
        ed25519 = _ed25519
        serialization = _serialization
        InvalidSignature = _InvalidSignature
        hashes = _hashes
        rsa = _rsa
        padding = _padding
        return True
    except:
        return False

# Try importing at module load time
_try_import_crypto()

# Define fallback implementations
if not CRYPTO_AVAILABLE:
    # Define dummy classes to allow module to load
    class ed25519:
        class Ed25519PrivateKey:
            pass
        class Ed25519PublicKey:
            pass

    class serialization:
        class Encoding:
            PEM = None
        class PrivateFormat:
            PKCS8 = None
        class PublicFormat:
            SubjectPublicKeyInfo = None
        class NoEncryption:
            pass
        class BestAvailableEncryption:
            def __init__(self, password): pass

        @staticmethod
        def load_pem_private_key(*args, **kwargs):
            raise CryptoError("Cryptography library not available")

        @staticmethod
        def load_pem_public_key(*args, **kwargs):
            raise CryptoError("Cryptography library not available")

    class InvalidSignature(Exception):
        pass

    def default_backend():
        return None
else:
    from cryptography.hazmat.backends import default_backend


# ============================================================================
# KEY MANAGEMENT
# ============================================================================

@dataclass
class KeyInfo:
    """Information about a cryptographic key."""
    key_id: str
    algorithm: str  # ed25519, rsa, gpg
    fingerprint: str
    created_at: str
    email: Optional[str] = None
    name: Optional[str] = None
    expires_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'KeyInfo':
        """Create from dictionary."""
        return KeyInfo(**data)


class Ed25519KeyPair:
    """Ed25519 key pair for signing."""

    def __init__(self, private_key=None, public_key=None):
        """Initialize key pair."""
        if not CRYPTO_AVAILABLE:
            raise CryptoError("Cryptography library not available")

        if private_key:
            self.private_key = private_key
            self.public_key = private_key.public_key()
        elif public_key:
            self.private_key = None
            self.public_key = public_key
        else:
            # Generate new key pair
            self.private_key = ed25519.Ed25519PrivateKey.generate()
            self.public_key = self.private_key.public_key()

    def sign(self, data: bytes) -> bytes:
        """Sign data."""
        if not self.private_key:
            raise CryptoError("No private key available for signing")
        return self.private_key.sign(data)

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify signature."""
        try:
            self.public_key.verify(signature, data)
            return True
        except InvalidSignature:
            return False

    def export_private_key(self, password: Optional[bytes] = None) -> bytes:
        """Export private key in PEM format."""
        if not self.private_key:
            raise CryptoError("No private key to export")

        if password:
            encryption = serialization.BestAvailableEncryption(password)
        else:
            encryption = serialization.NoEncryption()

        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )

    def export_public_key(self) -> bytes:
        """Export public key in PEM format."""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

    @staticmethod
    def load_private_key(data: bytes, password: Optional[bytes] = None) -> 'Ed25519KeyPair':
        """Load private key from PEM."""
        if not CRYPTO_AVAILABLE:
            raise CryptoError("Cryptography library not available")

        # Import at runtime to avoid top-level import issues
        from cryptography.hazmat.primitives import serialization as _ser
        from cryptography.hazmat.backends import default_backend as _backend

        private_key = _ser.load_pem_private_key(
            data,
            password=password,
            backend=_backend()
        )

        if not isinstance(private_key, ed25519.Ed25519PrivateKey):
            raise CryptoError("Not an Ed25519 private key")

        return Ed25519KeyPair(private_key=private_key)

    @staticmethod
    def load_public_key(data: bytes) -> 'Ed25519KeyPair':
        """Load public key from PEM."""
        if not CRYPTO_AVAILABLE:
            raise CryptoError("Cryptography library not available")

        # Import at runtime to avoid top-level import issues
        from cryptography.hazmat.primitives import serialization as _ser
        from cryptography.hazmat.backends import default_backend as _backend

        public_key = _ser.load_pem_public_key(
            data,
            backend=_backend()
        )

        if not isinstance(public_key, ed25519.Ed25519PublicKey):
            raise CryptoError("Not an Ed25519 public key")

        return Ed25519KeyPair(public_key=public_key)

    def get_fingerprint(self) -> str:
        """Get key fingerprint."""
        public_bytes = self.export_public_key()
        return hashlib.sha256(public_bytes).hexdigest()[:16]


class KeyStore:
    """Manages cryptographic keys."""

    def __init__(self, store_path: Optional[Path] = None):
        """Initialize key store."""
        if store_path:
            self.store_path = store_path
        else:
            self.store_path = Path.home() / '.lament' / 'keys'

        self.store_path.mkdir(parents=True, exist_ok=True)
        self.keys_file = self.store_path / 'keys.json'
        self._load_keys()

    def _load_keys(self) -> None:
        """Load keys index."""
        if self.keys_file.exists():
            with open(self.keys_file, 'r') as f:
                data = json.load(f)
                self.keys = {k: KeyInfo.from_dict(v) for k, v in data.items()}
        else:
            self.keys = {}

    def _save_keys(self) -> None:
        """Save keys index."""
        with open(self.keys_file, 'w') as f:
            data = {k: v.to_dict() for k, v in self.keys.items()}
            json.dump(data, f, indent=2)

    def generate_key(self, name: str, email: str, algorithm: str = 'ed25519') -> KeyInfo:
        """Generate a new key pair."""
        if algorithm != 'ed25519':
            raise CryptoError(f"Unsupported algorithm: {algorithm}")

        if not CRYPTO_AVAILABLE:
            raise CryptoError("Cryptography library not available")

        # Generate key pair
        keypair = Ed25519KeyPair()

        # Create key info
        fingerprint = keypair.get_fingerprint()
        key_id = fingerprint[:8]

        key_info = KeyInfo(
            key_id=key_id,
            algorithm=algorithm,
            fingerprint=fingerprint,
            created_at=datetime.now().isoformat(),
            email=email,
            name=name
        )

        # Save keys
        private_path = self.store_path / f'{key_id}.private.pem'
        public_path = self.store_path / f'{key_id}.public.pem'

        with open(private_path, 'wb') as f:
            f.write(keypair.export_private_key())

        with open(public_path, 'wb') as f:
            f.write(keypair.export_public_key())

        # Set restrictive permissions on private key
        os.chmod(private_path, 0o600)

        # Update index
        self.keys[key_id] = key_info
        self._save_keys()

        print(f"Generated key: {key_id}")
        print(f"Fingerprint: {fingerprint}")

        return key_info

    def import_key(self, key_data: bytes, key_type: str = 'public') -> KeyInfo:
        """Import a key."""
        if not CRYPTO_AVAILABLE:
            raise CryptoError("Cryptography library not available")

        if key_type == 'private':
            keypair = Ed25519KeyPair.load_private_key(key_data)
        else:
            keypair = Ed25519KeyPair.load_public_key(key_data)

        fingerprint = keypair.get_fingerprint()
        key_id = fingerprint[:8]

        # Check if key already exists
        if key_id in self.keys:
            print(f"Key {key_id} already exists")
            return self.keys[key_id]

        # Save key
        if key_type == 'private':
            path = self.store_path / f'{key_id}.private.pem'
            with open(path, 'wb') as f:
                f.write(keypair.export_private_key())
            os.chmod(path, 0o600)

        path = self.store_path / f'{key_id}.public.pem'
        with open(path, 'wb') as f:
            f.write(keypair.export_public_key())

        # Create key info
        key_info = KeyInfo(
            key_id=key_id,
            algorithm='ed25519',
            fingerprint=fingerprint,
            created_at=datetime.now().isoformat()
        )

        self.keys[key_id] = key_info
        self._save_keys()

        print(f"Imported key: {key_id}")
        return key_info

    def export_key(self, key_id: str, include_private: bool = False) -> bytes:
        """Export a key."""
        if key_id not in self.keys:
            raise CryptoError(f"Key not found: {key_id}")

        if include_private:
            path = self.store_path / f'{key_id}.private.pem'
            if not path.exists():
                raise CryptoError(f"Private key not available: {key_id}")
        else:
            path = self.store_path / f'{key_id}.public.pem'

        with open(path, 'rb') as f:
            return f.read()

    def get_key(self, key_id: str) -> Optional[KeyInfo]:
        """Get key info."""
        return self.keys.get(key_id)

    def list_keys(self) -> List[KeyInfo]:
        """List all keys."""
        return list(self.keys.values())

    def load_keypair(self, key_id: str) -> Ed25519KeyPair:
        """Load a key pair for signing."""
        if key_id not in self.keys:
            raise CryptoError(f"Key not found: {key_id}")

        private_path = self.store_path / f'{key_id}.private.pem'

        if private_path.exists():
            with open(private_path, 'rb') as f:
                return Ed25519KeyPair.load_private_key(f.read())
        else:
            # Load public key only
            public_path = self.store_path / f'{key_id}.public.pem'
            with open(public_path, 'rb') as f:
                return Ed25519KeyPair.load_public_key(f.read())


# ============================================================================
# GPG INTEGRATION
# ============================================================================

class GPGSigner:
    """GPG/PGP signing integration."""

    def __init__(self):
        """Initialize GPG signer."""
        self._check_gpg()

    def _check_gpg(self) -> bool:
        """Check if GPG is available."""
        try:
            subprocess.run(['gpg', '--version'], capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def _run_gpg(self, args: List[str], input_data: Optional[bytes] = None) -> bytes:
        """Run GPG command."""
        try:
            result = subprocess.run(
                ['gpg'] + args,
                input=input_data,
                capture_output=True,
                check=True
            )
            return result.stdout
        except subprocess.CalledProcessError as e:
            raise CryptoError(f"GPG command failed: {e.stderr.decode()}")

    def sign(self, data: bytes, key_id: Optional[str] = None) -> bytes:
        """Sign data with GPG."""
        args = ['--detach-sign', '--armor']
        if key_id:
            args.extend(['--local-user', key_id])

        return self._run_gpg(args, input_data=data)

    def verify(self, data: bytes, signature: bytes) -> bool:
        """Verify GPG signature."""
        # Write signature to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False) as sig_file:
            sig_file.write(signature)
            sig_path = sig_file.name

        try:
            self._run_gpg(['--verify', sig_path, '-'], input_data=data)
            return True
        except CryptoError:
            return False
        finally:
            os.unlink(sig_path)

    def list_keys(self) -> List[Dict[str, str]]:
        """List GPG keys."""
        output = self._run_gpg(['--list-keys', '--with-colons'])
        keys = []

        for line in output.decode().split('\n'):
            if line.startswith('pub:'):
                parts = line.split(':')
                keys.append({
                    'key_id': parts[4],
                    'algorithm': parts[3],
                    'created': parts[5]
                })

        return keys


# ============================================================================
# PACKAGE SIGNATURES
# ============================================================================

@dataclass
class PackageSignature:
    """Represents a package signature."""
    package_name: str
    version: str
    algorithm: str
    key_id: str
    signature: str
    checksum: str
    timestamp: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PackageSignature':
        """Create from dictionary."""
        return PackageSignature(**data)

    def to_file(self, filepath: Path) -> None:
        """Save signature to file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)

    @staticmethod
    def from_file(filepath: Path) -> 'PackageSignature':
        """Load signature from file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return PackageSignature.from_dict(data)


# ============================================================================
# PACKAGE SIGNER
# ============================================================================

class PackageSigner:
    """Signs and verifies Lament packages."""

    def __init__(self, keystore: Optional[KeyStore] = None):
        """Initialize package signer."""
        self.keystore = keystore or KeyStore()

    def sign_package(self, package_path: Path, key_id: str,
                    algorithm: str = 'ed25519') -> PackageSignature:
        """Sign a package file."""
        if not package_path.exists():
            raise CryptoError(f"Package not found: {package_path}")

        # Read package data
        with open(package_path, 'rb') as f:
            package_data = f.read()

        # Calculate checksum
        checksum = hashlib.sha256(package_data).hexdigest()

        # Sign based on algorithm
        if algorithm == 'ed25519':
            signature_bytes = self._sign_ed25519(package_data, key_id)
        elif algorithm == 'gpg':
            signature_bytes = self._sign_gpg(package_data, key_id)
        else:
            raise CryptoError(f"Unsupported algorithm: {algorithm}")

        # Encode signature
        signature = base64.b64encode(signature_bytes).decode()

        # Extract package info
        package_name = package_path.stem
        version = "unknown"

        # Create signature
        pkg_signature = PackageSignature(
            package_name=package_name,
            version=version,
            algorithm=algorithm,
            key_id=key_id,
            signature=signature,
            checksum=checksum,
            timestamp=datetime.now().isoformat(),
            metadata={
                'signer': self.keystore.get_key(key_id).email if key_id in self.keystore.keys else None
            }
        )

        # Save signature file
        sig_path = package_path.with_suffix(package_path.suffix + '.sig')
        pkg_signature.to_file(sig_path)

        print(f"Signed package: {package_path}")
        print(f"Signature saved: {sig_path}")
        print(f"Checksum: {checksum}")

        return pkg_signature

    def _sign_ed25519(self, data: bytes, key_id: str) -> bytes:
        """Sign with Ed25519."""
        if not CRYPTO_AVAILABLE:
            raise CryptoError("Cryptography library not available")

        keypair = self.keystore.load_keypair(key_id)
        return keypair.sign(data)

    def _sign_gpg(self, data: bytes, key_id: str) -> bytes:
        """Sign with GPG."""
        gpg = GPGSigner()
        return gpg.sign(data, key_id)

    def verify_package(self, package_path: Path,
                      signature_path: Optional[Path] = None) -> bool:
        """Verify a package signature."""
        if not package_path.exists():
            raise CryptoError(f"Package not found: {package_path}")

        # Load signature
        if not signature_path:
            signature_path = package_path.with_suffix(package_path.suffix + '.sig')

        if not signature_path.exists():
            raise CryptoError(f"Signature not found: {signature_path}")

        pkg_signature = PackageSignature.from_file(signature_path)

        # Read package data
        with open(package_path, 'rb') as f:
            package_data = f.read()

        # Verify checksum
        checksum = hashlib.sha256(package_data).hexdigest()
        if checksum != pkg_signature.checksum:
            print("Checksum mismatch!")
            return False

        # Decode signature
        signature_bytes = base64.b64decode(pkg_signature.signature)

        # Verify based on algorithm
        if pkg_signature.algorithm == 'ed25519':
            result = self._verify_ed25519(package_data, signature_bytes, pkg_signature.key_id)
        elif pkg_signature.algorithm == 'gpg':
            result = self._verify_gpg(package_data, signature_bytes)
        else:
            raise CryptoError(f"Unsupported algorithm: {pkg_signature.algorithm}")

        if result:
            print(f"Signature valid!")
            print(f"Signed by: {pkg_signature.key_id}")
            print(f"Timestamp: {pkg_signature.timestamp}")
        else:
            print("Signature verification failed!")

        return result

    def _verify_ed25519(self, data: bytes, signature: bytes, key_id: str) -> bool:
        """Verify Ed25519 signature."""
        if not CRYPTO_AVAILABLE:
            raise CryptoError("Cryptography library not available")

        try:
            keypair = self.keystore.load_keypair(key_id)
            return keypair.verify(data, signature)
        except Exception as e:
            print(f"Verification error: {e}")
            return False

    def _verify_gpg(self, data: bytes, signature: bytes) -> bool:
        """Verify GPG signature."""
        gpg = GPGSigner()
        return gpg.verify(data, signature)

    def sign_directory(self, directory: Path, key_id: str) -> List[PackageSignature]:
        """Sign all packages in a directory."""
        signatures = []

        for package_file in directory.glob('*.tar.gz'):
            try:
                sig = self.sign_package(package_file, key_id)
                signatures.append(sig)
            except CryptoError as e:
                print(f"Failed to sign {package_file}: {e}")

        return signatures


# ============================================================================
# TRUST CHAIN
# ============================================================================

@dataclass
class TrustEntry:
    """Trust chain entry."""
    key_id: str
    fingerprint: str
    trust_level: str  # ultimate, full, marginal, none
    verified_by: Optional[str] = None
    verified_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class TrustChain:
    """Manages trust relationships between keys."""

    def __init__(self, trust_file: Optional[Path] = None):
        """Initialize trust chain."""
        if trust_file:
            self.trust_file = trust_file
        else:
            self.trust_file = Path.home() / '.lament' / 'trust.json'

        self.trust_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_trust()

    def _load_trust(self) -> None:
        """Load trust data."""
        if self.trust_file.exists():
            with open(self.trust_file, 'r') as f:
                data = json.load(f)
                self.trusted_keys = {k: TrustEntry(**v) for k, v in data.items()}
        else:
            self.trusted_keys = {}

    def _save_trust(self) -> None:
        """Save trust data."""
        with open(self.trust_file, 'w') as f:
            data = {k: v.to_dict() for k, v in self.trusted_keys.items()}
            json.dump(data, f, indent=2)

    def trust_key(self, key_id: str, fingerprint: str,
                 trust_level: str = 'full', verified_by: Optional[str] = None) -> None:
        """Add a key to trust chain."""
        entry = TrustEntry(
            key_id=key_id,
            fingerprint=fingerprint,
            trust_level=trust_level,
            verified_by=verified_by,
            verified_at=datetime.now().isoformat()
        )

        self.trusted_keys[key_id] = entry
        self._save_trust()

        print(f"Trusted key {key_id} with {trust_level} trust")

    def is_trusted(self, key_id: str) -> bool:
        """Check if a key is trusted."""
        return key_id in self.trusted_keys

    def get_trust_level(self, key_id: str) -> Optional[str]:
        """Get trust level for a key."""
        if key_id in self.trusted_keys:
            return self.trusted_keys[key_id].trust_level
        return None

    def revoke_trust(self, key_id: str) -> None:
        """Revoke trust for a key."""
        if key_id in self.trusted_keys:
            del self.trusted_keys[key_id]
            self._save_trust()
            print(f"Revoked trust for key {key_id}")


# ============================================================================
# TIMESTAMPING
# ============================================================================

class TimestampService:
    """RFC 3161 timestamp service client."""

    def __init__(self, tsa_url: str = "http://timestamp.digicert.com"):
        """Initialize timestamp service."""
        self.tsa_url = tsa_url

    def timestamp(self, data: bytes) -> bytes:
        """Get timestamp for data."""
        # Calculate hash
        digest = hashlib.sha256(data).hexdigest()

        # For now, just create a simple timestamp structure
        # In production, this would use RFC 3161
        timestamp_data = {
            'digest': digest,
            'timestamp': datetime.now().isoformat(),
            'tsa': self.tsa_url
        }

        return json.dumps(timestamp_data).encode()

    def verify_timestamp(self, timestamp: bytes) -> bool:
        """Verify a timestamp."""
        try:
            data = json.loads(timestamp.decode())
            # Basic validation
            return 'digest' in data and 'timestamp' in data
        except:
            return False


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Package Signing - Cryptographic Security for the Soul"
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Keygen command
    keygen_parser = subparsers.add_parser('keygen', help='Generate new key pair')
    keygen_parser.add_argument('--name', required=True, help='Key owner name')
    keygen_parser.add_argument('--email', required=True, help='Key owner email')
    keygen_parser.add_argument('--algorithm', default='ed25519', help='Algorithm (ed25519)')

    # Import key command
    import_parser = subparsers.add_parser('import-key', help='Import a key')
    import_parser.add_argument('file', type=Path, help='Key file to import')
    import_parser.add_argument('--type', choices=['public', 'private'], default='public')

    # Export key command
    export_parser = subparsers.add_parser('export-key', help='Export a key')
    export_parser.add_argument('key_id', help='Key ID to export')
    export_parser.add_argument('--private', action='store_true', help='Export private key')
    export_parser.add_argument('--output', type=Path, help='Output file')

    # List keys command
    subparsers.add_parser('list-keys', help='List all keys')

    # Sign command
    sign_parser = subparsers.add_parser('sign', help='Sign a package')
    sign_parser.add_argument('package', type=Path, help='Package file to sign')
    sign_parser.add_argument('--key', required=True, help='Key ID to use')
    sign_parser.add_argument('--algorithm', default='ed25519', help='Algorithm')

    # Verify command
    verify_parser = subparsers.add_parser('verify', help='Verify a package signature')
    verify_parser.add_argument('package', type=Path, help='Package file to verify')
    verify_parser.add_argument('--signature', type=Path, help='Signature file')

    # Trust command
    trust_parser = subparsers.add_parser('trust', help='Trust a key')
    trust_parser.add_argument('key_id', help='Key ID to trust')
    trust_parser.add_argument('--level', default='full', choices=['ultimate', 'full', 'marginal'])

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'keygen':
            keystore = KeyStore()
            keystore.generate_key(
                name=args.name,
                email=args.email,
                algorithm=args.algorithm
            )

        elif args.command == 'import-key':
            keystore = KeyStore()
            with open(args.file, 'rb') as f:
                key_data = f.read()
            keystore.import_key(key_data, key_type=args.type)

        elif args.command == 'export-key':
            keystore = KeyStore()
            key_data = keystore.export_key(args.key_id, include_private=args.private)

            if args.output:
                with open(args.output, 'wb') as f:
                    f.write(key_data)
                print(f"Key exported to {args.output}")
            else:
                print(key_data.decode())

        elif args.command == 'list-keys':
            keystore = KeyStore()
            keys = keystore.list_keys()

            if not keys:
                print("No keys found")
            else:
                print("Available keys:")
                for key in keys:
                    print(f"  {key.key_id} - {key.algorithm}")
                    print(f"    Name: {key.name or 'N/A'}")
                    print(f"    Email: {key.email or 'N/A'}")
                    print(f"    Fingerprint: {key.fingerprint}")
                    print(f"    Created: {key.created_at}")
                    print()

        elif args.command == 'sign':
            signer = PackageSigner()
            signer.sign_package(
                package_path=args.package,
                key_id=args.key,
                algorithm=args.algorithm
            )

        elif args.command == 'verify':
            signer = PackageSigner()
            result = signer.verify_package(
                package_path=args.package,
                signature_path=args.signature
            )

            sys.exit(0 if result else 1)

        elif args.command == 'trust':
            keystore = KeyStore()
            key_info = keystore.get_key(args.key_id)

            if not key_info:
                print(f"Key not found: {args.key_id}")
                sys.exit(1)

            trust = TrustChain()
            trust.trust_key(
                key_id=args.key_id,
                fingerprint=key_info.fingerprint,
                trust_level=args.level
            )

    except CryptoError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
