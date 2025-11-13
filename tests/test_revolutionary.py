#!/usr/bin/env python3
"""
Test Suite for Revolutionary Features
======================================

Comprehensive tests for:
1. Security as Type (Taint Tracking)
2. Persistent Memory
3. Probability Distributions
"""

import unittest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lament.revolutionary import (
    TaintedValue, TaintLevel, sanitize, check_sql_safety, SecurityError,
    taint_propagate, unwrap_tainted, get_taint,
    PersistentStore,
    Distribution, DistributionType, uniform, normal, bernoulli,
    empirical_from_samples
)


class TestTaintTracking(unittest.TestCase):
    """Test security taint tracking features."""

    def test_tainted_value_creation(self):
        """Test creating tainted values."""
        trusted = TaintedValue("safe", TaintLevel.TRUSTED, source="literal")
        self.assertEqual(trusted.taint, TaintLevel.TRUSTED)
        self.assertEqual(trusted.value, "safe")

        untrusted = TaintedValue("dangerous", TaintLevel.UNTRUSTED, source="user_input")
        self.assertEqual(untrusted.taint, TaintLevel.UNTRUSTED)
        self.assertEqual(untrusted.value, "dangerous")

    def test_taint_propagation(self):
        """Test that taint propagates correctly."""
        trusted = TaintedValue("safe", TaintLevel.TRUSTED)
        untrusted = TaintedValue("unsafe", TaintLevel.UNTRUSTED)

        # Trusted + Trusted = Trusted
        result = taint_propagate(trusted, trusted, "+")
        self.assertEqual(result, TaintLevel.TRUSTED)

        # Untrusted + Trusted = Untrusted
        result = taint_propagate(untrusted, trusted, "+")
        self.assertEqual(result, TaintLevel.UNTRUSTED)

        # Trusted + Untrusted = Untrusted
        result = taint_propagate(trusted, untrusted, "+")
        self.assertEqual(result, TaintLevel.UNTRUSTED)

        # Untrusted + Untrusted = Untrusted
        result = taint_propagate(untrusted, untrusted, "+")
        self.assertEqual(result, TaintLevel.UNTRUSTED)

    def test_sanitize(self):
        """Test sanitization converts untrusted to trusted."""
        untrusted = TaintedValue("admin' OR '1'='1", TaintLevel.UNTRUSTED, source="user")
        sanitized = sanitize(untrusted)

        self.assertIsInstance(sanitized, TaintedValue)
        self.assertEqual(sanitized.taint, TaintLevel.TRUSTED)
        # Check that quotes are escaped
        self.assertIn("''", sanitized.value)

    def test_sql_injection_prevention(self):
        """Test SQL injection prevention."""
        # Safe query (trusted)
        safe_query = TaintedValue("SELECT * FROM users", TaintLevel.TRUSTED)
        try:
            check_sql_safety(safe_query)
            # Should not raise
        except SecurityError:
            self.fail("Safe query should not raise SecurityError")

        # Dangerous query (untrusted)
        dangerous_query = TaintedValue(
            "SELECT * FROM users WHERE name = 'admin' OR '1'='1'",
            TaintLevel.UNTRUSTED,
            source="user_input"
        )
        with self.assertRaises(SecurityError):
            check_sql_safety(dangerous_query)

    def test_unwrap_tainted(self):
        """Test unwrapping tainted values."""
        tainted = TaintedValue(42, TaintLevel.UNTRUSTED)
        self.assertEqual(unwrap_tainted(tainted), 42)

        # Unwrapping non-tainted value returns it as-is
        self.assertEqual(unwrap_tainted(42), 42)
        self.assertEqual(unwrap_tainted("hello"), "hello")

    def test_get_taint(self):
        """Test getting taint level."""
        tainted = TaintedValue(42, TaintLevel.UNTRUSTED)
        self.assertEqual(get_taint(tainted), TaintLevel.UNTRUSTED)

        # Non-tainted values are considered trusted
        self.assertEqual(get_taint(42), TaintLevel.TRUSTED)
        self.assertEqual(get_taint("hello"), TaintLevel.TRUSTED)

    def test_html_escaping(self):
        """Test HTML escaping in sanitization."""
        xss_attack = TaintedValue("<script>alert('XSS')</script>", TaintLevel.UNTRUSTED)
        sanitized = sanitize(xss_attack)

        self.assertIn("&lt;", sanitized.value)
        self.assertIn("&gt;", sanitized.value)
        self.assertEqual(sanitized.taint, TaintLevel.TRUSTED)


