#!/usr/bin/env python3
"""
Lament Tool Bootstrapper

This module provides a minimal bootstrap system for executing Lament tools
written in the Lament language itself. Instead of maintaining duplicate Python
implementations, we use this lightweight wrapper to load the Lament runtime
and execute .lament tool files.

Architecture:
    Python Wrapper (15 lines) -> bootstrap_tool.py (200 lines) -> .lament tool

This reduces ~20,000+ lines of Python code to ~600 lines total.

Usage:
    from bootstrap_tool import run_lament_tool
    run_lament_tool('formatter.lament', sys.argv[1:])

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import List, Optional, Dict, Any
import json


class ToolBootstrapper:
    """
    Generic bootstrapper for Lament tools.

    Responsibilities:
    - Locate Lament runtime/interpreter
    - Load and execute .lament tool files
    - Pass command-line arguments
    - Handle exit codes
    - Redirect stdout/stderr properly
    - Provide error messages if runtime not found
    """

    def __init__(self, tool_name: str):
        """
        Initialize the bootstrapper.

        Args:
            tool_name: Name of the .lament tool file (e.g., 'formatter.lament')
        """
        self.tool_name = tool_name
        self.repo_root = self._find_repo_root()
        self.tools_lament_dir = self.repo_root / 'tools_lament'
        self.tool_path = self.tools_lament_dir / tool_name

    def _find_repo_root(self) -> Path:
        """
        Find the repository root directory.

        Searches upward from the current file location for the root.

        Returns:
            Path to repository root
        """
        current = Path(__file__).resolve().parent

        # Go up one level from tools/ to repo root
        if current.name == 'tools':
            return current.parent

        # Search upward for .git directory or known marker files
        while current != current.parent:
            if (current / '.git').exists():
                return current
            if (current / 'lament.py').exists():
                return current
            current = current.parent

        # Default to parent of tools directory
        return Path(__file__).resolve().parent.parent

    def _find_lament_interpreter(self) -> Optional[Path]:
        """
        Locate the Lament interpreter.

        Search order:
        1. LAMENT_INTERPRETER environment variable
        2. lament.py in repo root
        3. lament in PATH
        4. python -m lament

        Returns:
            Path to interpreter or None if not found
        """
        # Check environment variable
        if 'LAMENT_INTERPRETER' in os.environ:
            interp = Path(os.environ['LAMENT_INTERPRETER'])
            if interp.exists():
                return interp

        # Check repo root for lament.py
        lament_py = self.repo_root / 'lament.py'
        if lament_py.exists():
            return lament_py

        # Check for lament in PATH
        try:
            result = subprocess.run(
                ['which', 'lament'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return Path(result.stdout.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        # Try python -m lament (if installed as module)
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'lament', '--version'],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                return 'python-m-lament'  # Special marker
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def _check_tool_exists(self) -> bool:
        """
        Check if the .lament tool file exists.

        Returns:
            True if tool file exists, False otherwise
        """
        return self.tool_path.exists()

    def _build_command(self, interpreter: Path, args: List[str]) -> List[str]:
        """
        Build the command to execute the Lament tool.

        Args:
            interpreter: Path to Lament interpreter
            args: Command-line arguments to pass to tool

        Returns:
            Command as list of strings
        """
        if interpreter == 'python-m-lament':
            # Use python -m lament
            cmd = [sys.executable, '-m', 'lament', str(self.tool_path)]
        elif str(interpreter).endswith('.py'):
            # Execute Python interpreter
            cmd = [sys.executable, str(interpreter), str(self.tool_path)]
        else:
            # Direct executable
            cmd = [str(interpreter), str(self.tool_path)]

        # Add tool arguments
        cmd.extend(args)

        return cmd

    def run(self, args: List[str]) -> int:
        """
        Execute the Lament tool.

        Args:
            args: Command-line arguments to pass to tool

        Returns:
            Exit code from tool (0 for success, non-zero for error)
        """
        # Check if tool file exists
        if not self._check_tool_exists():
            print(f"Error: Tool file not found: {self.tool_path}", file=sys.stderr)
            print(f"Expected location: {self.tools_lament_dir}", file=sys.stderr)
            print(f"\nThe Lament tool implementation may not exist yet.", file=sys.stderr)
            print(f"This is a bootstrap wrapper that executes .lament tools.", file=sys.stderr)
            return 127  # Command not found

        # Find interpreter
        interpreter = self._find_lament_interpreter()
        if interpreter is None:
            print("Error: Lament interpreter not found", file=sys.stderr)
            print("", file=sys.stderr)
            print("Tried:", file=sys.stderr)
            print("  1. LAMENT_INTERPRETER environment variable", file=sys.stderr)
            print(f"  2. {self.repo_root / 'lament.py'}", file=sys.stderr)
            print("  3. 'lament' in PATH", file=sys.stderr)
            print("  4. python -m lament", file=sys.stderr)
            print("", file=sys.stderr)
            print("Please ensure Lament is installed or set LAMENT_INTERPRETER.", file=sys.stderr)
            return 127

        # Build command
        cmd = self._build_command(interpreter, args)

        # Execute tool
        try:
            result = subprocess.run(
                cmd,
                # Don't capture - let stdout/stderr flow through naturally
                stdin=sys.stdin,
                stdout=sys.stdout,
                stderr=sys.stderr,
                cwd=os.getcwd()  # Use current working directory
            )
            return result.returncode

        except FileNotFoundError:
            print(f"Error: Could not execute: {' '.join(cmd)}", file=sys.stderr)
            return 127

        except KeyboardInterrupt:
            print("\nInterrupted", file=sys.stderr)
            return 130  # Standard exit code for SIGINT

        except Exception as e:
            print(f"Error executing tool: {e}", file=sys.stderr)
            return 1


def run_lament_tool(tool_name: str, args: List[str]) -> int:
    """
    Convenience function to run a Lament tool.

    This is the main entry point used by tool wrappers.

    Args:
        tool_name: Name of the .lament tool file (e.g., 'formatter.lament')
        args: Command-line arguments to pass to tool

    Returns:
        Exit code from tool

    Example:
        #!/usr/bin/env python3
        import sys
        from bootstrap_tool import run_lament_tool
        sys.exit(run_lament_tool('formatter.lament', sys.argv[1:]))
    """
    bootstrapper = ToolBootstrapper(tool_name)
    return bootstrapper.run(args)


def main():
    """
    Test/debug entry point.

    Usage: python bootstrap_tool.py <tool.lament> [args...]
    """
    if len(sys.argv) < 2:
        print("Usage: python bootstrap_tool.py <tool.lament> [args...]", file=sys.stderr)
        print("", file=sys.stderr)
        print("This is a generic bootstrapper for Lament tools.", file=sys.stderr)
        print("Tool wrappers should use run_lament_tool() instead.", file=sys.stderr)
        return 1

    tool_name = sys.argv[1]
    tool_args = sys.argv[2:]

    return run_lament_tool(tool_name, tool_args)


if __name__ == '__main__':
    sys.exit(main())
