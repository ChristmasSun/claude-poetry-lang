"""
Unit tests for Lament Temporal Advanced Features

Tests both CAUSAL DEBUGGING and TEMPORAL CONTRACTS functionality.
"""

import pytest
import sys
from lament.temporal_advanced import (
    CausalValue, CausalOrigin, create_causal_variable,
    why, track_operation,
    ContractManager, ContractViolation,
    Invariant, Ensures, Eventually
)


# ============================================================================
# CAUSAL DEBUGGING TESTS
# ============================================================================

class TestCausalValue:
    """Tests for CausalValue and causal tracking."""

    def test_create_causal_variable(self):
        """Test creating a causal variable."""
        cv = create_causal_variable("x", 10, "x = 10", line=1)
        assert cv.current == 10
        assert cv.name == "x"
        assert len(cv.causal_history) == 1
        assert cv.causal_history[0].value == 10
        assert cv.causal_history[0].line == 1

    def test_assign_with_cause(self):
        """Test assigning with causal tracking."""
        cv = create_causal_variable("x", 10)
        cv.assign_with_cause(20, "x = x + 10", line=2,
                           dependencies={"x@past": 10, "literal": 10},
                           operation="+")

        assert cv.current == 20
        assert len(cv.causal_history) == 2
        assert cv.causal_history[1].expression == "x = x + 10"
        assert cv.causal_history[1].dependencies == {"x@past": 10, "literal": 10}
        assert cv.causal_history[1].operation == "+"

    def test_causal_chain(self):
        """Test building a causal chain."""
        cv = create_causal_variable("x", 5)
        cv.assign_with_cause(10, "x = x + 5", dependencies={"x@past": 5})
        cv.assign_with_cause(20, "x = x * 2", dependencies={"x@past": 10})
        cv.assign_with_cause(25, "x = x + 5", dependencies={"x@past": 20})

        chain = cv.get_causal_chain()
        assert len(chain) == 4  # Initial + 3 assignments
        assert chain[0].value == 5
        assert chain[3].value == 20  # Last value before current

    def test_why_function(self):
        """Test the why() function."""
        cv = create_causal_variable("counter", 0, "counter = 0", line=1)
        cv.assign_with_cause(1, "counter = counter + 1", line=2,
                           dependencies={"counter@past": 0})

        result = why(cv)
        assert isinstance(result, str)
        assert "counter" in result
        assert "CAUSAL TRACE" in result
        assert "Current value: 1" in result

    def test_why_with_non_causal(self):
        """Test why() with non-causal values."""
        result = why(42)
        assert "Not a tracked variable" in result

    def test_nested_dependencies(self):
        """Test tracking nested dependencies."""
        a = create_causal_variable("a", 10, line=1)
        b = create_causal_variable("b", 20, line=2)

        c_value = a.current + b.current
        c = create_causal_variable("c", c_value, "c = a + b", line=3)
        c.causal_history.append(CausalOrigin(
            value=c_value,
            expression="a + b",
            line=3,
            dependencies={"a": a, "b": b},
            operation="+"
        ))

        result = why(c)
        assert "a" in result
        assert "b" in result
        assert "30" in str(c.current)


class TestTrackOperation:
    """Tests for operation tracking helper."""

    def test_track_simple_operation(self):
        """Test tracking a simple operation."""
        result = track_operation(
            15,
            "+",
            {"x": 10, "y": 5},
            "x + y",
            line=42
        )

        assert result.current == 15
        assert len(result.causal_history) == 1
        assert result.causal_history[0].operation == "+"
        assert result.causal_history[0].line == 42


# ============================================================================
# TEMPORAL CONTRACTS TESTS
# ============================================================================

class TestInvariant:
    """Tests for Invariant contracts."""

    def test_invariant_creation(self):
        """Test creating an invariant."""
        inv = Invariant(
            lambda s: s.get('x', 0) > 0,
            "x > 0",
            "positive x"
        )
        assert inv.condition_str == "x > 0"
        assert inv.name == "positive x"
        assert inv.active is True

    def test_invariant_satisfied(self):
        """Test invariant that is satisfied."""
        inv = Invariant(lambda s: s.get('x', 0) > 0, "x > 0")
        assert inv.check({'x': 10}) is True

    def test_invariant_violated(self):
        """Test invariant that is violated."""
        inv = Invariant(lambda s: s.get('x', 0) > 0, "x > 0")
        assert inv.check({'x': -5}) is False

    def test_invariant_activate_deactivate(self):
        """Test activating/deactivating invariants."""
        inv = Invariant(lambda s: True, "always true")
        assert inv.active is True

        inv.deactivate()
        assert inv.active is False

        inv.activate()
        assert inv.active is True


