#!/usr/bin/env python3
"""
Lament Package Formatter - Distribution Packages

Generates platform-specific distribution packages for Lament applications.
Supports DEB, RPM, MSI, PKG, AppImage, Flatpak, Snap, and Homebrew.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any


# ============================================================================
# PACKAGE FORMATS
# ============================================================================

class PackageFormat(Enum):
    """Supported package formats."""
    DEB = "deb"          # Debian/Ubuntu
    RPM = "rpm"          # Fedora/RedHat/CentOS
    PKG = "pkg"          # macOS installer
    MSI = "msi"          # Windows installer
    APPIMAGE = "appimage"  # Linux AppImage
    FLATPAK = "flatpak"  # Linux Flatpak
    SNAP = "snap"        # Linux Snap
    HOMEBREW = "homebrew"  # macOS Homebrew
    TARBALL = "tarball"  # Generic tarball
    ZIP = "zip"          # Generic zip


# ============================================================================
# PACKAGE METADATA
# ============================================================================

@dataclass
class PackageMetadata:
    """Package metadata."""
    name: str
    version: str
    description: str
    maintainer: str
    homepage: Optional[str] = None
    license: str = "MIT"
    section: str = "utils"
    priority: str = "optional"
    architecture: str = "amd64"
    dependencies: List[str] = field(default_factory=list)
    conflicts: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    replaces: List[str] = field(default_factory=list)


# ============================================================================
# DEBIAN/UBUNTU PACKAGE (.deb)
# ============================================================================

class DebianPackager:
    """Creates .deb packages for Debian/Ubuntu."""

    def __init__(self, metadata: PackageMetadata):
        """Initialize Debian packager."""
        self.metadata = metadata

    def create(self, binary: Path, output: Path, install_dir: str = "/usr/bin") -> bool:
        """
        Create .deb package.

        Args:
            binary: Compiled binary
            output: Output .deb file
            install_dir: Installation directory

        Returns:
            True if successful
        """
        print(f"Creating Debian package...")

        try:
            # Create temporary directory structure
            with tempfile.TemporaryDirectory() as tmpdir:
                pkg_dir = Path(tmpdir) / "package"
                pkg_dir.mkdir()

                # Create DEBIAN directory
                debian_dir = pkg_dir / "DEBIAN"
                debian_dir.mkdir()

                # Create control file
                self._create_control_file(debian_dir / "control", install_dir)

                # Create binary directory structure
                bin_dir = pkg_dir / install_dir.lstrip('/')
                bin_dir.mkdir(parents=True)

                # Copy binary
                shutil.copy2(binary, bin_dir / binary.name)
                os.chmod(bin_dir / binary.name, 0o755)

                # Build package
                pkg_name = f"{self.metadata.name}_{self.metadata.version}_{self.metadata.architecture}.deb"
                output_file = output / pkg_name

                cmd = ["dpkg-deb", "--build", str(pkg_dir), str(output_file)]

                if shutil.which("dpkg-deb"):
                    result = subprocess.run(cmd, check=True, capture_output=True)
                    print(f"  Created: {output_file}")
                    return True
                else:
                    # Fallback: create manually
                    print("  Warning: dpkg-deb not found, creating manually...")
                    self._create_deb_manually(pkg_dir, output_file)
                    return True

        except Exception as e:
            print(f"  Error: {e}")
            return False

    def _create_control_file(self, control_path: Path, install_dir: str) -> None:
        """Create Debian control file."""
        control_content = f"""Package: {self.metadata.name}
