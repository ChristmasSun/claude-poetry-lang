#!/usr/bin/env python3
"""
Database Manager for Lament Registry Server

Handles all database operations including:
- Package metadata storage
- User management
- API key management
- Download statistics
- Search indexing
- Version history
- Schema migrations

Supports SQLite and PostgreSQL backends.
"""

import asyncio
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Try to import async database libraries
try:
    import aiosqlite
    AIOSQLITE_AVAILABLE = True
except ImportError:
    AIOSQLITE_AVAILABLE = False

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False


# ============================================================================
# DATABASE MANAGER
# ============================================================================

class DatabaseManager:
    """Manages all database operations for the registry."""

    def __init__(self, database_url: str):
        """
        Initialize database manager.

        Args:
            database_url: Database connection string
                - SQLite: sqlite:///path/to/db.db
                - PostgreSQL: postgresql://user:pass@host/dbname
        """
        self.database_url = database_url
        self.db_type = self._parse_database_type(database_url)
        self.connection = None
        self.pool = None

    def _parse_database_type(self, url: str) -> str:
        """Parse database type from URL."""
        if url.startswith('sqlite'):
            return 'sqlite'
        elif url.startswith('postgresql'):
            return 'postgresql'
        else:
            raise ValueError(f"Unsupported database type: {url}")

    async def initialize(self):
        """Initialize database connection and create tables."""
        if self.db_type == 'sqlite':
            if not AIOSQLITE_AVAILABLE:
                raise RuntimeError("aiosqlite is required for SQLite support")

            # Extract path from URL
            db_path = self.database_url.replace('sqlite:///', '')
            self.connection = await aiosqlite.connect(db_path)
            self.connection.row_factory = aiosqlite.Row

        elif self.db_type == 'postgresql':
            if not ASYNCPG_AVAILABLE:
                raise RuntimeError("asyncpg is required for PostgreSQL support")

            # Create connection pool
            self.pool = await asyncpg.create_pool(
                self.database_url.replace('postgresql://', ''),
                min_size=2,
                max_size=10
            )

        # Create tables
        await self._create_tables()

    async def close(self):
        """Close database connections."""
        if self.db_type == 'sqlite' and self.connection:
            await self.connection.close()
        elif self.db_type == 'postgresql' and self.pool:
            await self.pool.close()

    async def _create_tables(self):
        """Create database tables."""
        # Users table
        await self._execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """ if self.db_type == 'sqlite' else """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # API keys table
        await self._execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                revoked BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """ if self.db_type == 'sqlite' else """
            CREATE TABLE IF NOT EXISTS api_keys (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                key_hash TEXT UNIQUE NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                revoked BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Packages table
        await self._execute("""
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                author TEXT,
                license TEXT,
                homepage TEXT,
                repository TEXT,
                keywords TEXT,
                dependencies TEXT,
                checksum TEXT NOT NULL,
                size INTEGER NOT NULL,
                downloads INTEGER DEFAULT 0,
                user_id INTEGER NOT NULL,
                published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, version),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """ if self.db_type == 'sqlite' else """
            CREATE TABLE IF NOT EXISTS packages (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                version TEXT NOT NULL,
                description TEXT,
                author TEXT,
                license TEXT,
                homepage TEXT,
                repository TEXT,
                keywords TEXT,
                dependencies TEXT,
                checksum TEXT NOT NULL,
                size INTEGER NOT NULL,
                downloads INTEGER DEFAULT 0,
                user_id INTEGER NOT NULL,
                published_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, version),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Download stats table
        await self._execute("""
            CREATE TABLE IF NOT EXISTS download_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                package_id INTEGER NOT NULL,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE
            )
        """ if self.db_type == 'sqlite' else """
            CREATE TABLE IF NOT EXISTS download_stats (
                id SERIAL PRIMARY KEY,
                package_id INTEGER NOT NULL,
                downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                user_agent TEXT,
                FOREIGN KEY (package_id) REFERENCES packages(id) ON DELETE CASCADE
            )
        """)

        # Create indexes
        await self._execute("CREATE INDEX IF NOT EXISTS idx_packages_name ON packages(name)")
        await self._execute("CREATE INDEX IF NOT EXISTS idx_packages_author ON packages(author)")
        await self._execute("CREATE INDEX IF NOT EXISTS idx_packages_downloads ON packages(downloads)")
        await self._execute("CREATE INDEX IF NOT EXISTS idx_download_stats_package ON download_stats(package_id)")

    async def _execute(self, query: str, *args) -> Any:
        """Execute a query."""
        if self.db_type == 'sqlite':
            async with self.connection.execute(query, args) as cursor:
                await self.connection.commit()
                return cursor
        else:  # postgresql
            async with self.pool.acquire() as conn:
                # Convert SQLite-style ? placeholders to PostgreSQL $1, $2, etc.
                pg_query = query
                for i in range(len(args), 0, -1):
                    pg_query = pg_query.replace('?', f'${i}', 1)
                return await conn.execute(pg_query, *args)

    async def _fetchone(self, query: str, *args) -> Optional[Dict[str, Any]]:
        """Fetch one row."""
        if self.db_type == 'sqlite':
            async with self.connection.execute(query, args) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None
        else:  # postgresql
            async with self.pool.acquire() as conn:
                # Convert placeholders
                pg_query = query
                for i in range(1, len(args) + 1):
                    pg_query = pg_query.replace('?', f'${i}', 1)
                row = await conn.fetchrow(pg_query, *args)
                return dict(row) if row else None

    async def _fetchall(self, query: str, *args) -> List[Dict[str, Any]]:
        """Fetch all rows."""
        if self.db_type == 'sqlite':
            async with self.connection.execute(query, args) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        else:  # postgresql
            async with self.pool.acquire() as conn:
                # Convert placeholders
                pg_query = query
                for i in range(1, len(args) + 1):
                    pg_query = pg_query.replace('?', f'${i}', 1)
                rows = await conn.fetch(pg_query, *args)
                return [dict(row) for row in rows]

    # ========================================================================
    # USER MANAGEMENT
    # ========================================================================

    async def create_user(
        self,
        username: str,
        email: str,
        password_hash: str,
        is_admin: bool = False
    ) -> Dict[str, Any]:
        """Create a new user."""
        await self._execute(
            "INSERT INTO users (username, email, password_hash, is_admin) VALUES (?, ?, ?, ?)",
            username, email, password_hash, is_admin
        )

        return await self._fetchone(
            "SELECT * FROM users WHERE username = ?",
            username
        )

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        return await self._fetchone(
            "SELECT * FROM users WHERE username = ?",
            username
        )

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        return await self._fetchone(
            "SELECT * FROM users WHERE email = ?",
            email
        )

    async def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        return await self._fetchone(
            "SELECT * FROM users WHERE id = ?",
            user_id
        )

    async def list_users(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """List all users."""
        return await self._fetchall(
            "SELECT id, username, email, is_admin, created_at FROM users ORDER BY created_at DESC LIMIT ? OFFSET ?",
            limit, offset
        )

    async def update_user_role(self, user_id: int, is_admin: bool) -> None:
        """Update user role."""
        await self._execute(
            "UPDATE users SET is_admin = ? WHERE id = ?",
            is_admin, user_id
        )

    async def delete_user(self, user_id: int) -> None:
        """Delete a user."""
        await self._execute("DELETE FROM users WHERE id = ?", user_id)

    # ========================================================================
    # API KEY MANAGEMENT
    # ========================================================================

    async def create_api_key(
        self,
        user_id: int,
        key_hash: str,
        name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new API key."""
        await self._execute(
            "INSERT INTO api_keys (user_id, key_hash, name) VALUES (?, ?, ?)",
            user_id, key_hash, name
        )

        return await self._fetchone(
            "SELECT * FROM api_keys WHERE key_hash = ?",
            key_hash
        )

    async def get_api_key(self, key_hash: str) -> Optional[Dict[str, Any]]:
        """Get API key by hash."""
        return await self._fetchone(
            "SELECT * FROM api_keys WHERE key_hash = ? AND revoked = 0",
            key_hash
        )

    async def get_user_api_keys(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all API keys for a user."""
        return await self._fetchall(
            "SELECT * FROM api_keys WHERE user_id = ? AND revoked = 0",
            user_id
        )

    async def update_api_key_last_used(self, key_id: int) -> None:
        """Update last used timestamp for an API key."""
        await self._execute(
            "UPDATE api_keys SET last_used = CURRENT_TIMESTAMP WHERE id = ?",
            key_id
        )

    async def revoke_api_key(self, key_hash: str) -> None:
        """Revoke an API key."""
        await self._execute(
            "UPDATE api_keys SET revoked = 1 WHERE key_hash = ?",
            key_hash
        )

    # ========================================================================
    # PACKAGE MANAGEMENT
    # ========================================================================

    async def create_package(
        self,
        name: str,
        version: str,
        description: str,
        author: str,
        license: str,
        homepage: str,
        repository: str,
        keywords: List[str],
        dependencies: List[Dict[str, str]],
        checksum: str,
        size: int,
        user_id: int
    ) -> Dict[str, Any]:
        """Create a new package."""
        await self._execute("""
            INSERT INTO packages
            (name, version, description, author, license, homepage, repository,
             keywords, dependencies, checksum, size, user_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            name, version, description, author, license, homepage, repository,
            json.dumps(keywords), json.dumps(dependencies), checksum, size, user_id
        )

        return await self._fetchone(
            "SELECT * FROM packages WHERE name = ? AND version = ?",
            name, version
        )

    async def get_package_version_info(self, name: str, version: str) -> Optional[Dict[str, Any]]:
        """Get specific package version information."""
        row = await self._fetchone(
            "SELECT * FROM packages WHERE name = ? AND version = ?",
            name, version
        )

        if row:
            row['keywords'] = json.loads(row['keywords']) if row['keywords'] else []
            row['dependencies'] = json.loads(row['dependencies']) if row['dependencies'] else []

        return row

    async def get_package_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get package information with all versions."""
        versions = await self._fetchall(
            "SELECT * FROM packages WHERE name = ? ORDER BY published_at DESC",
            name
        )

        if not versions:
            return None

        # Get latest version as primary info
        latest = versions[0]
        latest['keywords'] = json.loads(latest['keywords']) if latest['keywords'] else []
        latest['dependencies'] = json.loads(latest['dependencies']) if latest['dependencies'] else []
        latest['versions'] = [v['version'] for v in versions]

        return latest

    async def get_package_versions(self, name: str) -> List[str]:
        """Get all versions of a package."""
        rows = await self._fetchall(
            "SELECT version FROM packages WHERE name = ? ORDER BY published_at DESC",
            name
        )
        return [row['version'] for row in rows]

    async def list_packages(
        self,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List all packages (latest versions only)."""
        # Get latest version of each package
        if self.db_type == 'sqlite':
            query = """
                SELECT p.* FROM packages p
                INNER JOIN (
                    SELECT name, MAX(published_at) as latest
                    FROM packages
                    GROUP BY name
                ) latest ON p.name = latest.name AND p.published_at = latest.latest
                ORDER BY p.downloads DESC
                LIMIT ? OFFSET ?
            """
        else:  # postgresql
            query = """
                SELECT DISTINCT ON (name) *
                FROM packages
                ORDER BY name, published_at DESC
                LIMIT ? OFFSET ?
            """

        rows = await self._fetchall(query, limit, offset)

        for row in rows:
            row['keywords'] = json.loads(row['keywords']) if row['keywords'] else []
            row['dependencies'] = json.loads(row['dependencies']) if row['dependencies'] else []

        return rows

    async def delete_package_version(self, name: str, version: str) -> None:
        """Delete a specific package version."""
        await self._execute(
            "DELETE FROM packages WHERE name = ? AND version = ?",
            name, version
        )

    async def increment_downloads(self, name: str, version: str) -> None:
        """Increment download counter for a package."""
        await self._execute(
            "UPDATE packages SET downloads = downloads + 1 WHERE name = ? AND version = ?",
            name, version
        )

    async def get_user_packages(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all packages published by a user."""
        rows = await self._fetchall(
            "SELECT * FROM packages WHERE user_id = ? ORDER BY published_at DESC",
            user_id
        )

        for row in rows:
            row['keywords'] = json.loads(row['keywords']) if row['keywords'] else []
            row['dependencies'] = json.loads(row['dependencies']) if row['dependencies'] else []

        return rows

    # ========================================================================
    # DOWNLOAD STATISTICS
    # ========================================================================

    async def record_download(
        self,
        package_id: int,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> None:
        """Record a package download."""
        await self._execute(
            "INSERT INTO download_stats (package_id, ip_address, user_agent) VALUES (?, ?, ?)",
            package_id, ip_address, user_agent
        )

    async def get_download_stats(
        self,
        package_name: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """Get download statistics for a package."""
        # Total downloads
        total = await self._fetchone("""
            SELECT SUM(downloads) as total
            FROM packages
            WHERE name = ?
        """, package_name)

        # Recent downloads
        recent = await self._fetchone("""
            SELECT COUNT(*) as count
            FROM download_stats ds
            JOIN packages p ON ds.package_id = p.id
            WHERE p.name = ? AND ds.downloaded_at >= datetime('now', '-' || ? || ' days')
        """ if self.db_type == 'sqlite' else """
            SELECT COUNT(*) as count
            FROM download_stats ds
            JOIN packages p ON ds.package_id = p.id
            WHERE p.name = ? AND ds.downloaded_at >= NOW() - INTERVAL '%s days'
        """, package_name, days)

        # Downloads by version
        by_version = await self._fetchall("""
            SELECT p.version, p.downloads
            FROM packages p
            WHERE p.name = ?
            ORDER BY p.downloads DESC
        """, package_name)

        return {
            'total_downloads': total['total'] or 0,
            'recent_downloads': recent['count'] or 0,
            'by_version': by_version
        }

    # ========================================================================
    # SEARCH
    # ========================================================================

    async def search_packages(
        self,
        query: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search for packages."""
        query_pattern = f"%{query}%"

        rows = await self._fetchall("""
            SELECT * FROM packages
            WHERE name LIKE ? OR description LIKE ? OR keywords LIKE ? OR author LIKE ?
            GROUP BY name
            HAVING published_at = MAX(published_at)
            ORDER BY downloads DESC
            LIMIT ?
        """, query_pattern, query_pattern, query_pattern, query_pattern, limit)

        for row in rows:
            row['keywords'] = json.loads(row['keywords']) if row['keywords'] else []
            row['dependencies'] = json.loads(row['dependencies']) if row['dependencies'] else []

        return rows

    # ========================================================================
    # STATISTICS
    # ========================================================================

    async def get_stats(self) -> Dict[str, Any]:
        """Get overall registry statistics."""
        # Total packages (unique names)
        total_packages = await self._fetchone(
            "SELECT COUNT(DISTINCT name) as count FROM packages"
        )

        # Total versions
        total_versions = await self._fetchone(
            "SELECT COUNT(*) as count FROM packages"
        )

        # Total downloads
        total_downloads = await self._fetchone(
            "SELECT SUM(downloads) as total FROM packages"
        )

        # Total users
        total_users = await self._fetchone(
            "SELECT COUNT(*) as count FROM users"
        )

        # Storage used
        storage_used = await self._fetchone(
            "SELECT SUM(size) as total FROM packages"
        )

        # Recent packages
        recent_packages = await self._fetchall("""
            SELECT name, version, description, author, downloads, published_at
            FROM packages
            ORDER BY published_at DESC
            LIMIT 10
        """)

        return {
            'total_packages': total_packages['count'] or 0,
            'total_versions': total_versions['count'] or 0,
            'total_downloads': total_downloads['total'] or 0,
            'total_users': total_users['count'] or 0,
            'storage_used': storage_used['total'] or 0,
            'recent_packages': recent_packages
        }

    async def get_package_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """Get statistics for a specific package."""
        package = await self.get_package_info(name)
        if not package:
            return None

        download_stats = await self.get_download_stats(name)

        return {
            'name': name,
            'total_versions': len(package.get('versions', [])),
            'total_downloads': download_stats['total_downloads'],
            'recent_downloads': download_stats['recent_downloads'],
            'by_version': download_stats['by_version'],
            'latest_version': package['version'],
            'published_at': package['published_at']
        }

    # ========================================================================
    # MIGRATIONS
    # ========================================================================

    async def run_migrations(self):
        """Run database migrations."""
        # Future migrations can be added here
        pass
