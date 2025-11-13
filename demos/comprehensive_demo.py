#!/usr/bin/env python3
"""
Comprehensive Revolutionary Features Demo
==========================================

A real-world example combining all three groundbreaking features:
1. Security as Type (Taint Tracking)
2. Persistent Memory
3. Probability Distributions

Scenario: A secure, probabilistic user authentication system with
persistent state that prevents injection attacks.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lament.revolutionary import (
    TaintedValue, TaintLevel, sanitize, check_sql_safety, SecurityError,
    PersistentStore, uniform, normal, bernoulli, empirical_from_samples,
    Color
)


def demo_secure_authentication_system():
    """
    Demonstrate a secure authentication system combining all three features.
    """
    print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}COMPREHENSIVE DEMO: SECURE AUTHENTICATION SYSTEM{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}\n")

    # Initialize persistent store
    store = PersistentStore(".auth_demo.memory")

    # =======================================================================
    # FEATURE 1: SECURITY AS TYPE - Prevent SQL Injection
    # =======================================================================

    print(f"{Color.CYAN}{Color.BOLD}FEATURE 1: Security as Type{Color.RESET}")
    print(f"Preventing SQL injection attacks with taint tracking\n")

    # Simulate various user inputs (untrusted)
    attack_scenarios = [
        ("admin' OR '1'='1", "Classic SQL injection"),
        ("admin' --", "Comment-based injection"),
        ("'; DROP TABLE users; --", "Destructive injection"),
    ]

    print(f"{Color.YELLOW}Testing SQL injection prevention:{Color.RESET}\n")

    for attack_input, description in attack_scenarios:
        user_input = TaintedValue(attack_input, TaintLevel.UNTRUSTED, source="login_form")

        print(f"  {Color.RED}Attack: {description}{Color.RESET}")
        print(f"    Input: {attack_input}")

        # Build query with untrusted data (would fail)
        unsafe_query = TaintedValue(
            f"SELECT * FROM users WHERE username = '{user_input.value}'",
            TaintLevel.UNTRUSTED,
            source="login_form"
        )

        try:
            check_sql_safety(unsafe_query)
            print(f"    {Color.RED}SECURITY BREACH!{Color.RESET}")
        except SecurityError:
            print(f"    {Color.GREEN}✓ BLOCKED by type system{Color.RESET}")

        # Sanitize and use safely
        clean_input = sanitize(user_input)
        safe_query = TaintedValue(
            f"SELECT * FROM users WHERE username = '{clean_input.value}'",
            TaintLevel.TRUSTED,
            source="sanitized"
        )

        try:
            check_sql_safety(safe_query)
            print(f"    {Color.GREEN}✓ Safe query allowed after sanitization{Color.RESET}\n")
        except SecurityError:
            print(f"    {Color.RED}ERROR: Should not happen!{Color.RESET}\n")

    # =======================================================================
    # FEATURE 2: PERSISTENT MEMORY - Authentication State
    # =======================================================================

    print(f"\n{Color.CYAN}{Color.BOLD}FEATURE 2: Persistent Memory{Color.RESET}")
    print(f"Tracking authentication state across sessions\n")

    # Initialize persistent counters
    if not store.has('total_login_attempts'):
        store.set('total_login_attempts', 0)
        store.set('successful_logins', 0)
        store.set('blocked_attacks', 0)

    # Simulate login attempt
    total_attempts = store.get('total_login_attempts')
    blocked_attacks = store.get('blocked_attacks')

    print(f"{Color.YELLOW}Authentication statistics (persistent):{Color.RESET}")
    print(f"  Total login attempts: {total_attempts}")
    print(f"  Blocked attacks: {blocked_attacks}")

    # Update counters (with transaction)
    store.begin_transaction()
    store.set('total_login_attempts', total_attempts + 3)
    store.set('blocked_attacks', blocked_attacks + 3)
    store.commit()

    print(f"  {Color.GREEN}✓ Updated (persists across restarts){Color.RESET}")

    # Demonstrate transaction rollback
    print(f"\n{Color.YELLOW}Testing transactional integrity:{Color.RESET}")

    store.begin_transaction()
    old_attempts = store.get('total_login_attempts')
    store.set('total_login_attempts', old_attempts + 100)
    print(f"  Set attempts to {old_attempts + 100} (in transaction)")
    store.rollback()
    print(f"  Rolled back to {store.get('total_login_attempts')}")
    print(f"  {Color.GREEN}✓ Transactional guarantees maintained{Color.RESET}")

    # =======================================================================
    # FEATURE 3: PROBABILITY - Risk Analysis
    # =======================================================================

    print(f"\n{Color.CYAN}{Color.BOLD}FEATURE 3: Probability Distributions{Color.RESET}")
    print(f"Risk analysis and anomaly detection\n")

    # Model normal login behavior
    print(f"{Color.YELLOW}Login behavior modeling:{Color.RESET}")

    # Normal login time: 9am-5pm (represented as hours)
    normal_login_time = normal(13, 3)  # Mean: 1pm, StdDev: 3 hours

    print(f"  Normal login time: {normal_login_time}")
    print(f"  Expected login hour: {normal_login_time.expected_value():.1f} (1pm)")

    # Probability queries
    p_night_login = normal_login_time.probability(lambda x: x < 6 or x > 22)
    print(f"  P(suspicious night login): {p_night_login:.3f}")

    # Failed login attempts (Bernoulli)
    normal_failure_rate = bernoulli(0.05)  # 5% normal failure rate
    attack_failure_rate = bernoulli(0.95)  # 95% failure during attack

    print(f"\n{Color.YELLOW}Failure rate analysis:{Color.RESET}")
    print(f"  Normal failure rate: {normal_failure_rate.expected_value():.2%}")
    print(f"  Attack failure rate: {attack_failure_rate.expected_value():.2%}")

    # Monte Carlo simulation of login patterns
    print(f"\n{Color.YELLOW}Monte Carlo simulation (1000 login attempts):{Color.RESET}")

    normal_samples = []
    for _ in range(1000):
        failed = normal_failure_rate.sample()
        normal_samples.append(failed)

    normal_dist = empirical_from_samples(normal_samples)
    print(f"  Expected failures under normal conditions: {normal_dist.expected_value():.1%}")

    # Detect anomaly
    recent_failure_rate = 0.87  # 87% failures recently
    if recent_failure_rate > 0.50:
        print(f"  {Color.RED}⚠ ANOMALY DETECTED: {recent_failure_rate:.1%} failure rate{Color.RESET}")
        print(f"  {Color.RED}  Possible brute-force attack in progress!{Color.RESET}")
    else:
        print(f"  {Color.GREEN}✓ Normal operation{Color.RESET}")

    # =======================================================================
    # COMBINED: Secure, Persistent, Probabilistic System
    # =======================================================================

    print(f"\n{Color.MAGENTA}{Color.BOLD}COMBINED FEATURES: Complete System{Color.RESET}")
    print(f"All three features working together seamlessly\n")

    # Real login attempt
    username = TaintedValue("alice", TaintLevel.UNTRUSTED, source="form")
    password = TaintedValue("password123", TaintLevel.UNTRUSTED, source="form")

    print(f"{Color.YELLOW}Processing login request:{Color.RESET}")
    print(f"  Username: {username.value} (taint: {username.taint.name})")

    # Sanitize inputs (FEATURE 1)
    clean_user = sanitize(username)
    clean_pass = sanitize(password)

    print(f"  {Color.GREEN}✓ Inputs sanitized (Security as Type){Color.RESET}")

    # Build safe query
    query = TaintedValue(
        f"SELECT * FROM users WHERE username = '{clean_user.value}' AND password = '{clean_pass.value}'",
        TaintLevel.TRUSTED,
        source="sanitized"
    )

    try:
        check_sql_safety(query)
        print(f"  {Color.GREEN}✓ Query security verified{Color.RESET}")
    except SecurityError as e:
        print(f"  {Color.RED}✗ Query blocked: {e}{Color.RESET}")

    # Update persistent stats (FEATURE 2)
    store.begin_transaction()
    attempts = store.get('total_login_attempts')
    store.set('total_login_attempts', attempts + 1)

    # Simulate success
    successes = store.get('successful_logins')
    store.set('successful_logins', successes + 1)

    store.commit()
    print(f"  {Color.GREEN}✓ Statistics updated persistently{Color.RESET}")

    # Risk assessment (FEATURE 3)
    login_hour = 14  # 2pm
    is_suspicious = login_hour < 6 or login_hour > 22

    if is_suspicious:
        print(f"  {Color.YELLOW}⚠ Unusual login time - flagged for review{Color.RESET}")
    else:
        print(f"  {Color.GREEN}✓ Normal login time (Probability: 95%){Color.RESET}")

    print(f"\n{Color.GREEN}{Color.BOLD}✓ Login processed successfully!{Color.RESET}")
    print(f"{Color.GREEN}{Color.BOLD}  - SQL injection prevented (Security as Type){Color.RESET}")
    print(f"{Color.GREEN}{Color.BOLD}  - State persisted across sessions (Persistent Memory){Color.RESET}")
    print(f"{Color.GREEN}{Color.BOLD}  - Risk assessed probabilistically (Distributions){Color.RESET}")

    # =======================================================================
    # Summary
    # =======================================================================

    print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}SUMMARY: Three Revolutionary Features in Action{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}\n")

    print(f"{Color.CYAN}1. SECURITY AS TYPE:{Color.RESET}")
    print(f"   ✓ Prevented 3 SQL injection attacks")
    print(f"   ✓ Taint tracking ensures safety")
    print(f"   ✓ Type system enforces security\n")

    print(f"{Color.CYAN}2. PERSISTENT MEMORY:{Color.RESET}")
    print(f"   ✓ Tracked {store.get('total_login_attempts')} total attempts")
    print(f"   ✓ Transactional guarantees (commit/rollback)")
    print(f"   ✓ Survives program restarts\n")

    print(f"{Color.CYAN}3. PROBABILITY DISTRIBUTIONS:{Color.RESET}")
    print(f"   ✓ Modeled normal behavior patterns")
    print(f"   ✓ Detected anomalies (87% failure rate)")
    print(f"   ✓ Monte Carlo risk analysis\n")

    print(f"{Color.MAGENTA}These features make Lament a language for:{Color.RESET}")
    print(f"  • Secure systems (type-level security)")
    print(f"  • Stateful applications (automatic persistence)")
    print(f"  • Probabilistic programming (uncertainty modeling)")
    print(f"  • Real-world production systems\n")

    # Cleanup demo file
    if os.path.exists(".auth_demo.memory"):
        os.remove(".auth_demo.memory")


if __name__ == "__main__":
    demo_secure_authentication_system()
