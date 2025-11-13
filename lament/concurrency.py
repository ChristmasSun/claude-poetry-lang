"""
Lament Concurrency Module - Advanced Concurrent Programming Primitives

This module provides state-of-the-art concurrency primitives for Lament:
1. Actor Model - Message-passing concurrency with supervision
2. Software Transactional Memory (STM) - Lock-free transactions
3. Channels - Go-style communication primitives
4. Work-Stealing Scheduler - Efficient task distribution
5. Async Streams - Asynchronous iteration with backpressure

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import asyncio
import threading
import queue
import time
import weakref
from abc import ABC, abstractmethod
from collections import deque
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable, Optional, List, Dict, Set, Tuple, Generic, TypeVar
from concurrent.futures import ThreadPoolExecutor
import random
import inspect

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================

T = TypeVar('T')
R = TypeVar('R')
Message = Any


# ============================================================================
# ACTOR MODEL
# ============================================================================

class ActorState(Enum):
    """Actor lifecycle states"""
    CREATED = auto()
    RUNNING = auto()
    SUSPENDED = auto()
    STOPPING = auto()
    STOPPED = auto()
    FAILED = auto()
    RESTARTING = auto()


class SupervisionStrategy(Enum):
    """Supervision strategies for failed actors"""
    RESTART = auto()          # Restart the failed actor
    RESUME = auto()           # Resume the actor, ignoring the failure
    STOP = auto()             # Stop the actor
    ESCALATE = auto()         # Escalate to parent supervisor


@dataclass
class RestartPolicy:
    """Policy for restarting failed actors"""
    strategy: SupervisionStrategy = SupervisionStrategy.RESTART
    max_retries: int = 3
    within_seconds: float = 10.0
    backoff_multiplier: float = 2.0
    initial_delay: float = 0.1


class ActorMailbox:
    """Thread-safe mailbox for actor messages"""

    def __init__(self, capacity: Optional[int] = None):
        self.capacity = capacity
        if capacity:
            self._queue: queue.Queue = queue.Queue(maxsize=capacity)
        else:
            self._queue: queue.Queue = queue.Queue()
        self._priority_queue: queue.PriorityQueue = queue.PriorityQueue()
        self._lock = threading.Lock()

    def put(self, message: Message, priority: Optional[int] = None):
        """Add message to mailbox"""
        if priority is not None:
            self._priority_queue.put((priority, time.time(), message))
        else:
            self._queue.put(message)

    def get(self, timeout: Optional[float] = None) -> Message:
        """Get message from mailbox"""
        # Check priority queue first
        try:
            if not self._priority_queue.empty():
                _, _, message = self._priority_queue.get_nowait()
                return message
        except queue.Empty:
            pass

        return self._queue.get(timeout=timeout)

    def get_nowait(self) -> Message:
        """Get message without blocking"""
        try:
            if not self._priority_queue.empty():
                _, _, message = self._priority_queue.get_nowait()
                return message
        except queue.Empty:
            pass

        return self._queue.get_nowait()

    def qsize(self) -> int:
        """Get mailbox size"""
        return self._queue.qsize() + self._priority_queue.qsize()

    def empty(self) -> bool:
        """Check if mailbox is empty"""
        return self._queue.empty() and self._priority_queue.empty()


class Actor:
    """Base Actor class for message-passing concurrency"""

    _next_id = 0
    _id_lock = threading.Lock()

    def __init__(self, name: Optional[str] = None, mailbox_capacity: Optional[int] = None):
        with Actor._id_lock:
            self.actor_id = Actor._next_id
            Actor._next_id += 1

        self.name = name or f"Actor-{self.actor_id}"
        self.mailbox = ActorMailbox(capacity=mailbox_capacity)
        self.state = ActorState.CREATED
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._supervisor: Optional['ActorSupervisor'] = None
        self._restart_count = 0
        self._restart_times: List[float] = []
        self._children: Set['Actor'] = set()
        self._lock = threading.Lock()

    def receive(self, message: Message):
        """Override this method to handle messages"""
        pass

    def pre_start(self):
        """Called before actor starts"""
        pass

    def post_stop(self):
        """Called after actor stops"""
        pass

    def pre_restart(self, reason: Exception):
        """Called before actor restarts"""
        pass

    def post_restart(self, reason: Exception):
        """Called after actor restarts"""
        pass

    def _run(self):
        """Internal message processing loop"""
        self.state = ActorState.RUNNING
        self.pre_start()

        try:
            while not self._stop_event.is_set():
                try:
                    message = self.mailbox.get(timeout=0.1)

                    # Handle system messages
                    if isinstance(message, _StopMessage):
                        break
                    elif isinstance(message, _SuspendMessage):
                        self.state = ActorState.SUSPENDED
                        continue
                    elif isinstance(message, _ResumeMessage):
                        self.state = ActorState.RUNNING
                        continue

                    # Handle user messages
                    self.receive(message)

                except queue.Empty:
                    continue
                except Exception as e:
                    self.state = ActorState.FAILED
                    if self._supervisor:
                        self._supervisor._handle_failure(self, e)
                    else:
                        raise

        except Exception as e:
            self.state = ActorState.FAILED
            if self._supervisor:
                self._supervisor._handle_failure(self, e)
            else:
                raise
        finally:
            self.state = ActorState.STOPPED
            self.post_stop()

    def start(self) -> 'Actor':
        """Start the actor"""
        if self.state != ActorState.CREATED and self.state != ActorState.STOPPED:
            raise RuntimeError(f"Actor {self.name} already started")

        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, name=self.name, daemon=True)
        self._thread.start()
        return self

    def stop(self):
        """Stop the actor"""
        self.state = ActorState.STOPPING
        self.mailbox.put(_StopMessage())
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5.0)

    def send(self, message: Message, priority: Optional[int] = None):
        """Send message to this actor"""
        if self.state in (ActorState.STOPPED, ActorState.STOPPING):
            raise RuntimeError(f"Cannot send to stopped actor {self.name}")
        self.mailbox.put(message, priority)

    def __repr__(self):
        return f"Actor(id={self.actor_id}, name='{self.name}', state={self.state.name})"


# System messages
@dataclass
class _StopMessage:
    pass

@dataclass
class _SuspendMessage:
    pass

@dataclass
class _ResumeMessage:
    pass


class ActorSupervisor:
    """Supervisor for managing actor lifecycles"""

    def __init__(self, restart_policy: Optional[RestartPolicy] = None):
        self.restart_policy = restart_policy or RestartPolicy()
        self._supervised: Dict[int, Actor] = {}
        self._lock = threading.Lock()

    def supervise(self, actor: Actor) -> Actor:
        """Add actor to supervision"""
        with self._lock:
            actor._supervisor = self
            self._supervised[actor.actor_id] = actor
        return actor

    def _handle_failure(self, actor: Actor, error: Exception):
        """Handle actor failure based on restart policy"""
        strategy = self.restart_policy.strategy

        if strategy == SupervisionStrategy.RESUME:
            actor.state = ActorState.RUNNING
            return

        elif strategy == SupervisionStrategy.STOP:
            actor.stop()
            return

        elif strategy == SupervisionStrategy.RESTART:
            # Check restart limits
            now = time.time()
            actor._restart_times.append(now)

            # Remove old restart times outside the window
            cutoff = now - self.restart_policy.within_seconds
            actor._restart_times = [t for t in actor._restart_times if t > cutoff]

            if len(actor._restart_times) > self.restart_policy.max_retries:
                actor.stop()
                raise RuntimeError(
                    f"Actor {actor.name} exceeded max restarts "
                    f"({self.restart_policy.max_retries})"
                )

            # Restart with backoff
            delay = (self.restart_policy.initial_delay *
                    (self.restart_policy.backoff_multiplier ** actor._restart_count))
            time.sleep(delay)

            actor.pre_restart(error)
            actor._restart_count += 1
            actor.state = ActorState.RESTARTING
            actor.start()
            actor.post_restart(error)

        elif strategy == SupervisionStrategy.ESCALATE:
            raise error


def spawn_actor(actor_class: type, *args, **kwargs) -> Actor:
    """Spawn a new actor and start it"""
    actor = actor_class(*args, **kwargs)
    actor.start()
    return actor


def send_message(actor: Actor, message: Message, priority: Optional[int] = None):
    """Send a message to an actor"""
    actor.send(message, priority)


# ============================================================================
# SOFTWARE TRANSACTIONAL MEMORY (STM)
# ============================================================================

class TransactionState(Enum):
    """Transaction states"""
    ACTIVE = auto()
    COMMITTING = auto()
    COMMITTED = auto()
    ABORTED = auto()


class STMConflictError(Exception):
    """Raised when a transaction conflict occurs"""
    pass


@dataclass
class TVarVersion:
    """Versioned value for TVar"""
    value: Any
    version: int
    timestamp: float


class TVar(Generic[T]):
    """Transactional variable for STM"""

    _next_version = 0
    _version_lock = threading.Lock()

    def __init__(self, initial_value: T):
        with TVar._version_lock:
            self._version = TVar._next_version
            TVar._next_version += 1

        self._value = initial_value
        self._lock = threading.RLock()
        self._history: List[TVarVersion] = [
            TVarVersion(initial_value, self._version, time.time())
        ]
        self._max_history = 100

    def read(self, transaction: Optional['Transaction'] = None) -> T:
        """Read value (within transaction if provided)"""
        if transaction:
            return transaction._read(self)
        else:
            with self._lock:
                return self._value

    def write(self, value: T, transaction: Optional['Transaction'] = None):
        """Write value (within transaction if provided)"""
        if transaction:
            transaction._write(self, value)
        else:
            with self._lock:
                self._value = value
                with TVar._version_lock:
                    self._version = TVar._next_version
                    TVar._next_version += 1

                # Add to history
                self._history.append(
                    TVarVersion(value, self._version, time.time())
                )
                if len(self._history) > self._max_history:
                    self._history.pop(0)

    def _get_version(self) -> int:
        """Get current version"""
        with self._lock:
            return self._version

    def _commit_write(self, value: T) -> int:
        """Commit a write (internal use)"""
        with self._lock:
            self._value = value
            with TVar._version_lock:
                self._version = TVar._next_version
                TVar._next_version += 1

            self._history.append(
                TVarVersion(value, self._version, time.time())
            )
            if len(self._history) > self._max_history:
                self._history.pop(0)

            return self._version


class Transaction:
    """STM Transaction"""

    def __init__(self):
        self.state = TransactionState.ACTIVE
        self._read_set: Dict[TVar, int] = {}  # TVar -> version read
        self._write_set: Dict[TVar, Any] = {}  # TVar -> value to write
        self._lock = threading.Lock()

    def _read(self, tvar: TVar) -> Any:
        """Read TVar within transaction"""
        if self.state != TransactionState.ACTIVE:
            raise RuntimeError("Transaction is not active")

        # Check write set first
        if tvar in self._write_set:
            return self._write_set[tvar]

        # Read from TVar and record version
        with tvar._lock:
            value = tvar._value
            version = tvar._version

        self._read_set[tvar] = version
        return value

    def _write(self, tvar: TVar, value: Any):
        """Write TVar within transaction"""
        if self.state != TransactionState.ACTIVE:
            raise RuntimeError("Transaction is not active")

        self._write_set[tvar] = value

        # Also track in read set if not already
        if tvar not in self._read_set:
            self._read_set[tvar] = tvar._get_version()

    def _validate(self) -> bool:
        """Validate that no conflicts occurred"""
        for tvar, read_version in self._read_set.items():
            if tvar._get_version() != read_version:
                return False
        return True

    def _commit(self):
        """Commit the transaction"""
        with self._lock:
            if self.state != TransactionState.ACTIVE:
                raise RuntimeError("Transaction is not active")

            self.state = TransactionState.COMMITTING

            # Acquire all locks in a consistent order to prevent deadlock
            tvars = sorted(self._write_set.keys(), key=lambda t: id(t))
            locks = [tvar._lock for tvar in tvars]

            for lock in locks:
                lock.acquire()

            try:
                # Validate
                if not self._validate():
                    raise STMConflictError("Transaction conflict detected")

                # Commit writes
                for tvar, value in self._write_set.items():
                    tvar._commit_write(value)

                self.state = TransactionState.COMMITTED

            finally:
                for lock in locks:
                    lock.release()

    def _abort(self):
        """Abort the transaction"""
        self.state = TransactionState.ABORTED
        self._read_set.clear()
        self._write_set.clear()


_transaction_local = threading.local()


def atomic(func: Callable[..., R], max_retries: int = 100) -> Callable[..., R]:
    """
    Decorator for atomic transactions.

    Usage:
        @atomic
        def transfer(from_account, to_account, amount):
            balance_from = from_account.read()
            balance_to = to_account.read()
            from_account.write(balance_from - amount)
            to_account.write(balance_to + amount)
    """
    def wrapper(*args, **kwargs) -> R:
        retries = 0

        while retries < max_retries:
            transaction = Transaction()
            _transaction_local.current = transaction

            try:
                result = func(*args, **kwargs)
                transaction._commit()
                return result

            except STMConflictError:
                transaction._abort()
                retries += 1
                # Exponential backoff
                time.sleep(0.001 * (2 ** min(retries, 10)))

            finally:
                _transaction_local.current = None

        raise STMConflictError(f"Transaction failed after {max_retries} retries")

    return wrapper


def get_current_transaction() -> Optional[Transaction]:
    """Get the current transaction (if any)"""
    return getattr(_transaction_local, 'current', None)


# ============================================================================
# CHANNELS - Go-style Communication
# ============================================================================

class ChannelClosedError(Exception):
    """Raised when operating on a closed channel"""
    pass


class Channel(Generic[T]):
    """
    Go-style channel for communication between threads/coroutines.
    Supports both buffered and unbuffered channels.
    """

    def __init__(self, buffer_size: int = 0):
        self.buffer_size = buffer_size
        self._queue: queue.Queue = queue.Queue(maxsize=buffer_size if buffer_size > 0 else 1)
        self._closed = False
        self._lock = threading.Lock()
        self._send_waiters: List[threading.Condition] = []
        self._recv_waiters: List[threading.Condition] = []

    def send(self, value: T, timeout: Optional[float] = None):
        """Send value to channel"""
        with self._lock:
            if self._closed:
                raise ChannelClosedError("Cannot send on closed channel")

        try:
            self._queue.put(value, timeout=timeout)
        except queue.Full:
            raise TimeoutError("Channel send timeout")

    def receive(self, timeout: Optional[float] = None) -> T:
        """Receive value from channel"""
        try:
            value = self._queue.get(timeout=timeout)

            with self._lock:
                if value is None and self._closed:
                    raise ChannelClosedError("Channel is closed")

            return value

        except queue.Empty:
            with self._lock:
                if self._closed:
                    raise ChannelClosedError("Channel is closed")
            raise TimeoutError("Channel receive timeout")

    def try_send(self, value: T) -> bool:
        """Try to send without blocking"""
        with self._lock:
            if self._closed:
                return False

        try:
            self._queue.put_nowait(value)
            return True
        except queue.Full:
            return False

    def try_receive(self) -> Tuple[bool, Optional[T]]:
        """Try to receive without blocking"""
        try:
            value = self._queue.get_nowait()
            return True, value
        except queue.Empty:
            with self._lock:
                if self._closed:
                    return False, None
            return False, None

    def close(self):
        """Close the channel"""
        with self._lock:
            if self._closed:
                return
            self._closed = True

            # Put sentinel values to wake up receivers
            try:
                while not self._queue.full():
                    self._queue.put_nowait(None)
            except queue.Full:
                pass

    def is_closed(self) -> bool:
        """Check if channel is closed"""
        with self._lock:
            return self._closed

    def __iter__(self):
        """Iterate over channel values"""
        while True:
            try:
                value = self.receive(timeout=0.1)
                if value is None:
                    break
                yield value
            except (ChannelClosedError, TimeoutError):
                break


@dataclass
class SelectCase(Generic[T]):
    """Case for select statement"""
    channel: Channel[T]
    value: Optional[T] = None  # For send cases
    is_send: bool = False


def select(*cases: SelectCase, timeout: Optional[float] = None) -> Tuple[int, Any]:
    """
    Select over multiple channel operations.
    Returns (case_index, received_value) for receive cases,
    or (case_index, None) for send cases.
    """
    start_time = time.time()

    while True:
        # Try each case
        for i, case in enumerate(cases):
            if case.is_send:
                if case.channel.try_send(case.value):
                    return i, None
            else:
                success, value = case.channel.try_receive()
                if success:
                    return i, value

        # Check timeout
        if timeout is not None:
            elapsed = time.time() - start_time
            if elapsed >= timeout:
                raise TimeoutError("Select timeout")

        # Small sleep to avoid busy waiting
        time.sleep(0.001)


# ============================================================================
# WORK-STEALING SCHEDULER
# ============================================================================

@dataclass
class Task:
    """Task for work-stealing scheduler"""
    func: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 0
    task_id: Optional[int] = None


class WorkerThread:
    """Worker thread for work-stealing scheduler"""

    def __init__(self, worker_id: int, scheduler: 'WorkStealingScheduler'):
        self.worker_id = worker_id
        self.scheduler = scheduler
        self.queue: deque = deque()
        self.lock = threading.Lock()
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.stats = {
            'tasks_executed': 0,
            'tasks_stolen': 0,
            'steal_attempts': 0
        }

    def push_task(self, task: Task):
        """Push task to local queue"""
        with self.lock:
            self.queue.append(task)

    def pop_task(self) -> Optional[Task]:
        """Pop task from local queue"""
        with self.lock:
            if self.queue:
                return self.queue.pop()
        return None

    def steal_task(self) -> Optional[Task]:
        """Steal task from this worker (FIFO for better cache locality)"""
        with self.lock:
            if self.queue:
                return self.queue.popleft()
        return None

    def run(self):
        """Worker thread main loop"""
        while not self.stop_event.is_set():
            task = self.pop_task()

            if task is None:
                # Try to steal from other workers
                task = self._try_steal()

            if task is None:
                # No work available, sleep briefly
                time.sleep(0.001)
                continue

            # Execute task
            try:
                task.func(*task.args, **task.kwargs)
                self.stats['tasks_executed'] += 1
            except Exception as e:
                # Task failed, log it
                print(f"Task {task.task_id} failed: {e}")

    def _try_steal(self) -> Optional[Task]:
        """Try to steal task from another worker"""
        workers = self.scheduler.workers
        if len(workers) <= 1:
            return None

        # Random victim selection
        victims = [w for w in workers if w.worker_id != self.worker_id]
        random.shuffle(victims)

        for victim in victims:
            self.stats['steal_attempts'] += 1
            task = victim.steal_task()
            if task:
                self.stats['tasks_stolen'] += 1
                return task

        return None

    def start(self):
        """Start worker thread"""
        self.thread = threading.Thread(
            target=self.run,
            name=f"Worker-{self.worker_id}",
            daemon=True
        )
        self.thread.start()

    def stop(self):
        """Stop worker thread"""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=5.0)


class WorkStealingScheduler:
    """
    Work-stealing scheduler for efficient task distribution.
    Each worker has a local queue and can steal from others when idle.
    """

    def __init__(self, num_workers: Optional[int] = None):
        self.num_workers = num_workers or threading.active_count()
        self.workers: List[WorkerThread] = []
        self.next_worker = 0
        self.next_task_id = 0
        self.lock = threading.Lock()
        self._started = False

        # Initialize workers
        for i in range(self.num_workers):
            worker = WorkerThread(i, self)
            self.workers.append(worker)

    def start(self):
        """Start all worker threads"""
        if self._started:
            return

        for worker in self.workers:
            worker.start()

        self._started = True

    def stop(self):
        """Stop all worker threads"""
        for worker in self.workers:
            worker.stop()

        self._started = False

    def submit(self, func: Callable, *args, **kwargs) -> int:
        """Submit a task to the scheduler"""
        if not self._started:
            self.start()

        with self.lock:
            task_id = self.next_task_id
            self.next_task_id += 1

            # Round-robin assignment
            worker = self.workers[self.next_worker]
            self.next_worker = (self.next_worker + 1) % self.num_workers

        task = Task(func=func, args=args, kwargs=kwargs, task_id=task_id)
        worker.push_task(task)

        return task_id

    def get_stats(self) -> Dict[int, Dict]:
        """Get statistics for all workers"""
        return {
            worker.worker_id: worker.stats.copy()
            for worker in self.workers
        }

    def __enter__(self):
        """Context manager entry"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.stop()