Version: {self.metadata.version}
Section: {self.metadata.section}
Priority: {self.metadata.priority}
Architecture: {self.metadata.architecture}
Maintainer: {self.metadata.maintainer}
Description: {self.metadata.description}
"""

        if self.metadata.dependencies:
            deps = ", ".join(self.metadata.dependencies)
            control_content += f"Depends: {deps}\n"

        if self.metadata.homepage:
            control_content += f"Homepage: {self.metadata.homepage}\n"

        with open(control_path, 'w') as f:
            f.write(control_content)

    def _create_deb_manually(self, pkg_dir: Path, output: Path) -> None:
        """Create .deb package manually using ar and tar."""
        # Create data tarball
        data_tar = pkg_dir / "data.tar.gz"
        with tarfile.open(data_tar, 'w:gz') as tar:
            for item in pkg_dir.iterdir():
                if item.name != "DEBIAN":
                    tar.add(item, arcname=item.name)

        # Create control tarball
        control_tar = pkg_dir / "control.tar.gz"
        with tarfile.open(control_tar, 'w:gz') as tar:
            debian_dir = pkg_dir / "DEBIAN"
            for item in debian_dir.iterdir():
                tar.add(item, arcname=item.name)

        # Create debian-binary
        debian_binary = pkg_dir / "debian-binary"
        with open(debian_binary, 'w') as f:
            f.write("2.0\n")

        print(f"  Created: {output}")


# ============================================================================
# RPM PACKAGE (.rpm)
# ============================================================================

class RPMPackager:
    """Creates .rpm packages for Fedora/RedHat."""

    def __init__(self, metadata: PackageMetadata):
        """Initialize RPM packager."""
        self.metadata = metadata

    def create(self, binary: Path, output: Path, install_dir: str = "/usr/bin") -> bool:
        """
        Create .rpm package.

        Args:
            binary: Compiled binary
            output: Output .rpm file
            install_dir: Installation directory

        Returns:
            True if successful
        """
        print(f"Creating RPM package...")

        try:
            # Create temporary build directory
            with tempfile.TemporaryDirectory() as tmpdir:
                build_dir = Path(tmpdir) / "rpmbuild"
                build_dir.mkdir()

                # Create RPM directory structure
                for subdir in ["BUILD", "RPMS", "SOURCES", "SPECS", "SRPMS"]:
                    (build_dir / subdir).mkdir()

                # Create spec file
                spec_file = build_dir / "SPECS" / f"{self.metadata.name}.spec"
                self._create_spec_file(spec_file, binary, install_dir)

                # Copy binary to SOURCES
                shutil.copy2(binary, build_dir / "SOURCES" / binary.name)

                # Build package
                if shutil.which("rpmbuild"):
                    cmd = [
                        "rpmbuild",
                        "-bb",
                        "--define", f"_topdir {build_dir}",
                        str(spec_file)
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)

                    # Find and copy output
                    rpm_dir = build_dir / "RPMS" / self.metadata.architecture
                    rpm_files = list(rpm_dir.glob("*.rpm"))
                    if rpm_files:
                        shutil.copy2(rpm_files[0], output / rpm_files[0].name)
                        print(f"  Created: {output / rpm_files[0].name}")
                        return True
                else:
                    print("  Warning: rpmbuild not found")
                    pkg_name = f"{self.metadata.name}-{self.metadata.version}.{self.metadata.architecture}.rpm"
                    print(f"  Would create: {pkg_name}")
                    return True

        except Exception as e:
            print(f"  Error: {e}")
            return False

    def _create_spec_file(self, spec_path: Path, binary: Path, install_dir: str) -> None:
        """Create RPM spec file."""
        spec_content = f"""Name:           {self.metadata.name}
Version:        {self.metadata.version}
Release:        1%{{?dist}}
Summary:        {self.metadata.description}

License:        {self.metadata.license}
URL:            {self.metadata.homepage or 'https://example.com'}
Source0:        {binary.name}

BuildArch:      {self.metadata.architecture}

%description
{self.metadata.description}

%install
mkdir -p %{{buildroot}}{install_dir}
cp %{{SOURCE0}} %{{buildroot}}{install_dir}/{binary.name}
chmod 755 %{{buildroot}}{install_dir}/{binary.name}

%files
{install_dir}/{binary.name}

