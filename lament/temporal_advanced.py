"""
Lament Language: Temporal Advanced Features
===========================================

REVOLUTIONARY FEATURES:

1. CAUSAL DEBUGGING - Trace the WHY of every computation
   - Every assignment remembers its source and dependencies
   - `why(variable)` shows the complete causal chain
   - See the computational lineage of any value

2. TEMPORAL CONTRACTS - Enforce invariants across time
   - `invariant` - conditions that must ALWAYS hold
   - `ensures` - post-conditions that must be satisfied
   - `eventually(n)` - conditions that must become true within N steps
   - Beautiful, poetic violation messages

These features make time itself a first-class debugging tool.

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import sys
import time
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Callable, Set
from lament.types import TimelineValue, Color, bell


# ============================================================================
# CAUSAL TRACKING - Know the WHY of every value
# ============================================================================

@dataclass
class CausalOrigin:
    """Tracks the origin of a single value assignment.

    This captures not just WHAT a value is, but WHY it became that value.
    Every computation leaves a trail through time.

    Attributes:
        value: The actual value assigned
        expression: The source expression that created this value
        line: Line number in source code (if available)
        timestamp: When this assignment occurred
        dependencies: Which variables/values contributed to this computation
        operation: The operation performed ('+', '-', 'function_call', etc.)
    """
    value: Any
    expression: str = ""
    line: Optional[int] = None
    timestamp: float = field(default_factory=time.time)
    dependencies: Dict[str, Any] = field(default_factory=dict)
    operation: Optional[str] = None

    def __repr__(self):
        deps = ', '.join(f"{k}={v}" for k, v in self.dependencies.items())
        loc = f" [line {self.line}]" if self.line else ""
        return f"{self.expression} → {self.value}{loc} (deps: {deps})"


@dataclass
class CausalValue(TimelineValue):
    """A value that remembers not just its history, but the WHY of its history.

    Extends TimelineValue with complete causal tracking. Every assignment
    is annotated with its source expression, dependencies, and context.

    This enables revolutionary debugging: you can ask WHY any variable
    has its current value and trace the complete computational lineage.

    Attributes:
        current: Current value
        history: List of previous values
        born: When the timeline was created
        causal_history: Complete causal chain for every assignment
        name: Variable name (for debugging output)
    """
    causal_history: List[CausalOrigin] = field(default_factory=list)
    name: str = "<unnamed>"

    def assign_with_cause(self, value, expression="", line=None,
                          dependencies=None, operation=None):
        """Assign a new value with full causal tracking.

        Args:
            value: The new value
            expression: Source expression that created this value
            line: Line number in source code
            dependencies: Dict of {var_name: var_value} that contributed
            operation: The operation performed
        """
        # Store the causal origin
        origin = CausalOrigin(
            value=self.current,
            expression=expression or str(value),
            line=line,
            dependencies=dependencies or {},
            operation=operation
        )
        self.causal_history.append(origin)

        # Standard timeline assignment
        self.history.append(self.current)
        self.current = value

    def why(self, depth=0, visited=None) -> str:
        """Generate a causal explanation for the current value.

        This is the heart of causal debugging. It traces back through
        the complete computational lineage, showing:
        - What expressions created each value
        - What dependencies were involved
        - The complete chain of causation

        Args:
            depth: Current recursion depth (for formatting)
            visited: Set of visited variables (to avoid cycles)

        Returns:
            A beautifully formatted causal chain
        """
        if visited is None:
            visited = set()

        indent = "  " * depth
        lines = []

        # Header
        if depth == 0:
            lines.append(f"\n{Color.CYAN}{Color.BOLD}╔══════════════════════════════════════════════════════════╗{Color.RESET}")
            lines.append(f"{Color.CYAN}{Color.BOLD}║  🔍 CAUSAL TRACE: {self.name:<40}║{Color.RESET}")
            lines.append(f"{Color.CYAN}{Color.BOLD}╚══════════════════════════════════════════════════════════╝{Color.RESET}\n")

        # Current value
        lines.append(f"{indent}{Color.YELLOW}Current value:{Color.RESET} {Color.BOLD}{self.current}{Color.RESET}")

        if not self.causal_history:
            lines.append(f"{indent}{Color.MAGENTA}Origin:{Color.RESET} Initial value (never reassigned)")
            return "\n".join(lines)

        # Most recent assignment
        latest = self.causal_history[-1]
        lines.append(f"{indent}{Color.MAGENTA}Last assigned:{Color.RESET} {latest.expression}")
        if latest.line:
            lines.append(f"{indent}{Color.MAGENTA}Location:{Color.RESET} line {latest.line}")
        if latest.operation:
            lines.append(f"{indent}{Color.MAGENTA}Operation:{Color.RESET} {latest.operation}")

        # Dependencies
        if latest.dependencies:
            lines.append(f"{indent}{Color.GREEN}Dependencies:{Color.RESET}")
            for dep_name, dep_value in latest.dependencies.items():
                if dep_name not in visited:
                    visited.add(dep_name)
                    lines.append(f"{indent}  • {dep_name} = {dep_value}")
                    # If the dependency is also a CausalValue, recurse
                    if isinstance(dep_value, CausalValue):
                        sub_trace = dep_value.why(depth + 2, visited)
                        lines.append(sub_trace)

        # History summary
        if len(self.causal_history) > 1:
            lines.append(f"\n{indent}{Color.BLUE}Historical assignments ({len(self.causal_history)} total):{Color.RESET}")
            for i, origin in enumerate(reversed(self.causal_history[-5:])):  # Last 5
                age = len(self.causal_history) - i
                lines.append(f"{indent}  {age}. {origin.expression} → {origin.value}")

        return "\n".join(lines)

    def get_causal_chain(self) -> List[CausalOrigin]:
        """Get the complete causal chain.

        Returns:
            List of all CausalOrigin objects in chronological order
        """
        return self.causal_history.copy()


def why(variable) -> str:
    """Global function to explain the causal history of any variable.

    This is the main entry point for causal debugging. Pass any variable
    and get a complete explanation of WHY it has its current value.

    Usage:
        remember x = 5
        x = x + 3
        confess why(x)  # Shows: "x = 8 because x@past(1) was 5, added 3"

    Args:
        variable: The variable to explain (can be CausalValue or any value)

    Returns:
        A formatted causal explanation string
    """
    if isinstance(variable, CausalValue):
        return variable.why()
    elif isinstance(variable, TimelineValue):
        return (f"\n{Color.YELLOW}Variable has timeline but no causal tracking.{Color.RESET}\n"
                f"Current value: {variable.current}\n"
                f"Age: {variable.get_age()} assignments\n"
                f"Origin: {variable.get_origin()}")
    else:
        return f"\n{Color.RED}Not a tracked variable. Value: {variable}{Color.RESET}\n"


# ============================================================================
# TEMPORAL CONTRACTS - Enforce invariants across time
# ============================================================================

class ContractViolation(Exception):
    """Raised when a temporal contract is violated.

    This exception carries rich context about:
    - What contract was violated
    - When it was violated
    - The state of the system at violation time
    - Historical context
    """
    def __init__(self, contract, context, history=None):
        self.contract = contract
        self.context = context
        self.history = history or []
        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Create a beautiful, synesthetic error message."""
        lines = []
        lines.append(f"\n{Color.RED}{Color.BOLD}{'═'*70}{Color.RESET}")
        lines.append(f"{Color.RED}{Color.BOLD}║  💔 TEMPORAL CONTRACT VIOLATED 💔{' '*33}║{Color.RESET}")
        lines.append(f"{Color.RED}{Color.BOLD}{'═'*70}{Color.RESET}\n")

        # Contract type and description
        lines.append(f"{Color.CYAN}Contract Type:{Color.RESET} {Color.BOLD}{self.contract.__class__.__name__}{Color.RESET}")
        lines.append(f"{Color.CYAN}Condition:{Color.RESET} {self.contract.condition_str}")

        # Poetic description based on contract type
        if isinstance(self.contract, Invariant):
            lines.append(f"\n{Color.MAGENTA}The universe promised this would always be true,{Color.RESET}")
            lines.append(f"{Color.MAGENTA}but time has betrayed us. The invariant shattered.{Color.RESET}")
        elif isinstance(self.contract, Ensures):
            lines.append(f"\n{Color.MAGENTA}The function promised to ensure this condition,{Color.RESET}")
            lines.append(f"{Color.MAGENTA}but it returned without keeping its word.{Color.RESET}")
        elif isinstance(self.contract, Eventually):
            lines.append(f"\n{Color.MAGENTA}We waited for {self.contract.steps} steps,{Color.RESET}")
            lines.append(f"{Color.MAGENTA}but the future never arrived. Time ran out.{Color.RESET}")

        # Context
        lines.append(f"\n{Color.YELLOW}Context:{Color.RESET}")
        for key, value in self.context.items():
            lines.append(f"  {key}: {value}")

        # History (if available)
        if self.history:
            lines.append(f"\n{Color.BLUE}Recent History:{Color.RESET}")
            for i, event in enumerate(self.history[-5:], 1):
                lines.append(f"  {i}. {event}")

        lines.append(f"\n{Color.RED}{Color.BOLD}{'═'*70}{Color.RESET}\n")
        return "\n".join(lines)


