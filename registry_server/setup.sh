#!/bin/bash
# Setup script for Lament Registry Server

set -e

echo "=================================================="
echo "  Lament Registry Server - Setup Script"
echo "  The Vault of Souls"
echo "=================================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${YELLOW}→${NC} $1"
}

# Check Python version
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    print_error "Python $REQUIRED_VERSION or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

print_success "Python $PYTHON_VERSION found"

# Check if we're in the right directory
if [ ! -f "server.py" ]; then
    print_error "Please run this script from the registry_server directory"
    exit 1
fi

# Create virtual environment
print_info "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_info "Virtual environment already exists"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
print_info "Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r docker/requirements.txt > /dev/null 2>&1
print_success "Dependencies installed"

# Create directories
print_info "Creating directories..."
mkdir -p storage data logs
print_success "Directories created"

# Initialize configuration
print_info "Initializing configuration..."
if [ ! -f "config.json" ]; then
    python -m registry_server.server init-config --output config.json
    print_success "Configuration file created: config.json"
else
    print_info "Configuration file already exists"
fi

# Create database
print_info "Setting up database..."
# Database will be created automatically on first run
print_success "Database setup complete"

# Check if admin user exists
print_info "Checking for admin user..."
read -p "Do you want to create an admin user? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Admin username: " ADMIN_USERNAME
    read -p "Admin email: " ADMIN_EMAIL
    read -sp "Admin password: " ADMIN_PASSWORD
    echo

    python -m registry_server.server create-admin \
        --username "$ADMIN_USERNAME" \
        --email "$ADMIN_EMAIL" \
        --password "$ADMIN_PASSWORD"

    print_success "Admin user created"
fi

echo ""
echo "=================================================="
echo "  Setup Complete!"
echo "=================================================="
echo ""
echo "To start the server:"
echo "  1. Activate the virtual environment:"
echo "     source venv/bin/activate"
echo ""
echo "  2. Start the server:"
echo "     python -m registry_server.server start"
echo ""
echo "  Or use Docker:"
echo "     cd docker"
echo "     docker-compose up -d"
echo ""
echo "Access the registry at:"
echo "  http://localhost:8080"
echo ""
echo "API documentation:"
echo "  http://localhost:8080/api/docs"
echo ""
echo "=================================================="
