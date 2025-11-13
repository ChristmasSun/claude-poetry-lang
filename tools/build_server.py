#!/usr/bin/env python3
"""
Lament Build Server - Background Build Daemon

A background build server with HTTP API and WebSocket support for live updates.
Manages build queue, concurrent builds, and notifications.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import os
import sys
import json
import time
import threading
import queue
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Set, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import uuid
import signal

# Try to import web frameworks
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Warning: Flask not installed. HTTP API disabled.")
    print("Install with: pip install flask flask-cors")

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False
    print("Warning: websockets not installed. WebSocket support disabled.")
    print("Install with: pip install websockets")


# ============================================================================
# BUILD REQUEST
# ============================================================================

class BuildStatus(Enum):
    """Build status."""
    QUEUED = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BuildRequest:
    """Represents a build request."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    project_dir: Path = field(default_factory=Path.cwd)
    clean: bool = False
    incremental: bool = True
    parallel: bool = False
    num_jobs: Optional[int] = None
    requested_at: float = field(default_factory=time.time)
    priority: int = 0  # Higher priority = build first

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'project_dir': str(self.project_dir),
            'clean': self.clean,
            'incremental': self.incremental,
            'parallel': self.parallel,
            'num_jobs': self.num_jobs,
            'requested_at': self.requested_at,
            'priority': self.priority
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'BuildRequest':
        """Create from dictionary."""
        return BuildRequest(
            id=data.get('id', str(uuid.uuid4())),
            project_dir=Path(data.get('project_dir', Path.cwd())),
            clean=data.get('clean', False),
            incremental=data.get('incremental', True),
            parallel=data.get('parallel', False),
            num_jobs=data.get('num_jobs'),
            requested_at=data.get('requested_at', time.time()),
            priority=data.get('priority', 0)
        )


@dataclass
class BuildResult:
    """Represents a build result."""
    request_id: str
    status: BuildStatus
    started_at: Optional[float] = None
    finished_at: Optional[float] = None
    duration: Optional[float] = None
    message: str = ""
    logs: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'request_id': self.request_id,
            'status': self.status.value,
            'started_at': self.started_at,
            'finished_at': self.finished_at,
            'duration': self.duration,
            'message': self.message,
            'logs': self.logs,
            'errors': self.errors
        }


# ============================================================================
# BUILD QUEUE
# ============================================================================

class BuildQueue:
    """Thread-safe priority queue for build requests."""

    def __init__(self):
        """Initialize build queue."""
        self.queue: queue.PriorityQueue = queue.PriorityQueue()
        self.active_builds: Dict[str, BuildRequest] = {}
        self.completed_builds: Dict[str, BuildResult] = {}
        self.lock = threading.Lock()
        self.max_history = 100  # Keep last 100 builds

    def enqueue(self, request: BuildRequest) -> None:
        """
        Add a build request to the queue.

        Args:
            request: Build request
        """
        # Priority queue uses (priority, item) tuples
        # Negate priority so higher priority comes first
        self.queue.put((-request.priority, request.id, request))

        # Create initial result
        result = BuildResult(
            request_id=request.id,
            status=BuildStatus.QUEUED
        )

        with self.lock:
            self.completed_builds[request.id] = result

    def dequeue(self, timeout: Optional[float] = None) -> Optional[BuildRequest]:
        """
        Get next build request from queue.

        Args:
            timeout: Timeout in seconds

        Returns:
            Build request or None
        """
        try:
            _, _, request = self.queue.get(timeout=timeout)
            with self.lock:
                self.active_builds[request.id] = request
            return request
        except queue.Empty:
            return None

    def mark_started(self, request_id: str) -> None:
        """Mark a build as started."""
        with self.lock:
            if request_id in self.completed_builds:
                self.completed_builds[request_id].status = BuildStatus.RUNNING
                self.completed_builds[request_id].started_at = time.time()

    def mark_completed(self, result: BuildResult) -> None:
        """Mark a build as completed."""
        with self.lock:
            # Remove from active
            if result.request_id in self.active_builds:
                del self.active_builds[result.request_id]

            # Store result
            self.completed_builds[result.request_id] = result

            # Trim history
            if len(self.completed_builds) > self.max_history:
                oldest = sorted(
                    self.completed_builds.keys(),
                    key=lambda k: self.completed_builds[k].finished_at or 0
                )[0]
                del self.completed_builds[oldest]

    def get_result(self, request_id: str) -> Optional[BuildResult]:
        """Get build result by request ID."""
        with self.lock:
            return self.completed_builds.get(request_id)

    def get_active_builds(self) -> List[BuildRequest]:
        """Get list of active builds."""
        with self.lock:
            return list(self.active_builds.values())

    def get_recent_builds(self, limit: int = 10) -> List[BuildResult]:
        """Get recent build results."""
        with self.lock:
            results = sorted(
                self.completed_builds.values(),
                key=lambda r: r.finished_at or r.started_at or 0,
                reverse=True
            )
            return results[:limit]

    def cancel_build(self, request_id: str) -> bool:
        """
        Cancel a build.

        Args:
            request_id: Build request ID

        Returns:
            True if cancelled
        """
        # Note: Can only cancel queued builds, not running ones
        with self.lock:
            if request_id in self.completed_builds:
                result = self.completed_builds[request_id]
                if result.status == BuildStatus.QUEUED:
                    result.status = BuildStatus.CANCELLED
                    result.finished_at = time.time()
                    return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """Get queue statistics."""
        with self.lock:
            total = len(self.completed_builds)
            success = sum(1 for r in self.completed_builds.values()
                         if r.status == BuildStatus.SUCCESS)
            failed = sum(1 for r in self.completed_builds.values()
                        if r.status == BuildStatus.FAILED)

            return {
                'queued': self.queue.qsize(),
                'active': len(self.active_builds),
                'total_builds': total,
                'successful': success,
                'failed': failed,
                'success_rate': (success / total * 100) if total > 0 else 0
            }


