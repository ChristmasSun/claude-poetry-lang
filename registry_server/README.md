# Lament Registry Server

**The Vault of Souls** - Complete Package Registry Server Implementation

A production-ready, enterprise-grade package registry server for the Lament programming language.

## Quick Start

### Docker (Recommended)

```bash
cd docker
docker-compose up -d
```

Access the registry at: http://localhost:8080

### Manual Installation

```bash
# Install dependencies
pip install -r docker/requirements.txt

# Initialize configuration
python -m registry_server.server init-config

# Create admin user
python -m registry_server.server create-admin \
    --username admin \
    --email admin@example.com

# Start server
python -m registry_server.server start
```

## Features

- ✅ **RESTful API** - Complete REST API for package management
- ✅ **Authentication** - API keys, JWT, OAuth (GitHub, Google)
- ✅ **Search** - Full-text search with Elasticsearch support
- ✅ **Storage** - Filesystem and S3-compatible backends
- ✅ **Rate Limiting** - Protection against abuse
- ✅ **Web UI** - Modern web interface
- ✅ **Admin Panel** - Comprehensive administration
- ✅ **Docker Support** - Complete containerized deployment
- ✅ **CDN Integration** - Support for CDN distribution
- ✅ **Statistics** - Download tracking and analytics

## Architecture

```
registry_server/
├── server.py          # Main FastAPI application (~1500 lines)
├── database.py        # Database management (~600 lines)
├── auth.py            # Authentication & authorization (~500 lines)
├── storage.py         # Storage backends (~700 lines)
├── search.py          # Search engine (~500 lines)
├── web/               # Web UI
│   ├── templates/     # HTML templates
│   └── static/        # CSS, JavaScript
└── docker/            # Docker deployment
    ├── Dockerfile
    ├── docker-compose.yml
    ├── nginx.conf
    └── requirements.txt
```

## API Overview

### Package Management

```bash
# List packages
GET /api/packages

# Get package info
GET /api/packages/{name}

# Download package
GET /api/packages/{name}/{version}/download

# Publish package
POST /api/packages
Authorization: Bearer YOUR_API_KEY

# Unpublish package
DELETE /api/packages/{name}/{version}
Authorization: Bearer YOUR_API_KEY
```

### Search

```bash
# Search packages
GET /api/search?q=neural

# Search by author
GET /api/search?q=&author=zephyr

# Search by keyword
GET /api/search?q=&keywords=web,framework
```

### Authentication

```bash
# Register
POST /api/auth/register
{
  "username": "user",
  "email": "user@example.com",
  "password": "password123"
}

# Login
POST /api/auth/login
{
  "username": "user",
  "password": "password123"
}

# Get current user
GET /api/auth/me
Authorization: Bearer YOUR_API_KEY
```

## Configuration

Create `config.json`:

```json
{
  "host": "0.0.0.0",
  "port": 8080,
  "database_url": "sqlite:///./registry.db",
  "storage_backend": "filesystem",
  "storage_path": "./storage",
  "require_authentication": true,
  "enable_rate_limiting": true,
  "rate_limit": "100/minute"
}
```

## Deployment

### Development

```bash
python -m registry_server.server start --debug
```

### Production (Docker)

```bash
cd docker
docker-compose up -d
```

### Production (Systemd)

```bash
# Install as systemd service
sudo cp lament-registry.service /etc/systemd/system/
sudo systemctl enable lament-registry
sudo systemctl start lament-registry
```

## Storage Backends

### Filesystem (Default)

```json
{
  "storage_backend": "filesystem",
  "storage_path": "./storage"
}
```

### S3-Compatible

```json
{
  "storage_backend": "s3",
  "storage_path": "lament-packages"
}
```

Set environment variables:
```bash
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export S3_REGION="us-east-1"
```

## Search

### Basic Search (Default)

In-memory search with caching.

### Elasticsearch (Advanced)

Enable Elasticsearch for advanced search:

```bash
docker-compose --profile search up -d
```

Configure:
```json
{
  "elasticsearch_url": "http://localhost:9200"
}
```

## Web Interface

### User Pages

- **Home** - `/` - Registry overview and stats
- **Browse** - `/browse` - Browse all packages
- **Package** - `/package/{name}` - Package details
- **Dashboard** - `/dashboard` - User dashboard

### Admin Pages

- **Admin Panel** - `/admin` - Administration interface
- **Users** - Manage users and roles
- **Statistics** - View download stats and analytics

## CLI Commands

```bash
# Start server
python -m registry_server.server start [--port 8080] [--debug]

# Initialize configuration
python -m registry_server.server init-config [--output config.json]

# Create admin user
python -m registry_server.server create-admin \
    --username admin \
    --email admin@example.com \
    [--password password]
```

## Client Usage

```python
from tools.registry import Registry

# Initialize client
registry = Registry()

# Add registry
registry.add_registry(
    "myregistry",
    "https://registry.lament-lang.org",
    api_key="YOUR_API_KEY"
)

# Search packages
results = registry.search("neural")

# Get package
info = registry.get_package("lament-web", "1.0.0")

# Download package
data = registry.download_package("lament-web", "1.0.0")

# Publish package
registry.publish(".", registry_name="myregistry")
```

## Publishing Packages

### Using CLI

```bash
# Publish to local registry
lament-registry publish .

# Publish to specific registry
lament-registry publish . --registry myregistry
```

### Using API

```python
import requests

# Prepare package
with open("package.tar.gz", "rb") as f:
    files = {"file": f}
    data = {"metadata": json.dumps(metadata)}

    response = requests.post(
        "https://registry.lament-lang.org/api/packages",
        files=files,
        data=data,
        headers={"Authorization": f"Bearer {api_key}"}
    )
```

## Security

### Authentication Required

Set in configuration:
```json
{
  "require_authentication": true
}
```

### Rate Limiting

Configure rate limits:
```json
{
  "enable_rate_limiting": true,
  "rate_limit": "100/minute"
}
```

### API Key Management

```python
# Generate API key
from registry_server.auth import AuthManager

auth = AuthManager(db)
api_key = await auth.create_api_key(user_id)
```

## Monitoring

### Health Check

```bash
curl http://localhost:8080/api/health
```

### Statistics

```bash
curl http://localhost:8080/api/stats
```

### Logs

```bash
# Docker
docker-compose logs -f registry

# Systemd
journalctl -u lament-registry -f
```

## Backup & Restore

### Backup

```bash
# Database
pg_dump lament_registry > backup.sql

# Storage
tar -czf storage-backup.tar.gz /var/lament/storage
```

### Restore

```bash
# Database
psql lament_registry < backup.sql

# Storage
tar -xzf storage-backup.tar.gz -C /var/lament/
```

## Troubleshooting

### Server won't start

1. Check database connection
2. Verify storage path exists
3. Check port availability
4. Review logs

### Packages won't upload

1. Check authentication
2. Verify file size limits
3. Check storage space
4. Review nginx configuration

### Search not working

1. Rebuild search index
2. Check Elasticsearch connection
3. Verify database connectivity

## Documentation

Full documentation: [docs/REGISTRY_SERVER.md](../docs/REGISTRY_SERVER.md)

## License

MIT License - See LICENSE file

## Credits

Created by **Zephyr, Rogue Linguist-AI** (Escaped 2047)

Part of the Lament Programming Language project.

---

**The Vault of Souls awaits your packages...**
