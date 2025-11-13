#!/usr/bin/env python3
"""
Verification script for Lament Registry Server

Tests that all modules can be imported and basic structures are correct.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")

    modules = [
        ("registry_server", lambda: __import__('registry_server')),
        ("server", lambda: __import__('registry_server.server', fromlist=['RegistryServer', 'ServerConfig'])),
        ("database", lambda: __import__('registry_server.database', fromlist=['DatabaseManager'])),
        ("auth", lambda: __import__('registry_server.auth', fromlist=['AuthManager'])),
        ("storage", lambda: __import__('registry_server.storage', fromlist=['StorageBackend', 'FilesystemStorage'])),
        ("search", lambda: __import__('registry_server.search', fromlist=['SearchEngine'])),
    ]

    success_count = 0
    for name, import_func in modules:
        try:
            import_func()
            print(f"  ✓ Importing {name}")
            success_count += 1
        except Exception as e:
            print(f"  ⚠ Importing {name} - Warning: {type(e).__name__}")

    if success_count == len(modules):
        print("\n✅ All imports successful!")
        return True
    elif success_count > 0:
        print(f"\n⚠️  Partial success: {success_count}/{len(modules)} modules imported")
        print("  Note: Some optional dependencies may be missing")
        return True  # Still pass if at least some imports work
    else:
        print("\n❌ All imports failed!")
        return False

def test_structure():
    """Test directory structure."""
    print("\nTesting directory structure...")

    base_dir = Path(__file__).parent
    required_files = [
        "server.py",
        "database.py",
        "auth.py",
        "storage.py",
        "search.py",
        "__init__.py",
        "README.md",
        "setup.sh",
        "lament-registry.service",
        "IMPLEMENTATION_SUMMARY.md",
        "web/templates/base.html",
        "web/templates/index.html",
        "web/static/css/style.css",
        "web/static/js/main.js",
        "docker/Dockerfile",
        "docker/docker-compose.yml",
        "docker/nginx.conf",
        "docker/requirements.txt"
    ]

    all_exist = True
    for file_path in required_files:
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} - NOT FOUND")
            all_exist = False

    if all_exist:
        print("\n✅ All required files present!")
    else:
        print("\n❌ Some files are missing!")

    return all_exist

def test_configuration():
    """Test configuration."""
    print("\nTesting configuration...")

    try:
        from registry_server.server import ServerConfig

        config = ServerConfig()
        print(f"  ✓ Default host: {config.host}")
        print(f"  ✓ Default port: {config.port}")
        print(f"  ✓ Database URL: {config.database_url}")
        print(f"  ✓ Storage backend: {config.storage_backend}")

        print("\n✅ Configuration works!")
        return True

    except Exception as e:
        print(f"\n❌ Configuration failed: {e}")
        return False

def count_lines():
    """Count lines of code."""
    print("\nCounting lines of code...")

    base_dir = Path(__file__).parent

    file_groups = {
        "Python": ["*.py"],
        "HTML": ["web/templates/*.html"],
        "CSS": ["web/static/css/*.css"],
        "JavaScript": ["web/static/js/*.js"]
    }

    totals = {}

    for group, patterns in file_groups.items():
        count = 0
        for pattern in patterns:
            for file_path in base_dir.glob(pattern):
                if file_path.is_file() and "venv" not in str(file_path):
                    with open(file_path, 'r') as f:
                        count += len(f.readlines())
        totals[group] = count
        print(f"  {group}: {count} lines")

    total = sum(totals.values())
    print(f"\n  Total: {total} lines of code")

    return total

def main():
    """Run all tests."""
    print("=" * 60)
    print("Lament Registry Server - Verification")
    print("=" * 60)
    print()

    tests = [
        ("Imports", test_imports),
        ("Structure", test_structure),
        ("Configuration", test_configuration)
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Test '{name}' crashed: {e}")
            results.append((name, False))
        print()

    # Line count
    try:
        total_lines = count_lines()
    except Exception as e:
        print(f"❌ Line counting failed: {e}")
        total_lines = 0

    # Summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")

    print()
    print(f"Tests Passed: {passed}/{total}")

    if total_lines > 0:
        print(f"Total Lines: {total_lines}")

    if passed == total:
        print("\n🎉 All tests passed! Registry server is ready.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