# ============================================================================
# BUILD WORKER
# ============================================================================

class BuildWorker:
    """Worker thread that processes build requests."""

    def __init__(self, worker_id: int, build_queue: BuildQueue,
                 notification_callback: Optional[Any] = None):
        """
        Initialize build worker.

        Args:
            worker_id: Worker identifier
            build_queue: Build queue
            notification_callback: Callback for notifications
        """
        self.worker_id = worker_id
        self.build_queue = build_queue
        self.notification_callback = notification_callback
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.current_build: Optional[BuildRequest] = None

    def start(self) -> None:
        """Start worker thread."""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._work_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """Stop worker thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)

    def _work_loop(self) -> None:
        """Main worker loop."""
        print(f"Build worker {self.worker_id} started")

        while self.running:
            # Get next build request
            request = self.build_queue.dequeue(timeout=1.0)
            if not request:
                continue

            self.current_build = request
            self._execute_build(request)
            self.current_build = None

        print(f"Build worker {self.worker_id} stopped")

    def _execute_build(self, request: BuildRequest) -> None:
        """
        Execute a build request.

        Args:
            request: Build request
        """
        print(f"Worker {self.worker_id}: Building {request.project_dir}")

        # Mark as started
        self.build_queue.mark_started(request.id)
        start_time = time.time()

        # Create result
        result = BuildResult(
            request_id=request.id,
            status=BuildStatus.RUNNING,
            started_at=start_time
        )

        # Notify start
        self._notify('build_started', request.to_dict())

        try:
            # Import build system
            sys.path.insert(0, str(Path(__file__).parent))
            from builder import BuildSystem

            # Create build system
            build_system = BuildSystem(project_dir=request.project_dir)

            # Execute build
            if request.parallel:
                success = self._execute_parallel_build(
                    build_system, request, result
                )
            else:
                success = build_system.build(
                    incremental=request.incremental,
                    clean=request.clean
                )

            # Update result
            result.status = BuildStatus.SUCCESS if success else BuildStatus.FAILED
            result.message = "Build succeeded" if success else "Build failed"

        except Exception as e:
            result.status = BuildStatus.FAILED
            result.message = f"Build error: {e}"
            result.errors.append(str(e))
            import traceback
            result.errors.append(traceback.format_exc())

        finally:
            # Finish result
            result.finished_at = time.time()
            result.duration = result.finished_at - start_time

            # Mark as completed
            self.build_queue.mark_completed(result)

            # Notify completion
            self._notify('build_completed', result.to_dict())

            print(f"Worker {self.worker_id}: Build {result.status.value} "
                  f"in {result.duration:.2f}s")

    def _execute_parallel_build(self, build_system: Any,
                                request: BuildRequest,
                                result: BuildResult) -> bool:
        """Execute parallel build."""
        from parallel_builder import ParallelCompiler

        # Discover sources
        source_files = build_system.discover_sources()

        # Create parallel compiler
        compiler = ParallelCompiler(
            build_system.config,
            num_jobs=request.num_jobs
        )

        # Compile
        success, compile_results = compiler.compile_parallel(
            source_files,
            build_system.config.output_dir
        )

        # Store logs
        for compile_result in compile_results:
            result.logs.append(compile_result.message)
            if not compile_result.success:
                result.errors.append(compile_result.message)

        return success

    def _notify(self, event: str, data: Any) -> None:
        """Send notification."""
        if self.notification_callback:
            try:
                self.notification_callback(event, data)
            except Exception as e:
                print(f"Error sending notification: {e}")


# ============================================================================
# BUILD SERVER
# ============================================================================

class BuildServer:
    """Main build server orchestrator."""

    def __init__(self, num_workers: int = 2, host: str = 'localhost',
                 port: int = 8765):
        """
        Initialize build server.

        Args:
            num_workers: Number of worker threads
            num_workers: Number of concurrent build workers
            host: Server host
            port: Server port
        """
        self.num_workers = num_workers
        self.host = host
        self.port = port
        self.build_queue = BuildQueue()
        self.workers: List[BuildWorker] = []
        self.running = False
        self.start_time: Optional[float] = None
        self.websocket_clients: Set[Any] = set()
        self.app: Optional[Flask] = None

    def start(self) -> None:
        """Start build server."""
        if self.running:
            return

        print("="*60)
        print("Lament Build Server")
        print("="*60)
        print(f"Host: {self.host}:{self.port}")
        print(f"Workers: {self.num_workers}")
        print("="*60)

        self.running = True
        self.start_time = time.time()

        # Start workers
        for i in range(self.num_workers):
            worker = BuildWorker(
                i,
                self.build_queue,
                notification_callback=self._broadcast_notification
            )
            worker.start()
            self.workers.append(worker)

        # Start HTTP server (if Flask available)
        if FLASK_AVAILABLE:
            self._start_http_server()
        else:
            print("\nFlask not available. HTTP API disabled.")
            print("Install with: pip install flask flask-cors")

        # Keep running
        try:
            self._run_loop()
        except KeyboardInterrupt:
            print("\n\nReceived interrupt signal...")
        finally:
            self.stop()

    def _start_http_server(self) -> None:
        """Start HTTP API server."""
        self.app = Flask(__name__)
        CORS(self.app)

        # Routes
        @self.app.route('/health', methods=['GET'])
        def health():
            """Health check endpoint."""
            return jsonify({'status': 'healthy', 'uptime': time.time() - self.start_time})

        @self.app.route('/stats', methods=['GET'])
        def stats():
            """Get server statistics."""
            return jsonify(self.build_queue.get_stats())

        @self.app.route('/build', methods=['POST'])
        def build():
            """Submit a build request."""
            data = request.get_json()
            build_request = BuildRequest.from_dict(data)
            self.build_queue.enqueue(build_request)
            return jsonify({
                'request_id': build_request.id,
                'status': 'queued'
            })

        @self.app.route('/build/<request_id>', methods=['GET'])
        def get_build(request_id):
            """Get build result."""
            result = self.build_queue.get_result(request_id)
            if result:
                return jsonify(result.to_dict())
            return jsonify({'error': 'Build not found'}), 404

        @self.app.route('/build/<request_id>', methods=['DELETE'])
        def cancel_build(request_id):
            """Cancel a build."""
            if self.build_queue.cancel_build(request_id):
                return jsonify({'status': 'cancelled'})
            return jsonify({'error': 'Cannot cancel build'}), 400

        @self.app.route('/builds/recent', methods=['GET'])
        def recent_builds():
            """Get recent builds."""
            limit = request.args.get('limit', 10, type=int)
            builds = self.build_queue.get_recent_builds(limit)
            return jsonify([b.to_dict() for b in builds])

        @self.app.route('/builds/active', methods=['GET'])
        def active_builds():
            """Get active builds."""
            builds = self.build_queue.get_active_builds()
            return jsonify([b.to_dict() for b in builds])

        # Start server in thread
        def run_flask():
            self.app.run(host=self.host, port=self.port, threaded=True, debug=False)

        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

        print(f"\nHTTP API running on http://{self.host}:{self.port}")
        print(f"  Health: http://{self.host}:{self.port}/health")
        print(f"  Stats: http://{self.host}:{self.port}/stats")

    def _broadcast_notification(self, event: str, data: Any) -> None:
        """Broadcast notification to WebSocket clients."""
        if not WEBSOCKETS_AVAILABLE:
            return

        notification = {
            'event': event,
            'data': data,
            'timestamp': time.time()
        }

        # This is simplified - in production you'd use async WebSocket handling
        print(f"Notification: {event}")

    def _run_loop(self) -> None:
        """Main server loop."""
        print("\nServer ready. Press Ctrl+C to stop.\n")

        while self.running:
            time.sleep(1.0)

            # Periodically show stats
            if int(time.time()) % 60 == 0:
                self._show_stats()

    def _show_stats(self) -> None:
        """Show server statistics."""
        stats = self.build_queue.get_stats()
        uptime = time.time() - self.start_time if self.start_time else 0

        print(f"\n--- Server Stats (uptime {uptime/60:.1f} min) ---")
        print(f"  Queued: {stats['queued']}")
        print(f"  Active: {stats['active']}")
        print(f"  Total: {stats['total_builds']}")
        print(f"  Success rate: {stats['success_rate']:.1f}%")

    def stop(self) -> None:
        """Stop build server."""
        if not self.running:
            return

        print("\nStopping build server...")
        self.running = False

        # Stop workers
        for worker in self.workers:
            worker.stop()

        # Show final stats
        print("\n" + "="*60)
        print("Build Server Summary")
        print("="*60)
        self._show_stats()
        print("\nServer stopped.")


# ============================================================================
# CLI
# ============================================================================

def main():
    """CLI entry point for build server."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Lament Build Server - Background Build Daemon",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Start command
    start_parser = subparsers.add_parser('start', help='Start build server')
    start_parser.add_argument('--workers', type=int, default=2,
                             help='Number of worker threads (default: 2)')
    start_parser.add_argument('--host', type=str, default='localhost',
                             help='Server host (default: localhost)')
    start_parser.add_argument('--port', type=int, default=8765,
                             help='Server port (default: 8765)')

    # Status command
    subparsers.add_parser('status', help='Get server status')

    # Build command
    build_parser = subparsers.add_parser('build', help='Submit build request')
    build_parser.add_argument('--project-dir', type=Path, default=Path.cwd(),
                             help='Project directory')
    build_parser.add_argument('--clean', action='store_true',
                             help='Clean before building')
    build_parser.add_argument('--parallel', action='store_true',
                             help='Use parallel compilation')
    build_parser.add_argument('--jobs', type=int, default=None,
                             help='Number of parallel jobs')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    if args.command == 'start':
        # Start server
        server = BuildServer(
            num_workers=args.workers,
            host=args.host,
            port=args.port
        )
        server.start()

    elif args.command == 'status':
        # Query server status
        if FLASK_AVAILABLE:
            import requests
            try:
                response = requests.get('http://localhost:8765/stats')
                print(json.dumps(response.json(), indent=2))
            except Exception as e:
                print(f"Error querying server: {e}")
        else:
            print("Flask not available for status queries")

    elif args.command == 'build':
        # Submit build request
        if FLASK_AVAILABLE:
            import requests
            request_data = {
                'project_dir': str(args.project_dir),
                'clean': args.clean,
                'parallel': args.parallel,
                'num_jobs': args.jobs
            }
            try:
                response = requests.post('http://localhost:8765/build',
                                        json=request_data)
                result = response.json()
                print(f"Build queued: {result['request_id']}")
                print(f"Status: {result['status']}")
            except Exception as e:
                print(f"Error submitting build: {e}")
        else:
            print("Flask not available for build submissions")


if __name__ == '__main__':
    main()
