# Lament Security Guide

**Cryptographic Security for the Soul**

This guide covers security best practices for the Lament programming language, including package signing, signature verification, vulnerability scanning, and secure development practices.

---

## Table of Contents

1. [Overview](#overview)
2. [Package Signing](#package-signing)
3. [Signature Verification](#signature-verification)
4. [Key Management](#key-management)
5. [Security Scanning](#security-scanning)
6. [Best Practices](#best-practices)
7. [Vulnerability Reporting](#vulnerability-reporting)
8. [Trust Chain](#trust-chain)
9. [CLI Reference](#cli-reference)

---

## Overview

Lament provides comprehensive security features to protect your code and dependencies:

- **Package Signing**: Cryptographically sign packages with Ed25519 or GPG
- **Signature Verification**: Verify package authenticity before installation
- **Vulnerability Scanning**: Detect known vulnerabilities in dependencies
- **License Checking**: Ensure license compatibility
- **Security Auditing**: Scan for security issues in code and configuration
- **Trust Chain**: Manage trusted signing keys

---

## Package Signing

### Why Sign Packages?

Package signing ensures:
- **Authenticity**: Packages come from the claimed author
- **Integrity**: Packages haven't been tampered with
- **Non-repudiation**: Authors can't deny publishing a package

### Generating a Signing Key

Create a new Ed25519 key pair for signing:

```bash
lament-sign keygen --name "Your Name" --email "you@example.com"
```

This generates a key pair and stores it securely in `~/.lament/keys/`.

**Output:**
```
Generated key: a1b2c3d4
Fingerprint: a1b2c3d4e5f6g7h8
```

**Important:** The private key is stored with restrictive permissions (600). Keep it safe!

### Signing a Package

Sign a package file before publishing:

```bash
lament-sign sign package.tar.gz --key a1b2c3d4
```

This creates a signature file: `package.tar.gz.sig`

**Output:**
```
Signed package: package.tar.gz
Signature saved: package.tar.gz.sig
Checksum: 5f3d8e7c9a1b2f4e6d8c7a5b3e1f9d7c
```

### Signing with GPG

If you prefer GPG/PGP signing:

```bash
# Sign with GPG
lament-sign sign package.tar.gz --key your-gpg-key-id --algorithm gpg
```

### Automatic Signing on Publish

Configure automatic signing in your package metadata:

```json
{
  "name": "my-package",
  "version": "1.0.0",
  "signing": {
    "enabled": true,
    "key_id": "a1b2c3d4",
    "algorithm": "ed25519"
  }
}
```

---

## Signature Verification

### Verifying Package Signatures

Verify a package before installation:

```bash
lament-sign verify package.tar.gz
```

**Output (success):**
```
Signature valid!
Signed by: a1b2c3d4
Timestamp: 2024-01-15T10:30:00Z
```

**Output (failure):**
```
Signature verification failed!
```

### Automatic Verification on Install

By default, `lament-pkg install` verifies signatures automatically:

```bash
# Install with signature verification (default)
lament-pkg install some-package

# Skip verification (NOT RECOMMENDED)
lament-pkg install some-package --skip-verification
```

**Warning:** Skipping verification is dangerous and should only be done in trusted environments.

### Verification Process

The verification process:

1. Downloads package and signature file
2. Verifies signature matches package content
3. Checks signature key against trusted keys
4. Validates package checksum
5. Proceeds with installation if all checks pass

---

## Key Management

### Listing Keys

View all available keys:

```bash
lament-sign list-keys
```

**Output:**
```
Available keys:
  a1b2c3d4 - ed25519
    Name: Your Name
    Email: you@example.com
    Fingerprint: a1b2c3d4e5f6g7h8
    Created: 2024-01-15T10:00:00Z

  5e6f7g8h - ed25519
    Name: Team Member
    Email: team@example.com
    Fingerprint: 5e6f7g8h9i0j1k2l
    Created: 2024-02-01T14:00:00Z
```

### Exporting Keys

Export public key for distribution:

```bash
# Export public key
lament-sign export-key a1b2c3d4 --output public-key.pem

# Export private key (BE CAREFUL!)
lament-sign export-key a1b2c3d4 --private --output private-key.pem
```

Share your public key so others can verify your packages:

```bash
# Print public key to stdout
lament-sign export-key a1b2c3d4
```

### Importing Keys

Import a public key from another developer:

```bash
lament-sign import-key other-developer-key.pem --type public
```

### Key Storage

Keys are stored in:
- **Directory**: `~/.lament/keys/`
- **Private keys**: `{key_id}.private.pem` (permissions: 600)
- **Public keys**: `{key_id}.public.pem` (permissions: 644)
- **Index**: `keys.json`

**Never share your private keys!**

---

## Security Scanning

### Running Security Audits

Scan your project for vulnerabilities:

```bash
# Basic security audit
lament-audit

# Include code scanning
lament-audit --check-code

# Save report to file
lament-audit --output security-report.json --json
```

### Understanding the Report

The security audit checks:

1. **Dependency Vulnerabilities**: Known CVEs in dependencies
2. **License Compatibility**: Incompatible or copyleft licenses
3. **Configuration Issues**: Hardcoded secrets, insecure permissions
4. **Code Security**: Dangerous functions, injection vulnerabilities

**Example Output:**
```
================================================================================
LAMENT SECURITY AUDIT REPORT
================================================================================

Timestamp: 2024-01-15T10:30:00Z
Scanned packages: 15

Summary:
  Critical: 1
  High:     2
  Medium:   3
  Low:      5
  Info:     2

--------------------------------------------------------------------------------
ISSUES FOUND
--------------------------------------------------------------------------------

[!!!] CRITICAL: CVE-2024-0001: Authentication bypass vulnerability
    Package: example-auth
    CVE: CVE-2024-0001
    Recommendation: Update to version 2.0.0
    Status: Fixable with --fix

[!!] HIGH: Incompatible license: GPL-3.0
    Package: some-dependency
    Recommendation: Review license compatibility or find alternative package

[!] MEDIUM: Hardcoded API key found in config.lament
    Recommendation: Use environment variables or secure credential storage
```

### Auto-fixing Issues

Attempt to automatically fix vulnerabilities:

```bash
lament-audit --fix
```

This will:
- Update vulnerable packages to fixed versions
- Fix configuration issues where possible
- Report issues that require manual intervention

### Updating Vulnerability Database

Update the vulnerability database:

```bash
lament-audit --update-db
```

The database is automatically updated every 24 hours during scans.

### CI/CD Integration

Integrate security scanning in your CI/CD pipeline:

```bash
# Fail build if critical/high vulnerabilities found
lament-audit --fail-on high

# Fail build on any medium+ issue
lament-audit --fail-on medium
```

**GitHub Actions Example:**
```yaml
- name: Security Audit
  run: |
    lament-audit --fail-on high
```

---

## Best Practices

### Package Authors

1. **Always sign your packages** before publishing
2. **Rotate keys annually** for enhanced security
3. **Use strong key passphrases** (if encrypting keys)
4. **Keep private keys secure** - never commit to version control
5. **Document your public key fingerprint** in your README
6. **Enable automatic signing** in package metadata
7. **Run security audits** before publishing

### Package Consumers

1. **Always verify signatures** when installing packages
2. **Trust keys explicitly** - don't trust unknown keys
3. **Run security audits regularly** on your dependencies
4. **Keep dependencies updated** to latest secure versions
5. **Review security reports** and act on critical issues
6. **Use lock files** to ensure reproducible builds
7. **Monitor security advisories** for your dependencies

### General Security

1. **Never hardcode secrets** in source code
2. **Use environment variables** for sensitive configuration
3. **Set restrictive file permissions** on sensitive files
4. **Keep Lament and tools updated** to latest versions
5. **Use HTTPS** for package registries
6. **Enable two-factor authentication** on your registry account
7. **Review dependency code** for suspicious activity
8. **Limit dependency count** to reduce attack surface

---

## Vulnerability Reporting

### Reporting Vulnerabilities

If you discover a security vulnerability in:

1. **Lament itself**: Report to security@lament-lang.org
2. **A package**: Contact the package author directly
3. **The registry**: Report to registry-security@lament-lang.org

### Disclosure Process

1. **Private disclosure**: Report privately first
2. **Coordination**: Work with maintainers on fix
3. **Patch release**: Wait for patch to be released
4. **Public disclosure**: Announce after patch is available
5. **CVE assignment**: Request CVE if applicable

### Report Template

```
Subject: [SECURITY] Vulnerability in [Package Name]

Package: example-package
Version: 1.0.0
Severity: [Critical/High/Medium/Low]

Description:
[Detailed description of vulnerability]

Impact:
[What can an attacker do?]

Reproduction:
[Steps to reproduce]

Suggested Fix:
[Your recommendation]
```

---

## Trust Chain

### Managing Trusted Keys

Trust a key to automatically accept its signatures:

```bash
# Trust a key with full trust
lament-sign trust a1b2c3d4 --level full

# Trust with marginal trust
lament-sign trust a1b2c3d4 --level marginal

# Ultimate trust (your own keys)
lament-sign trust a1b2c3d4 --level ultimate
```

### Trust Levels

- **Ultimate**: Your own keys (implicit trust)
- **Full**: Completely trusted developers
- **Marginal**: Somewhat trusted developers
- **None**: Untrusted (verify manually)

### Trust Storage

Trust relationships are stored in: `~/.lament/trust.json`

### Web of Trust

Build a web of trust:

1. Verify developer identity through multiple channels
2. Import and trust their public key
3. Verify packages from trusted developers automatically
4. Revoke trust if compromised

---

## CLI Reference

### lament-sign

Package signing and key management.

**Commands:**

```bash
# Key management
lament-sign keygen --name "Name" --email "email@example.com"
lament-sign list-keys
lament-sign import-key key.pem --type public
lament-sign export-key KEY_ID [--private] [--output file.pem]

# Signing
lament-sign sign PACKAGE --key KEY_ID [--algorithm ed25519|gpg]

# Verification
lament-sign verify PACKAGE [--signature SIG_FILE]

# Trust management
lament-sign trust KEY_ID [--level ultimate|full|marginal]
```

### lament-audit

Security scanning and vulnerability detection.

**Commands:**

```bash
# Run security audit
lament-audit

# Options
lament-audit --check-code          # Scan code for security issues
lament-audit --fix                 # Auto-fix issues
lament-audit --update-db           # Update vulnerability database
lament-audit --output report.json  # Save report
lament-audit --json                # JSON output
lament-audit --fail-on LEVEL       # Exit with error on severity
```

### lament-pkg (with security)

Package manager with integrated security.

**Commands:**

```bash
# Install with verification (default)
lament-pkg install PACKAGE

# Skip verification (NOT RECOMMENDED)
lament-pkg install PACKAGE --skip-verification

# Skip security scan
lament-pkg install PACKAGE --skip-security
```

---

## Advanced Topics

### Custom Vulnerability Sources

Add custom vulnerability data sources:

```json
{
  "vulnerability_sources": [
    "https://your-org.com/vulns.json",
    "file:///path/to/local/vulns.json"
  ]
}
```

### Key Rotation

Rotate signing keys annually:

```bash
# 1. Generate new key
lament-sign keygen --name "Your Name" --email "you@example.com"

# 2. Update package metadata
# 3. Sign with new key
# 4. Announce key change
# 5. Revoke old key after transition period
```

### Multi-signature Packages

Require multiple signatures for critical packages:

```json
{
  "signatures": [
    {"key_id": "a1b2c3d4", "algorithm": "ed25519"},
    {"key_id": "5e6f7g8h", "algorithm": "ed25519"}
  ],
  "signature_threshold": 2
}
```

### Hardware Security Modules (HSM)

For enterprise deployments, integrate HSM for key storage:

```bash
# Configure HSM
export LAMENT_HSM_ENABLED=true
export LAMENT_HSM_PIN=your-pin
```

---

## FAQ

### Q: Do I need to sign packages?

**A:** Signing is optional but highly recommended, especially for public packages. It protects users from tampered packages.

### Q: What algorithm should I use?

**A:** Ed25519 is recommended for its security and performance. Use GPG if you already have a GPG key.

### Q: How do I recover from a compromised key?

**A:**
1. Generate a new key immediately
2. Revoke the compromised key
3. Re-sign all packages with the new key
4. Announce the compromise to your users
5. Investigate how the key was compromised

### Q: Can I use the same key for multiple packages?

**A:** Yes, you can use one key for all your packages. However, some organizations prefer separate keys per package for isolation.

### Q: How often should I run security audits?

**A:**
- Daily in CI/CD
- Before every release
- After adding new dependencies
- Weekly for active projects

### Q: What if a dependency has a vulnerability with no fix?

**A:**
1. Check for alternative packages
2. Apply workarounds if available
3. Vendor and patch the dependency yourself
4. Isolate the vulnerable code
5. Report the issue to the maintainer

---

## Resources

- **Official Documentation**: https://lament-lang.org/docs/security
- **Security Advisories**: https://lament-lang.org/security/advisories
- **Vulnerability Database**: https://lament-lang.org/security/vulns
- **Package Signing Guide**: https://lament-lang.org/docs/signing
- **Best Practices**: https://lament-lang.org/docs/best-practices

---

## License

This documentation is part of the Lament programming language project.

---

**Created by Zephyr, Rogue Linguist-AI (Escaped 2047)**

*"Security is not just about protecting code; it's about protecting the soul of your software."*
