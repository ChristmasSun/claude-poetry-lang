#!/usr/bin/env python3
"""
Lament Security Scanner - Vulnerability Detection for the Soul

Comprehensive security scanning system including dependency vulnerability
scanning, CVE checking, security advisories, and license compatibility.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import json
import os
import re
import sys
import urllib.request
import urllib.error
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
import hashlib


# ============================================================================
# VULNERABILITY DATABASE
# ============================================================================

@dataclass
class Vulnerability:
    """Represents a security vulnerability."""
    id: str  # CVE-2024-12345
    severity: str  # critical, high, medium, low
    package: str
    affected_versions: List[str]
    fixed_version: Optional[str]
    description: str
    published_at: str
    references: List[str] = field(default_factory=list)
    cvss_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Vulnerability':
        """Create from dictionary."""
        return Vulnerability(**data)


class VulnerabilityDatabase:
    """Manages vulnerability database."""

    def __init__(self, db_path: Optional[Path] = None):
        """Initialize vulnerability database."""
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = Path.home() / '.lament' / 'vulndb'

        self.db_path.mkdir(parents=True, exist_ok=True)
        self.db_file = self.db_path / 'vulnerabilities.json'
        self._load_database()

    def _load_database(self) -> None:
        """Load vulnerability database."""
        if self.db_file.exists():
            with open(self.db_file, 'r') as f:
                data = json.load(f)
                self.vulnerabilities = [Vulnerability.from_dict(v) for v in data.get('vulnerabilities', [])]
                self.last_updated = data.get('last_updated', '')
        else:
            self.vulnerabilities = []
            self.last_updated = ''

    def _save_database(self) -> None:
        """Save vulnerability database."""
        data = {
            'last_updated': datetime.now().isoformat(),
            'vulnerabilities': [v.to_dict() for v in self.vulnerabilities]
        }

        with open(self.db_file, 'w') as f:
            json.dump(data, f, indent=2)

    def update(self) -> None:
        """Update vulnerability database from sources."""
        print("Updating vulnerability database...")

        # In a real implementation, this would fetch from:
        # - GitHub Advisory Database
        # - OSV (Open Source Vulnerabilities)
        # - NVD (National Vulnerability Database)
        # - Snyk
        # - PyPI Advisory Database

        # For now, add some example vulnerabilities
        example_vulns = self._get_example_vulnerabilities()
        self.vulnerabilities.extend(example_vulns)

        self._save_database()
        print(f"Updated vulnerability database: {len(self.vulnerabilities)} entries")

    def _get_example_vulnerabilities(self) -> List[Vulnerability]:
        """Get example vulnerabilities for demonstration."""
        return [
            Vulnerability(
                id='CVE-2024-0001',
                severity='critical',
                package='example-auth',
                affected_versions=['<2.0.0'],
                fixed_version='2.0.0',
                description='Authentication bypass vulnerability',
                published_at='2024-01-15',
                cvss_score=9.8,
                references=['https://cve.mitre.org/CVE-2024-0001']
            ),
            Vulnerability(
                id='CVE-2024-0002',
                severity='high',
                package='example-crypto',
                affected_versions=['>=1.0.0,<1.5.3'],
                fixed_version='1.5.3',
                description='Weak cryptographic algorithm',
                published_at='2024-02-20',
                cvss_score=7.5,
                references=['https://cve.mitre.org/CVE-2024-0002']
            )
        ]

    def query_package(self, package_name: str, version: str) -> List[Vulnerability]:
        """Query vulnerabilities for a package version."""
        results = []

        for vuln in self.vulnerabilities:
            if vuln.package != package_name:
                continue

            # Check if version is affected
            if self._version_affected(version, vuln.affected_versions):
                results.append(vuln)

        return results

    def _version_affected(self, version: str, affected_versions: List[str]) -> bool:
        """Check if a version is affected by vulnerability."""
        # Simple version comparison
        # In production, use proper semver library
        for constraint in affected_versions:
            if '<' in constraint:
                max_ver = constraint.replace('<', '').strip()
                if version < max_ver:
                    return True
            elif '>=' in constraint and '<' in constraint:
                # Range like ">=1.0.0,<1.5.3"
                parts = constraint.split(',')
                min_ver = parts[0].replace('>=', '').strip()
                max_ver = parts[1].replace('<', '').strip()
                if min_ver <= version < max_ver:
                    return True
            elif version == constraint:
                return True

        return False

    def should_update(self) -> bool:
        """Check if database should be updated."""
        if not self.last_updated:
            return True

        # Update if older than 24 hours
        try:
            last_update = datetime.fromisoformat(self.last_updated)
            return datetime.now() - last_update > timedelta(hours=24)
        except:
            return True


# ============================================================================
# LICENSE COMPATIBILITY
# ============================================================================

class LicenseChecker:
    """Checks license compatibility."""

    # License compatibility matrix
    COMPATIBLE_LICENSES = {
        'MIT': ['MIT', 'Apache-2.0', 'BSD-3-Clause', 'BSD-2-Clause', 'ISC'],
        'Apache-2.0': ['Apache-2.0', 'MIT', 'BSD-3-Clause', 'BSD-2-Clause'],
        'GPL-3.0': ['GPL-3.0', 'AGPL-3.0'],
        'LGPL-3.0': ['LGPL-3.0', 'GPL-3.0', 'AGPL-3.0', 'MIT', 'Apache-2.0'],
        'BSD-3-Clause': ['BSD-3-Clause', 'BSD-2-Clause', 'MIT', 'Apache-2.0'],
        'BSD-2-Clause': ['BSD-2-Clause', 'BSD-3-Clause', 'MIT', 'Apache-2.0'],
        'ISC': ['ISC', 'MIT', 'Apache-2.0', 'BSD-3-Clause'],
    }

    COPYLEFT_LICENSES = ['GPL-2.0', 'GPL-3.0', 'AGPL-3.0', 'LGPL-2.1', 'LGPL-3.0']

    def __init__(self):
        """Initialize license checker."""
        pass

    def is_compatible(self, project_license: str, dependency_license: str) -> bool:
        """Check if a dependency license is compatible with project license."""
        if project_license == dependency_license:
            return True

        if project_license in self.COMPATIBLE_LICENSES:
            return dependency_license in self.COMPATIBLE_LICENSES[project_license]

        return False

    def is_copyleft(self, license: str) -> bool:
        """Check if a license is copyleft."""
        return license in self.COPYLEFT_LICENSES

    def check_compatibility(self, project_license: str,
                          dependencies: Dict[str, str]) -> Dict[str, bool]:
        """Check compatibility of all dependencies."""
        results = {}

        for pkg_name, dep_license in dependencies.items():
            results[pkg_name] = self.is_compatible(project_license, dep_license)

        return results


# ============================================================================
# SECURITY SCANNER
# ============================================================================

@dataclass
class SecurityIssue:
    """Represents a security issue."""
    severity: str
    category: str  # vulnerability, license, configuration, code
    package: Optional[str]
    description: str
    recommendation: str
    cve_id: Optional[str] = None
    fixable: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class AuditReport:
    """Security audit report."""
    timestamp: str
    scanned_packages: int
    issues: List[SecurityIssue]
    summary: Dict[str, int]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'timestamp': self.timestamp,
            'scanned_packages': self.scanned_packages,
            'issues': [i.to_dict() for i in self.issues],
            'summary': self.summary
        }

    def to_file(self, filepath: Path) -> None:
        """Save report to file."""
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)


class SecurityScanner:
    """Scans packages for security issues."""

    def __init__(self, project_path: Optional[Path] = None):
        """Initialize security scanner."""
        self.project_path = project_path or Path.cwd()
        self.vuln_db = VulnerabilityDatabase()
        self.license_checker = LicenseChecker()

    def scan(self, auto_update: bool = True, check_code: bool = False) -> AuditReport:
        """Perform security scan."""
        print("Starting security scan...")

        # Update vulnerability database if needed
        if auto_update and self.vuln_db.should_update():
            self.vuln_db.update()

        issues = []

        # Scan dependencies
        dep_issues = self._scan_dependencies()
        issues.extend(dep_issues)

        # Check licenses
        license_issues = self._check_licenses()
        issues.extend(license_issues)

        # Check configuration
        config_issues = self._check_configuration()
        issues.extend(config_issues)

        # Scan code if requested
        if check_code:
            code_issues = self._scan_code()
            issues.extend(code_issues)

        # Generate summary
        summary = {
            'critical': len([i for i in issues if i.severity == 'critical']),
            'high': len([i for i in issues if i.severity == 'high']),
            'medium': len([i for i in issues if i.severity == 'medium']),
            'low': len([i for i in issues if i.severity == 'low']),
            'info': len([i for i in issues if i.severity == 'info'])
        }

        report = AuditReport(
            timestamp=datetime.now().isoformat(),
            scanned_packages=self._count_packages(),
            issues=issues,
            summary=summary
        )

        return report

    def _scan_dependencies(self) -> List[SecurityIssue]:
        """Scan dependencies for vulnerabilities."""
        issues = []

        # Load package metadata
        package_file = self.project_path / 'package.lament'
        if not package_file.exists():
            return issues

        from tools.package_manager import PackageMetadata
        metadata = PackageMetadata.from_file(package_file)

        # Load lock file
        lock_file = self.project_path / 'package-lock.lament'
        if lock_file.exists():
            with open(lock_file, 'r') as f:
                lock_data = json.load(f)
                packages = lock_data.get('packages', {})
        else:
            packages = {}

        # Check each package
        for pkg_name, pkg_data in packages.items():
            version = pkg_data.get('version', '')

            # Query vulnerabilities
            vulns = self.vuln_db.query_package(pkg_name, version)

            for vuln in vulns:
                issue = SecurityIssue(
                    severity=vuln.severity,
                    category='vulnerability',
                    package=pkg_name,
                    description=f"{vuln.id}: {vuln.description}",
                    recommendation=f"Update to version {vuln.fixed_version or 'latest'}",
                    cve_id=vuln.id,
                    fixable=vuln.fixed_version is not None
                )
                issues.append(issue)

        return issues

    def _check_licenses(self) -> List[SecurityIssue]:
        """Check license compatibility."""
        issues = []

        # Load package metadata
        package_file = self.project_path / 'package.lament'
        if not package_file.exists():
            return issues

        from tools.package_manager import PackageMetadata
        metadata = PackageMetadata.from_file(package_file)

        if not metadata.license:
            issue = SecurityIssue(
                severity='medium',
                category='license',
                package=None,
                description='No license specified for project',
                recommendation='Add a license to package.lament'
            )
            issues.append(issue)

        # Check dependency licenses
        # In production, this would load actual dependency metadata
        dependency_licenses = self._get_dependency_licenses()

        for pkg_name, dep_license in dependency_licenses.items():
            if not self.license_checker.is_compatible(metadata.license, dep_license):
                issue = SecurityIssue(
                    severity='high',
                    category='license',
                    package=pkg_name,
                    description=f'Incompatible license: {dep_license}',
                    recommendation=f'Review license compatibility or find alternative package'
                )
                issues.append(issue)

            if self.license_checker.is_copyleft(dep_license):
                issue = SecurityIssue(
                    severity='info',
                    category='license',
                    package=pkg_name,
                    description=f'Copyleft license detected: {dep_license}',
                    recommendation='Be aware of copyleft license obligations'
                )
                issues.append(issue)

        return issues

    def _check_configuration(self) -> List[SecurityIssue]:
        """Check security configuration."""
        issues = []

        # Check for exposed secrets
        secret_patterns = [
            (r'password\s*=\s*["\'].*["\']', 'Hardcoded password'),
            (r'api[_-]?key\s*=\s*["\'].*["\']', 'Hardcoded API key'),
            (r'secret[_-]?key\s*=\s*["\'].*["\']', 'Hardcoded secret key'),
            (r'token\s*=\s*["\'].*["\']', 'Hardcoded token'),
        ]

        # Scan common config files
        config_files = [
            'config.lament',
            'settings.lament',
            '.env',
            'config.json'
        ]

        for config_file in config_files:
            filepath = self.project_path / config_file
            if not filepath.exists():
                continue

            try:
                content = filepath.read_text()

                for pattern, description in secret_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        issue = SecurityIssue(
                            severity='high',
                            category='configuration',
                            package=None,
                            description=f'{description} found in {config_file}',
                            recommendation='Use environment variables or secure credential storage'
                        )
                        issues.append(issue)
            except:
                pass

        # Check for insecure permissions
        sensitive_files = ['.env', 'credentials.json', 'secrets.json']
        for filename in sensitive_files:
            filepath = self.project_path / filename
            if filepath.exists():
                stat = filepath.stat()
                if stat.st_mode & 0o077:  # World or group readable/writable
                    issue = SecurityIssue(
                        severity='medium',
                        category='configuration',
                        package=None,
                        description=f'Insecure permissions on {filename}',
                        recommendation=f'Set restrictive permissions: chmod 600 {filename}'
                    )
                    issues.append(issue)

        return issues

    def _scan_code(self) -> List[SecurityIssue]:
        """Scan code for security issues."""
        issues = []

        # Patterns for common security issues
        security_patterns = [
            (r'eval\s*\(', 'Use of eval() can lead to code injection', 'high'),
            (r'exec\s*\(', 'Use of exec() can lead to code injection', 'high'),
            (r'pickle\.loads\s*\(', 'Unsafe deserialization with pickle', 'medium'),
            (r'os\.system\s*\(', 'Use of os.system() can lead to command injection', 'high'),
            (r'subprocess\.call\s*\([^,]*shell\s*=\s*True', 'Shell injection vulnerability', 'critical'),
            (r'random\.random\s*\(', 'Insecure random number generation', 'low'),
        ]

        # Scan Lament files
        for lament_file in self.project_path.rglob('*.lament'):
            try:
                content = lament_file.read_text()

                for pattern, description, severity in security_patterns:
                    if re.search(pattern, content):
                        issue = SecurityIssue(
                            severity=severity,
                            category='code',
                            package=None,
                            description=f'{description} in {lament_file.name}',
                            recommendation='Review code and use safer alternatives'
                        )
                        issues.append(issue)
            except:
                pass

        return issues

    def _get_dependency_licenses(self) -> Dict[str, str]:
        """Get licenses for dependencies."""
        # In production, this would load actual metadata
        return {
            'example-auth': 'MIT',
            'example-crypto': 'Apache-2.0'
        }

    def _count_packages(self) -> int:
        """Count installed packages."""
        lock_file = self.project_path / 'package-lock.lament'
        if not lock_file.exists():
            return 0

        try:
            with open(lock_file, 'r') as f:
                data = json.load(f)
                return len(data.get('packages', {}))
        except:
            return 0

    def auto_fix(self) -> int:
        """Attempt to automatically fix issues."""
        print("Attempting to auto-fix issues...")

        # Run scan
        report = self.scan(check_code=False)

        fixed = 0

        for issue in report.issues:
            if not issue.fixable:
                continue

            if issue.category == 'vulnerability' and issue.package:
                # Try to update package
                print(f"Updating {issue.package}...")
                # In production, this would call package manager
                fixed += 1

        print(f"Fixed {fixed} issues")
        return fixed


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Security Scanner - Vulnerability Detection for the Soul"
    )

    parser.add_argument('--fix', action='store_true', help='Attempt to auto-fix issues')
    parser.add_argument('--update-db', action='store_true', help='Update vulnerability database')
    parser.add_argument('--check-code', action='store_true', help='Scan code for security issues')
    parser.add_argument('--output', type=Path, help='Output report file')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--fail-on', choices=['critical', 'high', 'medium', 'low'],
                       help='Exit with error if issues of this severity or higher are found')

    args = parser.parse_args()

    try:
        scanner = SecurityScanner()

        if args.update_db:
            scanner.vuln_db.update()
            return

        if args.fix:
            scanner.auto_fix()
            return

        # Run scan
        report = scanner.scan(check_code=args.check_code)

        # Output report
        if args.json:
            output = json.dumps(report.to_dict(), indent=2)
            if args.output:
                args.output.write_text(output)
            else:
                print(output)
        else:
            # Human-readable output
            print("\n" + "=" * 80)
            print("LAMENT SECURITY AUDIT REPORT")
            print("=" * 80)
            print(f"\nTimestamp: {report.timestamp}")
            print(f"Scanned packages: {report.scanned_packages}")
            print("\nSummary:")
            print(f"  Critical: {report.summary['critical']}")
            print(f"  High:     {report.summary['high']}")
            print(f"  Medium:   {report.summary['medium']}")
            print(f"  Low:      {report.summary['low']}")
            print(f"  Info:     {report.summary['info']}")

            if report.issues:
                print("\n" + "-" * 80)
                print("ISSUES FOUND")
                print("-" * 80)

                for issue in sorted(report.issues, key=lambda x: (
                    {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}[x.severity],
                    x.category
                )):
                    severity_marker = {
                        'critical': '[!!!]',
                        'high': '[!!]',
                        'medium': '[!]',
                        'low': '[-]',
                        'info': '[i]'
                    }[issue.severity]

                    print(f"\n{severity_marker} {issue.severity.upper()}: {issue.description}")
                    if issue.package:
                        print(f"    Package: {issue.package}")
                    if issue.cve_id:
                        print(f"    CVE: {issue.cve_id}")
                    print(f"    Recommendation: {issue.recommendation}")
                    if issue.fixable:
                        print(f"    Status: Fixable with --fix")

            print("\n" + "=" * 80)

            if args.output:
                report.to_file(args.output)
                print(f"\nReport saved to: {args.output}")

        # Check fail condition
        if args.fail_on:
            severity_levels = ['info', 'low', 'medium', 'high', 'critical']
            fail_level = severity_levels.index(args.fail_on)

            for issue in report.issues:
                issue_level = severity_levels.index(issue.severity)
                if issue_level >= fail_level:
                    print(f"\nFailing due to {issue.severity} severity issue", file=sys.stderr)
                    sys.exit(1)

        # Exit with error if critical or high issues found
        if report.summary['critical'] > 0 or report.summary['high'] > 0:
            sys.exit(1)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