# ============================================================================
# ASYNC STREAMS
# ============================================================================

class AsyncStream(Generic[T]):
    """
    Asynchronous stream for processing data with backpressure.
    Supports map, filter, reduce, and other functional operations.
    """

    def __init__(self, source: Optional[Callable[[], T]] = None, buffer_size: int = 10):
        self.source = source
        self.buffer_size = buffer_size
        self._buffer: asyncio.Queue = None  # Initialized on first use
        self._closed = False
        self._operators: List[Callable] = []
        self._backpressure_limit = buffer_size

    async def _ensure_buffer(self):
        """Ensure buffer is initialized"""
        if self._buffer is None:
            self._buffer = asyncio.Queue(maxsize=self.buffer_size)

    async def emit(self, value: T):
        """Emit a value to the stream"""
        await self._ensure_buffer()
        if self._closed:
            raise RuntimeError("Cannot emit to closed stream")
        await self._buffer.put(value)

    async def next(self) -> T:
        """Get next value from stream"""
        await self._ensure_buffer()
        if self._closed and self._buffer.empty():
            raise StopAsyncIteration

        try:
            value = await asyncio.wait_for(self._buffer.get(), timeout=1.0)

            # Apply operators
            for op in self._operators:
                value = op(value)
                if value is None:
                    # Filtered out, get next
                    return await self.next()

            return value

        except asyncio.TimeoutError:
            if self._closed:
                raise StopAsyncIteration
            raise

    def map(self, func: Callable[[T], R]) -> 'AsyncStream[R]':
        """Map operation on stream"""
        new_stream = AsyncStream(buffer_size=self.buffer_size)
        new_stream._operators = self._operators + [func]
        new_stream._buffer = self._buffer
        new_stream._closed = self._closed
        return new_stream

    def filter(self, predicate: Callable[[T], bool]) -> 'AsyncStream[T]':
        """Filter operation on stream"""
        def filter_op(value):
            return value if predicate(value) else None

        new_stream = AsyncStream(buffer_size=self.buffer_size)
        new_stream._operators = self._operators + [filter_op]
        new_stream._buffer = self._buffer
        new_stream._closed = self._closed
        return new_stream

    async def reduce(self, func: Callable[[R, T], R], initial: R) -> R:
        """Reduce operation on stream"""
        accumulator = initial

        try:
            while True:
                value = await self.next()
                accumulator = func(accumulator, value)
        except StopAsyncIteration:
            pass

        return accumulator

    async def collect(self) -> List[T]:
        """Collect all values into a list"""
        result = []

        try:
            while True:
                value = await self.next()
                result.append(value)
        except StopAsyncIteration:
            pass

        return result

    async def take(self, n: int) -> List[T]:
        """Take first n values"""
        result = []

        try:
            for _ in range(n):
                value = await self.next()
                result.append(value)
        except StopAsyncIteration:
            pass

        return result

    async def skip(self, n: int) -> 'AsyncStream[T]':
        """Skip first n values"""
        for _ in range(n):
            try:
                await self.next()
            except StopAsyncIteration:
                break
        return self

    def batch(self, size: int) -> 'AsyncStream[List[T]]':
        """Batch values into groups"""
        async def batch_generator():
            batch = []
            try:
                while True:
                    value = await self.next()
                    batch.append(value)

                    if len(batch) >= size:
                        yield batch
                        batch = []
            except StopAsyncIteration:
                if batch:
                    yield batch

        return AsyncStream.from_async_iterator(batch_generator())

    async def for_each(self, func: Callable[[T], None]):
        """Apply function to each value"""
        try:
            while True:
                value = await self.next()
                func(value)
        except StopAsyncIteration:
            pass

    def close(self):
        """Close the stream"""
        self._closed = True

    def is_closed(self) -> bool:
        """Check if stream is closed"""
        return self._closed

    @staticmethod
    def from_iterable(iterable: List[T], buffer_size: int = 10) -> 'AsyncStream[T]':
        """Create stream from iterable"""
        stream = AsyncStream(buffer_size=buffer_size)

        async def producer():
            await stream._ensure_buffer()
            for item in iterable:
                await stream.emit(item)
            stream.close()

        # Start producer in background
        asyncio.create_task(producer())

        return stream

    @staticmethod
    def from_async_iterator(async_iter) -> 'AsyncStream[T]':
        """Create stream from async iterator"""
        stream = AsyncStream()

        async def producer():
            await stream._ensure_buffer()
            async for item in async_iter:
                await stream.emit(item)
            stream.close()

        asyncio.create_task(producer())

        return stream

    @staticmethod
    def interval(duration: float, buffer_size: int = 10) -> 'AsyncStream[int]':
        """Create stream that emits incrementing numbers at intervals"""
        stream = AsyncStream(buffer_size=buffer_size)

        async def producer():
            await stream._ensure_buffer()
            counter = 0
            while not stream.is_closed():
                await stream.emit(counter)
                counter += 1
                await asyncio.sleep(duration)

        asyncio.create_task(producer())

        return stream

    def __aiter__(self):
        """Async iterator protocol"""
        return self

    async def __anext__(self):
        """Async iterator protocol"""
        return await self.next()