class Contract:
    """Base class for all temporal contracts.

    Contracts are conditions that the program promises to uphold.
    When violated, they produce beautiful, informative error messages.
    """
    def __init__(self, condition: Callable, condition_str: str, name: str = ""):
        self.condition = condition
        self.condition_str = condition_str
        self.name = name
        self.active = True

    def check(self, scope: Dict[str, Any]) -> bool:
        """Check if the contract is satisfied.

        Args:
            scope: Current variable scope

        Returns:
            True if contract is satisfied, False otherwise
        """
        try:
            return self.condition(scope)
        except Exception as e:
            # If condition evaluation fails, treat as violation
            return False

    def deactivate(self):
        """Temporarily deactivate this contract."""
        self.active = False

    def activate(self):
        """Reactivate this contract."""
        self.active = True


class Invariant(Contract):
    """A condition that must ALWAYS be true.

    Invariants are checked on every variable assignment. They represent
    fundamental truths about your program's state that must never be violated.

    Example:
        invariant("balance >= 0", lambda s: s.get('balance', 0) >= 0)
    """
    def __init__(self, condition: Callable, condition_str: str, name: str = ""):
        super().__init__(condition, condition_str, name)


class Ensures(Contract):
    """A post-condition that must be true after a function returns.

    Ensures contracts are checked when a function exits. They guarantee
    that the function has done its job correctly.

    Example:
        ensures("result > 0", lambda s: s.get('result', 0) > 0)
    """
    def __init__(self, condition: Callable, condition_str: str, name: str = ""):
        super().__init__(condition, condition_str, name)


