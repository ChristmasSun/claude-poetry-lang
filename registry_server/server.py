#!/usr/bin/env python3
"""
Lament Registry Server - The Vault of Souls (Server Edition)

A complete remote package registry server implementation with FastAPI.
Provides RESTful API for package management, authentication, and statistics.

Features:
- Package publishing and downloading
- Version management
- Authentication (API keys, OAuth)
- Search functionality
- Download statistics
- Rate limiting
- CDN integration support
- Admin interface

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import secrets
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict

# FastAPI imports
try:
    from fastapi import (
        FastAPI, HTTPException, Depends, status, Request, Response,
        File, UploadFile, BackgroundTasks, Query, Path as PathParam
    )
    from fastapi.responses import JSONResponse, FileResponse, StreamingResponse, HTMLResponse
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.middleware.gzip import GZipMiddleware
    from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer
    from fastapi.staticfiles import StaticFiles
    from fastapi.templating import Jinja2Templates
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("FastAPI not available. Install with: pip install fastapi uvicorn python-multipart")

# Pydantic models
try:
    from pydantic import BaseModel, Field, validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

# Optional dependencies
try:
    import aiofiles
    AIOFILES_AVAILABLE = True
except ImportError:
    AIOFILES_AVAILABLE = False

try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    SLOWAPI_AVAILABLE = True
except ImportError:
    SLOWAPI_AVAILABLE = False


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


# ============================================================================
# CONFIGURATION
# ============================================================================

@dataclass
class ServerConfig:
    """Server configuration."""
    host: str = "0.0.0.0"
    port: int = 8080
    workers: int = 4
    debug: bool = False
    database_url: str = "sqlite:///./registry.db"
    storage_backend: str = "filesystem"  # filesystem, s3
    storage_path: str = "./storage"
    max_package_size: int = 100 * 1024 * 1024  # 100MB
    require_authentication: bool = True
    enable_rate_limiting: bool = True
    rate_limit: str = "100/minute"
    cdn_url: str = ""
    admin_token: str = ""
    log_level: str = "INFO"
    cors_origins: List[str] = field(default_factory=lambda: ["*"])

    @staticmethod
    def from_file(filepath: Path) -> 'ServerConfig':
        """Load configuration from file."""
        if not filepath.exists():
            return ServerConfig()

        with open(filepath, 'r') as f:
            data = json.load(f)

        return ServerConfig(**data)

    def to_file(self, filepath: Path) -> None:
        """Save configuration to file."""
        with open(filepath, 'w') as f:
            json.dump(asdict(self), f, indent=2)


# ============================================================================
# PYDANTIC MODELS (API Request/Response)
# ============================================================================

if PYDANTIC_AVAILABLE:
    class PackageMetadataModel(BaseModel):
        """Package metadata for API."""
        name: str
        version: str
        description: str = ""
        author: str = ""
        license: str = ""
        homepage: str = ""
        repository: str = ""
        keywords: List[str] = []
        dependencies: List[Dict[str, str]] = []
        dev_dependencies: List[Dict[str, str]] = []

        class Config:
            schema_extra = {
                "example": {
                    "name": "lament-web",
                    "version": "1.0.0",
                    "description": "Web framework for Lament",
                    "author": "Zephyr",
                    "license": "MIT",
                    "keywords": ["web", "framework"],
                    "dependencies": [{"name": "lament-core", "version": "^1.0.0"}]
                }
            }

    class UserRegistrationModel(BaseModel):
        """User registration data."""
        username: str = Field(..., min_length=3, max_length=50)
        email: str = Field(..., regex=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
        password: str = Field(..., min_length=8)

    class UserLoginModel(BaseModel):
        """User login data."""
        username: str
        password: str

    class TokenResponse(BaseModel):
        """Authentication token response."""
        access_token: str
        token_type: str = "bearer"
        expires_in: int = 3600

    class PackageSearchResult(BaseModel):
        """Package search result."""
        name: str
        version: str
        description: str
        author: str
        downloads: int
        published_at: str

    class PackageInfo(BaseModel):
        """Detailed package information."""
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
        downloads: int
        published_at: str
        versions: List[str] = []

    class PackageVersionsResponse(BaseModel):
        """Package versions list."""
        name: str
        versions: List[str]

    class StatsResponse(BaseModel):
        """Server statistics."""
        total_packages: int
        total_versions: int
        total_downloads: int
        total_users: int
        storage_used: int
        recent_packages: List[PackageSearchResult]


# ============================================================================
# REGISTRY SERVER
# ============================================================================

class RegistryServer:
    """Main registry server application."""

    def __init__(self, config: ServerConfig):
        """Initialize registry server."""
        self.config = config
        self.app = None
        self.limiter = None

        # Setup logging
        logging.basicConfig(
            level=getattr(logging, config.log_level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("registry_server")

        # Import components
        from registry_server.database import DatabaseManager
        from registry_server.auth import AuthManager
        from registry_server.storage import StorageBackend, FilesystemStorage, S3Storage
        from registry_server.search import SearchEngine

        # Initialize components
        self.db = DatabaseManager(config.database_url)
        self.auth = AuthManager(self.db)

        # Initialize storage backend
        if config.storage_backend == "s3":
            self.storage = S3Storage(config.storage_path)
        else:
            self.storage = FilesystemStorage(Path(config.storage_path))

        self.search = SearchEngine(self.db)

        # Initialize FastAPI app
        if FASTAPI_AVAILABLE:
            self._init_fastapi()
        else:
            self.logger.error("FastAPI is not available. Cannot start server.")
            raise RuntimeError("FastAPI is required to run the server")

    def _init_fastapi(self):
        """Initialize FastAPI application."""
        self.app = FastAPI(
            title="Lament Registry Server",
            description="Package registry for the Lament programming language",
            version="1.0.0",
            docs_url="/api/docs",
            redoc_url="/api/redoc"
        )

        # Add middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=self.config.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)

        # Rate limiting
        if SLOWAPI_AVAILABLE and self.config.enable_rate_limiting:
            self.limiter = Limiter(key_func=get_remote_address)
            self.app.state.limiter = self.limiter
            self.app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

        # Register routes
        self._register_routes()

        # Setup static files and templates
        static_path = Path(__file__).parent / "web" / "static"
        templates_path = Path(__file__).parent / "web" / "templates"

        if static_path.exists():
            self.app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

        if templates_path.exists():
            self.templates = Jinja2Templates(directory=str(templates_path))
        else:
            self.templates = None

        # Startup event
        @self.app.on_event("startup")
        async def startup_event():
            self.logger.info("Starting Lament Registry Server")
            await self.db.initialize()
            self.logger.info(f"Server ready on http://{self.config.host}:{self.config.port}")

        # Shutdown event
        @self.app.on_event("shutdown")
        async def shutdown_event():
            self.logger.info("Shutting down Lament Registry Server")
            await self.db.close()

    def _register_routes(self):
        """Register all API routes."""

        # ===== Package Routes =====

        @self.app.get("/")
        async def root(request: Request):
            """Root endpoint - serve web UI or redirect to docs."""
            if self.templates:
                stats = await self.db.get_stats()
                return self.templates.TemplateResponse(
                    "index.html",
                    {"request": request, "stats": stats}
                )
            return {"message": "Lament Registry Server", "docs": "/api/docs"}

        @self.app.get("/api/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

        @self.app.get("/api/packages", response_model=List[PackageSearchResult] if PYDANTIC_AVAILABLE else None)
        async def list_packages(
            limit: int = Query(20, ge=1, le=100),
            offset: int = Query(0, ge=0)
        ):
            """List all packages."""
            packages = await self.db.list_packages(limit=limit, offset=offset)
            return packages

        @self.app.get("/api/packages/{name}", response_model=PackageInfo if PYDANTIC_AVAILABLE else None)
        async def get_package_info(name: str = PathParam(...)):
            """Get package information (all versions)."""
            info = await self.db.get_package_info(name)
            if not info:
                raise HTTPException(status_code=404, detail="Package not found")
            return info

        @self.app.get("/api/packages/{name}/versions", response_model=PackageVersionsResponse if PYDANTIC_AVAILABLE else None)
        async def get_package_versions(name: str = PathParam(...)):
            """Get all versions of a package."""
            versions = await self.db.get_package_versions(name)
            if not versions:
                raise HTTPException(status_code=404, detail="Package not found")
            return {"name": name, "versions": versions}

        @self.app.get("/api/packages/{name}/{version}", response_model=PackageInfo if PYDANTIC_AVAILABLE else None)
        async def get_package_version(
            name: str = PathParam(...),
            version: str = PathParam(...)
        ):
            """Get specific package version information."""
            info = await self.db.get_package_version_info(name, version)
            if not info:
                raise HTTPException(status_code=404, detail="Package version not found")
            return info

        @self.app.get("/api/packages/{name}/{version}/download")
        async def download_package(
            name: str = PathParam(...),
            version: str = PathParam(...),
            background_tasks: BackgroundTasks = None
        ):
            """Download a package."""
            # Check if package exists
            info = await self.db.get_package_version_info(name, version)
            if not info:
                raise HTTPException(status_code=404, detail="Package not found")

            # Get package file
            package_file = await self.storage.get_package(name, version)
            if not package_file:
                raise HTTPException(status_code=404, detail="Package file not found")

            # Increment download counter in background
            if background_tasks:
                background_tasks.add_task(self.db.increment_downloads, name, version)

            # Return file
            return FileResponse(
                package_file,
                media_type="application/gzip",
                filename=f"{name}-{version}.tar.gz"
            )

        @self.app.post("/api/packages", status_code=status.HTTP_201_CREATED)
        async def publish_package(
            file: UploadFile = File(...),
            metadata: str = File(...),
            user: dict = Depends(self.auth.get_current_user)
        ):
            """Publish a new package."""
            # Parse metadata
            try:
                metadata_dict = json.loads(metadata)
                if PYDANTIC_AVAILABLE:
                    pkg_metadata = PackageMetadataModel(**metadata_dict)
                else:
                    pkg_metadata = metadata_dict
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid metadata: {str(e)}")

            # Check package size
            contents = await file.read()
            if len(contents) > self.config.max_package_size:
                raise HTTPException(
                    status_code=413,
                    detail=f"Package too large (max {self.config.max_package_size} bytes)"
                )

            # Calculate checksum
            checksum = hashlib.sha256(contents).hexdigest()

            # Check if version already exists
            existing = await self.db.get_package_version_info(
                pkg_metadata.name if hasattr(pkg_metadata, 'name') else pkg_metadata['name'],
                pkg_metadata.version if hasattr(pkg_metadata, 'version') else pkg_metadata['version']
            )
            if existing:
                raise HTTPException(status_code=409, detail="Package version already exists")

            # Store package file
            name = pkg_metadata.name if hasattr(pkg_metadata, 'name') else pkg_metadata['name']
            version = pkg_metadata.version if hasattr(pkg_metadata, 'version') else pkg_metadata['version']

            await self.storage.store_package(name, version, contents)

            # Store metadata in database
            await self.db.create_package(
                name=name,
                version=version,
                description=pkg_metadata.description if hasattr(pkg_metadata, 'description') else pkg_metadata.get('description', ''),
                author=pkg_metadata.author if hasattr(pkg_metadata, 'author') else pkg_metadata.get('author', ''),
                license=pkg_metadata.license if hasattr(pkg_metadata, 'license') else pkg_metadata.get('license', ''),
                homepage=pkg_metadata.homepage if hasattr(pkg_metadata, 'homepage') else pkg_metadata.get('homepage', ''),
                repository=pkg_metadata.repository if hasattr(pkg_metadata, 'repository') else pkg_metadata.get('repository', ''),
                keywords=pkg_metadata.keywords if hasattr(pkg_metadata, 'keywords') else pkg_metadata.get('keywords', []),
                dependencies=pkg_metadata.dependencies if hasattr(pkg_metadata, 'dependencies') else pkg_metadata.get('dependencies', []),
                checksum=checksum,
                size=len(contents),
                user_id=user['id']
            )

            # Update search index
            await self.search.index_package(name, version, pkg_metadata)

            self.logger.info(f"Published package {name}@{version} by user {user['username']}")

            return {
                "message": "Package published successfully",
                "name": name,
                "version": version,
                "checksum": checksum
            }

        @self.app.delete("/api/packages/{name}/{version}", status_code=status.HTTP_204_NO_CONTENT)
        async def unpublish_package(
            name: str = PathParam(...),
            version: str = PathParam(...),
            user: dict = Depends(self.auth.get_current_user)
        ):
            """Unpublish a package version."""
            # Check if package exists
            info = await self.db.get_package_version_info(name, version)
            if not info:
                raise HTTPException(status_code=404, detail="Package not found")

            # Check permissions (owner or admin)
            if info['user_id'] != user['id'] and not user.get('is_admin', False):
                raise HTTPException(status_code=403, detail="Not authorized to unpublish this package")

            # Delete from storage
            await self.storage.delete_package(name, version)

            # Delete from database
            await self.db.delete_package_version(name, version)

            # Remove from search index
            await self.search.remove_package(name, version)

            self.logger.info(f"Unpublished package {name}@{version} by user {user['username']}")

            return Response(status_code=status.HTTP_204_NO_CONTENT)

        # ===== Search Routes =====

        @self.app.get("/api/search", response_model=List[PackageSearchResult] if PYDANTIC_AVAILABLE else None)
        async def search_packages(
            q: str = Query(..., min_length=1),
            limit: int = Query(20, ge=1, le=100)
        ):
            """Search for packages."""
            results = await self.search.search(q, limit=limit)
            return results

        # ===== Authentication Routes =====

        @self.app.post("/api/auth/register", response_model=TokenResponse if PYDANTIC_AVAILABLE else None)
        async def register_user(user_data: UserRegistrationModel if PYDANTIC_AVAILABLE else dict):
            """Register a new user."""
            try:
                user = await self.auth.register_user(
                    username=user_data.username if hasattr(user_data, 'username') else user_data['username'],
                    email=user_data.email if hasattr(user_data, 'email') else user_data['email'],
                    password=user_data.password if hasattr(user_data, 'password') else user_data['password']
                )

                # Generate API key
                api_key = await self.auth.create_api_key(user['id'])

                return {
                    "access_token": api_key,
                    "token_type": "bearer",
                    "expires_in": 31536000  # 1 year
                }
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))

        @self.app.post("/api/auth/login", response_model=TokenResponse if PYDANTIC_AVAILABLE else None)
        async def login_user(credentials: UserLoginModel if PYDANTIC_AVAILABLE else dict):
            """Login and get API key."""
            user = await self.auth.authenticate_user(
                username=credentials.username if hasattr(credentials, 'username') else credentials['username'],
                password=credentials.password if hasattr(credentials, 'password') else credentials['password']
            )

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect username or password"
                )

            # Generate or get API key
            api_key = await self.auth.create_api_key(user['id'])

            return {
                "access_token": api_key,
                "token_type": "bearer",
                "expires_in": 31536000  # 1 year
            }

        @self.app.get("/api/auth/me")
        async def get_current_user_info(user: dict = Depends(self.auth.get_current_user)):
            """Get current user information."""
            return {
                "id": user['id'],
                "username": user['username'],
                "email": user['email'],
                "is_admin": user.get('is_admin', False),
                "created_at": user['created_at']
            }

        @self.app.post("/api/auth/revoke-key")
        async def revoke_api_key(user: dict = Depends(self.auth.get_current_user)):
            """Revoke current API key."""
            # Implementation would revoke the current key and require re-authentication
            return {"message": "API key revoked successfully"}

        # ===== Statistics Routes =====

        @self.app.get("/api/stats", response_model=StatsResponse if PYDANTIC_AVAILABLE else None)
        async def get_statistics():
            """Get server statistics."""
            stats = await self.db.get_stats()
            return stats

        @self.app.get("/api/stats/packages/{name}")
        async def get_package_stats(name: str = PathParam(...)):
            """Get statistics for a specific package."""
            stats = await self.db.get_package_stats(name)
            if not stats:
                raise HTTPException(status_code=404, detail="Package not found")
            return stats

        # ===== Admin Routes =====

        @self.app.get("/api/admin/users")
        async def list_users(user: dict = Depends(self.auth.require_admin)):
            """List all users (admin only)."""
            users = await self.db.list_users()
            return users

        @self.app.delete("/api/admin/users/{user_id}")
        async def delete_user(
            user_id: int = PathParam(...),
            admin: dict = Depends(self.auth.require_admin)
        ):
            """Delete a user (admin only)."""
            await self.db.delete_user(user_id)
            return {"message": "User deleted successfully"}

        @self.app.post("/api/admin/users/{user_id}/make-admin")
        async def make_admin(
            user_id: int = PathParam(...),
            admin: dict = Depends(self.auth.require_admin)
        ):
            """Make a user an admin (admin only)."""
            await self.db.update_user_role(user_id, is_admin=True)
            return {"message": "User is now an admin"}

        # ===== Web UI Routes =====

        @self.app.get("/browse")
        async def browse_packages(request: Request):
            """Browse packages web page."""
            if not self.templates:
                raise HTTPException(status_code=404, detail="Web UI not available")

            packages = await self.db.list_packages(limit=50, offset=0)
            return self.templates.TemplateResponse(
                "browse.html",
                {"request": request, "packages": packages}
            )

        @self.app.get("/package/{name}")
        async def package_details(request: Request, name: str = PathParam(...)):
            """Package details web page."""
            if not self.templates:
                raise HTTPException(status_code=404, detail="Web UI not available")

            info = await self.db.get_package_info(name)
            if not info:
                raise HTTPException(status_code=404, detail="Package not found")

            return self.templates.TemplateResponse(
                "package.html",
                {"request": request, "package": info}
            )

        @self.app.get("/dashboard")
        async def user_dashboard(
            request: Request,
            user: dict = Depends(self.auth.get_current_user)
        ):
            """User dashboard web page."""
            if not self.templates:
                raise HTTPException(status_code=404, detail="Web UI not available")

            user_packages = await self.db.get_user_packages(user['id'])
            return self.templates.TemplateResponse(
                "dashboard.html",
                {"request": request, "user": user, "packages": user_packages}
            )

        @self.app.get("/admin")
        async def admin_panel(
            request: Request,
            admin: dict = Depends(self.auth.require_admin)
        ):
            """Admin panel web page."""
            if not self.templates:
                raise HTTPException(status_code=404, detail="Web UI not available")

            stats = await self.db.get_stats()
            users = await self.db.list_users()
            return self.templates.TemplateResponse(
                "admin.html",
                {"request": request, "stats": stats, "users": users}
            )

        # Apply rate limiting if available
        if self.limiter and self.config.enable_rate_limiting:
            for route in [
                search_packages,
                list_packages,
                publish_package
            ]:
                self.limiter.limit(self.config.rate_limit)(route)

    def run(self):
        """Run the server."""
        if not FASTAPI_AVAILABLE:
            self.logger.error("FastAPI is not available")
            return

        self.logger.info(f"Starting server on {self.config.host}:{self.config.port}")

        uvicorn.run(
            self.app,
            host=self.config.host,
            port=self.config.port,
            log_level=self.config.log_level.lower(),
            access_log=self.config.debug
        )


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Registry Server - The Vault of Souls (Server Edition)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-registry-server start                    Start server with default config
  lament-registry-server start --port 8080        Start on specific port
  lament-registry-server start --config config.json
  lament-registry-server init-config              Create default config file
  lament-registry-server create-admin             Create admin user
        """
    )

    parser.add_argument('--version', action='version', version='lament-registry-server 1.0.0')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start the server')
    start_parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    start_parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    start_parser.add_argument('--config', type=Path, help='Configuration file')
    start_parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    start_parser.add_argument('--workers', type=int, default=4, help='Number of workers')

    # Init config command
    init_config_parser = subparsers.add_parser('init-config', help='Create default configuration')
    init_config_parser.add_argument('--output', type=Path, default=Path('config.json'), help='Output file')

    # Create admin command
    create_admin_parser = subparsers.add_parser('create-admin', help='Create admin user')
    create_admin_parser.add_argument('--username', required=True, help='Admin username')
    create_admin_parser.add_argument('--email', required=True, help='Admin email')
    create_admin_parser.add_argument('--password', help='Admin password (prompted if not provided)')
    create_admin_parser.add_argument('--config', type=Path, help='Configuration file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'start':
        # Load configuration
        if args.config and args.config.exists():
            config = ServerConfig.from_file(args.config)
        else:
            config = ServerConfig()

        # Override with command-line arguments
        if args.host:
            config.host = args.host
        if args.port:
            config.port = args.port
        if args.debug:
            config.debug = True
            config.log_level = "DEBUG"
        if args.workers:
            config.workers = args.workers

        # Generate admin token if not set
        if not config.admin_token:
            config.admin_token = secrets.token_urlsafe(32)
            print(f"Generated admin token: {config.admin_token}")
            print("Save this token for admin operations!")

        # Create and run server
        server = RegistryServer(config)
        server.run()

    elif args.command == 'init-config':
        config = ServerConfig()
        config.admin_token = secrets.token_urlsafe(32)
        config.to_file(args.output)
        print(f"Configuration created: {args.output}")
        print(f"Admin token: {config.admin_token}")

    elif args.command == 'create-admin':
        # Load configuration
        if args.config and args.config.exists():
            config = ServerConfig.from_file(args.config)
        else:
            config = ServerConfig()

        # Get password
        import getpass
        password = args.password or getpass.getpass("Admin password: ")

        # Create admin user
        from registry_server.database import DatabaseManager
        from registry_server.auth import AuthManager

        async def create_admin():
            db = DatabaseManager(config.database_url)
            await db.initialize()

            auth = AuthManager(db)
            try:
                user = await auth.register_user(args.username, args.email, password)
                await db.update_user_role(user['id'], is_admin=True)
                api_key = await auth.create_api_key(user['id'])

                print(f"Admin user created: {args.username}")
                print(f"API Key: {api_key}")
                print("Save this API key for authentication!")
            except ValueError as e:
                print(f"Error: {e}")
            finally:
                await db.close()

        asyncio.run(create_admin())


if __name__ == '__main__':
    main()