class TestPersistentMemory(unittest.TestCase):
    """Test persistent memory features."""

    def setUp(self):
        """Create test persistent store."""
        self.test_file = ".test_persistence.memory"
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.store = PersistentStore(self.test_file)

    def tearDown(self):
        """Clean up test file."""
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_set_and_get(self):
        """Test basic set/get operations."""
        self.store.set("counter", 42)
        self.assertEqual(self.store.get("counter"), 42)

    def test_persistence_across_instances(self):
        """Test that data persists across store instances."""
        self.store.set("persistent_value", 123)
        del self.store

        # Create new store instance
        new_store = PersistentStore(self.test_file)
        self.assertEqual(new_store.get("persistent_value"), 123)

    def test_has(self):
        """Test checking variable existence."""
        self.assertFalse(self.store.has("nonexistent"))
        self.store.set("exists", True)
        self.assertTrue(self.store.has("exists"))

    def test_delete(self):
        """Test deleting variables."""
        self.store.set("to_delete", 42)
        self.assertTrue(self.store.has("to_delete"))

        self.store.delete("to_delete")
        self.assertFalse(self.store.has("to_delete"))

    def test_transaction_commit(self):
        """Test transaction commit."""
        self.store.begin_transaction()
        self.store.set("tx_var", 100)
        self.store.commit()

        # Value should be persisted
        new_store = PersistentStore(self.test_file)
        self.assertEqual(new_store.get("tx_var"), 100)

    def test_transaction_rollback(self):
        """Test transaction rollback."""
        self.store.set("initial", 50)

        self.store.begin_transaction()
        self.store.set("initial", 100)
        self.store.set("new_var", 200)
        self.store.rollback()

        # Changes should be reverted
        self.assertEqual(self.store.get("initial"), 50)
        self.assertFalse(self.store.has("new_var"))

    def test_persistent_tainted_values(self):
        """Test persisting tainted values."""
        tainted = TaintedValue("data", TaintLevel.UNTRUSTED, source="user")
        self.store.set("tainted_var", tainted)

        # Reload
        new_store = PersistentStore(self.test_file)
        loaded = new_store.get("tainted_var")

        self.assertIsInstance(loaded, TaintedValue)
        self.assertEqual(loaded.value, "data")
        self.assertEqual(loaded.taint, TaintLevel.UNTRUSTED)
        self.assertEqual(loaded.source, "user")