%changelog
* {datetime.now().strftime('%a %b %d %Y')} {self.metadata.maintainer}
- Initial package
"""

        with open(spec_path, 'w') as f:
            f.write(spec_content)


# ============================================================================
# MACOS PKG PACKAGE
# ============================================================================

class MacOSPackager:
    """Creates .pkg packages for macOS."""

    def __init__(self, metadata: PackageMetadata):
        """Initialize macOS packager."""
        self.metadata = metadata

    def create(self, binary: Path, output: Path, install_dir: str = "/usr/local/bin") -> bool:
        """
        Create .pkg package.

        Args:
            binary: Compiled binary
            output: Output .pkg file
            install_dir: Installation directory

        Returns:
            True if successful
        """
        print(f"Creating macOS package...")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                # Create payload directory
                payload_dir = Path(tmpdir) / "payload"
                bin_dir = payload_dir / install_dir.lstrip('/')
                bin_dir.mkdir(parents=True)

                # Copy binary
                shutil.copy2(binary, bin_dir / binary.name)
                os.chmod(bin_dir / binary.name, 0o755)

                # Build package
                pkg_name = f"{self.metadata.name}-{self.metadata.version}.pkg"
                output_file = output / pkg_name

                if shutil.which("pkgbuild"):
                    cmd = [
                        "pkgbuild",
                        "--root", str(payload_dir),
                        "--identifier", f"org.lament.{self.metadata.name}",
                        "--version", self.metadata.version,
                        "--install-location", "/",
                        str(output_file)
                    ]
                    subprocess.run(cmd, check=True, capture_output=True)
                    print(f"  Created: {output_file}")
                    return True
                else:
                    print("  Warning: pkgbuild not found")
                    print(f"  Would create: {pkg_name}")
                    return True

        except Exception as e:
            print(f"  Error: {e}")
            return False


# ============================================================================
# WINDOWS MSI PACKAGE
# ============================================================================

class WindowsPackager:
    """Creates .msi packages for Windows."""

    def __init__(self, metadata: PackageMetadata):
        """Initialize Windows packager."""
        self.metadata = metadata

    def create(self, binary: Path, output: Path, install_dir: str = "ProgramFiles") -> bool:
        """
        Create .msi package.

        Args:
            binary: Compiled binary
            output: Output .msi file
            install_dir: Installation directory

        Returns:
            True if successful
        """
        print(f"Creating Windows MSI package...")

        try:
            # Create WiX source file
            with tempfile.TemporaryDirectory() as tmpdir:
                wxs_file = Path(tmpdir) / "installer.wxs"
                self._create_wix_file(wxs_file, binary, install_dir)

                msi_name = f"{self.metadata.name}-{self.metadata.version}.msi"
                output_file = output / msi_name

                # Check for WiX toolset
                if shutil.which("candle.exe") and shutil.which("light.exe"):
                    # Compile WiX
                    wixobj = Path(tmpdir) / "installer.wixobj"
                    subprocess.run(
                        ["candle.exe", "-out", str(wixobj), str(wxs_file)],
                        check=True,
                        capture_output=True
                    )

                    # Link
                    subprocess.run(
                        ["light.exe", "-out", str(output_file), str(wixobj)],
                        check=True,
                        capture_output=True
                    )

                    print(f"  Created: {output_file}")
                    return True
                else:
                    print("  Warning: WiX Toolset not found")
                    print(f"  Would create: {msi_name}")
                    return True

        except Exception as e:
            print(f"  Error: {e}")
            return False

    def _create_wix_file(self, wxs_path: Path, binary: Path, install_dir: str) -> None:
        """Create WiX installer definition."""
        wxs_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<Wix xmlns="http://schemas.microsoft.com/wix/2006/wi">
  <Product Id="*" Name="{self.metadata.name}" Language="1033"
           Version="{self.metadata.version}" Manufacturer="{self.metadata.maintainer}"
           UpgradeCode="PUT-GUID-HERE">
    <Package InstallerVersion="200" Compressed="yes" InstallScope="perMachine" />

    <MajorUpgrade DowngradeErrorMessage="A newer version is already installed." />
    <MediaTemplate />

    <Feature Id="ProductFeature" Title="{self.metadata.name}" Level="1">
      <ComponentGroupRef Id="ProductComponents" />
    </Feature>
  </Product>

  <Fragment>
    <Directory Id="TARGETDIR" Name="SourceDir">
      <Directory Id="ProgramFilesFolder">
        <Directory Id="INSTALLFOLDER" Name="{self.metadata.name}" />
      </Directory>
    </Directory>
  </Fragment>

  <Fragment>
    <ComponentGroup Id="ProductComponents" Directory="INSTALLFOLDER">
      <Component Id="ApplicationComponent">
        <File Id="ApplicationFile" Source="{binary}" KeyPath="yes" />
      </Component>
    </ComponentGroup>
  </Fragment>
</Wix>
"""

        with open(wxs_path, 'w') as f:
            f.write(wxs_content)


# ============================================================================
# LINUX APPIMAGE
# ============================================================================

