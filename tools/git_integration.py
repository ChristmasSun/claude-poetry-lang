#!/usr/bin/env python3
"""
Lament Git Integration - Version Control for the Soul

Comprehensive git integration for Lament packages including auto-commit,
version tagging, changelog generation, hooks, and release automation.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
import urllib.request
import urllib.error
import urllib.parse


# ============================================================================
# GIT UTILITIES
# ============================================================================

class GitError(Exception):
    """Git operation error."""
    pass


class GitRepo:
    """Wrapper for git repository operations."""

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize git repository wrapper."""
        self.repo_path = repo_path or Path.cwd()
        if not self._is_git_repo():
            raise GitError(f"Not a git repository: {self.repo_path}")

    def _is_git_repo(self) -> bool:
        """Check if directory is a git repository."""
        try:
            self._run_git(['rev-parse', '--git-dir'])
            return True
        except GitError:
            return False

    def _run_git(self, args: List[str], check: bool = True) -> str:
        """Run git command and return output."""
        try:
            result = subprocess.run(
                ['git'] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise GitError(f"Git command failed: {e.stderr}")

    def init(self) -> None:
        """Initialize a new git repository."""
        self._run_git(['init'])

    def add(self, files: List[str]) -> None:
        """Add files to staging area."""
        self._run_git(['add'] + files)

    def commit(self, message: str, author: Optional[str] = None) -> str:
        """Create a commit and return the commit hash."""
        args = ['commit', '-m', message]
        if author:
            args.extend(['--author', author])
        self._run_git(args)
        return self.get_current_commit()

    def tag(self, tag_name: str, message: Optional[str] = None, annotated: bool = True) -> None:
        """Create a tag."""
        if annotated and message:
            self._run_git(['tag', '-a', tag_name, '-m', message])
        else:
            self._run_git(['tag', tag_name])

    def get_tags(self) -> List[str]:
        """Get all tags."""
        output = self._run_git(['tag', '--list'])
        return [t for t in output.split('\n') if t]

    def get_current_branch(self) -> str:
        """Get current branch name."""
        return self._run_git(['rev-parse', '--abbrev-ref', 'HEAD'])

    def get_current_commit(self) -> str:
        """Get current commit hash."""
        return self._run_git(['rev-parse', 'HEAD'])

    def get_remote_url(self, remote: str = 'origin') -> Optional[str]:
        """Get remote URL."""
        try:
            return self._run_git(['remote', 'get-url', remote])
        except GitError:
            return None

    def push(self, remote: str = 'origin', branch: Optional[str] = None, tags: bool = False) -> None:
        """Push commits to remote."""
        args = ['push', remote]
        if branch:
            args.append(branch)
        if tags:
            args.append('--tags')
        self._run_git(args)

    def get_commits(self, since: Optional[str] = None, until: Optional[str] = None,
                    count: Optional[int] = None) -> List[Dict[str, str]]:
        """Get commit history."""
        args = ['log', '--pretty=format:%H|%an|%ae|%at|%s|%b']

        if since and until:
            args.append(f'{since}..{until}')
        elif since:
            args.append(f'{since}..HEAD')

        if count:
            args.extend(['-n', str(count)])

        output = self._run_git(args)
        if not output:
            return []

        commits = []
        for line in output.split('\n'):
            if not line:
                continue
            parts = line.split('|', 5)
            if len(parts) >= 5:
                commits.append({
                    'hash': parts[0],
                    'author': parts[1],
                    'email': parts[2],
                    'timestamp': parts[3],
                    'subject': parts[4],
                    'body': parts[5] if len(parts) > 5 else ''
                })

        return commits

    def get_status(self) -> Dict[str, List[str]]:
        """Get repository status."""
        output = self._run_git(['status', '--porcelain'])

        status = {
            'modified': [],
            'added': [],
            'deleted': [],
            'untracked': []
        }

        for line in output.split('\n'):
            if not line:
                continue

            state = line[:2]
            filename = line[3:]

            if state.strip() == '??':
                status['untracked'].append(filename)
            elif 'M' in state:
                status['modified'].append(filename)
            elif 'A' in state:
                status['added'].append(filename)
            elif 'D' in state:
                status['deleted'].append(filename)

        return status

    def has_changes(self) -> bool:
        """Check if repository has uncommitted changes."""
        status = self.get_status()
        return any(status.values())

    def create_branch(self, branch_name: str, checkout: bool = True) -> None:
        """Create a new branch."""
        args = ['branch', branch_name]
        self._run_git(args)
        if checkout:
            self._run_git(['checkout', branch_name])

    def checkout(self, branch: str) -> None:
        """Checkout a branch."""
        self._run_git(['checkout', branch])

    def merge(self, branch: str, message: Optional[str] = None) -> None:
        """Merge a branch."""
        args = ['merge', branch]
        if message:
            args.extend(['-m', message])
        self._run_git(args)


# ============================================================================
# CHANGELOG GENERATION
# ============================================================================

@dataclass
class ChangelogEntry:
    """Represents a changelog entry."""
    type: str  # feat, fix, docs, chore, etc.
    scope: Optional[str]
    description: str
    breaking: bool = False
    commit_hash: str = ""
    author: str = ""

    @staticmethod
    def from_commit(commit: Dict[str, str]) -> Optional['ChangelogEntry']:
        """Parse a changelog entry from a commit message."""
        subject = commit['subject']

        # Parse conventional commit format: type(scope): description
        pattern = r'^(\w+)(?:\(([^)]+)\))?: (.+)$'
        match = re.match(pattern, subject)

        if match:
            type_str, scope, description = match.groups()
            breaking = 'BREAKING CHANGE' in commit.get('body', '')

            return ChangelogEntry(
                type=type_str,
                scope=scope,
                description=description,
                breaking=breaking,
                commit_hash=commit['hash'][:8],
                author=commit['author']
            )

        # Fallback: treat as misc change
        return ChangelogEntry(
            type='misc',
            scope=None,
            description=subject,
            commit_hash=commit['hash'][:8],
            author=commit['author']
        )


class ChangelogGenerator:
    """Generates changelogs from git commits."""

    def __init__(self, repo: GitRepo):
        """Initialize changelog generator."""
        self.repo = repo

    def generate(self, since: Optional[str] = None, until: Optional[str] = None,
                version: Optional[str] = None) -> str:
        """Generate changelog content."""
        commits = self.repo.get_commits(since=since, until=until)

        if not commits:
            return "No changes"

        # Parse changelog entries
        entries = []
        for commit in commits:
            entry = ChangelogEntry.from_commit(commit)
            if entry:
                entries.append(entry)

        # Group by type
        groups = {
            'breaking': [],
            'feat': [],
            'fix': [],
            'docs': [],
            'perf': [],
            'refactor': [],
            'test': [],
            'chore': [],
            'misc': []
        }

        for entry in entries:
            if entry.breaking:
                groups['breaking'].append(entry)
            elif entry.type in groups:
                groups[entry.type].append(entry)
            else:
                groups['misc'].append(entry)

        # Format changelog
        lines = []

        if version:
            lines.append(f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}")
        else:
            lines.append(f"## Changes - {datetime.now().strftime('%Y-%m-%d')}")

        lines.append("")

        # Breaking changes first
        if groups['breaking']:
            lines.append("### BREAKING CHANGES")
            lines.append("")
            for entry in groups['breaking']:
                scope_str = f"**{entry.scope}**: " if entry.scope else ""
                lines.append(f"- {scope_str}{entry.description} ({entry.commit_hash})")
            lines.append("")

        # Features
        if groups['feat']:
            lines.append("### Features")
            lines.append("")
            for entry in groups['feat']:
                scope_str = f"**{entry.scope}**: " if entry.scope else ""
                lines.append(f"- {scope_str}{entry.description} ({entry.commit_hash})")
            lines.append("")

        # Bug fixes
        if groups['fix']:
            lines.append("### Bug Fixes")
            lines.append("")
            for entry in groups['fix']:
                scope_str = f"**{entry.scope}**: " if entry.scope else ""
                lines.append(f"- {scope_str}{entry.description} ({entry.commit_hash})")
            lines.append("")

        # Performance improvements
        if groups['perf']:
            lines.append("### Performance Improvements")
            lines.append("")
            for entry in groups['perf']:
                scope_str = f"**{entry.scope}**: " if entry.scope else ""
                lines.append(f"- {scope_str}{entry.description} ({entry.commit_hash})")
            lines.append("")

        # Documentation
        if groups['docs']:
            lines.append("### Documentation")
            lines.append("")
            for entry in groups['docs']:
                lines.append(f"- {entry.description} ({entry.commit_hash})")
            lines.append("")

        # Miscellaneous
        other_changes = groups['refactor'] + groups['test'] + groups['chore'] + groups['misc']
        if other_changes:
            lines.append("### Other Changes")
            lines.append("")
            for entry in other_changes:
                lines.append(f"- {entry.description} ({entry.commit_hash})")
            lines.append("")

        return '\n'.join(lines)

    def update_changelog_file(self, content: str, filepath: Path) -> None:
        """Update CHANGELOG.md file with new content."""
        if filepath.exists():
            with open(filepath, 'r') as f:
                existing = f.read()

            # Insert new content after title
            if existing.startswith('# Changelog'):
                lines = existing.split('\n')
                new_content = '\n'.join(lines[:2]) + '\n\n' + content + '\n' + '\n'.join(lines[2:])
            else:
                new_content = content + '\n\n' + existing
        else:
            new_content = "# Changelog\n\n" + content

        with open(filepath, 'w') as f:
            f.write(new_content)


# ============================================================================
# GIT HOOKS
# ============================================================================

class GitHooks:
    """Manages git hooks for Lament projects."""

    HOOK_TEMPLATES = {
        'pre-commit': '''#!/bin/bash
# Lament pre-commit hook

echo "Running Lament pre-commit checks..."

# Run linter
if command -v lament-lint &> /dev/null; then
    lament-lint --check || exit 1
fi

# Run formatter check
if command -v lament-fmt &> /dev/null; then
    lament-fmt --check || exit 1
fi

# Run tests
if command -v lament test &> /dev/null; then
    lament test || exit 1
fi

echo "All pre-commit checks passed!"
''',

        'pre-push': '''#!/bin/bash
# Lament pre-push hook

echo "Running Lament pre-push checks..."

# Run security audit
if command -v lament-audit &> /dev/null; then
    lament-audit || exit 1
fi

# Verify package signatures
if command -v lament-sign &> /dev/null; then
    lament-sign verify || exit 1
fi

echo "All pre-push checks passed!"
''',

        'commit-msg': '''#!/bin/bash
# Lament commit message hook

commit_msg_file=$1
commit_msg=$(cat "$commit_msg_file")

# Check for conventional commit format
if ! echo "$commit_msg" | grep -qE "^(feat|fix|docs|style|refactor|perf|test|chore)(\(.+\))?: .+"; then
    echo "Error: Commit message must follow conventional commit format"
    echo "Format: type(scope): description"
    echo "Types: feat, fix, docs, style, refactor, perf, test, chore"
    exit 1
fi

echo "Commit message format valid!"
'''
    }

    def __init__(self, repo: GitRepo):
        """Initialize git hooks manager."""
        self.repo = repo
        self.hooks_dir = repo.repo_path / '.git' / 'hooks'

    def install_hook(self, hook_name: str) -> None:
        """Install a git hook."""
        if hook_name not in self.HOOK_TEMPLATES:
            raise ValueError(f"Unknown hook: {hook_name}")

        hook_path = self.hooks_dir / hook_name

        with open(hook_path, 'w') as f:
            f.write(self.HOOK_TEMPLATES[hook_name])

        # Make executable
        os.chmod(hook_path, 0o755)

        print(f"Installed {hook_name} hook")

    def uninstall_hook(self, hook_name: str) -> None:
        """Uninstall a git hook."""
        hook_path = self.hooks_dir / hook_name
        if hook_path.exists():
            hook_path.unlink()
            print(f"Uninstalled {hook_name} hook")

    def install_all(self) -> None:
        """Install all Lament git hooks."""
        for hook_name in self.HOOK_TEMPLATES:
            self.install_hook(hook_name)


# ============================================================================
# GITHUB/GITLAB API INTEGRATION
# ============================================================================

class GitHubAPI:
    """GitHub API client."""

    def __init__(self, token: Optional[str] = None):
        """Initialize GitHub API client."""
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.api_base = 'https://api.github.com'

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request."""
        url = f"{self.api_base}{endpoint}"

        headers = {
            'Accept': 'application/vnd.github.v3+json'
        }

        if self.token:
            headers['Authorization'] = f'token {self.token}'

        if data:
            data_bytes = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        else:
            req = urllib.request.Request(url, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise GitError(f"GitHub API error: {e.code} {e.reason}")

    def create_release(self, owner: str, repo: str, tag: str, name: str,
                      body: str, draft: bool = False, prerelease: bool = False) -> Dict:
        """Create a GitHub release."""
        data = {
            'tag_name': tag,
            'name': name,
            'body': body,
            'draft': draft,
            'prerelease': prerelease
        }

        return self._request('POST', f'/repos/{owner}/{repo}/releases', data)

    def get_releases(self, owner: str, repo: str) -> List[Dict]:
        """Get repository releases."""
        return self._request('GET', f'/repos/{owner}/{repo}/releases')


class GitLabAPI:
    """GitLab API client."""

    def __init__(self, token: Optional[str] = None, instance: str = 'https://gitlab.com'):
        """Initialize GitLab API client."""
        self.token = token or os.getenv('GITLAB_TOKEN')
        self.api_base = f'{instance}/api/v4'

    def _request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict:
        """Make API request."""
        url = f"{self.api_base}{endpoint}"

        headers = {}
        if self.token:
            headers['PRIVATE-TOKEN'] = self.token

        if data:
            data_bytes = json.dumps(data).encode('utf-8')
            headers['Content-Type'] = 'application/json'
            req = urllib.request.Request(url, data=data_bytes, headers=headers, method=method)
        else:
            req = urllib.request.Request(url, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            raise GitError(f"GitLab API error: {e.code} {e.reason}")

    def create_release(self, project_id: str, tag: str, name: str, description: str) -> Dict:
        """Create a GitLab release."""
        data = {
            'tag_name': tag,
            'name': name,
            'description': description
        }

        return self._request('POST', f'/projects/{project_id}/releases', data)


# ============================================================================
# GIT INTEGRATION
# ============================================================================

class GitIntegration:
    """Main git integration class for Lament."""

    def __init__(self, repo_path: Optional[Path] = None):
        """Initialize git integration."""
        self.repo_path = repo_path or Path.cwd()

        try:
            self.repo = GitRepo(self.repo_path)
        except GitError:
            self.repo = None

    def init_repository(self) -> None:
        """Initialize a new git repository."""
        if self.repo:
            print(f"Repository already initialized at {self.repo_path}")
            return

        self.repo = GitRepo(self.repo_path)
        self.repo.init()

        # Create .gitignore
        gitignore_path = self.repo_path / '.gitignore'
        if not gitignore_path.exists():
            with open(gitignore_path, 'w') as f:
                f.write(self._default_gitignore())

        print(f"Initialized git repository at {self.repo_path}")

    def _default_gitignore(self) -> str:
        """Get default .gitignore content for Lament projects."""
        return """# Lament
.lament/
*.lament.cache
package-lock.lament

# Build artifacts
dist/
build/
*.tar.gz

# Python
__pycache__/
*.py[cod]
*.so
.Python
venv/
env/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
"""

    def auto_commit(self, version: str, package_name: str) -> str:
        """Auto-commit changes for a package publish."""
        if not self.repo:
            raise GitError("Not a git repository")

        if not self.repo.has_changes():
            print("No changes to commit")
            return self.repo.get_current_commit()

        # Stage all changes
        self.repo.add(['.'])

        # Create commit
        message = f"chore(release): publish {package_name} v{version}"
        commit_hash = self.repo.commit(message)

        print(f"Created commit: {commit_hash[:8]}")
        return commit_hash

    def create_version_tag(self, version: str, changelog: Optional[str] = None) -> None:
        """Create a version tag."""
        if not self.repo:
            raise GitError("Not a git repository")

        tag_name = f"v{version}"

        # Check if tag exists
        if tag_name in self.repo.get_tags():
            print(f"Tag {tag_name} already exists")
            return

        # Create annotated tag
        message = changelog or f"Release version {version}"
        self.repo.tag(tag_name, message=message)

        print(f"Created tag: {tag_name}")

    def generate_changelog(self, since_tag: Optional[str] = None,
                          version: Optional[str] = None) -> str:
        """Generate changelog from commits."""
        if not self.repo:
            raise GitError("Not a git repository")

        generator = ChangelogGenerator(self.repo)

        # If no since_tag, use latest tag
        if not since_tag:
            tags = self.repo.get_tags()
            if tags:
                since_tag = tags[-1]

        changelog = generator.generate(since=since_tag, version=version)

        # Update CHANGELOG.md
        changelog_file = self.repo_path / 'CHANGELOG.md'
        generator.update_changelog_file(changelog, changelog_file)

        print(f"Updated {changelog_file}")
        return changelog

    def install_hooks(self) -> None:
        """Install git hooks."""
        if not self.repo:
            raise GitError("Not a git repository")

        hooks = GitHooks(self.repo)
        hooks.install_all()

    def create_release(self, version: str, changelog: str, push: bool = True) -> None:
        """Create a release (commit, tag, push)."""
        if not self.repo:
            raise GitError("Not a git repository")

        # Load package metadata
        from tools.package_manager import PackageMetadata
        package_file = self.repo_path / 'package.lament'

        if not package_file.exists():
            raise GitError("No package.lament found")

        metadata = PackageMetadata.from_file(package_file)

        # Auto-commit changes
        commit_hash = self.auto_commit(version, metadata.name)

        # Create tag
        self.create_version_tag(version, changelog)

        # Push if requested
        if push:
            remote_url = self.repo.get_remote_url()
            if remote_url:
                print(f"Pushing to {remote_url}...")
                self.repo.push(tags=True)
                print("Push successful!")
            else:
                print("Warning: No remote configured, skipping push")

        print(f"\nRelease {version} created successfully!")
        print(f"Commit: {commit_hash[:8]}")
        print(f"Tag: v{version}")

    def publish_github_release(self, version: str, changelog: str) -> None:
        """Publish release to GitHub."""
        if not self.repo:
            raise GitError("Not a git repository")

        # Parse repository info from remote URL
        remote_url = self.repo.get_remote_url()
        if not remote_url:
            raise GitError("No remote repository configured")

        # Parse owner/repo from URL
        match = re.search(r'github\.com[:/]([^/]+)/(.+?)(?:\.git)?$', remote_url)
        if not match:
            raise GitError("Not a GitHub repository")

        owner, repo_name = match.groups()

        # Create release
        api = GitHubAPI()
        tag = f"v{version}"

        release = api.create_release(
            owner=owner,
            repo=repo_name,
            tag=tag,
            name=f"Release {version}",
            body=changelog
        )

        print(f"Published release to GitHub: {release['html_url']}")


# ============================================================================
# CLI
# ============================================================================

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lament Git Integration - Version Control for the Soul",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Init command
    subparsers.add_parser('init', help='Initialize git repository')

    # Tag command
    tag_parser = subparsers.add_parser('tag', help='Create version tag')
    tag_parser.add_argument('version', help='Version to tag')
    tag_parser.add_argument('--message', '-m', help='Tag message')

    # Changelog command
    changelog_parser = subparsers.add_parser('changelog', help='Generate changelog')
    changelog_parser.add_argument('--since', help='Since tag/commit')
    changelog_parser.add_argument('--version', help='Version for changelog')

    # Release command
    release_parser = subparsers.add_parser('release', help='Create release')
    release_parser.add_argument('version', help='Version to release')
    release_parser.add_argument('--no-push', action='store_true', help='Skip push to remote')
    release_parser.add_argument('--github', action='store_true', help='Publish to GitHub')

    # Hooks command
    hooks_parser = subparsers.add_parser('hooks', help='Manage git hooks')
    hooks_parser.add_argument('action', choices=['install', 'uninstall'], help='Action')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        git = GitIntegration()

        if args.command == 'init':
            git.init_repository()

        elif args.command == 'tag':
            git.create_version_tag(args.version, args.message)

        elif args.command == 'changelog':
            changelog = git.generate_changelog(
                since_tag=args.since,
                version=args.version
            )
            print("\nGenerated changelog:")
            print(changelog)

        elif args.command == 'release':
            # Generate changelog
            changelog = git.generate_changelog(version=args.version)

            # Create release
            git.create_release(
                version=args.version,
                changelog=changelog,
                push=not args.no_push
            )

            # Publish to GitHub if requested
            if args.github:
                git.publish_github_release(args.version, changelog)

        elif args.command == 'hooks':
            if args.action == 'install':
                git.install_hooks()
            else:
                hooks = GitHooks(git.repo)
                for hook in GitHooks.HOOK_TEMPLATES:
                    hooks.uninstall_hook(hook)

    except GitError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
