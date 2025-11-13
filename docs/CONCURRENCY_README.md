# Lament Concurrency Module

A comprehensive concurrency library providing state-of-the-art concurrent programming primitives for the Lament language.

## Overview

The Lament Concurrency Module (`lament/concurrency.py`) is a **2030+ line** implementation featuring five major concurrency paradigms:

1. **Actor Model** - Message-passing concurrency with supervision
2. **Software Transactional Memory (STM)** - Lock-free transactions
3. **Channels** - Go-style communication primitives
4. **Work-Stealing Scheduler** - Efficient task distribution
5. **Async Streams** - Asynchronous iteration with backpressure

---

## 1. Actor Model

Message-passing concurrency based on the Actor Model, inspired by Erlang/OTP and Akka.

### Features

#### Basic Actors
- **Actor** base class with mailbox
- **spawn_actor()** - Create and start actors
- **send_message()** - Send messages to actors
- Priority message delivery
- Actor lifecycle management (CREATED, RUNNING, STOPPED, etc.)

#### Actor Supervision
- **ActorSupervisor** - Supervise actor lifecycles
- **RestartPolicy** - Configure restart behavior
- **SupervisionStrategy**:
  - `RESTART` - Restart failed actors
  - `RESUME` - Resume after failure
  - `STOP` - Stop on failure
  - `ESCALATE` - Escalate to parent

#### Advanced Actor Patterns
- **RouterActor** - Round-robin load balancing
- **BroadcastActor** - Pub/sub message broadcasting
- **ActorPool** - Managed pool of worker actors
- **FutureActor** - Request-response pattern with timeouts

### Usage Example

```python
from lament.concurrency import Actor, spawn_actor, send_message

class CounterActor(Actor):
    def __init__(self):
        super().__init__(name="Counter")
        self.count = 0

    def receive(self, message):
        if message == "increment":
            self.count += 1
        elif message == "get":
            print(f"Count: {self.count}")

# Create and start actor
counter = spawn_actor(CounterActor)

# Send messages
send_message(counter, "increment")
send_message(counter, "get")

counter.stop()
```

### Supervision Example

```python
from lament.concurrency import ActorSupervisor, RestartPolicy, SupervisionStrategy

supervisor = ActorSupervisor(
    restart_policy=RestartPolicy(
        strategy=SupervisionStrategy.RESTART,
        max_retries=5,
        initial_delay=0.1
    )
)

actor = supervisor.supervise(MyActor())
actor.start()
```

---

## 2. Software Transactional Memory (STM)

Lock-free transactions with automatic conflict detection and retry.

### Features

#### Basic STM
- **TVar** - Transactional variables
- **@atomic** decorator - Atomic transaction blocks
- **Transaction** - Explicit transaction control
- Automatic conflict detection
- Optimistic concurrency control
- Composable transactions

#### Advanced STM
- **retry()** - Explicit transaction retry
- **or_else()** - Composable choice operator
- **TMVar** - Transactional MVar (empty/full)
- **TArray** - Transactional array

### Usage Example

```python
from lament.concurrency import TVar, atomic, get_current_transaction

# Create transactional variables
account1 = TVar(1000)
account2 = TVar(500)

@atomic
def transfer(from_acc, to_acc, amount):
    tx = get_current_transaction()

    balance_from = from_acc.read(tx)
    balance_to = to_acc.read(tx)

    if balance_from < amount:
        raise ValueError("Insufficient funds")

    from_acc.write(balance_from - amount, tx)
    to_acc.write(balance_to + amount, tx)

# Atomic transfer
transfer(account1, account2, 200)

print(f"Account 1: ${account1.read()}")  # 800
print(f"Account 2: ${account2.read()}")  # 700
```

### Advanced STM Example

```python
from lament.concurrency import TMVar, TArray

# TMVar - synchronization primitive
mvar = TMVar()

@atomic
def producer():
    tx = get_current_transaction()
    mvar.put(42, tx)

@atomic
def consumer():
    tx = get_current_transaction()
    value = mvar.take(tx)
    return value

# TArray - transactional array
array = TArray(10, initial_value=0)

@atomic
def swap_elements():
    tx = get_current_transaction()
    array.swap(0, 9, tx)
```

---

## 3. Channels

Go-style channels for communication between threads and coroutines.

### Features

#### Basic Channels
- **Channel** - Buffered/unbuffered channels
- **send()** / **receive()** - Blocking operations
- **try_send()** / **try_receive()** - Non-blocking operations
- **select()** - Multi-channel operations
- Iteration support

#### Advanced Channels
- **BoundedChannel** - Explicit capacity
- **UnboundedChannel** - Unlimited buffer
- **PriorityChannel** - Priority-based delivery
- **fan_out()** - One-to-many broadcasting
- **fan_in()** - Many-to-one merging

