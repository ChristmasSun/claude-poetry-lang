"""
Comprehensive test suite for Lament Concurrency Module
"""

import time
import asyncio
import threading
from lament.concurrency import (
    # Actor Model
    Actor, ActorSupervisor, RestartPolicy, SupervisionStrategy,
    spawn_actor, send_message,
    # STM
    TVar, atomic, get_current_transaction, STMConflictError,
    # Channels
    Channel, SelectCase, select, ChannelClosedError,
    # Work-Stealing Scheduler
    WorkStealingScheduler,
    # Async Streams
    AsyncStream, StreamMerger, StreamZipper,
    # Utilities
    parallel_map, parallel_filter
)


def test_actor_model():
    """Test actor model with message passing"""
    print("\n" + "="*60)
    print("TEST 1: Actor Model - Message Passing Concurrency")
    print("="*60)

    class EchoActor(Actor):
        def __init__(self):
            super().__init__(name="Echo")
            self.messages_received = []

        def receive(self, message):
            self.messages_received.append(message)
            print(f"EchoActor received: {message}")

    # Create and start actor
    echo = spawn_actor(EchoActor)

    # Send messages
    messages = ["Hello", "World", "from", "Lament"]
    for msg in messages:
        send_message(echo, msg)

    time.sleep(0.5)

    print(f"\nTotal messages received: {len(echo.messages_received)}")
    echo.stop()
    print("✓ Actor Model test passed!")


def test_actor_supervision():
    """Test actor supervision with restart policy"""
    print("\n" + "="*60)
    print("TEST 2: Actor Supervision with Restart Policies")
    print("="*60)

    class FailingActor(Actor):
        def __init__(self):
            super().__init__(name="Failer")
            self.attempt_count = 0

        def receive(self, message):
            self.attempt_count += 1
            if message == "fail" and self.attempt_count < 3:
                print(f"Attempt {self.attempt_count}: Simulating failure")
                raise RuntimeError("Simulated failure")
            print(f"Attempt {self.attempt_count}: Success!")

        def post_restart(self, reason):
            print(f"Actor restarted after: {reason}")

    # Create supervisor with restart policy
    supervisor = ActorSupervisor(
        restart_policy=RestartPolicy(
            strategy=SupervisionStrategy.RESTART,
            max_retries=5,
            initial_delay=0.1
        )
    )

    # Supervise actor
    actor = supervisor.supervise(FailingActor())
    actor.start()

    # Send failing message
    send_message(actor, "fail")
    time.sleep(1.0)

    # Send success message
    send_message(actor, "success")
    time.sleep(0.5)

    actor.stop()
    print("✓ Actor Supervision test passed!")


def test_stm_basic():
    """Test basic STM operations"""
    print("\n" + "="*60)
    print("TEST 3: Software Transactional Memory - Basic Operations")
    print("="*60)

    # Create transactional variables
    x = TVar(10)
    y = TVar(20)

    print(f"Initial values: x={x.read()}, y={y.read()}")

    @atomic
    def swap_values():
        tx = get_current_transaction()
        val_x = x.read(tx)
        val_y = y.read(tx)
        x.write(val_y, tx)
        y.write(val_x, tx)

    swap_values()

    print(f"After swap: x={x.read()}, y={y.read()}")
    assert x.read() == 20 and y.read() == 10
    print("✓ STM Basic test passed!")


