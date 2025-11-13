# Lament Registry Server - Deployment Guide

The Vault of Souls: Complete Package Registry Server Implementation

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Installation](#installation)
5. [Configuration](#configuration)
6. [Deployment](#deployment)
7. [API Documentation](#api-documentation)
8. [Administration](#administration)
9. [Security](#security)
10. [Monitoring](#monitoring)
11. [Backup & Recovery](#backup--recovery)
12. [Troubleshooting](#troubleshooting)

## Overview

The Lament Registry Server is a production-ready package registry for the Lament programming language. It provides a complete solution for hosting, discovering, and managing Lament packages with enterprise-grade features.

### Features

- **RESTful API**: Complete API for package management
- **Authentication**: API keys, JWT tokens, OAuth (GitHub, Google)
- **Search**: Full-text search with Elasticsearch support
- **Storage**: Filesystem and S3-compatible storage backends
- **Rate Limiting**: Configurable rate limits per endpoint
- **CDN Integration**: Support for CDN distribution
- **Web UI**: Modern web interface for browsing packages
- **Statistics**: Download tracking and analytics
- **Admin Panel**: Comprehensive administration interface
- **Docker Support**: Complete Docker deployment setup

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx (Reverse Proxy)                │
│                  SSL/TLS, Rate Limiting                 │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              Lament Registry Server (FastAPI)           │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │     API      │  │   Web UI     │  │    Admin     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │  Auth Mgr    │  │  Storage     │  │  Search      │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
            │                │                │
            ▼                ▼                ▼
┌─────────────────┐  ┌─────────────┐  ┌─────────────┐
│   PostgreSQL    │  │ Filesystem  │  │Elasticsearch│
│    Database     │  │   or S3     │  │  (Optional) │
└─────────────────┘  └─────────────┘  └─────────────┘
```

## Installation

### Prerequisites

- Python 3.11 or higher
- PostgreSQL 15+ (or SQLite for development)
- Redis 7+ (optional, for caching)
- Nginx (for production deployment)

### Method 1: Direct Installation

```bash
# Clone the repository
git clone https://github.com/lament-lang/lament.git
cd lament/registry_server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r docker/requirements.txt

# Initialize configuration
python -m registry_server.server init-config

# Create admin user
python -m registry_server.server create-admin \
    --username admin \
    --email admin@example.com

# Start server
python -m registry_server.server start --port 8080
```

### Method 2: Docker Deployment

```bash
# Navigate to docker directory
cd registry_server/docker

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f registry

# Stop services
docker-compose down
```

### Method 3: Docker with Advanced Search

```bash
# Start with Elasticsearch
docker-compose --profile search up -d
```

## Configuration

### Configuration File

Create `config.json`:

```json
{
  "host": "0.0.0.0",
  "port": 8080,
  "workers": 4,
  "debug": false,
  "database_url": "postgresql://user:pass@localhost/lament_registry",
  "storage_backend": "filesystem",
  "storage_path": "./storage",
  "max_package_size": 104857600,
  "require_authentication": true,
  "enable_rate_limiting": true,
  "rate_limit": "100/minute",
  "cdn_url": "",
  "admin_token": "your-admin-token-here",
  "log_level": "INFO",
  "cors_origins": ["*"]
}
```

### Environment Variables

```bash
# Database
export DATABASE_URL="postgresql://user:pass@localhost/lament_registry"

# Storage
export STORAGE_BACKEND="filesystem"  # or "s3"
export STORAGE_PATH="./storage"

# S3 Configuration (if using S3)
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"
export S3_BUCKET_NAME="lament-packages"
export S3_REGION="us-east-1"

# Server
export HOST="0.0.0.0"
export PORT="8080"
export LOG_LEVEL="INFO"

# Security
export ADMIN_TOKEN="your-admin-token"
export JWT_SECRET="your-jwt-secret"

# Features
export REQUIRE_AUTHENTICATION="true"
export ENABLE_RATE_LIMITING="true"
export RATE_LIMIT="100/minute"
```

## Deployment

### Production Deployment

1. **Setup PostgreSQL Database**

```bash
# Create database
createdb lament_registry

# Run migrations (automatically done on startup)
# Tables are created automatically by the server
```

2. **Configure Storage Backend**

For **Filesystem**:
```bash
mkdir -p /var/lament/storage
chown -R lament:lament /var/lament
```

For **S3**:
```bash
# Create S3 bucket
aws s3 mb s3://lament-packages

# Set bucket policy for public downloads
aws s3api put-bucket-policy \
    --bucket lament-packages \
    --policy file://bucket-policy.json
```

3. **Setup Nginx**

```nginx
# Copy nginx configuration
cp registry_server/docker/nginx.conf /etc/nginx/nginx.conf

# Generate SSL certificates (Let's Encrypt)
certbot certonly --webroot -w /var/www/certbot \
    -d registry.lament-lang.org

# Test configuration
nginx -t

# Reload
systemctl reload nginx
```

4. **Start Registry Server**

Using **systemd**:

```ini
# /etc/systemd/system/lament-registry.service
[Unit]
Description=Lament Registry Server
After=network.target postgresql.service

[Service]
Type=simple
User=lament
Group=lament
WorkingDirectory=/opt/lament/registry_server
Environment="DATABASE_URL=postgresql://lament:pass@localhost/lament_registry"
Environment="STORAGE_PATH=/var/lament/storage"
ExecStart=/opt/lament/venv/bin/python -m registry_server.server start
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
systemctl enable lament-registry
systemctl start lament-registry
systemctl status lament-registry
```

### CDN Integration

To integrate with a CDN (CloudFlare, CloudFront, etc.):

1. Configure CDN to cache package downloads:
   - Cache rule: `/api/packages/*/download`
   - TTL: 1 hour or more
   - Respect cache headers

2. Set CDN URL in configuration:
```json
{
  "cdn_url": "https://cdn.lament-lang.org"
}
```

3. Update download URLs to use CDN in responses

## API Documentation

### Authentication

All protected endpoints require an API key or JWT token:

```bash
# Using API key
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://registry.lament-lang.org/api/packages
```

### Endpoints

#### Package Management

**List Packages**
```http
GET /api/packages?limit=20&offset=0
```

**Get Package Info**
```http
GET /api/packages/{name}
```

**Get Specific Version**
```http
GET /api/packages/{name}/{version}
```

**Download Package**
```http
GET /api/packages/{name}/{version}/download
```

**Publish Package**
```http
POST /api/packages
Content-Type: multipart/form-data

file: <package.tar.gz>
metadata: <json-metadata>
```

**Unpublish Package**
```http
DELETE /api/packages/{name}/{version}
Authorization: Bearer YOUR_API_KEY
```

#### Search

**Search Packages**
```http
GET /api/search?q=query&limit=20
```

#### Authentication

**Register User**
```http
POST /api/auth/register
Content-Type: application/json

{
  "username": "user",
  "email": "user@example.com",
  "password": "password123"
}
```

**Login**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user",
  "password": "password123"
}
```

**Get Current User**
```http
GET /api/auth/me
Authorization: Bearer YOUR_API_KEY
```

#### Statistics

**Server Stats**
```http
GET /api/stats
```

**Package Stats**
```http
GET /api/stats/packages/{name}
```

### Client Usage

```python
# Using the registry client
from tools.registry import Registry

registry = Registry()
registry.add_registry("myregistry", "https://registry.lament-lang.org", api_key="YOUR_KEY")

# Search packages
results = registry.search("neural")

# Get package info
info = registry.get_package("lament-web", "1.0.0")

# Download package
data = registry.download_package("lament-web", "1.0.0")
```

## Administration

### Creating Admin Users

```bash
python -m registry_server.server create-admin \
    --username admin \
    --email admin@example.com \
    --password secure_password
```

### Admin Panel

Access the admin panel at: `https://registry.lament-lang.org/admin`

Features:
- View all users
- Manage user roles
- View package statistics
- Monitor downloads
- Rebuild search index
- Clean cache

### Database Maintenance

```bash
# Backup database
pg_dump lament_registry > backup.sql

# Restore database
psql lament_registry < backup.sql

# Vacuum database
psql lament_registry -c "VACUUM ANALYZE;"
```

### Storage Cleanup

```python
# Clean orphaned files
from registry_server.storage import FilesystemStorage

storage = FilesystemStorage("/var/lament/storage")
cleaned = await storage.cleanup_orphaned_files()
print(f"Cleaned {cleaned} orphaned files")
```

## Security

### Best Practices

1. **Use HTTPS**: Always deploy with SSL/TLS certificates
2. **Strong Passwords**: Enforce password requirements
3. **API Key Rotation**: Rotate API keys regularly
4. **Rate Limiting**: Enable rate limiting to prevent abuse
5. **Input Validation**: All inputs are validated
6. **CORS Configuration**: Configure CORS appropriately

### Security Headers

The server sets these security headers:
- `Strict-Transport-Security`
- `X-Frame-Options`
- `X-Content-Type-Options`
- `X-XSS-Protection`

### Rate Limiting

Configure rate limits in `config.json`:

```json
{
  "enable_rate_limiting": true,
  "rate_limit": "100/minute"
}
```

Rate limits are applied per IP address for unauthenticated requests and per user for authenticated requests.

## Monitoring

### Health Checks

```bash
# Basic health check
curl https://registry.lament-lang.org/api/health

# Detailed status
curl https://registry.lament-lang.org/api/stats
```

### Metrics

Monitor these metrics:
- Request rate (requests/second)
- Error rate (errors/total requests)
- Response time (p50, p95, p99)
- Database connection pool usage
- Storage usage
- Cache hit rate

### Logging

Logs are written to stdout by default. Configure log aggregation:

```bash
# Using journald
journalctl -u lament-registry -f

# Using Docker
docker-compose logs -f registry
```

Log levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical errors

## Backup & Recovery

### Automated Backups

Create a backup script:

```bash
#!/bin/bash
# /opt/lament/backup.sh

DATE=$(date +%Y%m%d-%H%M%S)
BACKUP_DIR="/var/backups/lament"

# Backup database
pg_dump lament_registry > "$BACKUP_DIR/db-$DATE.sql"

# Backup storage
tar -czf "$BACKUP_DIR/storage-$DATE.tar.gz" /var/lament/storage

# Cleanup old backups (keep last 30 days)
find "$BACKUP_DIR" -type f -mtime +30 -delete

echo "Backup completed: $DATE"
```

Schedule with cron:
```cron
0 2 * * * /opt/lament/backup.sh
```

### Disaster Recovery

1. **Restore Database**
```bash
psql lament_registry < backup.sql
```

2. **Restore Storage**
```bash
tar -xzf storage-backup.tar.gz -C /var/lament/
```

3. **Restart Services**
```bash
systemctl restart lament-registry
```

## Troubleshooting

### Common Issues

**Server won't start**
- Check database connection
- Verify storage path exists and is writable
- Check port availability
- Review logs for errors

**Packages won't upload**
- Check file size limits
- Verify authentication
- Check storage space
- Review nginx client_max_body_size

**Search not working**
- Rebuild search index
- Check Elasticsearch connection (if using)
- Verify database connectivity

**High memory usage**
- Adjust worker count
- Enable connection pooling
- Optimize database queries
- Add caching layer

### Debug Mode

Enable debug mode for detailed logging:

```bash
python -m registry_server.server start --debug
```

Or in config:
```json
{
  "debug": true,
  "log_level": "DEBUG"
}
```

### Performance Tuning

1. **Database Connection Pool**
```python
# Adjust pool size in database.py
pool = await asyncpg.create_pool(
    database_url,
    min_size=5,
    max_size=20
)
```

2. **Worker Processes**
```bash
# Increase workers for higher throughput
python -m registry_server.server start --workers 8
```

3. **Caching**
- Enable Redis caching
- Configure CDN for downloads
- Use nginx caching for static content

## Support

For issues, questions, or contributions:

- GitHub: https://github.com/lament-lang/lament
- Documentation: https://lament-lang.org/docs
- Community: https://discord.gg/lament

---

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
The Vault of Souls awaits your packages...