### Usage Example

```python
from lament.concurrency import Channel
import threading

channel = Channel(buffer_size=5)

def producer():
    for i in range(10):
        channel.send(i)
    channel.close()

def consumer():
    for value in channel:
        print(f"Received: {value}")

threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
```

### Select Example

```python
from lament.concurrency import Channel, SelectCase, select

ch1 = Channel()
ch2 = Channel()

# Select from multiple channels
case_idx, value = select(
    SelectCase(ch1),
    SelectCase(ch2),
    timeout=1.0
)

print(f"Received from channel {case_idx}: {value}")
```

### Fan-Out/Fan-In Example

```python
from lament.concurrency import Channel, fan_out, fan_in

# Fan-out: one input → many outputs
input_ch = Channel()
outputs = [Channel() for _ in range(3)]
fan_out(input_ch, outputs)

# Fan-in: many inputs → one output
inputs = [Channel() for _ in range(3)]
output_ch = Channel()
fan_in(inputs, output_ch)
```

---

## 4. Work-Stealing Scheduler

Efficient task distribution with work stealing for load balancing.

### Features

- **WorkStealingScheduler** - Multi-threaded task scheduler
- **Per-worker queues** - Local LIFO for cache locality
- **Work stealing** - Random victim selection
- **Task statistics** - Monitor execution and stealing
- **Context manager** support

### Usage Example

```python
from lament.concurrency import WorkStealingScheduler

def compute_task(n):
    result = sum(i * i for i in range(n))
    print(f"Task {n}: {result}")
    return result

# Create scheduler with 4 workers
with WorkStealingScheduler(num_workers=4) as scheduler:
    # Submit tasks
    for i in range(20):
        scheduler.submit(compute_task, i * 100)

    # Scheduler automatically distributes and load-balances
    time.sleep(1.0)

    # Get statistics
    stats = scheduler.get_stats()
    for worker_id, worker_stats in stats.items():
        print(f"Worker {worker_id}: {worker_stats}")
```

---

## 5. Async Streams

Asynchronous iteration with functional operations and backpressure handling.

### Features

#### Stream Operations
- **map()** - Transform elements
- **filter()** - Filter elements
- **reduce()** - Aggregate values
- **collect()** - Gather all values
- **take()** / **skip()** - Limit operations
- **batch()** - Group elements
- **for_each()** - Apply side effects

#### Stream Creation
- **from_iterable()** - From list/iterable
- **from_async_iterator()** - From async iterator
- **interval()** - Timed emissions

#### Stream Composition
- **StreamMerger** - Merge multiple streams
- **StreamZipper** - Zip streams into tuples

### Usage Example

```python
from lament.concurrency import AsyncStream
import asyncio

async def process_stream():
    # Create stream from list
    stream = AsyncStream.from_iterable([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

    # Chain operations
    result = (stream
        .map(lambda x: x * 2)
        .filter(lambda x: x > 10)
    )

    # Collect results
    values = await result.collect()
    print(values)  # [12, 14, 16, 18, 20]

    # Reduce
    stream2 = AsyncStream.from_iterable([1, 2, 3, 4, 5])
    total = await stream2.reduce(lambda acc, x: acc + x, 0)
    print(total)  # 15

asyncio.run(process_stream())
```

### Stream Merging Example

```python
from lament.concurrency import AsyncStream, StreamMerger

async def merge_streams():
    stream1 = AsyncStream.from_iterable([1, 2, 3])
    stream2 = AsyncStream.from_iterable([4, 5, 6])
    stream3 = AsyncStream.from_iterable([7, 8, 9])

    merger = StreamMerger(stream1, stream2, stream3)
    merged = await merger.merge()

    results = await merged.collect()
    print(results)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]

asyncio.run(merge_streams())
```

---

## Additional Features

### Pipeline Pattern

Chain processing stages with automatic parallelism:

```python
from lament.concurrency import Pipeline

pipeline = Pipeline()
pipeline.add_stage(lambda x: x * 2, parallelism=2)
pipeline.add_stage(lambda x: x + 1, parallelism=2)
pipeline.add_stage(lambda x: x ** 2, parallelism=2)

results = pipeline.run([1, 2, 3, 4, 5])
print(results)
```

### Synchronization Primitives

#### Semaphore

```python
from lament.concurrency import Semaphore

sem = Semaphore(3)  # Allow 3 concurrent accesses

with sem:
    # Critical section
    pass
```

#### Barrier

```python
from lament.concurrency import Barrier

barrier = Barrier(parties=4)  # Wait for 4 threads

@atomic
def worker():
    # Do work...
    barrier.wait()  # Synchronize here
```

### Performance Monitoring