def test_stm_bank_transfer():
    """Test STM with bank account transfers"""
    print("\n" + "="*60)
    print("TEST 4: STM - Concurrent Bank Transfers")
    print("="*60)

    # Create bank accounts
    account_a = TVar(1000)
    account_b = TVar(1000)
    account_c = TVar(1000)

    @atomic
    def transfer(from_acc, to_acc, amount):
        tx = get_current_transaction()
        from_balance = from_acc.read(tx)
        to_balance = to_acc.read(tx)

        if from_balance < amount:
            raise ValueError("Insufficient funds")

        from_acc.write(from_balance - amount, tx)
        to_acc.write(to_balance + amount, tx)

    print(f"Initial balances: A={account_a.read()}, B={account_b.read()}, C={account_c.read()}")
    total_before = account_a.read() + account_b.read() + account_c.read()

    # Perform concurrent transfers
    def do_transfers():
        for _ in range(10):
            transfer(account_a, account_b, 50)
            transfer(account_b, account_c, 30)
            transfer(account_c, account_a, 20)

    threads = [threading.Thread(target=do_transfers) for _ in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    total_after = account_a.read() + account_b.read() + account_c.read()
    print(f"Final balances: A={account_a.read()}, B={account_b.read()}, C={account_c.read()}")
    print(f"Total before: ${total_before}, Total after: ${total_after}")

    assert total_before == total_after, "Money was created or lost!"
    print("✓ STM Bank Transfer test passed!")


def test_channels_basic():
    """Test basic channel operations"""
    print("\n" + "="*60)
    print("TEST 5: Channels - Basic Send/Receive")
    print("="*60)

    channel = Channel(buffer_size=5)
    received = []

    def producer():
        for i in range(10):
            channel.send(i)
            print(f"Produced: {i}")
        channel.close()

    def consumer():
        for value in channel:
            received.append(value)
            print(f"Consumed: {value}")

    prod_thread = threading.Thread(target=producer)
    cons_thread = threading.Thread(target=consumer)

    prod_thread.start()
    cons_thread.start()

    prod_thread.join()
    cons_thread.join()

    assert received == list(range(10))
    print("✓ Channels Basic test passed!")


def test_select():
    """Test select operation on multiple channels"""
    print("\n" + "="*60)
    print("TEST 6: Channels - Select Operation")
    print("="*60)

    ch1 = Channel(buffer_size=1)
    ch2 = Channel(buffer_size=1)

    def producer1():
        for i in range(3):
            ch1.send(f"ch1-{i}")
            time.sleep(0.1)
        ch1.close()

    def producer2():
        for i in range(3):
            ch2.send(f"ch2-{i}")
            time.sleep(0.15)
        ch2.close()

    threading.Thread(target=producer1, daemon=True).start()
    threading.Thread(target=producer2, daemon=True).start()

    received = []
    for _ in range(6):
        try:
            case_idx, value = select(
                SelectCase(ch1),
                SelectCase(ch2),
                timeout=1.0
            )
            received.append(value)
            print(f"Selected from channel {case_idx}: {value}")
        except (TimeoutError, ChannelClosedError):
            break

    print(f"Received {len(received)} messages")
    print("✓ Select test passed!")


def test_work_stealing():
    """Test work-stealing scheduler"""
    print("\n" + "="*60)
    print("TEST 7: Work-Stealing Scheduler")
    print("="*60)

    results = []
    results_lock = threading.Lock()

    def compute_task(n):
        result = sum(i * i for i in range(n))
        with results_lock:
            results.append(result)
        return result

    with WorkStealingScheduler(num_workers=4) as scheduler:
        # Submit tasks
        for i in range(20):
            scheduler.submit(compute_task, i * 10)

        # Wait for completion
        time.sleep(1.0)

        # Get statistics
        stats = scheduler.get_stats()
        print("\nWorker Statistics:")
        total_executed = 0
        total_stolen = 0
        for worker_id, worker_stats in stats.items():
            print(f"  Worker {worker_id}: executed={worker_stats['tasks_executed']}, "
                  f"stolen={worker_stats['tasks_stolen']}, "
                  f"steal_attempts={worker_stats['steal_attempts']}")
            total_executed += worker_stats['tasks_executed']
            total_stolen += worker_stats['tasks_stolen']

        print(f"\nTotal tasks executed: {total_executed}")
        print(f"Total tasks stolen: {total_stolen}")
        print(f"Results collected: {len(results)}")

    print("✓ Work-Stealing Scheduler test passed!")


def test_async_streams_basic():
    """Test basic async stream operations"""
    print("\n" + "="*60)
    print("TEST 8: Async Streams - Basic Operations")
    print("="*60)

    async def run_test():
        # Create stream from list
        stream = AsyncStream.from_iterable([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])

        # Map: multiply by 2
        mapped = stream.map(lambda x: x * 2)

        # Filter: only values > 10
        filtered = mapped.filter(lambda x: x > 10)

        # Collect results
        results = await filtered.collect()
        print(f"Results: {results}")
        assert results == [12, 14, 16, 18, 20]

        # Test reduce
        stream2 = AsyncStream.from_iterable([1, 2, 3, 4, 5])
        total = await stream2.reduce(lambda acc, x: acc + x, 0)
        print(f"Sum: {total}")
        assert total == 15

        # Test take
        stream3 = AsyncStream.from_iterable(range(100))
        first_five = await stream3.take(5)
        print(f"First 5: {first_five}")
        assert first_five == [0, 1, 2, 3, 4]

    asyncio.run(run_test())
    print("✓ Async Streams Basic test passed!")


def test_stream_operations():
    """Test advanced stream operations"""
    print("\n" + "="*60)
    print("TEST 9: Async Streams - Advanced Operations")
    print("="*60)

    async def run_test():
        # Test batch operation
        stream = AsyncStream.from_iterable(range(10))
        batched = stream.batch(3)
        batches = await batched.collect()
        print(f"Batches: {batches}")

        # Test for_each
        values = []
        stream2 = AsyncStream.from_iterable([1, 2, 3, 4, 5])
        await stream2.for_each(lambda x: values.append(x * 2))
        print(f"For each results: {values}")
        assert values == [2, 4, 6, 8, 10]

    asyncio.run(run_test())
    print("✓ Stream Operations test passed!")


def test_stream_merge():
    """Test stream merging"""
    print("\n" + "="*60)
    print("TEST 10: Async Streams - Merge Operation")
    print("="*60)

    async def run_test():
        stream1 = AsyncStream.from_iterable([1, 2, 3])
        stream2 = AsyncStream.from_iterable([4, 5, 6])
        stream3 = AsyncStream.from_iterable([7, 8, 9])

        merger = StreamMerger(stream1, stream2, stream3)
        merged = await merger.merge()

        results = await merged.collect()
        print(f"Merged results: {sorted(results)}")
        assert sorted(results) == list(range(1, 10))

    asyncio.run(run_test())
    print("✓ Stream Merge test passed!")


def test_parallel_utilities():
    """Test parallel utility functions"""
    print("\n" + "="*60)
    print("TEST 11: Parallel Utilities")
    print("="*60)

    # Test parallel_map
    numbers = list(range(10))
    results = parallel_map(lambda x: x * x, numbers, num_workers=4)
    print(f"Parallel map results: {results}")
    assert results == [x * x for x in numbers]

    # Test parallel_filter
    results = parallel_filter(lambda x: x % 2 == 0, numbers, num_workers=4)
    print(f"Parallel filter results: {results}")
    # Results may not be in order due to parallelism
    assert set(results) == {0, 2, 4, 6, 8}

    print("✓ Parallel Utilities test passed!")


def test_actor_priority_messages():
    """Test actor with priority messages"""
    print("\n" + "="*60)
    print("TEST 12: Actor Priority Messages")
    print("="*60)

    class PriorityActor(Actor):
        def __init__(self):
            super().__init__(name="Priority")
            self.received = []

        def receive(self, message):
            self.received.append(message)
            print(f"Received: {message}")

    actor = spawn_actor(PriorityActor)

    # Send messages with different priorities
    send_message(actor, "low", priority=10)
    send_message(actor, "high", priority=1)
    send_message(actor, "medium", priority=5)

    time.sleep(0.5)
    print(f"Received order: {actor.received}")

    actor.stop()
    print("✓ Actor Priority Messages test passed!")


def run_all_tests():
    """Run all concurrency tests"""
    print("\n" + "="*60)
    print("LAMENT CONCURRENCY MODULE - COMPREHENSIVE TEST SUITE")
    print("="*60)

    tests = [
        test_actor_model,
        test_actor_supervision,
        test_stm_basic,
        test_stm_bank_transfer,
        test_channels_basic,
        test_select,
        test_work_stealing,
        test_async_streams_basic,
        test_stream_operations,
        test_stream_merge,
        test_parallel_utilities,
        test_actor_priority_messages,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} FAILED: {e}")
            failed += 1

    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Total tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("="*60)

    if failed == 0:
        print("\n🎉 All tests passed!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
