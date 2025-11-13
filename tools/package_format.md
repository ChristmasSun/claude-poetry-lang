# Lament Package Format Specification

## Overview

The Lament package format defines the structure and metadata for distributing Lament libraries and applications. Packages use JSON format with the `.lament` extension for configuration files.

## Package Metadata File: `package.lament`

Every Lament package must include a `package.lament` file in its root directory.

### Format

```json
{
  "name": "package-name",
  "version": "1.2.3",
  "description": "A brief description of what this package does",
  "author": "Author Name <author@example.com>",
  "license": "MIT",
  "homepage": "https://example.com/package",
  "repository": "https://github.com/author/package",
  "keywords": ["emotion", "temporal", "neural"],

  "entry_point": "src/main.lament",

  "dependencies": [
    {
      "name": "other-package",
      "version": "^1.0.0",
      "optional": false
    }
  ],

  "dev_dependencies": [
    {
      "name": "test-framework",
      "version": "~2.0.0",
      "optional": false
    }
  ],

  "include": [
    "src/**/*.lament",
    "lib/**/*.lament",
    "README.md",
    "LICENSE"
  ],

  "exclude": [
    "tests/**",
    "examples/**",
    "**/*.test.lament",
    ".lament/**",
    "build/**"
  ],

  "build_script": "scripts/build.sh"
}
```

## Field Descriptions

### Required Fields

- **name** (string): Package name. Must be lowercase, alphanumeric with hyphens.
  - Valid: `my-package`, `emotion-core`, `neural-net`
  - Invalid: `My_Package`, `package!`, `PACKAGE`

- **version** (string): Semantic version number (MAJOR.MINOR.PATCH)
  - Format: `X.Y.Z[-prerelease][+build]`
  - Examples: `1.0.0`, `2.1.3-alpha`, `1.0.0+20130313144700`

### Optional Fields

- **description** (string): Short description of the package

- **author** (string): Author name and email
  - Format: `Name <email@example.com>`

- **license** (string): Software license identifier
  - Common values: `MIT`, `Apache-2.0`, `GPL-3.0`, `BSD-3-Clause`

- **homepage** (string): URL to package homepage

- **repository** (string): URL to source repository

- **keywords** (array of strings): Search keywords for package discovery

- **entry_point** (string): Main file to execute (for executables)

- **dependencies** (array): Runtime dependencies
  - Each dependency is an object with:
    - `name`: Package name
    - `version`: Version constraint
    - `optional`: Boolean (default: false)

- **dev_dependencies** (array): Development dependencies
  - Same format as dependencies
  - Not installed for package consumers

- **include** (array of strings): File patterns to include in package
  - Uses glob patterns
  - Default: `["**/*.lament"]`

- **exclude** (array of strings): File patterns to exclude from package
  - Uses glob patterns
  - Default: `["tests/**", "examples/**"]`

- **build_script** (string): Path to custom build script

## Version Constraints

Version constraints specify which versions of a dependency are acceptable:

### Exact Version
```json
"version": "1.2.3"
"version": "=1.2.3"
```
Only version 1.2.3 is acceptable.

### Greater Than / Less Than
```json
"version": ">1.2.3"   // Greater than 1.2.3
"version": ">=1.2.3"  // Greater than or equal to 1.2.3
"version": "<2.0.0"   // Less than 2.0.0
"version": "<=2.0.0"  // Less than or equal to 2.0.0
```

### Caret (^) - Compatible Updates
```json
"version": "^1.2.3"
```
Allows changes that do not modify the left-most non-zero digit:
- `^1.2.3` allows `>=1.2.3` and `<2.0.0`
- `^0.2.3` allows `>=0.2.3` and `<0.3.0`
- `^0.0.3` allows `>=0.0.3` and `<0.0.4`

### Tilde (~) - Patch Updates
```json
"version": "~1.2.3"
```
Allows patch-level changes (same major.minor version):
- `~1.2.3` allows `>=1.2.3` and `<1.3.0`
- `~1.2` allows `>=1.2.0` and `<1.3.0`

## Lock File: `package-lock.lament`

The lock file records exact versions of all dependencies installed. It ensures reproducible builds across different environments.

### Format

```json
{
  "created_at": "2025-11-13T10:30:00",
  "packages": {
    "package-name": {
      "name": "package-name",
      "version": "1.2.3",
      "checksum": "sha256:abc123...",
      "dependencies": ["dep1", "dep2"]
    }
  }
}
```

### Fields

- **created_at** (string): ISO 8601 timestamp of lock file creation

- **packages** (object): Map of package name to locked package info
  - **name**: Package name
  - **version**: Exact version installed
  - **checksum**: SHA-256 hash of package contents
  - **dependencies**: List of direct dependency names

## Build Configuration: `build.lament`