class TestEnsures:
    """Tests for Ensures contracts."""

    def test_ensures_creation(self):
        """Test creating an ensures contract."""
        ens = Ensures(
            lambda s: s.get('result', 0) > 0,
            "result > 0",
            "positive result"
        )
        assert ens.condition_str == "result > 0"

    def test_ensures_satisfied(self):
        """Test ensures contract that is satisfied."""
        ens = Ensures(lambda s: s.get('result', 0) == 42, "result == 42")
        assert ens.check({'result': 42}) is True

    def test_ensures_violated(self):
        """Test ensures contract that is violated."""
        ens = Ensures(lambda s: s.get('result', 0) == 42, "result == 42")
        assert ens.check({'result': 0}) is False


class TestEventually:
    """Tests for Eventually contracts."""

    def test_eventually_creation(self):
        """Test creating an eventually contract."""
        evt = Eventually(
            10,
            lambda s: s.get('x', 0) > 100,
            "x > 100",
            "x reaches 100"
        )
        assert evt.steps == 10
        assert evt.remaining == 10
        assert evt.condition_str == "x > 100"

    def test_eventually_satisfied_in_time(self):
        """Test eventually contract satisfied within time limit."""
        evt = Eventually(5, lambda s: s.get('x', 0) >= 10, "x >= 10")

        # Not satisfied yet
        assert evt.tick({'x': 0}) is False
        assert evt.remaining == 4

        assert evt.tick({'x': 5}) is False
        assert evt.remaining == 3

        # Satisfied!
        assert evt.tick({'x': 10}) is True
        assert evt.remaining == 5  # Reset

    def test_eventually_timeout(self):
        """Test eventually contract that times out."""
        evt = Eventually(3, lambda s: s.get('x', 0) >= 100, "x >= 100")

        with pytest.raises(ContractViolation) as exc_info:
            evt.tick({'x': 10})
            evt.tick({'x': 20})
            evt.tick({'x': 30})  # Time's up!

        assert "Eventually" in str(exc_info.value)
        assert "time ran out" in str(exc_info.value).lower()

    def test_eventually_history(self):
        """Test that eventually tracks history."""
        evt = Eventually(3, lambda s: s.get('x', 0) >= 10, "x >= 10")

        evt.tick({'x': 5})
        evt.tick({'x': 7})

        assert len(evt.history) == 2
        assert evt.history[0]['step'] == 1
        assert evt.history[1]['step'] == 2


class TestContractManager:
    """Tests for ContractManager."""

    def test_manager_creation(self):
        """Test creating a contract manager."""
        manager = ContractManager()
        assert len(manager.invariants) == 0
        assert len(manager.ensures) == 0
        assert len(manager.eventually) == 0
        assert manager.step_count == 0

    def test_add_invariant(self):
        """Test adding an invariant."""
        manager = ContractManager()
        inv = manager.add_invariant(lambda s: True, "always true")

        assert len(manager.invariants) == 1
        assert isinstance(inv, Invariant)

    def test_add_ensures(self):
        """Test adding an ensures contract."""
        manager = ContractManager()
        ens = manager.add_ensures(lambda s: True, "always true")

        assert len(manager.ensures) == 1
        assert isinstance(ens, Ensures)

    def test_add_eventually(self):
        """Test adding an eventually contract."""
        manager = ContractManager()
        evt = manager.add_eventually(10, lambda s: True, "always true")

        assert len(manager.eventually) == 1
        assert isinstance(evt, Eventually)

    def test_check_invariants_success(self):
        """Test checking invariants that pass."""
        manager = ContractManager()
        manager.add_invariant(lambda s: s.get('x', 0) > 0, "x > 0")

        # Should not raise
        manager.check_invariants({'x': 10})

    def test_check_invariants_failure(self):
        """Test checking invariants that fail."""
        manager = ContractManager()
        manager.add_invariant(lambda s: s.get('x', 0) > 0, "x > 0")

        with pytest.raises(ContractViolation) as exc_info:
            manager.check_invariants({'x': -5}, 'x')

        assert "Invariant" in str(exc_info.value)
        assert "invariant shattered" in str(exc_info.value).lower()

    def test_check_ensures_success(self):
        """Test checking ensures contracts that pass."""
        manager = ContractManager()
        manager.add_ensures(lambda s: s.get('result', 0) == 42, "result == 42")

        # Should not raise
        manager.check_ensures({'result': 42}, 'my_func')

    def test_check_ensures_failure(self):
        """Test checking ensures contracts that fail."""
        manager = ContractManager()
        manager.add_ensures(lambda s: s.get('result', 0) == 42, "result == 42")

        with pytest.raises(ContractViolation) as exc_info:
            manager.check_ensures({'result': 0}, 'my_func')

        assert "Ensures" in str(exc_info.value)
        assert "keeping its word" in str(exc_info.value).lower()

    def test_step_tracking(self):
        """Test that steps are tracked correctly."""
        manager = ContractManager()
        assert manager.step_count == 0

        manager.step({'x': 1})
        assert manager.step_count == 1

        manager.step({'x': 2})
        assert manager.step_count == 2

    def test_step_with_eventually(self):
        """Test step() with eventually contracts."""
        manager = ContractManager()
        manager.add_eventually(3, lambda s: s.get('x', 0) >= 10, "x >= 10")

        # Should not raise yet
        manager.step({'x': 5})
        manager.step({'x': 10})  # Satisfied!

        # Eventually should be satisfied, no exception

    def test_clear_eventually(self):
        """Test clearing eventually contracts."""
        manager = ContractManager()
        manager.add_eventually(5, lambda s: True, "always true")
        assert len(manager.eventually) == 1

        manager.clear_eventually()
        assert len(manager.eventually) == 0

    def test_summary(self):
        """Test contract summary."""
        manager = ContractManager()
        manager.add_invariant(lambda s: True, "inv1")
        manager.add_ensures(lambda s: True, "ens1")
        manager.add_eventually(5, lambda s: True, "evt1")
        manager.step({})

        summary = manager.summary()
        assert "Invariants: 1" in summary
        assert "Ensures: 1" in summary
        assert "Eventually: 1" in summary
        assert "Total steps: 1" in summary


