#!/usr/bin/env python3
"""
Lament Temporal Advanced Features - Comprehensive Demo
=======================================================

This demo showcases the revolutionary CAUSAL DEBUGGING and TEMPORAL CONTRACTS
features that make time itself a first-class debugging tool.

Run this to see:
1. How WHY queries trace computational lineage
2. How contracts enforce invariants across time
3. How beautiful error messages guide you through violations

Usage:
    python temporal_advanced_demo.py
"""

import sys
import time
from lament.temporal_advanced import (
    CausalValue, create_causal_variable, why, track_operation,
    ContractManager, ContractViolation, Invariant, Ensures, Eventually,
    CausalOrigin
)
from lament.types import Color


def print_section(title: str):
    """Print a beautiful section header."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'═'*70}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}  {title}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'═'*70}{Color.RESET}\n")
    time.sleep(0.5)


def demo_basic_causal():
    """Demo 1: Basic causal debugging."""
    print_section("DEMO 1: Basic Causal Debugging")

    print(f"{Color.YELLOW}Creating variables with causal tracking...{Color.RESET}\n")

    # Simple computation
    x = create_causal_variable("x", 10, "x = 10", line=1)
    print(f"x = {x.current}")

    x.assign_with_cause(15, "x = x + 5", line=2,
                       dependencies={"x@past": 10, "literal": 5},
                       operation="+")
    print(f"x = {x.current} (after x = x + 5)")

    x.assign_with_cause(30, "x = x * 2", line=3,
                       dependencies={"x@past": 15, "literal": 2},
                       operation="*")
    print(f"x = {x.current} (after x = x * 2)")

    # Ask WHY
    print(f"\n{Color.MAGENTA}Now let's ask: WHY does x equal {x.current}?{Color.RESET}")
    print(why(x))

    input(f"\n{Color.GREEN}Press Enter to continue...{Color.RESET}")


def demo_complex_causal():
    """Demo 2: Complex multi-variable causal chains."""
    print_section("DEMO 2: Complex Causal Chains")

    print(f"{Color.YELLOW}Computing with multiple dependent variables...{Color.RESET}\n")

    # Create a chain of computations
    price = create_causal_variable("price", 100, "price = 100", line=10)
    quantity = create_causal_variable("quantity", 5, "quantity = 5", line=11)

    print(f"price = {price.current}")
    print(f"quantity = {quantity.current}")

    # Calculate subtotal
    subtotal_value = price.current * quantity.current
    subtotal = create_causal_variable("subtotal", subtotal_value,
                                     "subtotal = price * quantity", line=12)
    subtotal.causal_history.append(CausalOrigin(
        value=subtotal_value,
        expression="price * quantity",
        line=12,
        dependencies={"price": price, "quantity": quantity},
        operation="*"
    ))
    print(f"subtotal = {subtotal.current}")

    # Apply tax
    tax_rate = 0.1
    tax_value = subtotal.current * tax_rate
    tax = create_causal_variable("tax", tax_value,
                                f"tax = subtotal * {tax_rate}", line=13)
    tax.causal_history.append(CausalOrigin(
        value=tax_value,
        expression=f"subtotal * {tax_rate}",
        line=13,
        dependencies={"subtotal": subtotal, "tax_rate": tax_rate},
        operation="*"
    ))
    print(f"tax = {tax.current}")

    # Calculate total
    total_value = subtotal.current + tax.current
    total = create_causal_variable("total", total_value,
                                  "total = subtotal + tax", line=14)
    total.causal_history.append(CausalOrigin(
        value=total_value,
        expression="subtotal + tax",
        line=14,
        dependencies={"subtotal": subtotal, "tax": tax},
        operation="+"
    ))
    print(f"total = {total.current}")

    # The magic: trace the complete computational lineage
    print(f"\n{Color.MAGENTA}WHY does total equal {total.current}?{Color.RESET}")
    print(f"{Color.MAGENTA}Let's trace the ENTIRE causal chain...{Color.RESET}")
    print(why(total))

    input(f"\n{Color.GREEN}Press Enter to continue...{Color.RESET}")


def demo_fibonacci_causal():
    """Demo 3: Fibonacci with full causal tracking."""
    print_section("DEMO 3: Fibonacci Sequence with Causal Tracking")

    print(f"{Color.YELLOW}Computing Fibonacci numbers with full causality...{Color.RESET}\n")

    # Initialize
    a = create_causal_variable("fib_a", 0, "fib_a = 0", line=20)
    b = create_causal_variable("fib_b", 1, "fib_b = 1", line=21)

    print(f"fib(0) = {a.current}")
    print(f"fib(1) = {b.current}")

    # Compute first few Fibonacci numbers
    for i in range(2, 8):
        next_val = a.current + b.current
        next_fib = create_causal_variable(f"fib({i})", next_val,
                                         f"fib({i}) = fib({i-2}) + fib({i-1})",
                                         line=20+i)
        next_fib.causal_history.append(CausalOrigin(
            value=next_val,
            expression=f"fib({i-2}) + fib({i-1})",
            line=20+i,
            dependencies={f"fib({i-2})": a.current, f"fib({i-1})": b.current},
            operation="+"
        ))

        print(f"fib({i}) = {next_val}")

        # Advance
        a = b
        b = next_fib

    # Show the causal trace of the last number
    print(f"\n{Color.MAGENTA}How did we arrive at fib(7) = {b.current}?{Color.RESET}")
    print(why(b))

    input(f"\n{Color.GREEN}Press Enter to continue...{Color.RESET}")


def demo_invariant_contracts():
    """Demo 4: Invariant contracts (success and failure)."""
    print_section("DEMO 4: Invariant Contracts")

    manager = ContractManager()

    print(f"{Color.YELLOW}Setting up invariants for a bank account...{Color.RESET}\n")

    # Add invariants
    manager.add_invariant(
        lambda s: s.get('balance', 0) >= 0,
        "balance >= 0",
        "non-negative balance"
    )
    manager.add_invariant(
        lambda s: s.get('balance', 0) <= 1000000,
        "balance <= 1,000,000",
        "reasonable balance limit"
    )

    print(f"{Color.GREEN}✓ Invariants registered:{Color.RESET}")
    print(f"  1. balance >= 0 (no negative balances)")
    print(f"  2. balance <= 1,000,000 (reasonable limit)\n")

    # Test 1: Valid transactions
    print(f"{Color.CYAN}Test 1: Valid transactions{Color.RESET}")
    scope = {'balance': 1000}
    print(f"Initial balance: ${scope['balance']}")

    try:
        manager.check_invariants(scope)
        print(f"{Color.GREEN}✓ All invariants satisfied{Color.RESET}\n")
    except ContractViolation as e:
        print(e)

    # Deposit
    scope['balance'] += 500
    print(f"After deposit: ${scope['balance']}")
    try:
        manager.check_invariants(scope, 'balance')
        print(f"{Color.GREEN}✓ All invariants satisfied{Color.RESET}\n")
    except ContractViolation as e:
        print(e)

    # Test 2: Violation - negative balance
    print(f"{Color.CYAN}Test 2: Attempting overdraft...{Color.RESET}")
    scope['balance'] = -100
    print(f"After overdraft attempt: ${scope['balance']}")

    try:
        manager.check_invariants(scope, 'balance')
        print(f"{Color.GREEN}✓ All invariants satisfied{Color.RESET}\n")
    except ContractViolation as e:
        print(e)
        print(f"{Color.GREEN}✓ Invariant violation caught! The universe is protected.{Color.RESET}\n")

    input(f"\n{Color.GREEN}Press Enter to continue...{Color.RESET}")


def demo_eventually_contracts():
    """Demo 5: Eventually contracts."""
    print_section("DEMO 5: Eventually Contracts")

    print(f"{Color.YELLOW}Eventually contracts ensure conditions become true within N steps...{Color.RESET}\n")

    # Demo 5a: Success case
    print(f"{Color.CYAN}Test 1: Convergence within time limit (SUCCESS){Color.RESET}\n")

    manager = ContractManager()
    manager.add_eventually(
        10,
        lambda s: s.get('temperature', 0) <= 20,
        "temperature <= 20",
        "cooling system reaches target"
    )

    scope = {'temperature': 100}
    print(f"Initial temperature: {scope['temperature']}°C")
    print(f"Target: ≤20°C within 10 steps\n")

    try:
        for step in range(15):
            # Simulate cooling
            scope['temperature'] = max(20, scope['temperature'] - 10)
            manager.step(scope)
            print(f"Step {step + 1}: temperature = {scope['temperature']}°C")

            if scope['temperature'] <= 20:
                print(f"\n{Color.GREEN}✓ Eventually contract satisfied! Target reached.{Color.RESET}\n")
                break
    except ContractViolation as e:
        print(e)

    # Demo 5b: Failure case
    print(f"{Color.CYAN}Test 2: Condition not met within time limit (FAILURE){Color.RESET}\n")

    manager2 = ContractManager()
    manager2.add_eventually(
        5,
        lambda s: s.get('counter', 0) >= 100,
        "counter >= 100",
        "counter reaches 100"
    )

    scope2 = {'counter': 0}
    print(f"Initial counter: {scope2['counter']}")
    print(f"Target: ≥100 within 5 steps\n")

    try:
        for step in range(10):
            scope2['counter'] += 10  # Too slow!
            manager2.step(scope2)
            print(f"Step {step + 1}: counter = {scope2['counter']}")

            if scope2['counter'] >= 100:
                print(f"\n{Color.GREEN}✓ Eventually contract satisfied!{Color.RESET}\n")
                break
    except ContractViolation as e:
        print(e)
        print(f"{Color.GREEN}✓ Eventually contract violation detected! Time ran out.{Color.RESET}\n")

    input(f"\n{Color.GREEN}Press Enter to continue...{Color.RESET}")


def demo_ensures_contracts():
    """Demo 6: Ensures contracts (post-conditions)."""
    print_section("DEMO 6: Ensures Contracts (Post-conditions)")

    manager = ContractManager()

    print(f"{Color.YELLOW}Ensures contracts verify function post-conditions...{Color.RESET}\n")

    # Add ensures contract
    manager.add_ensures(
        lambda s: s.get('result', 0) > 0,
        "result > 0",
        "positive result"
    )
    manager.add_ensures(
        lambda s: s.get('result', 0) == s.get('a', 0) + s.get('b', 0),
        "result == a + b",
        "correct addition"
    )

    print(f"{Color.GREEN}✓ Ensures contracts registered:{Color.RESET}")
    print(f"  1. result > 0 (positive output)")
    print(f"  2. result == a + b (correct computation)\n")

    # Test 1: Valid function
    print(f"{Color.CYAN}Test 1: Valid function execution{Color.RESET}")
    scope = {'a': 10, 'b': 20, 'result': 30}
    print(f"Function: add(a={scope['a']}, b={scope['b']}) → result={scope['result']}")

    try:
        manager.check_ensures(scope, 'add')
        print(f"{Color.GREEN}✓ All post-conditions satisfied{Color.RESET}\n")
    except ContractViolation as e:
        print(e)

    # Test 2: Violated post-condition
    print(f"{Color.CYAN}Test 2: Buggy function (wrong result){Color.RESET}")
    scope2 = {'a': 10, 'b': 20, 'result': 25}  # Wrong!
    print(f"Function: add(a={scope2['a']}, b={scope2['b']}) → result={scope2['result']} (WRONG!)")

    try:
        manager.check_ensures(scope2, 'add')
        print(f"{Color.GREEN}✓ All post-conditions satisfied{Color.RESET}\n")
    except ContractViolation as e:
        print(e)
        print(f"{Color.GREEN}✓ Post-condition violation caught! The bug is revealed.{Color.RESET}\n")

    input(f"\n{Color.GREEN}Press Enter to continue...{Color.RESET}")


def demo_combined_features():
    """Demo 7: Combining causal debugging with contracts."""
    print_section("DEMO 7: The Power Combo - Causality + Contracts")

    print(f"{Color.YELLOW}Combining causal debugging with temporal contracts...{Color.RESET}\n")

    manager = ContractManager()
    manager.add_invariant(
        lambda s: s.get('velocity', 0) <= 100,
        "velocity <= 100",
        "speed limit"
    )

    # Create causal variables
    velocity = create_causal_variable("velocity", 0, "velocity = 0", line=100)
    print(f"Initial velocity: {velocity.current} m/s")

    # Accelerate
    for i in range(1, 6):
        old_v = velocity.current
        new_v = old_v + 15
        velocity.assign_with_cause(
            new_v,
            f"velocity = velocity + 15 [iteration {i}]",
            line=100 + i,
            dependencies={"velocity@past": old_v, "acceleration": 15},
            operation="+"
        )
        print(f"Iteration {i}: velocity = {velocity.current} m/s")

        # Check invariant
        scope = {'velocity': velocity.current}
        try:
            manager.check_invariants(scope, 'velocity')
        except ContractViolation as e:
            print(f"\n{Color.RED}SPEED LIMIT VIOLATION!{Color.RESET}\n")
            print(e)

            # Now use causal debugging to understand HOW we got here
            print(f"\n{Color.MAGENTA}Let's use causal debugging to understand HOW this happened:{Color.RESET}")
            print(why(velocity))

            print(f"\n{Color.GREEN}✓ Causality + Contracts = Ultimate debugging power!{Color.RESET}")
            print(f"{Color.GREEN}  We know WHAT went wrong (contract) and WHY (causality).{Color.RESET}\n")
            break

    input(f"\n{Color.GREEN}Press Enter to finish...{Color.RESET}")


def print_finale():
    """Print the grand finale message."""
    print(f"\n{Color.MAGENTA}{Color.BOLD}{'═'*70}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}                          🌌 FINALE 🌌{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'═'*70}{Color.RESET}\n")

    print(f"{Color.CYAN}You have witnessed the power of temporal advanced features:{Color.RESET}\n")

    print(f"{Color.YELLOW}1. CAUSAL DEBUGGING:{Color.RESET}")
    print(f"   • Every value remembers WHY it exists")
    print(f"   • Complete computational lineage")
    print(f"   • Trace dependencies across time\n")

    print(f"{Color.YELLOW}2. TEMPORAL CONTRACTS:{Color.RESET}")
    print(f"   • Invariants: conditions that must ALWAYS hold")
    print(f"   • Ensures: post-conditions for functions")
    print(f"   • Eventually: conditions that must become true in time")
    print(f"   • Beautiful, poetic violation messages\n")

    print(f"{Color.MAGENTA}Time itself is now your debugging tool.{Color.RESET}")
    print(f"{Color.MAGENTA}The past, present, and future unite to guide you.{Color.RESET}\n")

    print(f"{Color.MAGENTA}{Color.BOLD}{'═'*70}{Color.RESET}\n")


def main():
    """Run the complete demo."""
    print(f"\n{Color.MAGENTA}{Color.BOLD}{'═'*70}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}     🚀 LAMENT TEMPORAL ADVANCED FEATURES - COMPLETE DEMO 🚀{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'═'*70}{Color.RESET}\n")

    print(f"{Color.CYAN}This demo will showcase two revolutionary features:{Color.RESET}\n")
    print(f"{Color.YELLOW}1. CAUSAL DEBUGGING{Color.RESET} - Ask WHY any value is what it is")
    print(f"{Color.YELLOW}2. TEMPORAL CONTRACTS{Color.RESET} - Enforce invariants across time\n")

    input(f"{Color.GREEN}Press Enter to begin the journey...{Color.RESET}")

    try:
        # Run all demos
        demo_basic_causal()
        demo_complex_causal()
        demo_fibonacci_causal()
        demo_invariant_contracts()
        demo_eventually_contracts()
        demo_ensures_contracts()
        demo_combined_features()

        # Grand finale
        print_finale()

    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Demo interrupted. Time waits for no one.{Color.RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
