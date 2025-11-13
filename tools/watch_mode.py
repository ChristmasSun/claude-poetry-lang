#!/usr/bin/env python3
"""
Lament Watch Mode - Auto-rebuild on File Changes

A file watching system that automatically rebuilds when source files change.
Features debouncing, smart detection, live reload support, and terminal UI.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from enum import Enum
import fnmatch
import hashlib

# Try to import watchdog, fallback to polling if not available
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileSystemEvent
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. Using polling mode.")
    print("Install with: pip install watchdog")


# ============================================================================
# FILE CHANGE EVENT
# ============================================================================

class ChangeType(Enum):
    """Type of file change."""
    CREATED = "created"
    MODIFIED = "modified"
    DELETED = "deleted"
    MOVED = "moved"


@dataclass
class FileChangeEvent:
    """Represents a file change event."""
    path: Path
    change_type: ChangeType
    timestamp: float = field(default_factory=time.time)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.change_type.value}: {self.path.name}"


# ============================================================================
# DEBOUNCER
# ============================================================================

class Debouncer:
    """Debounces rapid file changes to avoid rebuilding too frequently."""

    def __init__(self, delay: float = 0.5):
        """
        Initialize debouncer.

        Args:
            delay: Delay in seconds before triggering callback
        """
        self.delay = delay
        self.timer: Optional[threading.Timer] = None
        self.pending_events: List[FileChangeEvent] = []
        self.lock = threading.Lock()
        self.callback: Optional[Callable] = None

    def trigger(self, event: FileChangeEvent, callback: Callable) -> None:
        """
        Trigger debouncer with a new event.

        Args:
            event: File change event
            callback: Callback to execute after delay
        """
        with self.lock:
            self.pending_events.append(event)
            self.callback = callback

            # Cancel existing timer
            if self.timer:
                self.timer.cancel()

            # Start new timer
            self.timer = threading.Timer(self.delay, self._execute)
            self.timer.start()

    def _execute(self) -> None:
        """Execute the callback with pending events."""
        with self.lock:
            if self.callback and self.pending_events:
                events = self.pending_events.copy()
                self.pending_events.clear()
                # Execute outside lock
                threading.Thread(
                    target=self.callback,
                    args=(events,),
                    daemon=True
                ).start()

    def cancel(self) -> None:
        """Cancel pending debounced execution."""
        with self.lock:
            if self.timer:
                self.timer.cancel()
                self.timer = None
            self.pending_events.clear()


# ============================================================================
# FILE WATCHER (Watchdog-based)
# ============================================================================

if WATCHDOG_AVAILABLE:
    class LamentFileSystemEventHandler(FileSystemEventHandler):
        """Custom file system event handler for Lament files."""

        def __init__(self, watcher: 'FileWatcher'):
            """Initialize handler."""
            super().__init__()
            self.watcher = watcher

        def on_created(self, event: FileSystemEvent) -> None:
            """Handle file creation."""
            if not event.is_directory:
                path = Path(event.src_path)
                if self.watcher.should_watch(path):
                    self.watcher.handle_change(
                        FileChangeEvent(path, ChangeType.CREATED)
                    )

        def on_modified(self, event: FileSystemEvent) -> None:
            """Handle file modification."""
            if not event.is_directory:
                path = Path(event.src_path)
                if self.watcher.should_watch(path):
                    self.watcher.handle_change(
                        FileChangeEvent(path, ChangeType.MODIFIED)
                    )

        def on_deleted(self, event: FileSystemEvent) -> None:
            """Handle file deletion."""
            if not event.is_directory:
                path = Path(event.src_path)
                if self.watcher.should_watch(path):
                    self.watcher.handle_change(
                        FileChangeEvent(path, ChangeType.DELETED)
                    )

        def on_moved(self, event: FileSystemEvent) -> None:
            """Handle file move."""
            if not event.is_directory:
                path = Path(event.dest_path)
                if self.watcher.should_watch(path):
                    self.watcher.handle_change(
                        FileChangeEvent(path, ChangeType.MOVED)
                    )


# ============================================================================
# POLLING FILE WATCHER (Fallback)
# ============================================================================

class PollingWatcher:
    """Fallback file watcher using polling."""

    def __init__(self, directories: List[Path], callback: Callable):
        """Initialize polling watcher."""
        self.directories = directories
        self.callback = callback
        self.file_mtimes: Dict[Path, float] = {}
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.poll_interval = 1.0  # seconds

    def start(self) -> None:
        """Start polling."""
        self.running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop polling."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=2.0)

    def _poll_loop(self) -> None:
        """Main polling loop."""
        while self.running:
            self._check_changes()
            time.sleep(self.poll_interval)

    def _check_changes(self) -> None:
        """Check for file changes."""
        current_files = {}

        # Scan all directories
        for directory in self.directories:
            if not directory.exists():
                continue

            for path in directory.rglob('*'):
                if path.is_file():
                    try:
                        mtime = path.stat().st_mtime
                        current_files[path] = mtime
                    except OSError:
                        pass

        # Detect changes
        for path, mtime in current_files.items():
            if path not in self.file_mtimes:
                # New file
                self.callback(FileChangeEvent(path, ChangeType.CREATED))
            elif mtime > self.file_mtimes[path]:
                # Modified file
                self.callback(FileChangeEvent(path, ChangeType.MODIFIED))

        # Detect deletions
        for path in self.file_mtimes:
            if path not in current_files:
                self.callback(FileChangeEvent(path, ChangeType.DELETED))

        self.file_mtimes = current_files


# ============================================================================
# FILE WATCHER
# ============================================================================

class FileWatcher:
    """Watches source files and triggers rebuilds on changes."""

    def __init__(self,
                 directories: List[Path],
                 patterns: List[str] = None,
                 exclude_patterns: List[str] = None,
                 debounce_delay: float = 0.5):
        """
        Initialize file watcher.

        Args:
            directories: Directories to watch
            patterns: File patterns to watch (e.g., "*.lament")
            exclude_patterns: Patterns to exclude
            debounce_delay: Delay before triggering rebuild
        """
        self.directories = directories
        self.patterns = patterns or ["*.lament"]
        self.exclude_patterns = exclude_patterns or ["**/test_*.lament", "**/__pycache__/**"]
        self.debouncer = Debouncer(delay=debounce_delay)
        self.callbacks: List[Callable] = []
        self.observer: Optional[Any] = None
        self.polling_watcher: Optional[PollingWatcher] = None
        self.running = False
        self.change_count = 0
        self.last_rebuild_time: Optional[float] = None
        self.file_checksums: Dict[Path, str] = {}

    def should_watch(self, path: Path) -> bool:
        """
        Check if a file should be watched.

        Args:
            path: File path to check

        Returns:
            True if file should be watched
        """
        # Check exclude patterns
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(str(path), pattern) or path.match(pattern):
                return False

        # Check include patterns
        for pattern in self.patterns:
            if fnmatch.fnmatch(path.name, pattern) or path.match(pattern):
                return True

        return False

    def register_callback(self, callback: Callable[[List[FileChangeEvent]], None]) -> None:
        """
        Register a callback for file changes.

        Args:
            callback: Function to call with list of change events
        """
        self.callbacks.append(callback)

    def handle_change(self, event: FileChangeEvent) -> None:
        """
        Handle a file change event.

        Args:
            event: File change event
        """
        # Check if file actually changed (avoid duplicate events)
        if event.change_type == ChangeType.MODIFIED:
            if not self._file_actually_changed(event.path):
                return

        self.change_count += 1

        # Trigger callbacks through debouncer
        def trigger_callbacks(events: List[FileChangeEvent]) -> None:
            for callback in self.callbacks:
                try:
                    callback(events)
                except Exception as e:
                    print(f"Error in change callback: {e}")

        self.debouncer.trigger(event, trigger_callbacks)

    def _file_actually_changed(self, path: Path) -> bool:
        """
        Check if file content actually changed (not just touched).

        Args:
            path: File path

        Returns:
            True if content changed
        """
        try:
            with open(path, 'rb') as f:
                content = f.read()
            checksum = hashlib.sha256(content).hexdigest()

            if path in self.file_checksums:
                if self.file_checksums[path] == checksum:
                    return False

            self.file_checksums[path] = checksum
            return True

        except Exception:
            return True  # Assume changed if we can't read

    def start(self) -> None:
        """Start watching for file changes."""
        if self.running:
            return

        self.running = True
        print(f"Starting file watcher for {len(self.directories)} directory(ies)...")

        if WATCHDOG_AVAILABLE:
            self._start_watchdog()
        else:
            self._start_polling()

        print("File watcher started. Waiting for changes...")

    def _start_watchdog(self) -> None:
        """Start watchdog-based file watcher."""
        self.observer = Observer()
        event_handler = LamentFileSystemEventHandler(self)

        for directory in self.directories:
            if directory.exists():
                self.observer.schedule(event_handler, str(directory), recursive=True)
                print(f"  Watching: {directory}")

        self.observer.start()

    def _start_polling(self) -> None:
        """Start polling-based file watcher."""
        self.polling_watcher = PollingWatcher(
            self.directories,
            self.handle_change
        )
        self.polling_watcher.start()

    def stop(self) -> None:
        """Stop watching for file changes."""
        if not self.running:
            return

        print("\nStopping file watcher...")
        self.running = False
        self.debouncer.cancel()

        if WATCHDOG_AVAILABLE and self.observer:
            self.observer.stop()
            self.observer.join()
        elif self.polling_watcher:
            self.polling_watcher.stop()

    def get_stats(self) -> Dict[str, Any]:
        """Get watcher statistics."""
        return {
            'running': self.running,
            'directories': len(self.directories),
            'changes_detected': self.change_count,
            'last_rebuild': self.last_rebuild_time,
            'mode': 'watchdog' if WATCHDOG_AVAILABLE else 'polling'
        }


# ============================================================================
# BUILD COORDINATOR
# ============================================================================

class BuildCoordinator:
    """Coordinates rebuilds when files change."""

    def __init__(self, build_system: Any):
        """
        Initialize build coordinator.

        Args:
            build_system: BuildSystem instance
        """
        self.build_system = build_system
        self.is_building = False
        self.build_queue: List[List[FileChangeEvent]] = []
        self.build_lock = threading.Lock()
        self.total_builds = 0
        self.successful_builds = 0
        self.failed_builds = 0

    def handle_changes(self, events: List[FileChangeEvent]) -> None:
        """
        Handle file change events.

        Args:
            events: List of file change events
        """
        print(f"\n{'='*60}")
        print(f"Detected {len(events)} file change(s):")
        for event in events:
            print(f"  {event}")

        # Queue build
        with self.build_lock:
            if self.is_building:
                print("Build already in progress, queueing...")
                self.build_queue.append(events)
                return

            self.is_building = True

        # Execute build
        self._execute_build(events)

        # Process queue
        while True:
            with self.build_lock:
                if not self.build_queue:
                    self.is_building = False
                    break
                next_events = self.build_queue.pop(0)

            self._execute_build(next_events)

    def _execute_build(self, events: List[FileChangeEvent]) -> None:
        """
        Execute a build.

        Args:
            events: File change events that triggered this build
        """
        print(f"\n{'-'*60}")
        print(f"Rebuilding at {datetime.now().strftime('%H:%M:%S')}...")
        print(f"{'-'*60}")

        start_time = time.time()
        self.total_builds += 1

        try:
            # Determine affected files
            affected_files = self._determine_affected_files(events)

            if affected_files:
                print(f"Rebuilding {len(affected_files)} affected file(s)...")
                # Perform incremental build
                success = self.build_system.build(incremental=True, clean=False)
            else:
                # Full rebuild
                success = self.build_system.build(incremental=True, clean=False)

            duration = time.time() - start_time

            if success:
                self.successful_builds += 1
                print(f"\n✓ Build succeeded in {duration:.2f}s")
            else:
                self.failed_builds += 1
                print(f"\n✗ Build failed in {duration:.2f}s")

        except Exception as e:
            self.failed_builds += 1
            print(f"\n✗ Build error: {e}")
            import traceback
            traceback.print_exc()

    def _determine_affected_files(self, events: List[FileChangeEvent]) -> Set[Path]:
        """
        Determine which files are affected by the changes.

        Args:
            events: File change events

        Returns:
            Set of affected file paths
        """
        affected = set()

        for event in events:
            if event.change_type != ChangeType.DELETED:
                affected.add(event.path)

                # TODO: Add dependency analysis to find dependents
                # For now, just rebuild the changed files

        return affected

    def get_stats(self) -> Dict[str, Any]:
        """Get build coordinator statistics."""
        return {
            'total_builds': self.total_builds,
            'successful_builds': self.successful_builds,
            'failed_builds': self.failed_builds,
            'is_building': self.is_building,
            'queued_builds': len(self.build_queue)
        }


# ============================================================================
# WATCH MODE
# ============================================================================

class WatchMode:
    """Main watch mode orchestrator."""

    def __init__(self, build_system: Any, debounce_delay: float = 0.5):
        """
        Initialize watch mode.

        Args:
            build_system: BuildSystem instance
            debounce_delay: Delay before triggering rebuild
        """
        self.build_system = build_system
        self.watcher: Optional[FileWatcher] = None
        self.coordinator: Optional[BuildCoordinator] = None
        self.running = False
        self.start_time: Optional[float] = None
        self.debounce_delay = debounce_delay

    def start(self) -> None:
        """Start watch mode."""
        if self.running:
            return

        print("="*60)
        print("Lament Watch Mode - Auto-rebuild on Changes")
        print("="*60)

        # Initial build
        print("\nPerforming initial build...")
        if not self.build_system.build(incremental=True, clean=False):
            print("\nInitial build failed. Fix errors and watch mode will auto-rebuild.")

        # Setup watcher
        directories = self.build_system.config.source_dirs
        self.watcher = FileWatcher(
            directories=directories,
            patterns=self.build_system.config.include_patterns,
            exclude_patterns=self.build_system.config.exclude_patterns,
            debounce_delay=self.debounce_delay
        )

        # Setup coordinator
        self.coordinator = BuildCoordinator(self.build_system)
        self.watcher.register_callback(self.coordinator.handle_changes)

        # Start watching
        self.watcher.start()
        self.running = True
        self.start_time = time.time()

        # Wait for changes
        try:
            self._run_loop()
        except KeyboardInterrupt:
            print("\n\nReceived interrupt signal...")
        finally:
            self.stop()

    def _run_loop(self) -> None:
        """Main watch loop."""
        print("\nPress Ctrl+C to stop watching\n")

        while self.running:
            time.sleep(1.0)

            # Periodically show stats
            if int(time.time()) % 30 == 0:
                self._show_stats()

    def _show_stats(self) -> None:
        """Show watch mode statistics."""
        if not self.coordinator or not self.watcher:
            return

        watcher_stats = self.watcher.get_stats()
        coordinator_stats = self.coordinator.get_stats()
        elapsed = time.time() - self.start_time if self.start_time else 0

        print(f"\n--- Watch Mode Stats (running {elapsed/60:.1f} min) ---")
        print(f"  Changes detected: {watcher_stats['changes_detected']}")
        print(f"  Total builds: {coordinator_stats['total_builds']}")
        print(f"  Successful: {coordinator_stats['successful_builds']}")
        print(f"  Failed: {coordinator_stats['failed_builds']}")

    def stop(self) -> None:
        """Stop watch mode."""
        if not self.running:
            return

        self.running = False

        if self.watcher:
            self.watcher.stop()

        # Show final stats
        print("\n" + "="*60)
        print("Watch Mode Summary")
        print("="*60)
        self._show_stats()
        print("\nWatch mode stopped.")


# ============================================================================
# CLI
# ============================================================================

def main():
    """CLI entry point for watch mode."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Lament Watch Mode - Auto-rebuild on Changes",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--debounce', type=float, default=0.5,
                       help='Debounce delay in seconds (default: 0.5)')
    parser.add_argument('--project-dir', type=Path, default=None,
                       help='Project directory (default: current directory)')

    args = parser.parse_args()

    # Import build system
    sys.path.insert(0, str(Path(__file__).parent))
    from builder import BuildSystem

    # Create build system
    build_system = BuildSystem(project_dir=args.project_dir)

    # Start watch mode
    watch_mode = WatchMode(build_system, debounce_delay=args.debounce)
    watch_mode.start()


if __name__ == '__main__':
    main()