class StreamMerger:
    """Merge multiple async streams"""

    def __init__(self, *streams: AsyncStream):
        self.streams = list(streams)
        self.output = AsyncStream()

    async def merge(self) -> AsyncStream:
        """Merge all streams into one"""
        await self.output._ensure_buffer()

        async def merge_stream(stream):
            try:
                while True:
                    value = await stream.next()
                    await self.output.emit(value)
            except StopAsyncIteration:
                pass

        # Start all merge tasks
        tasks = [asyncio.create_task(merge_stream(s)) for s in self.streams]

        # Wait for all to complete
        async def wait_and_close():
            await asyncio.gather(*tasks)
            self.output.close()

        asyncio.create_task(wait_and_close())

        return self.output


class StreamZipper:
    """Zip multiple async streams"""

    def __init__(self, *streams: AsyncStream):
        self.streams = list(streams)
        self.output = AsyncStream()

    async def zip(self) -> AsyncStream[Tuple]:
        """Zip all streams into tuples"""
        await self.output._ensure_buffer()

        async def zipper():
            try:
                while True:
                    values = []
                    for stream in self.streams:
                        value = await stream.next()
                        values.append(value)
                    await self.output.emit(tuple(values))
            except StopAsyncIteration:
                self.output.close()

        asyncio.create_task(zipper())

        return self.output