class Eventually(Contract):
    """A condition that must become true within N steps.

    Eventually contracts track state over time and ensure that a condition
    becomes true within a specified time window.

    Example:
        eventually(10, "x > 100", lambda s: s.get('x', 0) > 100)
    """
    def __init__(self, steps: int, condition: Callable, condition_str: str, name: str = ""):
        super().__init__(condition, condition_str, name)
        self.steps = steps
        self.remaining = steps
        self.history = []

    def tick(self, scope: Dict[str, Any]) -> bool:
        """Advance one step and check if condition is met.

        Args:
            scope: Current variable scope

        Returns:
            True if condition is satisfied, False if time ran out

        Raises:
            ContractViolation: If time runs out without condition being met
        """
        self.remaining -= 1
        satisfied = self.check(scope)

        # Record history
        self.history.append({
            'step': self.steps - self.remaining,
            'satisfied': satisfied,
            'scope_snapshot': {k: v for k, v in scope.items() if not callable(v)}
        })

        if satisfied:
            self.remaining = self.steps  # Reset for next use
            return True

        if self.remaining <= 0:
            raise ContractViolation(
                self,
                {
                    'steps_waited': self.steps,
                    'condition': self.condition_str,
                    'final_scope': {k: v for k, v in scope.items() if not callable(v)}
                },
                [f"Step {h['step']}: {h['satisfied']}" for h in self.history]
            )

        return False