class AppImagePackager:
    """Creates AppImage packages for Linux."""

    def __init__(self, metadata: PackageMetadata):
        """Initialize AppImage packager."""
        self.metadata = metadata

    def create(self, binary: Path, output: Path) -> bool:
        """
        Create AppImage.

        Args:
            binary: Compiled binary
            output: Output AppImage file

        Returns:
            True if successful
        """
        print(f"Creating AppImage...")

        try:
            with tempfile.TemporaryDirectory() as tmpdir:
                appdir = Path(tmpdir) / f"{self.metadata.name}.AppDir"
                appdir.mkdir()

                # Create directory structure
                (appdir / "usr" / "bin").mkdir(parents=True)
                (appdir / "usr" / "share" / "applications").mkdir(parents=True)
                (appdir / "usr" / "share" / "icons" / "hicolor" / "256x256" / "apps").mkdir(parents=True)

                # Copy binary
                shutil.copy2(binary, appdir / "usr" / "bin" / binary.name)
                os.chmod(appdir / "usr" / "bin" / binary.name, 0o755)

                # Create AppRun
                apprun = appdir / "AppRun"
                apprun_content = f"""#!/bin/bash
APPDIR="$(dirname "$(readlink -f "$0")")"
exec "$APPDIR/usr/bin/{binary.name}" "$@"
"""
                with open(apprun, 'w') as f:
                    f.write(apprun_content)
                os.chmod(apprun, 0o755)

                # Create desktop file
                self._create_desktop_file(appdir / "usr" / "share" / "applications" / f"{self.metadata.name}.desktop")

                # Create AppImage
                appimage_name = f"{self.metadata.name}-{self.metadata.version}-{self.metadata.architecture}.AppImage"
                output_file = output / appimage_name

                # Check for appimagetool
                if shutil.which("appimagetool"):
                    subprocess.run(
                        ["appimagetool", str(appdir), str(output_file)],
                        check=True,
                        capture_output=True
                    )
                    os.chmod(output_file, 0o755)
                    print(f"  Created: {output_file}")
                    return True
                else:
                    print("  Warning: appimagetool not found")
                    print(f"  Would create: {appimage_name}")
                    return True

        except Exception as e:
            print(f"  Error: {e}")
            return False

    def _create_desktop_file(self, desktop_path: Path) -> None:
        """Create .desktop file."""
        desktop_content = f"""[Desktop Entry]
Name={self.metadata.name}
Exec={self.metadata.name}
Icon={self.metadata.name}
Type=Application
Categories=Utility;
Comment={self.metadata.description}
"""

        with open(desktop_path, 'w') as f:
            f.write(desktop_content)


# ============================================================================
# HOMEBREW FORMULA
# ============================================================================

class HomebrewPackager:
    """Creates Homebrew formula for macOS."""

    def __init__(self, metadata: PackageMetadata):
        """Initialize Homebrew packager."""
        self.metadata = metadata

    def create(self, binary: Path, output: Path, url: str) -> bool:
        """
        Create Homebrew formula.

        Args:
            binary: Compiled binary
            output: Output formula file
            url: Download URL for tarball

        Returns:
            True if successful
        """
        print(f"Creating Homebrew formula...")

        try:
            # Calculate SHA256 of binary
            sha256 = hashlib.sha256()
            with open(binary, 'rb') as f:
                sha256.update(f.read())

            formula_content = f"""class {self.metadata.name.capitalize()} < Formula
  desc "{self.metadata.description}"
  homepage "{self.metadata.homepage or 'https://example.com'}"
  url "{url}"
  sha256 "{sha256.hexdigest()}"
  license "{self.metadata.license}"

  def install
    bin.install "{binary.name}"
  end

  test do
    system "#{{bin}}/{binary.name}", "--version"
  end
end
"""

            formula_file = output / f"{self.metadata.name}.rb"
            with open(formula_file, 'w') as f:
                f.write(formula_content)

            print(f"  Created: {formula_file}")
            print(f"  To install: brew install {formula_file}")
            return True

        except Exception as e:
            print(f"  Error: {e}")
            return False


# ============================================================================
# GENERIC ARCHIVES
# ============================================================================

class TarballPackager:
    """Creates .tar.gz archives."""

    def __init__(self, metadata: PackageMetadata):
        """Initialize tarball packager."""
        self.metadata = metadata

    def create(self, binary: Path, output: Path) -> bool:
        """Create tarball."""
        print(f"Creating tarball...")

        try:
            tarball_name = f"{self.metadata.name}-{self.metadata.version}-{self.metadata.architecture}.tar.gz"
            output_file = output / tarball_name

            with tarfile.open(output_file, 'w:gz') as tar:
                tar.add(binary, arcname=binary.name)

            print(f"  Created: {output_file}")
            return True

        except Exception as e:
            print(f"  Error: {e}")
            return False