```python
from lament.concurrency import get_metrics, reset_metrics

# Get metrics
metrics = get_metrics()
print(metrics.report())

# Reset metrics
reset_metrics()
```

### Parallel Utilities

```python
from lament.concurrency import (
    parallel_map,
    parallel_filter,
    parallel_reduce,
    async_parallel_map,
    async_parallel_filter
)

# Parallel map
results = parallel_map(lambda x: x * x, [1, 2, 3, 4, 5], num_workers=4)

# Parallel filter
evens = parallel_filter(lambda x: x % 2 == 0, range(100), num_workers=4)

# Parallel reduce
total = parallel_reduce(lambda a, b: a + b, [1, 2, 3, 4, 5], 0, num_workers=4)

# Async parallel map
async def process():
    results = await async_parallel_map(lambda x: x * 2, [1, 2, 3, 4, 5])
    return results
```

---

## Module Statistics

- **Total Lines**: 2030+
- **Classes**: 30+
- **Functions**: 40+
- **Concurrency Paradigms**: 5

### Class Breakdown

#### Actor Model (8 classes)
- Actor
- ActorMailbox
- ActorSupervisor
- RouterActor
- BroadcastActor
- ActorPool
- FutureActor
- ActorState, SupervisionStrategy, RestartPolicy (enums/dataclasses)

#### STM (7 classes)
- TVar
- Transaction
- TMVar
- TArray
- TransactionState (enum)
- STMConflictError (exception)

#### Channels (7 classes)
- Channel
- BoundedChannel
- UnboundedChannel
- PriorityChannel
- SelectCase
- ChannelClosedError (exception)

#### Scheduler (3 classes)
- WorkStealingScheduler
- WorkerThread
- Task

#### Async Streams (3 classes)
- AsyncStream
- StreamMerger
- StreamZipper

#### Utilities (4 classes)
- Pipeline
- Semaphore
- Barrier
- ConcurrencyMetrics

---

## Key Features Summary

### 1. Actor Model
- ✓ Message-passing concurrency
- ✓ Actor supervision and restart policies
- ✓ Priority message delivery
- ✓ Router, Broadcast, Pool, Future patterns
- ✓ Lifecycle management

### 2. Software Transactional Memory
- ✓ Lock-free transactions
- ✓ Automatic conflict detection
- ✓ Composable with @atomic decorator
- ✓ Retry and or_else combinators
- ✓ TMVar and TArray primitives

### 3. Channels
- ✓ Go-style send/receive
- ✓ Select operation
- ✓ Buffered and unbuffered
- ✓ Priority channels
- ✓ Fan-out/Fan-in patterns
- ✓ Multi-producer multi-consumer

### 4. Work-Stealing Scheduler
- ✓ Per-worker task queues
- ✓ Random work stealing
- ✓ Load balancing
- ✓ Task statistics
- ✓ Context manager support

### 5. Async Streams
- ✓ Map, filter, reduce operations
- ✓ Backpressure handling
- ✓ Stream merging and zipping
- ✓ Batch operations
- ✓ Async iteration protocol

---

## Testing

A comprehensive test suite is provided in `test_concurrency.py` with 12 tests covering:

1. Actor message passing
2. Actor supervision
3. STM basic operations
4. STM concurrent bank transfers
5. Channel send/receive
6. Channel select operation
7. Work-stealing scheduler
8. Async streams basic operations
9. Async streams advanced operations
10. Stream merging
11. Parallel utilities
12. Actor priority messages

### Running Tests

```bash
python test_concurrency.py
```

**Test Results**: 10/12 tests passing (83% pass rate)

---

## Implementation Details

### Thread Safety
- All primitives are thread-safe
- TVar uses versioning for optimistic concurrency
- Channels use queue.Queue internally
- Actors have dedicated mailbox threads

### Performance Considerations
- Work stealing reduces contention
- STM uses exponential backoff on conflicts
- Channels support buffering for throughput
- Async streams provide backpressure

### Design Patterns
- Actor Model: Erlang/OTP, Akka
- STM: Haskell STM, Clojure
- Channels: Go channels
- Work Stealing: Java Fork/Join
- Streams: ReactiveX, Akka Streams

---

## Future Enhancements

Potential additions:
- Distributed actors (network communication)
- STM with nested transactions
- Channel timeout operations
- Stream windowing operations
- Task priorities in scheduler
- Dead letter queues for actors
- Circuit breaker pattern

---

## License

Part of the Lament Language project.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)

---

## See Also

- `lament/actor.py` - Actor system integration
- `lament/neural.py` - Neural network primitives
- `lament/bytecode.py` - Bytecode compiler and VM
- `lament/temporal_advanced.py` - Temporal programming

---

**Lament Concurrency Module** - State-of-the-art concurrent programming for a language that feels alive.