Optional build configuration file for advanced build settings.

### Format

```json
{
  "name": "my-project",
  "target": "executable",
  "entry_point": "src/main.lament",
  "output_dir": "build/out",
  "source_dirs": ["src", "lib"],

  "include_patterns": ["**/*.lament"],
  "exclude_patterns": ["tests/**", "**/test_*.lament"],

  "dependencies": ["emotion-core", "neural-net"],

  "optimization_level": 2,
  "debug": false,
  "warnings_as_errors": true,
  "custom_flags": ["--enable-jit", "--inline-threshold=500"]
}
```

### Fields

- **name** (string): Project name

- **target** (string): Build target type
  - `executable`: Standalone executable
  - `library`: Reusable library
  - `module`: Single module

- **entry_point** (string): Main source file

- **output_dir** (string): Directory for build artifacts

- **source_dirs** (array): Directories to search for source files

- **include_patterns** (array): Glob patterns for files to include

- **exclude_patterns** (array): Glob patterns for files to exclude

- **dependencies** (array): Package dependencies

- **optimization_level** (integer): Optimization level (0-3)
  - 0: No optimization
  - 1: Basic optimization
  - 2: Full optimization
  - 3: Aggressive optimization

- **debug** (boolean): Enable debug information

- **warnings_as_errors** (boolean): Treat warnings as errors

- **custom_flags** (array): Additional compiler flags

## Package Structure

Recommended directory structure for a Lament package:

```
my-package/
├── package.lament           # Package metadata
├── package-lock.lament      # Lock file (generated)
├── build.lament             # Build configuration (optional)
├── README.md                # Documentation
├── LICENSE                  # License file
├── src/                     # Source files
│   ├── main.lament
│   ├── utils.lament
│   └── module/
│       └── helper.lament
├── lib/                     # Library files
│   └── vendor.lament
├── tests/                   # Test files (excluded from package)
│   ├── test_main.lament
│   └── test_utils.lament
├── examples/                # Example files (excluded from package)
│   └── demo.lament
├── build/                   # Build artifacts (excluded from package)
│   ├── out/
│   └── .build_cache
└── .lament/                 # Package manager files (excluded)
    ├── packages/
    └── cache/
```

## Publishing a Package

To publish a package:

1. Ensure `package.lament` is complete and valid
2. Test the package locally
3. Run `lament-pkg install` to verify dependencies
4. Run `lament-build build` to verify it compiles
5. Publish: `lament-registry publish . --registry local`

For remote registries (requires authentication):
```bash
lament-registry publish . --registry official --api-key YOUR_KEY
```

## Installing a Package

```bash
# Install from package.lament dependencies
lament-pkg install

# Install specific package
lament-pkg install emotion-core@^1.0.0

# Install as dev dependency
lament-pkg install --dev test-framework@~2.0.0
```

## Semantic Versioning Guide

Follow semantic versioning (SemVer) principles:

- **MAJOR** version: Incompatible API changes
- **MINOR** version: Add functionality (backwards-compatible)
- **PATCH** version: Bug fixes (backwards-compatible)

Examples:
- `1.0.0` → `1.0.1`: Bug fix
- `1.0.1` → `1.1.0`: New feature
- `1.1.0` → `2.0.0`: Breaking change

Pre-release versions:
- `1.0.0-alpha`: Alpha release
- `1.0.0-beta.1`: Beta release
- `1.0.0-rc.2`: Release candidate

Build metadata:
- `1.0.0+20130313144700`: Build timestamp
- `1.0.0+exp.sha.5114f85`: Experimental build

## Best Practices

1. **Versioning**: Always follow semantic versioning
2. **Dependencies**: Specify minimum compatible versions
3. **Documentation**: Include README.md and inline comments
4. **License**: Always include a license file
5. **Testing**: Write tests before publishing
6. **Changelog**: Maintain a CHANGELOG.md file
7. **Git Tags**: Tag releases in version control
8. **Build Scripts**: Keep build scripts simple and documented
9. **File Size**: Keep packages small by excluding unnecessary files
10. **Security**: Never commit API keys or secrets

## Example: Complete Package

See `examples/sample-package/` for a complete package example.

## Registry Configuration

Configure registries in `~/.lament/registries.json`:

```json
{
  "registries": [
    {
      "name": "official",
      "url": "https://registry.lament-lang.org",
      "priority": 100,
      "enabled": true
    },
    {
      "name": "local",
      "url": "file://~/.lament/local-registry",
      "priority": 50,
      "enabled": true
    },
    {
      "name": "company-internal",
      "url": "https://registry.company.internal",
      "api_key": "secret-key",
      "priority": 75,
      "enabled": true
    }
  ]
}
```

Multiple registries are searched in priority order (highest first).