class TestContractViolation:
    """Tests for ContractViolation exception."""

    def test_violation_creation(self):
        """Test creating a contract violation."""
        inv = Invariant(lambda s: False, "x > 0")
        context = {'x': -5}
        violation = ContractViolation(inv, context)

        assert violation.contract == inv
        assert violation.context == context

    def test_violation_message_format(self):
        """Test that violation messages are formatted beautifully."""
        inv = Invariant(lambda s: False, "balance >= 0")
        violation = ContractViolation(inv, {'balance': -100})

        message = str(violation)
        assert "TEMPORAL CONTRACT VIOLATED" in message
        assert "Invariant" in message
        assert "balance >= 0" in message

    def test_violation_with_history(self):
        """Test violation messages include history."""
        evt = Eventually(3, lambda s: False, "x >= 10")
        context = {'x': 5}
        history = ["Step 1: False", "Step 2: False", "Step 3: False"]
        violation = ContractViolation(evt, context, history)

        message = str(violation)
        assert "Recent History" in message
        assert "Step 1: False" in message


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegration:
    """Integration tests combining causal debugging and contracts."""

    def test_causal_with_invariant_violation(self):
        """Test that we can trace causality when invariant is violated."""
        manager = ContractManager()
        manager.add_invariant(lambda s: s.get('x', 0) <= 100, "x <= 100")

        x = create_causal_variable("x", 0)
        x.assign_with_cause(50, "x = 50", dependencies={})
        x.assign_with_cause(150, "x = 150", dependencies={})  # Violates!

        scope = {'x': x.current}

        # Should raise violation
        with pytest.raises(ContractViolation):
            manager.check_invariants(scope, 'x')

        # But we can still trace causality
        trace = why(x)
        assert "150" in trace
        assert "CAUSAL TRACE" in trace

    def test_multiple_contracts_on_same_variable(self):
        """Test multiple contracts on the same variable."""
        manager = ContractManager()
        manager.add_invariant(lambda s: s.get('x', 0) >= 0, "x >= 0")
        manager.add_invariant(lambda s: s.get('x', 0) <= 100, "x <= 100")

        # Both satisfied
        manager.check_invariants({'x': 50})

        # First violated
        with pytest.raises(ContractViolation):
            manager.check_invariants({'x': -10})

        # Second violated
        with pytest.raises(ContractViolation):
            manager.check_invariants({'x': 200})

    def test_contract_deactivation(self):
        """Test that deactivated contracts are not checked."""
        manager = ContractManager()
        inv = manager.add_invariant(lambda s: s.get('x', 0) > 0, "x > 0")

        # Should raise
        with pytest.raises(ContractViolation):
            manager.check_invariants({'x': -5})

        # Deactivate
        inv.deactivate()

        # Should not raise
        manager.check_invariants({'x': -5})


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