# ============================================================================
# ADVANCED ACTOR PATTERNS
# ============================================================================

class RouterActor(Actor):
    """
    Router actor that distributes messages to worker actors.
    Implements round-robin load balancing.
    """

    def __init__(self, workers: List[Actor], name: Optional[str] = None):
        super().__init__(name=name or "Router")
        self.workers = workers
        self.next_worker = 0
        self._lock = threading.Lock()

    def receive(self, message: Message):
        """Route message to next worker"""
        with self._lock:
            worker = self.workers[self.next_worker]
            self.next_worker = (self.next_worker + 1) % len(self.workers)

        worker.send(message)


class BroadcastActor(Actor):
    """
    Broadcast actor that sends messages to all subscribed actors.
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name or "Broadcast")
        self.subscribers: Set[Actor] = set()
        self._lock = threading.Lock()

    def subscribe(self, actor: Actor):
        """Subscribe actor to broadcasts"""
        with self._lock:
            self.subscribers.add(actor)

    def unsubscribe(self, actor: Actor):
        """Unsubscribe actor from broadcasts"""
        with self._lock:
            self.subscribers.discard(actor)

    def receive(self, message: Message):
        """Broadcast message to all subscribers"""
        with self._lock:
            subscribers = list(self.subscribers)

        for subscriber in subscribers:
            try:
                subscriber.send(message)
            except Exception as e:
                print(f"Failed to send to {subscriber.name}: {e}")


class ActorPool:
    """
    Pool of actors for parallel message processing.
    Automatically creates and manages worker actors.
    """

    def __init__(self, actor_class: type, pool_size: int, *args, **kwargs):
        self.actor_class = actor_class
        self.pool_size = pool_size
        self.workers: List[Actor] = []
        self.router: Optional[RouterActor] = None

        # Create workers
        for i in range(pool_size):
            worker = actor_class(*args, **kwargs)
            worker.name = f"{worker.name}-{i}"
            self.workers.append(worker)

        # Create router
        self.router = RouterActor(self.workers, name="PoolRouter")

    def start(self):
        """Start all workers and router"""
        for worker in self.workers:
            worker.start()
        self.router.start()

    def stop(self):
        """Stop all workers and router"""
        self.router.stop()
        for worker in self.workers:
            worker.stop()

    def send(self, message: Message):
        """Send message to pool (will be routed to a worker)"""
        self.router.send(message)


class FutureActor(Actor):
    """
    Actor that can return future results from async operations.
    """

    def __init__(self, name: Optional[str] = None):
        super().__init__(name=name or "Future")
        self._futures: Dict[int, threading.Event] = {}
        self._results: Dict[int, Any] = {}
        self._next_future_id = 0
        self._lock = threading.Lock()

    def ask(self, message: Message, timeout: Optional[float] = None) -> Any:
        """
        Send message and wait for response.
        Returns the result or raises TimeoutError.
        """
        with self._lock:
            future_id = self._next_future_id
            self._next_future_id += 1
            event = threading.Event()
            self._futures[future_id] = event

        # Send request with future ID
        self.send((future_id, message))

        # Wait for response
        if event.wait(timeout=timeout):
            with self._lock:
                result = self._results.pop(future_id)
                del self._futures[future_id]
            return result
        else:
            with self._lock:
                del self._futures[future_id]
            raise TimeoutError("Ask timeout")

    def reply(self, future_id: int, result: Any):
        """Reply to a future request"""
        with self._lock:
            if future_id in self._futures:
                self._results[future_id] = result
                self._futures[future_id].set()


# ============================================================================
# ADVANCED STM FEATURES
# ============================================================================

def retry(transaction: Optional[Transaction] = None):
    """
    Retry transaction explicitly.
    Useful for waiting on conditions.
    """
    raise STMConflictError("Explicit retry")


def or_else(func1: Callable[[], R], func2: Callable[[], R]) -> R:
    """
    Try func1, if it retries, try func2.
    Composable choice operator for STM.
    """
    try:
        return func1()
    except STMConflictError:
        return func2()


class TMVar(Generic[T]):
    """
    Transactional MVar - a TVar that can be empty or full.
    Useful for synchronization in STM.
    """

    def __init__(self):
        self._tvar: TVar[Optional[T]] = TVar(None)
        self._is_empty = TVar(True)

    def put(self, value: T, transaction: Optional[Transaction] = None):
        """Put value (blocks if full)"""
        tx = transaction or get_current_transaction()

        if not self._is_empty.read(tx):
            retry(tx)

        self._tvar.write(value, tx)
        self._is_empty.write(False, tx)

    def take(self, transaction: Optional[Transaction] = None) -> T:
        """Take value (blocks if empty)"""
        tx = transaction or get_current_transaction()

        if self._is_empty.read(tx):
            retry(tx)

        value = self._tvar.read(tx)
        self._is_empty.write(True, tx)
        return value

    def read(self, transaction: Optional[Transaction] = None) -> T:
        """Read value without taking (blocks if empty)"""
        tx = transaction or get_current_transaction()

        if self._is_empty.read(tx):
            retry(tx)

        return self._tvar.read(tx)

    def try_put(self, value: T, transaction: Optional[Transaction] = None) -> bool:
        """Try to put value, returns False if full"""
        tx = transaction or get_current_transaction()

        if not self._is_empty.read(tx):
            return False

        self._tvar.write(value, tx)
        self._is_empty.write(False, tx)
        return True

    def try_take(self, transaction: Optional[Transaction] = None) -> Optional[T]:
        """Try to take value, returns None if empty"""
        tx = transaction or get_current_transaction()

        if self._is_empty.read(tx):
            return None

        value = self._tvar.read(tx)
        self._is_empty.write(True, tx)
        return value

    def is_empty(self, transaction: Optional[Transaction] = None) -> bool:
        """Check if TMVar is empty"""
        tx = transaction or get_current_transaction()
        return self._is_empty.read(tx)


class TArray(Generic[T]):
    """Transactional array"""

    def __init__(self, size: int, initial_value: Optional[T] = None):
        self.size = size
        self._array: List[TVar[T]] = [TVar(initial_value) for _ in range(size)]

    def read(self, index: int, transaction: Optional[Transaction] = None) -> T:
        """Read value at index"""
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} out of range [0, {self.size})")
        return self._array[index].read(transaction)

    def write(self, index: int, value: T, transaction: Optional[Transaction] = None):
        """Write value at index"""
        if not 0 <= index < self.size:
            raise IndexError(f"Index {index} out of range [0, {self.size})")
        self._array[index].write(value, transaction)

    def swap(self, i: int, j: int, transaction: Optional[Transaction] = None):
        """Swap values at two indices"""
        tx = transaction or get_current_transaction()
        val_i = self.read(i, tx)
        val_j = self.read(j, tx)
        self.write(i, val_j, tx)
        self.write(j, val_i, tx)


# ============================================================================
# ADVANCED CHANNEL PATTERNS
# ============================================================================

class BoundedChannel(Channel[T]):
    """
    Bounded channel with explicit capacity and blocking behavior.
    """

    def __init__(self, capacity: int):
        super().__init__(buffer_size=capacity)
        self.capacity = capacity

    def len(self) -> int:
        """Get current number of items in channel"""
        return self._queue.qsize()

    def cap(self) -> int:
        """Get channel capacity"""
        return self.capacity


class UnboundedChannel(Channel[T]):
    """
    Unbounded channel that never blocks on send.
    """

    def __init__(self):
        super().__init__(buffer_size=0)
        self._queue = queue.Queue(maxsize=0)  # Unbounded

    def send(self, value: T, timeout: Optional[float] = None):
        """Send value (never blocks)"""
        with self._lock:
            if self._closed:
                raise ChannelClosedError("Cannot send on closed channel")

        self._queue.put(value)


def fan_out(input_channel: Channel[T], output_channels: List[Channel[T]]):
    """
    Fan-out pattern: read from one channel, write to many.
    Broadcasts each message to all output channels.
    """
    def worker():
        try:
            for value in input_channel:
                for ch in output_channels:
                    try:
                        ch.send(value)
                    except ChannelClosedError:
                        pass
        except ChannelClosedError:
            pass
        finally:
            for ch in output_channels:
                ch.close()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    return thread


def fan_in(input_channels: List[Channel[T]], output_channel: Channel[T]):
    """
    Fan-in pattern: read from many channels, write to one.
    Merges messages from all input channels.
    """
    def worker(ch: Channel[T]):
        try:
            for value in ch:
                output_channel.send(value)
        except ChannelClosedError:
            pass

    threads = []
    for ch in input_channels:
        thread = threading.Thread(target=worker, args=(ch,), daemon=True)
        thread.start()
        threads.append(thread)

    def closer():
        for thread in threads:
            thread.join()
        output_channel.close()

    threading.Thread(target=closer, daemon=True).start()
    return threads


class PriorityChannel(Generic[T]):
    """
    Channel with priority-based message ordering.
    Lower priority numbers are delivered first.
    """

    def __init__(self, buffer_size: int = 0):
        self.buffer_size = buffer_size
        self._queue: queue.PriorityQueue = queue.PriorityQueue(
            maxsize=buffer_size if buffer_size > 0 else 0
        )
        self._closed = False
        self._lock = threading.Lock()
        self._counter = 0  # For stable sorting

    def send(self, value: T, priority: int = 0, timeout: Optional[float] = None):
        """Send value with priority"""
        with self._lock:
            if self._closed:
                raise ChannelClosedError("Cannot send on closed channel")
            counter = self._counter
            self._counter += 1

        try:
            self._queue.put((priority, counter, value), timeout=timeout)
        except queue.Full:
            raise TimeoutError("Channel send timeout")

    def receive(self, timeout: Optional[float] = None) -> T:
        """Receive value"""
        try:
            _, _, value = self._queue.get(timeout=timeout)
            with self._lock:
                if value is None and self._closed:
                    raise ChannelClosedError("Channel is closed")
            return value
        except queue.Empty:
            with self._lock:
                if self._closed:
                    raise ChannelClosedError("Channel is closed")
            raise TimeoutError("Channel receive timeout")

    def close(self):
        """Close channel"""
        with self._lock:
            if self._closed:
                return
            self._closed = True


# ============================================================================
# PIPELINE PATTERNS
# ============================================================================

class Pipeline:
    """
    Pipeline for chaining processing stages.
    Each stage runs in parallel and communicates via channels.
    """

    def __init__(self):
        self.stages: List[Tuple[Callable, int]] = []  # (function, parallelism)

    def add_stage(self, func: Callable[[T], R], parallelism: int = 1) -> 'Pipeline':
        """Add processing stage"""
        self.stages.append((func, parallelism))
        return self

    def run(self, input_items: List[T]) -> List[R]:
        """Run pipeline on input items"""
        if not self.stages:
            return input_items

        # Create channels between stages
        channels = [Channel(buffer_size=10) for _ in range(len(self.stages) + 1)]

        # Start workers for each stage
        def stage_worker(stage_idx: int, func: Callable, input_ch: Channel, output_ch: Channel):
            try:
                for value in input_ch:
                    result = func(value)
                    output_ch.send(result)
            except ChannelClosedError:
                pass
            finally:
                output_ch.close()

        threads = []
        for i, (func, parallelism) in enumerate(self.stages):
            for _ in range(parallelism):
                thread = threading.Thread(
                    target=stage_worker,
                    args=(i, func, channels[i], channels[i + 1]),
                    daemon=True
                )
                thread.start()
                threads.append(thread)

        # Feed input
        def feed_input():
            for item in input_items:
                channels[0].send(item)
            channels[0].close()

        input_thread = threading.Thread(target=feed_input, daemon=True)
        input_thread.start()

        # Collect output
        results = []
        try:
            for value in channels[-1]:
                results.append(value)
        except ChannelClosedError:
            pass

        # Wait for completion
        input_thread.join()
        for thread in threads:
            thread.join()

        return results


# ============================================================================
# PERFORMANCE MONITORING
# ============================================================================

@dataclass
class ConcurrencyMetrics:
    """Metrics for concurrency primitives"""
    actor_count: int = 0
    actor_messages_sent: int = 0
    actor_messages_processed: int = 0
    stm_transactions_started: int = 0
    stm_transactions_committed: int = 0
    stm_transactions_retried: int = 0
    channel_sends: int = 0
    channel_receives: int = 0
    tasks_submitted: int = 0
    tasks_completed: int = 0

    def report(self) -> str:
        """Generate metrics report"""
        lines = [
            "=== Concurrency Metrics ===",
            f"Actors: {self.actor_count}",
            f"  Messages sent: {self.actor_messages_sent}",
            f"  Messages processed: {self.actor_messages_processed}",
            f"STM Transactions:",
            f"  Started: {self.stm_transactions_started}",
            f"  Committed: {self.stm_transactions_committed}",
            f"  Retried: {self.stm_transactions_retried}",
            f"Channels:",
            f"  Sends: {self.channel_sends}",
            f"  Receives: {self.channel_receives}",
            f"Tasks:",
            f"  Submitted: {self.tasks_submitted}",
            f"  Completed: {self.tasks_completed}",
        ]
        return "\n".join(lines)


_global_metrics = ConcurrencyMetrics()


def get_metrics() -> ConcurrencyMetrics:
    """Get global concurrency metrics"""
    return _global_metrics


def reset_metrics():
    """Reset global metrics"""
    global _global_metrics
    _global_metrics = ConcurrencyMetrics()


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def parallel_map(func: Callable[[T], R], items: List[T], num_workers: Optional[int] = None) -> List[R]:
    """
    Parallel map using work-stealing scheduler.
    """
    results = [None] * len(items)
    results_lock = threading.Lock()

    def task(index, item):
        result = func(item)
        with results_lock:
            results[index] = result

    with WorkStealingScheduler(num_workers=num_workers) as scheduler:
        for i, item in enumerate(items):
            scheduler.submit(task, i, item)

        # Wait for completion (simple polling)
        while any(r is None for r in results):
            time.sleep(0.01)

    return results


def parallel_filter(predicate: Callable[[T], bool], items: List[T], num_workers: Optional[int] = None) -> List[T]:
    """
    Parallel filter using work-stealing scheduler.
    """
    results = []
    results_lock = threading.Lock()

    def task(item):
        if predicate(item):
            with results_lock:
                results.append(item)

    with WorkStealingScheduler(num_workers=num_workers) as scheduler:
        for item in items:
            scheduler.submit(task, item)

        # Brief wait for completion
        time.sleep(0.1)

    return results


def parallel_reduce(func: Callable[[R, T], R], items: List[T], initial: R, num_workers: Optional[int] = None) -> R:
    """
    Parallel reduce using divide-and-conquer.
    """
    if not items:
        return initial

    if len(items) == 1:
        return func(initial, items[0])

    # Split into chunks
    num_workers = num_workers or threading.active_count()
    chunk_size = max(1, len(items) // num_workers)
    chunks = [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

    # Reduce each chunk
    partial_results = []
    results_lock = threading.Lock()

    def reduce_chunk(chunk):
        result = initial
        for item in chunk:
            result = func(result, item)
        with results_lock:
            partial_results.append(result)

    threads = []
    for chunk in chunks:
        thread = threading.Thread(target=reduce_chunk, args=(chunk,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    # Combine partial results
    final_result = initial
    for partial in partial_results:
        final_result = func(final_result, partial)

    return final_result


async def async_parallel_map(func: Callable[[T], R], items: List[T]) -> List[R]:
    """
    Async parallel map.
    """
    async def map_item(item):
        if asyncio.iscoroutinefunction(func):
            return await func(item)
        else:
            return func(item)

    tasks = [map_item(item) for item in items]
    return await asyncio.gather(*tasks)


async def async_parallel_filter(predicate: Callable[[T], bool], items: List[T]) -> List[T]:
    """
    Async parallel filter.
    """
    async def check_item(item):
        if asyncio.iscoroutinefunction(predicate):
            return (item, await predicate(item))
        else:
            return (item, predicate(item))

    results = await asyncio.gather(*[check_item(item) for item in items])
    return [item for item, keep in results if keep]


class Semaphore:
    """
    Semaphore for limiting concurrent access.
    """

    def __init__(self, count: int):
        self._count = TVar(count)
        self._max_count = count

    @atomic
    def acquire(self):
        """Acquire semaphore"""
        tx = get_current_transaction()
        count = self._count.read(tx)
        if count <= 0:
            retry(tx)
        self._count.write(count - 1, tx)

    @atomic
    def release(self):
        """Release semaphore"""
        tx = get_current_transaction()
        count = self._count.read(tx)
        if count >= self._max_count:
            raise RuntimeError("Semaphore released too many times")
        self._count.write(count + 1, tx)

    def __enter__(self):
        """Context manager entry"""
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.release()


class Barrier:
    """
    Barrier for synchronizing multiple threads.
    """

    def __init__(self, parties: int):
        self._parties = parties
        self._count = TVar(0)
        self._generation = TVar(0)

    @atomic
    def wait(self):
        """Wait at barrier"""
        tx = get_current_transaction()
        gen = self._generation.read(tx)
        count = self._count.read(tx)

        count += 1
        self._count.write(count, tx)

        if count >= self._parties:
            # Last thread, reset barrier
            self._count.write(0, tx)
            self._generation.write(gen + 1, tx)
        else:
            # Wait for generation to change
            while self._generation.read(tx) == gen:
                retry(tx)


# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Actor Model - Basic
    'Actor',
    'ActorState',
    'ActorMailbox',
    'ActorSupervisor',
    'SupervisionStrategy',
    'RestartPolicy',
    'spawn_actor',
    'send_message',

    # Actor Model - Advanced
    'RouterActor',
    'BroadcastActor',
    'ActorPool',
    'FutureActor',

    # STM - Basic
    'TVar',
    'Transaction',
    'TransactionState',
    'STMConflictError',
    'atomic',
    'get_current_transaction',

    # STM - Advanced
    'retry',
    'or_else',
    'TMVar',
    'TArray',

    # Channels - Basic
    'Channel',
    'ChannelClosedError',
    'SelectCase',
    'select',

    # Channels - Advanced
    'BoundedChannel',
    'UnboundedChannel',
    'PriorityChannel',
    'fan_out',
    'fan_in',

    # Pipeline
    'Pipeline',

    # Work-Stealing Scheduler
    'WorkStealingScheduler',
    'WorkerThread',
    'Task',

    # Async Streams
    'AsyncStream',
    'StreamMerger',
    'StreamZipper',

    # Synchronization Primitives
    'Semaphore',
    'Barrier',

    # Monitoring
    'ConcurrencyMetrics',
    'get_metrics',
    'reset_metrics',

    # Utilities
    'parallel_map',
    'parallel_filter',
    'parallel_reduce',
    'async_parallel_map',
    'async_parallel_filter',
]


# ============================================================================
# DEMO CODE
# ============================================================================

def demo_actor_model():
    """Demonstrate actor model"""
    print("=== Actor Model Demo ===\n")

    class CounterActor(Actor):
        def __init__(self):
            super().__init__(name="Counter")
            self.count = 0

        def receive(self, message):
            if message == "increment":
                self.count += 1
                print(f"Counter: {self.count}")
            elif message == "get":
                print(f"Current count: {self.count}")

    # Create and start actor
    counter = spawn_actor(CounterActor)

    # Send messages
    for _ in range(5):
        send_message(counter, "increment")

    send_message(counter, "get")

    time.sleep(0.5)
    counter.stop()
    print()


def demo_stm():
    """Demonstrate STM"""
    print("=== Software Transactional Memory Demo ===\n")

    # Bank account transfer
    account1 = TVar(1000)
    account2 = TVar(500)

    @atomic
    def transfer(from_acc, to_acc, amount):
        balance_from = from_acc.read(get_current_transaction())
        balance_to = to_acc.read(get_current_transaction())

        if balance_from < amount:
            raise ValueError("Insufficient funds")

        from_acc.write(balance_from - amount, get_current_transaction())
        to_acc.write(balance_to + amount, get_current_transaction())

    print(f"Account 1: ${account1.read()}")
    print(f"Account 2: ${account2.read()}")

    transfer(account1, account2, 200)

    print(f"After transfer of $200:")
    print(f"Account 1: ${account1.read()}")
    print(f"Account 2: ${account2.read()}")
    print()


def demo_channels():
    """Demonstrate channels"""
    print("=== Channels Demo ===\n")

    channel = Channel(buffer_size=3)

    def producer():
        for i in range(5):
            channel.send(i)
            print(f"Produced: {i}")
            time.sleep(0.1)
        channel.close()

    def consumer():
        for value in channel:
            print(f"Consumed: {value}")

    prod_thread = threading.Thread(target=producer)
    cons_thread = threading.Thread(target=consumer)

    prod_thread.start()
    cons_thread.start()

    prod_thread.join()
    cons_thread.join()
    print()


def demo_work_stealing():
    """Demonstrate work-stealing scheduler"""
    print("=== Work-Stealing Scheduler Demo ===\n")

    def task(n):
        result = sum(i * i for i in range(n))
        print(f"Task {n}: result = {result}")

    with WorkStealingScheduler(num_workers=4) as scheduler:
        for i in range(10):
            scheduler.submit(task, i * 100)

        time.sleep(0.5)

        print("\nScheduler stats:")
        for worker_id, stats in scheduler.get_stats().items():
            print(f"Worker {worker_id}: {stats}")
    print()


def demo_async_streams():
    """Demonstrate async streams"""
    print("=== Async Streams Demo ===\n")

    async def demo():
        # Create stream from list
        stream = AsyncStream.from_iterable([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Map and filter
        result_stream = stream.map(lambda x: x * 2).filter(lambda x: x > 10)

        # Collect results
        results = await result_stream.collect()
        print(f"Results: {results}")

        # Reduce
        stream2 = AsyncStream.from_iterable([1, 2, 3, 4, 5])
        total = await stream2.reduce(lambda acc, x: acc + x, 0)
        print(f"Sum: {total}")

    asyncio.run(demo())
    print()


if __name__ == "__main__":
    print("Lament Concurrency Module - Comprehensive Demo\n")
    print("=" * 60)
    print()

    demo_actor_model()
    demo_stm()
    demo_channels()
    demo_work_stealing()
    demo_async_streams()

    print("All demos completed!")