class TestProbabilityDistributions(unittest.TestCase):
    """Test probability distribution features."""

    def test_uniform_distribution(self):
        """Test uniform distribution."""
        dist = uniform(0, 10)
        self.assertEqual(dist.dist_type, DistributionType.UNIFORM)
        self.assertEqual(dist.expected_value(), 5.0)

        # Test sampling is in range
        for _ in range(100):
            sample = dist.sample()
            self.assertGreaterEqual(sample, 0)
            self.assertLessEqual(sample, 10)

    def test_normal_distribution(self):
        """Test normal distribution."""
        dist = normal(100, 15)
        self.assertEqual(dist.dist_type, DistributionType.NORMAL)
        self.assertEqual(dist.expected_value(), 100.0)

        # Test sampling (most samples should be near mean)
        samples = [dist.sample() for _ in range(1000)]
        mean = sum(samples) / len(samples)
        self.assertAlmostEqual(mean, 100, delta=5)

    def test_bernoulli_distribution(self):
        """Test Bernoulli distribution."""
        dist = bernoulli(0.7)
        self.assertEqual(dist.dist_type, DistributionType.BERNOULLI)
        self.assertEqual(dist.expected_value(), 0.7)

        # Test sampling (should be 0 or 1)
        for _ in range(100):
            sample = dist.sample()
            self.assertIn(sample, [0.0, 1.0])

        # Test probability (~70% should be 1)
        samples = [dist.sample() for _ in range(1000)]
        proportion = sum(samples) / len(samples)
        self.assertAlmostEqual(proportion, 0.7, delta=0.1)

    def test_bernoulli_validation(self):
        """Test Bernoulli parameter validation."""
        with self.assertRaises(ValueError):
            bernoulli(-0.1)  # Invalid: p < 0

        with self.assertRaises(ValueError):
            bernoulli(1.5)  # Invalid: p > 1

    def test_empirical_distribution(self):
        """Test empirical distribution from samples."""
        samples = [1.0, 2.0, 3.0, 4.0, 5.0]
        dist = empirical_from_samples(samples)

        self.assertEqual(dist.dist_type, DistributionType.EMPIRICAL)
        self.assertEqual(dist.expected_value(), 3.0)

        # Samples should come from the original list
        for _ in range(100):
            sample = dist.sample()
            self.assertIn(sample, samples)

    def test_probability_query(self):
        """Test probability queries using Monte Carlo."""
        dist = uniform(0, 10)

        # P(X > 5) should be ~0.5
        p = dist.probability(lambda x: x > 5)
        self.assertAlmostEqual(p, 0.5, delta=0.05)

        # P(X > 9) should be ~0.1
        p = dist.probability(lambda x: x > 9)
        self.assertAlmostEqual(p, 0.1, delta=0.05)

    def test_distribution_str(self):
        """Test string representation of distributions."""
        u = uniform(0, 10)
        self.assertIn("Uniform", str(u))
        self.assertIn("0", str(u))
        self.assertIn("10", str(u))

        n = normal(100, 15)
        self.assertIn("Normal", str(n))
        self.assertIn("100", str(n))
        self.assertIn("15", str(n))

        b = bernoulli(0.5)
        self.assertIn("Bernoulli", str(b))
        self.assertIn("0.5", str(b))


class TestIntegration(unittest.TestCase):
    """Integration tests combining multiple features."""

    def test_tainted_persistent_values(self):
        """Test storing tainted values persistently."""
        test_file = ".test_integration.memory"
        if os.path.exists(test_file):
            os.remove(test_file)

        try:
            store = PersistentStore(test_file)

            # Store untrusted data persistently
            user_input = TaintedValue("admin' OR '1'='1", TaintLevel.UNTRUSTED, source="form")
            store.set("user_data", user_input)

            # Reload and verify taint is preserved
            new_store = PersistentStore(test_file)
            loaded = new_store.get("user_data")

            self.assertIsInstance(loaded, TaintedValue)
            self.assertEqual(loaded.taint, TaintLevel.UNTRUSTED)

            # Should still fail SQL safety check
            with self.assertRaises(SecurityError):
                check_sql_safety(loaded)

        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_distribution_statistics(self):
        """Test statistical properties of distributions."""
        # Test that normal distribution samples follow expected properties
        dist = normal(100, 15)
        samples = [dist.sample() for _ in range(10000)]

        # Calculate mean and std dev
        mean = sum(samples) / len(samples)
        variance = sum((x - mean) ** 2 for x in samples) / len(samples)
        std_dev = variance ** 0.5

        # Should be close to parameters
        self.assertAlmostEqual(mean, 100, delta=1)
        self.assertAlmostEqual(std_dev, 15, delta=1)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == "__main__":
    run_tests()