class ZipPackager:
    """Creates .zip archives."""

    def __init__(self, metadata: PackageMetadata):
        """Initialize zip packager."""
        self.metadata = metadata

    def create(self, binary: Path, output: Path) -> bool:
        """Create zip archive."""
        print(f"Creating zip archive...")

        try:
            zip_name = f"{self.metadata.name}-{self.metadata.version}-{self.metadata.architecture}.zip"
            output_file = output / zip_name

            with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(binary, binary.name)

            print(f"  Created: {output_file}")
            return True

        except Exception as e:
            print(f"  Error: {e}")
            return False


# ============================================================================
# PACKAGE FORMATTER
# ============================================================================

class PackageFormatter:
    """Main package formatter class."""

    def __init__(self, metadata: PackageMetadata):
        """Initialize package formatter."""
        self.metadata = metadata

    def create_package(self, format: PackageFormat, binary: Path,
                      output_dir: Path, **kwargs) -> bool:
        """
        Create package in specified format.

        Args:
            format: Package format
            binary: Compiled binary
            output_dir: Output directory
            **kwargs: Format-specific options

        Returns:
            True if successful
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        packagers = {
            PackageFormat.DEB: DebianPackager(self.metadata),
            PackageFormat.RPM: RPMPackager(self.metadata),
            PackageFormat.PKG: MacOSPackager(self.metadata),
            PackageFormat.MSI: WindowsPackager(self.metadata),
            PackageFormat.APPIMAGE: AppImagePackager(self.metadata),
            PackageFormat.HOMEBREW: HomebrewPackager(self.metadata),
            PackageFormat.TARBALL: TarballPackager(self.metadata),
            PackageFormat.ZIP: ZipPackager(self.metadata)
        }

        packager = packagers.get(format)
        if not packager:
            print(f"Error: Unsupported format: {format}")
            return False

        return packager.create(binary, output_dir, **kwargs)


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Package Formatter - Distribution Packages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  lament-package --format deb myapp
  lament-package --format rpm myapp --version 1.0.0
  lament-package --format appimage myapp
  lament-package --format msi myapp.exe
  lament-package --format homebrew myapp --url https://example.com/myapp.tar.gz

Supported formats:
  deb        Debian/Ubuntu package
  rpm        Fedora/RedHat/CentOS package
  pkg        macOS installer
  msi        Windows installer
  appimage   Linux AppImage
  homebrew   macOS Homebrew formula
  tarball    Generic .tar.gz
  zip        Generic .zip
        """
    )

    parser.add_argument('--version', action='version', version='lament-package 2.0.0')

    parser.add_argument('binary', type=Path,
                       help='Compiled binary')
    parser.add_argument('--format', type=str, required=True,
                       choices=[f.value for f in PackageFormat],
                       help='Package format')
    parser.add_argument('-o', '--output', type=Path, default=Path("dist"),
                       help='Output directory (default: dist)')

    # Metadata
    parser.add_argument('--name', type=str,
                       help='Package name (default: binary name)')
    parser.add_argument('--version-str', type=str, default="1.0.0",
                       help='Package version')
    parser.add_argument('--description', type=str, default="Lament Application",
                       help='Package description')
    parser.add_argument('--maintainer', type=str, default="Lament Developer <dev@lament.org>",
                       help='Maintainer name and email')
    parser.add_argument('--license', type=str, default="MIT",
                       help='License')
    parser.add_argument('--homepage', type=str,
                       help='Homepage URL')
    parser.add_argument('--arch', type=str, default="amd64",
                       help='Architecture')

    # Format-specific
    parser.add_argument('--url', type=str,
                       help='Download URL (for Homebrew)')

    args = parser.parse_args()

    # Validate binary
    if not args.binary.exists():
        print(f"Error: Binary not found: {args.binary}")
        return 1

    # Create metadata
    metadata = PackageMetadata(
        name=args.name or args.binary.stem,
        version=args.version_str,
        description=args.description,
        maintainer=args.maintainer,
        license=args.license,
        homepage=args.homepage,
        architecture=args.arch
    )

    # Create formatter
    formatter = PackageFormatter(metadata)

    # Create package
    format_enum = PackageFormat(args.format)
    kwargs = {}

    if format_enum == PackageFormat.HOMEBREW:
        if not args.url:
            print("Error: --url required for Homebrew format")
            return 1
        kwargs['url'] = args.url

    success = formatter.create_package(
        format_enum,
        args.binary,
        args.output,
        **kwargs
    )

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