class ContractManager:
    """Manages all active contracts and enforces them.

    This integrates with the interpreter to check contracts at appropriate times:
    - Invariants: On every variable mutation
    - Ensures: When functions return
    - Eventually: On each step of execution
    """
    def __init__(self):
        self.invariants: List[Invariant] = []
        self.ensures: List[Ensures] = []
        self.eventually: List[Eventually] = []
        self.step_count = 0
        self.history = []

    def add_invariant(self, condition: Callable, condition_str: str, name: str = ""):
        """Register a new invariant contract."""
        inv = Invariant(condition, condition_str, name)
        self.invariants.append(inv)
        return inv

    def add_ensures(self, condition: Callable, condition_str: str, name: str = ""):
        """Register a new ensures contract."""
        ens = Ensures(condition, condition_str, name)
        self.ensures.append(ens)
        return ens

    def add_eventually(self, steps: int, condition: Callable, condition_str: str, name: str = ""):
        """Register a new eventually contract."""
        evt = Eventually(steps, condition, condition_str, name)
        self.eventually.append(evt)
        return evt

    def check_invariants(self, scope: Dict[str, Any], changed_var: str = None):
        """Check all active invariants.

        Args:
            scope: Current variable scope
            changed_var: Name of variable that just changed (for error context)

        Raises:
            ContractViolation: If any invariant is violated
        """
        for inv in self.invariants:
            if inv.active and not inv.check(scope):
                context = {
                    'violated_by': changed_var or 'unknown',
                    'scope': {k: v for k, v in scope.items() if not callable(v)}
                }
                raise ContractViolation(inv, context, self.history[-10:])

    def check_ensures(self, scope: Dict[str, Any], function_name: str = None):
        """Check all active ensures contracts.

        Args:
            scope: Current variable scope (after function execution)
            function_name: Name of function that just returned

        Raises:
            ContractViolation: If any ensures contract is violated
        """
        for ens in self.ensures:
            if ens.active and not ens.check(scope):
                context = {
                    'function': function_name or 'unknown',
                    'scope': {k: v for k, v in scope.items() if not callable(v)}
                }
                raise ContractViolation(ens, context, self.history[-10:])

    def step(self, scope: Dict[str, Any]):
        """Advance one execution step and check eventually contracts.

        Args:
            scope: Current variable scope
        """
        self.step_count += 1
        self.history.append(f"Step {self.step_count}: {list(scope.keys())}")

        # Check all eventually contracts
        for evt in self.eventually:
            if evt.active:
                evt.tick(scope)

    def clear_eventually(self):
        """Clear all eventually contracts (useful for function boundaries)."""
        self.eventually.clear()

    def summary(self) -> str:
        """Get a summary of all active contracts."""
        lines = []
        lines.append(f"\n{Color.CYAN}{Color.BOLD}Active Contracts:{Color.RESET}")
        lines.append(f"  Invariants: {len([i for i in self.invariants if i.active])}")
        lines.append(f"  Ensures: {len([e for e in self.ensures if e.active])}")
        lines.append(f"  Eventually: {len([e for e in self.eventually if e.active])}")
        lines.append(f"  Total steps: {self.step_count}")
        return "\n".join(lines)


# ============================================================================
# INTEGRATION HELPERS
# ============================================================================

def create_causal_variable(name: str, initial_value: Any, expression: str = "",
                          line: int = None) -> CausalValue:
    """Factory function to create a new causal variable.

    Args:
        name: Variable name
        initial_value: Initial value
        expression: Source expression
        line: Line number in source

    Returns:
        A new CausalValue instance
    """
    cv = CausalValue(current=initial_value)
    cv.name = name
    if expression or line:
        cv.causal_history.append(CausalOrigin(
            value=initial_value,
            expression=expression or str(initial_value),
            line=line
        ))
    return cv


