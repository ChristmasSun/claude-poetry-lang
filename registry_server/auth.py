#!/usr/bin/env python3
"""
Authentication Manager for Lament Registry Server

Handles:
- User registration and login
- API key generation and validation
- Token-based authentication
- OAuth integration (GitHub, Google)
- Permission management
- Role-based access control (RBAC)

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Try to import optional dependencies
try:
    from fastapi import HTTPException, status, Depends
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False


# ============================================================================
# AUTHENTICATION MANAGER
# ============================================================================

class AuthManager:
    """Manages authentication and authorization."""

    def __init__(self, database_manager, jwt_secret: Optional[str] = None):
        """
        Initialize authentication manager.

        Args:
            database_manager: Database manager instance
            jwt_secret: Secret key for JWT tokens
        """
        self.db = database_manager
        self.jwt_secret = jwt_secret or secrets.token_urlsafe(32)
        self.jwt_algorithm = "HS256"
        self.token_expiry = 3600  # 1 hour

        if FASTAPI_AVAILABLE:
            self.security = HTTPBearer()
        else:
            self.security = None

    # ========================================================================
    # PASSWORD HASHING
    # ========================================================================

    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt or fallback to SHA256."""
        if BCRYPT_AVAILABLE:
            # Use bcrypt for secure password hashing
            salt = bcrypt.gensalt()
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        else:
            # Fallback to SHA256 with salt (less secure)
            salt = secrets.token_hex(16)
            hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
            return f"sha256${salt}${hashed}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        if BCRYPT_AVAILABLE and not password_hash.startswith('sha256$'):
            # Use bcrypt verification
            try:
                return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            except Exception:
                return False
        else:
            # Fallback SHA256 verification
            try:
                _, salt, stored_hash = password_hash.split('$')
                computed_hash = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
                return hmac.compare_digest(computed_hash, stored_hash)
            except Exception:
                return False

    # ========================================================================
    # API KEY MANAGEMENT
    # ========================================================================

    def generate_api_key(self) -> str:
        """Generate a new API key."""
        return secrets.token_urlsafe(32)

    def hash_api_key(self, api_key: str) -> str:
        """Hash an API key for storage."""
        return hashlib.sha256(api_key.encode('utf-8')).hexdigest()

    async def create_api_key(
        self,
        user_id: int,
        name: Optional[str] = None
    ) -> str:
        """
        Create a new API key for a user.

        Args:
            user_id: User ID
            name: Optional name for the API key

        Returns:
            The generated API key (plain text, should be saved by user)
        """
        api_key = self.generate_api_key()
        key_hash = self.hash_api_key(api_key)

        await self.db.create_api_key(user_id, key_hash, name)

        return api_key

    async def validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """
        Validate an API key and return associated user.

        Args:
            api_key: API key to validate

        Returns:
            User dict if valid, None otherwise
        """
        key_hash = self.hash_api_key(api_key)
        key_record = await self.db.get_api_key(key_hash)

        if not key_record:
            return None

        # Update last used timestamp
        await self.db.update_api_key_last_used(key_record['id'])

        # Get user
        user = await self.db.get_user_by_id(key_record['user_id'])
        return user

    async def revoke_api_key(self, api_key: str) -> bool:
        """
        Revoke an API key.

        Args:
            api_key: API key to revoke

        Returns:
            True if revoked, False if not found
        """
        key_hash = self.hash_api_key(api_key)
        key_record = await self.db.get_api_key(key_hash)

        if not key_record:
            return False

        await self.db.revoke_api_key(key_hash)
        return True

    # ========================================================================
    # JWT TOKEN MANAGEMENT
    # ========================================================================

    def create_jwt_token(self, user_id: int, username: str) -> str:
        """
        Create a JWT token for a user.

        Args:
            user_id: User ID
            username: Username

        Returns:
            JWT token string
        """
        if not JWT_AVAILABLE:
            raise RuntimeError("PyJWT is required for JWT token support")

        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(seconds=self.token_expiry),
            'iat': datetime.utcnow()
        }

        token = jwt.encode(payload, self.jwt_secret, algorithm=self.jwt_algorithm)
        return token

    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Verify a JWT token and return payload.

        Args:
            token: JWT token to verify

        Returns:
            Token payload if valid, None otherwise
        """
        if not JWT_AVAILABLE:
            return None

        try:
            payload = jwt.decode(token, self.jwt_secret, algorithms=[self.jwt_algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None

    # ========================================================================
    # USER REGISTRATION AND LOGIN
    # ========================================================================

    async def register_user(
        self,
        username: str,
        email: str,
        password: str
    ) -> Dict[str, Any]:
        """
        Register a new user.

        Args:
            username: Username
            email: Email address
            password: Password

        Returns:
            User dict

        Raises:
            ValueError: If username or email already exists
        """
        # Validate input
        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        if '@' not in email:
            raise ValueError("Invalid email address")

        # Check if username exists
        existing_user = await self.db.get_user_by_username(username)
        if existing_user:
            raise ValueError("Username already exists")

        # Check if email exists
        existing_email = await self.db.get_user_by_email(email)
        if existing_email:
            raise ValueError("Email already exists")

        # Hash password
        password_hash = self.hash_password(password)

        # Create user
        user = await self.db.create_user(username, email, password_hash)

        return user

    async def authenticate_user(
        self,
        username: str,
        password: str
    ) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with username and password.

        Args:
            username: Username
            password: Password

        Returns:
            User dict if authenticated, None otherwise
        """
        user = await self.db.get_user_by_username(username)
        if not user:
            return None

        if not self.verify_password(password, user['password_hash']):
            return None

        return user

    # ========================================================================
    # OAUTH INTEGRATION
    # ========================================================================

    async def authenticate_github(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with GitHub OAuth.

        Args:
            code: OAuth authorization code

        Returns:
            User dict if authenticated, None otherwise
        """
        # TODO: Implement GitHub OAuth
        # This would involve:
        # 1. Exchange code for access token
        # 2. Get user info from GitHub API
        # 3. Create or get user in database
        # 4. Return user
        raise NotImplementedError("GitHub OAuth not yet implemented")

    async def authenticate_google(self, code: str) -> Optional[Dict[str, Any]]:
        """
        Authenticate a user with Google OAuth.

        Args:
            code: OAuth authorization code

        Returns:
            User dict if authenticated, None otherwise
        """
        # TODO: Implement Google OAuth
        raise NotImplementedError("Google OAuth not yet implemented")

    # ========================================================================
    # FASTAPI DEPENDENCIES
    # ========================================================================

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()) if FASTAPI_AVAILABLE else None
    ) -> Dict[str, Any]:
        """
        FastAPI dependency to get current authenticated user.

        Args:
            credentials: HTTP authorization credentials

        Returns:
            User dict

        Raises:
            HTTPException: If authentication fails
        """
        if not FASTAPI_AVAILABLE:
            raise RuntimeError("FastAPI is required for this feature")

        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing authentication credentials"
            )

        # Try API key authentication first
        user = await self.validate_api_key(credentials.credentials)

        if not user:
            # Try JWT token authentication
            if JWT_AVAILABLE:
                payload = self.verify_jwt_token(credentials.credentials)
                if payload:
                    user = await self.db.get_user_by_id(payload['user_id'])

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        return user

    async def require_admin(
        self,
        user: Dict[str, Any] = Depends(get_current_user) if FASTAPI_AVAILABLE else None
    ) -> Dict[str, Any]:
        """
        FastAPI dependency to require admin user.

        Args:
            user: Current user

        Returns:
            User dict

        Raises:
            HTTPException: If user is not admin
        """
        if not FASTAPI_AVAILABLE:
            raise RuntimeError("FastAPI is required for this feature")

        if not user.get('is_admin', False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )

        return user

    # ========================================================================
    # PERMISSION MANAGEMENT
    # ========================================================================

    async def check_package_permission(
        self,
        user: Dict[str, Any],
        package_name: str,
        action: str = "read"
    ) -> bool:
        """
        Check if user has permission to perform action on package.

        Args:
            user: User dict
            package_name: Package name
            action: Action to perform (read, write, delete)

        Returns:
            True if permitted, False otherwise
        """
        # Admins can do anything
        if user.get('is_admin', False):
            return True

        # Read is allowed for everyone
        if action == "read":
            return True

        # For write/delete, user must own the package
        packages = await self.db.get_user_packages(user['id'])
        package_names = [p['name'] for p in packages]

        return package_name in package_names

    # ========================================================================
    # RATE LIMITING
    # ========================================================================

    def get_rate_limit_key(self, user: Optional[Dict[str, Any]], ip: str) -> str:
        """
        Get rate limit key for user or IP.

        Args:
            user: User dict or None
            ip: IP address

        Returns:
            Rate limit key
        """
        if user:
            return f"user:{user['id']}"
        return f"ip:{ip}"


# ============================================================================
# OAUTH PROVIDERS
# ============================================================================

@dataclass
class OAuthProvider:
    """OAuth provider configuration."""
    name: str
    client_id: str
    client_secret: str
    authorize_url: str
    token_url: str
    user_info_url: str
    scopes: List[str]


class OAuthManager:
    """Manages OAuth authentication flows."""

    def __init__(self):
        """Initialize OAuth manager."""
        self.providers: Dict[str, OAuthProvider] = {}

    def register_provider(self, provider: OAuthProvider):
        """Register an OAuth provider."""
        self.providers[provider.name] = provider

    def get_authorization_url(self, provider_name: str, redirect_uri: str, state: str) -> str:
        """
        Get OAuth authorization URL.

        Args:
            provider_name: Provider name (github, google, etc.)
            redirect_uri: Redirect URI after authorization
            state: State parameter for CSRF protection

        Returns:
            Authorization URL
        """
        provider = self.providers.get(provider_name)
        if not provider:
            raise ValueError(f"Unknown provider: {provider_name}")

        params = {
            'client_id': provider.client_id,
            'redirect_uri': redirect_uri,
            'state': state,
            'scope': ' '.join(provider.scopes)
        }

        param_str = '&'.join(f"{k}={v}" for k, v in params.items())
        return f"{provider.authorize_url}?{param_str}"

    async def exchange_code_for_token(
        self,
        provider_name: str,
        code: str,
        redirect_uri: str
    ) -> Optional[str]:
        """
        Exchange authorization code for access token.

        Args:
            provider_name: Provider name
            code: Authorization code
            redirect_uri: Redirect URI

        Returns:
            Access token if successful, None otherwise
        """
        # TODO: Implement token exchange
        raise NotImplementedError("OAuth token exchange not yet implemented")

    async def get_user_info(
        self,
        provider_name: str,
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get user information from OAuth provider.

        Args:
            provider_name: Provider name
            access_token: Access token

        Returns:
            User info dict if successful, None otherwise
        """
        # TODO: Implement user info retrieval
        raise NotImplementedError("OAuth user info not yet implemented")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def generate_state_token() -> str:
    """Generate a state token for OAuth CSRF protection."""
    return secrets.token_urlsafe(32)


def validate_email(email: str) -> bool:
    """Validate email address format."""
    if '@' not in email:
        return False

    local, domain = email.rsplit('@', 1)

    if not local or not domain:
        return False

    if '.' not in domain:
        return False

    return True


def validate_username(username: str) -> bool:
    """Validate username format."""
    if len(username) < 3 or len(username) > 50:
        return False

    # Allow alphanumeric, underscore, and hyphen
    allowed = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-')
    return all(c in allowed for c in username)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"

    if len(password) > 128:
        return False, "Password must be at most 128 characters"

    has_upper = any(c.isupper() for c in password)
    has_lower = any(c.islower() for c in password)
    has_digit = any(c.isdigit() for c in password)

    if not (has_upper and has_lower and has_digit):
        return False, "Password must contain uppercase, lowercase, and digit"

    return True, ""