def track_operation(result: Any, operation: str, dependencies: Dict[str, Any],
                   expression: str = "", line: int = None) -> CausalValue:
    """Create a causal value from an operation result.

    Args:
        result: The result value
        operation: Operation performed ('+', '-', 'call', etc.)
        dependencies: Dict of variables that contributed
        expression: Source expression
        line: Line number

    Returns:
        A CausalValue with full tracking
    """
    cv = CausalValue(current=result)
    cv.causal_history.append(CausalOrigin(
        value=result,
        expression=expression or str(result),
        line=line,
        dependencies=dependencies,
        operation=operation
    ))
    return cv


# ============================================================================
# DEMO MODE
# ============================================================================

def demo_causal_debugging():
    """Demonstrate causal debugging with a complex example."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}  CAUSAL DEBUGGING DEMO{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}\n")

    # Create causal variables
    a = create_causal_variable("a", 10, "initial", line=1)
    b = create_causal_variable("b", 20, "initial", line=2)

    # Simulate operations
    a.assign_with_cause(15, "a + 5", line=3, dependencies={"a@past": 10}, operation="+")
    b.assign_with_cause(25, "b + 5", line=4, dependencies={"b@past": 20}, operation="+")

    # Complex operation
    result = a.current + b.current
    c = create_causal_variable("c", result, "a + b", line=5)
    c.causal_history.append(CausalOrigin(
        value=result,
        expression="a + b",
        line=5,
        dependencies={"a": a, "b": b},
        operation="+"
    ))

    # Show causal traces
    print(why(c))
    print(f"\n{Color.GREEN}✓ Causal debugging allows you to trace the WHY of any computation!{Color.RESET}\n")


def demo_temporal_contracts():
    """Demonstrate temporal contracts with violations."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}  TEMPORAL CONTRACTS DEMO{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}\n")

    manager = ContractManager()

    # Demo 1: Invariant (success)
    print(f"{Color.YELLOW}Demo 1: Invariant Contract (Success){Color.RESET}")
    manager.add_invariant(
        lambda s: s.get('balance', 0) >= 0,
        "balance >= 0",
        "non-negative balance"
    )

    scope = {'balance': 100}
    try:
        manager.check_invariants(scope)
        print(f"{Color.GREEN}✓ Invariant satisfied: balance = {scope['balance']}{Color.RESET}\n")
    except ContractViolation as e:
        print(e)

    # Demo 2: Invariant violation
    print(f"{Color.YELLOW}Demo 2: Invariant Contract (Violation){Color.RESET}")
    scope['balance'] = -50
    try:
        manager.check_invariants(scope, 'balance')
        print(f"{Color.GREEN}✓ Invariant satisfied{Color.RESET}\n")
    except ContractViolation as e:
        print(e)
        print(f"{Color.GREEN}✓ Contract violation detected and reported beautifully!{Color.RESET}\n")

    # Demo 3: Eventually contract
    print(f"{Color.YELLOW}Demo 3: Eventually Contract{Color.RESET}")
    manager2 = ContractManager()
    manager2.add_eventually(
        5,
        lambda s: s.get('counter', 0) >= 10,
        "counter >= 10",
        "counter reaches 10"
    )

    scope2 = {'counter': 0}
    try:
        for i in range(7):
            scope2['counter'] = i
            manager2.step(scope2)
            if scope2['counter'] >= 10:
                print(f"{Color.GREEN}✓ Eventually contract satisfied at step {i+1}{Color.RESET}\n")
                break
    except ContractViolation as e:
        print(e)
        print(f"{Color.GREEN}✓ Eventually contract violation detected - time ran out!{Color.RESET}\n")

    # Summary
    print(manager2.summary())


def run_full_demo():
    """Run complete demonstration of both features."""
    print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}  🚀 LAMENT TEMPORAL ADVANCED FEATURES DEMO 🚀{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}\n")

    demo_causal_debugging()
    time.sleep(1)
    demo_temporal_contracts()

    print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}  Demo complete! Time itself is now your debugging tool. 🌌{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}\n")


if __name__ == "__main__":
    run_full_demo()
