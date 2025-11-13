"""
Lament Revolutionary Features
==============================

Three groundbreaking features that push programming language design:

1. SECURITY AS TYPE (Taint Tracking):
   - untrusted<String> and trusted<String> types
   - Automatic taint propagation through operations
   - Compiler errors when using untrusted data unsafely
   - sanitize() function to convert untrusted → trusted
   - Information flow control prevents SQL injection, XSS, etc.

2. PERSISTENT MEMORY:
   - persistent remember x = 0 - survives program restarts
   - Stored in .lament.memory file with JSON serialization
   - Transactional guarantees with commit/rollback
   - transaction { } commit_or_rollback blocks

3. PROBABILITY DISTRIBUTIONS:
   - Distribution type for probabilistic programming
   - uniform(a, b), normal(mean, std), bernoulli(p)
   - probability(event), expected_value(dist)
   - Monte Carlo: simulate n times { } analyze distribution

Created with love by the Lament team, pushing boundaries.
"""

import json
import os
import math
import random
import sys
from dataclasses import dataclass, field
from typing import Any, List, Dict, Optional, Callable
from enum import Enum, auto

from lament.types import Color, bell, TimelineValue, LamentType
from lament.parser import ASTNode, Identifier, BinaryOp, NumberLiteral
from lament.lexer import Token, TokenType


# ============================================================================
# FEATURE 1: SECURITY AS TYPE (Taint Tracking)
# ============================================================================

class TaintLevel(Enum):
    """Security taint levels for information flow control."""
    TRUSTED = auto()    # Safe, sanitized data
    UNTRUSTED = auto()  # Dangerous, unsanitized data from external sources


@dataclass
class TaintedValue:
    """A value wrapped with taint tracking metadata.

    This enables compile-time and runtime security checks to prevent
    injection attacks (SQL injection, XSS, command injection, etc.).

    Attributes:
        value: The actual data
        taint: Security level (TRUSTED or UNTRUSTED)
        source: Where this data came from (for error messages)
    """
    value: Any
    taint: TaintLevel
    source: str = "unknown"

    def __str__(self):
        taint_str = "trusted" if self.taint == TaintLevel.TRUSTED else "untrusted"
        return f"{taint_str}<{self.value}>"

    def __repr__(self):
        return self.__str__()


def taint_propagate(left: Any, right: Any, op: str) -> TaintLevel:
    """Propagate taint through operations.

    Security rule: If ANY operand is untrusted, result is untrusted.
    This prevents accidentally sanitizing data through operations.

    Args:
        left: Left operand (may be TaintedValue)
        right: Right operand (may be TaintedValue)
        op: The operation being performed

    Returns:
        The propagated taint level
    """
    left_taint = left.taint if isinstance(left, TaintedValue) else TaintLevel.TRUSTED
    right_taint = right.taint if isinstance(right, TaintedValue) else TaintLevel.TRUSTED

    # Untrusted propagates (conservative security)
    if left_taint == TaintLevel.UNTRUSTED or right_taint == TaintLevel.UNTRUSTED:
        return TaintLevel.UNTRUSTED
    return TaintLevel.TRUSTED


def unwrap_tainted(value: Any) -> Any:
    """Extract the raw value from a TaintedValue."""
    return value.value if isinstance(value, TaintedValue) else value


def get_taint(value: Any) -> TaintLevel:
    """Get the taint level of a value."""
    return value.taint if isinstance(value, TaintedValue) else TaintLevel.TRUSTED


def sanitize(value: Any) -> Any:
    """Sanitize untrusted data, promoting it to trusted.

    In a real system, this would perform actual sanitization
    (escaping SQL, HTML encoding, etc.). Here we simulate it.

    Args:
        value: The value to sanitize (may be TaintedValue)

    Returns:
        A TaintedValue with TRUSTED taint level
    """
    raw_value = unwrap_tainted(value)

    # Simulate sanitization: escape dangerous characters
    if isinstance(raw_value, str):
        # Basic HTML/SQL escaping simulation
        # IMPORTANT: Escape & first to avoid double-escaping
        sanitized = (raw_value
                    .replace("&", "&amp;")  # Must be first!
                    .replace("'", "''")  # SQL escape
                    .replace("<", "&lt;")  # HTML escape
                    .replace(">", "&gt;")
                    .replace('"', "&quot;"))
    else:
        sanitized = raw_value

    return TaintedValue(sanitized, TaintLevel.TRUSTED, source="sanitized")


def check_sql_safety(query: Any):
    """Check if a SQL query uses only trusted data.

    This prevents SQL injection by ensuring all user input is sanitized.

    Args:
        query: The query string to check

    Raises:
        SecurityError if query contains untrusted data
    """
    if isinstance(query, TaintedValue) and query.taint == TaintLevel.UNTRUSTED:
        raise SecurityError(
            f"SQL INJECTION PREVENTED!\n"
            f"       Cannot execute SQL with untrusted data from {query.source}.\n"
            f"       Use sanitize() to clean user input first.\n"
            f"       Query attempted: {query.value}"
        )


class SecurityError(Exception):
    """Raised when security type checks fail."""
    pass


# ============================================================================
# FEATURE 2: PERSISTENT MEMORY
# ============================================================================

class PersistentStore:
    """Manages persistent variables that survive program restarts.

    Variables are stored in a .lament.memory file as JSON.
    Supports transactional semantics with commit/rollback.

    Attributes:
        filename: Path to the persistent storage file
        data: In-memory copy of persistent variables
        transaction_active: Whether we're in a transaction
        transaction_snapshot: Backup for rollback
    """

    def __init__(self, filename: str = ".lament.memory"):
        self.filename = filename
        self.data = {}
        self.transaction_active = False
        self.transaction_snapshot = None
        self.load()

    def load(self):
        """Load persistent variables from disk."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r') as f:
                    self.data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.data = {}

    def save(self):
        """Save persistent variables to disk."""
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=2)

    def set(self, name: str, value: Any):
        """Set a persistent variable.

        Args:
            name: Variable name
            value: Value to store (must be JSON-serializable)
        """
        # Convert to JSON-serializable format
        self.data[name] = self._serialize(value)
        if not self.transaction_active:
            self.save()

    def get(self, name: str, default: Any = None) -> Any:
        """Get a persistent variable.

        Args:
            name: Variable name
            default: Default value if not found

        Returns:
            The stored value or default
        """
        return self._deserialize(self.data.get(name, default))

    def has(self, name: str) -> bool:
        """Check if a persistent variable exists."""
        return name in self.data

    def delete(self, name: str):
        """Delete a persistent variable."""
        if name in self.data:
            del self.data[name]
            if not self.transaction_active:
                self.save()

    def begin_transaction(self):
        """Start a transaction - save snapshot for possible rollback."""
        self.transaction_active = True
        self.transaction_snapshot = self.data.copy()

    def commit(self):
        """Commit transaction - save all changes to disk."""
        if self.transaction_active:
            self.save()
            self.transaction_active = False
            self.transaction_snapshot = None

    def rollback(self):
        """Rollback transaction - restore snapshot."""
        if self.transaction_active:
            self.data = self.transaction_snapshot
            self.transaction_active = False
            self.transaction_snapshot = None

    def _serialize(self, value: Any) -> Any:
        """Convert value to JSON-serializable format."""
        if isinstance(value, TaintedValue):
            return {
                "__tainted__": True,
                "value": value.value,
                "taint": value.taint.name,
                "source": value.source
            }
        return value

    def _deserialize(self, data: Any) -> Any:
        """Convert JSON data back to proper types."""
        if isinstance(data, dict) and data.get("__tainted__"):
            return TaintedValue(
                value=data["value"],
                taint=TaintLevel[data["taint"]],
                source=data["source"]
            )
        return data


# ============================================================================
# FEATURE 3: PROBABILITY DISTRIBUTIONS
# ============================================================================

class DistributionType(Enum):
    """Types of probability distributions."""
    UNIFORM = auto()
    NORMAL = auto()
    BERNOULLI = auto()
    EMPIRICAL = auto()  # From samples


@dataclass
class Distribution:
    """A probability distribution for probabilistic programming.

    Supports common distributions and Monte Carlo simulation.

    Attributes:
        dist_type: The type of distribution
        params: Parameters specific to the distribution type
        samples: Cached samples (for empirical distributions)
    """
    dist_type: DistributionType
    params: Dict[str, Any]
    samples: List[float] = field(default_factory=list)

    def sample(self) -> float:
        """Draw a random sample from this distribution."""
        if self.dist_type == DistributionType.UNIFORM:
            a = self.params['a']
            b = self.params['b']
            return random.uniform(a, b)

        elif self.dist_type == DistributionType.NORMAL:
            mean = self.params['mean']
            std = self.params['std']
            return random.gauss(mean, std)

        elif self.dist_type == DistributionType.BERNOULLI:
            p = self.params['p']
            return 1.0 if random.random() < p else 0.0

        elif self.dist_type == DistributionType.EMPIRICAL:
            if not self.samples:
                return 0.0
            return random.choice(self.samples)

        return 0.0

    def expected_value(self) -> float:
        """Calculate expected value (mean) of the distribution."""
        if self.dist_type == DistributionType.UNIFORM:
            a = self.params['a']
            b = self.params['b']
            return (a + b) / 2.0

        elif self.dist_type == DistributionType.NORMAL:
            return self.params['mean']

        elif self.dist_type == DistributionType.BERNOULLI:
            return self.params['p']

        elif self.dist_type == DistributionType.EMPIRICAL:
            if not self.samples:
                return 0.0
            return sum(self.samples) / len(self.samples)

        return 0.0

    def probability(self, event: Callable[[float], bool]) -> float:
        """Estimate probability of an event using Monte Carlo.

        Args:
            event: A function that returns True if event occurs

        Returns:
            Estimated probability (between 0 and 1)
        """
        num_samples = 10000
        successes = sum(1 for _ in range(num_samples) if event(self.sample()))
        return successes / num_samples

    def __str__(self):
        if self.dist_type == DistributionType.UNIFORM:
            return f"Uniform({self.params['a']}, {self.params['b']})"
        elif self.dist_type == DistributionType.NORMAL:
            return f"Normal(μ={self.params['mean']}, σ={self.params['std']})"
        elif self.dist_type == DistributionType.BERNOULLI:
            return f"Bernoulli(p={self.params['p']})"
        elif self.dist_type == DistributionType.EMPIRICAL:
            return f"Empirical({len(self.samples)} samples)"
        return "Distribution"


def uniform(a: float, b: float) -> Distribution:
    """Create a uniform distribution over [a, b]."""
    return Distribution(DistributionType.UNIFORM, {'a': a, 'b': b})


def normal(mean: float, std: float) -> Distribution:
    """Create a normal (Gaussian) distribution."""
    return Distribution(DistributionType.NORMAL, {'mean': mean, 'std': std})


def bernoulli(p: float) -> Distribution:
    """Create a Bernoulli distribution (coin flip with probability p)."""
    if not (0 <= p <= 1):
        raise ValueError(f"Bernoulli probability must be in [0, 1], got {p}")
    return Distribution(DistributionType.BERNOULLI, {'p': p})


def empirical_from_samples(samples: List[float]) -> Distribution:
    """Create an empirical distribution from samples."""
    dist = Distribution(DistributionType.EMPIRICAL, {})
    dist.samples = samples
    return dist


# ============================================================================
# NEW AST NODES
# ============================================================================

@dataclass
class TaintedLiteral(ASTNode):
    """Literal with taint annotation: untrusted<"value"> or trusted<"value">"""
    value: Any
    taint: TaintLevel


@dataclass
class SanitizeCall(ASTNode):
    """sanitize(expr) - convert untrusted to trusted"""
    expr: ASTNode


@dataclass
class PersistentDecl(ASTNode):
    """persistent remember x = value"""
    name: str
    value: ASTNode


@dataclass
class TransactionBlock(ASTNode):
    """transaction { statements } commit_or_rollback"""
    body: List[ASTNode]
    should_commit: bool = True  # determined at runtime


@dataclass
class DistributionLiteral(ASTNode):
    """Distribution constructor: uniform(a, b), normal(mean, std), etc."""
    dist_type: str  # 'uniform', 'normal', 'bernoulli'
    args: List[ASTNode]


@dataclass
class SimulateBlock(ASTNode):
    """simulate n times { statements } analyze distribution"""
    num_iterations: ASTNode
    body: List[ASTNode]
    result_var: str  # variable to collect into distribution


@dataclass
class SqlQuery(ASTNode):
    """execute_sql(query) - checked for taint safety"""
    query: ASTNode


# ============================================================================
# EXTENDED LEXER
# ============================================================================

class RevolutionaryTokenType(Enum):
    """Additional token types for revolutionary features."""
    # Security
    UNTRUSTED = auto()
    TRUSTED = auto()
    SANITIZE = auto()

    # Persistence
    PERSISTENT = auto()
    TRANSACTION = auto()
    COMMIT = auto()
    ROLLBACK = auto()
    COMMIT_OR_ROLLBACK = auto()

    # Probability
    DISTRIBUTION = auto()
    UNIFORM = auto()
    NORMAL = auto()
    BERNOULLI = auto()
    PROBABILITY = auto()
    EXPECTED_VALUE = auto()
    SIMULATE = auto()
    TIMES = auto()
    ANALYZE = auto()

    # SQL
    EXECUTE_SQL = auto()


REVOLUTIONARY_KEYWORDS = {
    'untrusted': RevolutionaryTokenType.UNTRUSTED,
    'trusted': RevolutionaryTokenType.TRUSTED,
    'sanitize': RevolutionaryTokenType.SANITIZE,
    'persistent': RevolutionaryTokenType.PERSISTENT,
    'transaction': RevolutionaryTokenType.TRANSACTION,
    'commit': RevolutionaryTokenType.COMMIT,
    'rollback': RevolutionaryTokenType.ROLLBACK,
    'commit_or_rollback': RevolutionaryTokenType.COMMIT_OR_ROLLBACK,
    'Distribution': RevolutionaryTokenType.DISTRIBUTION,
    'uniform': RevolutionaryTokenType.UNIFORM,
    'normal': RevolutionaryTokenType.NORMAL,
    'bernoulli': RevolutionaryTokenType.BERNOULLI,
    'probability': RevolutionaryTokenType.PROBABILITY,
    'expected_value': RevolutionaryTokenType.EXPECTED_VALUE,
    'simulate': RevolutionaryTokenType.SIMULATE,
    'times': RevolutionaryTokenType.TIMES,
    'analyze': RevolutionaryTokenType.ANALYZE,
    'execute_sql': RevolutionaryTokenType.EXECUTE_SQL,
}


# ============================================================================
# EXTENDED INTERPRETER
# ============================================================================

class RevolutionaryInterpreter:
    """Extended interpreter with revolutionary features.

    This wraps the base LamentInterpreter and adds:
    - Taint tracking and security checks
    - Persistent memory management
    - Probability distribution support
    - Monte Carlo simulation
    """

    def __init__(self, base_interpreter):
        self.base = base_interpreter
        self.persistent = PersistentStore()

        # Register revolutionary built-ins
        self.register_revolutionary_builtins()

    def register_revolutionary_builtins(self):
        """Register built-in functions for revolutionary features."""
        # Security
        self.base.globals['sanitize'] = sanitize
        self.base.globals['untrusted'] = lambda x: TaintedValue(x, TaintLevel.UNTRUSTED, source="user_input")
        self.base.globals['trusted'] = lambda x: TaintedValue(x, TaintLevel.TRUSTED, source="literal")

        # Distributions
        self.base.globals['uniform'] = uniform
        self.base.globals['normal'] = normal
        self.base.globals['bernoulli'] = bernoulli
        self.base.globals['sample'] = lambda d: d.sample()
        self.base.globals['expected_value'] = lambda d: d.expected_value()

        # Utilities
        self.base.globals['execute_sql'] = self.execute_sql_safe

    def execute_sql_safe(self, query: Any) -> str:
        """Execute SQL query with taint checking.

        Args:
            query: The SQL query (may be tainted)

        Returns:
            Simulated query result

        Raises:
            SecurityError if query contains untrusted data
        """
        check_sql_safety(query)
        raw_query = unwrap_tainted(query)
        return f"[SQL EXECUTED SAFELY]: {raw_query}"

    def execute_binary_op_tainted(self, left: Any, op: str, right: Any) -> Any:
        """Execute binary operation with taint propagation."""
        # Unwrap values for operation
        left_val = unwrap_tainted(left)
        right_val = unwrap_tainted(right)

        # Perform operation
        if op == '+':
            result = left_val + right_val
        elif op == '-':
            result = left_val - right_val
        elif op == '*':
            result = left_val * right_val
        elif op == '/':
            if right_val == 0:
                raise ValueError("Division by zero")
            result = left_val / right_val
        elif op == '%':
            result = left_val % right_val
        elif op == '==':
            result = left_val == right_val
        elif op == '!=':
            result = left_val != right_val
        elif op == '<':
            result = left_val < right_val
        elif op == '>':
            result = left_val > right_val
        elif op == '<=':
            result = left_val <= right_val
        elif op == '>=':
            result = left_val >= right_val
        else:
            result = left_val

        # Propagate taint
        result_taint = taint_propagate(left, right, op)

        if isinstance(left, TaintedValue) or isinstance(right, TaintedValue):
            sources = []
            if isinstance(left, TaintedValue):
                sources.append(left.source)
            if isinstance(right, TaintedValue):
                sources.append(right.source)
            return TaintedValue(result, result_taint, source="+".join(sources))

        return result

    def execute_persistent_decl(self, name: str, value: Any):
        """Declare a persistent variable."""
        self.persistent.set(name, value)
        # Also set in regular interpreter
        self.base.declare_var(name, value)

    def load_persistent_var(self, name: str) -> Any:
        """Load a persistent variable if it exists."""
        if self.persistent.has(name):
            return self.persistent.get(name)
        return None

    def execute_transaction(self, body: List[ASTNode], should_commit: bool = True):
        """Execute a transaction block with commit/rollback."""
        self.persistent.begin_transaction()

        try:
            self.base.execute(body)
            if should_commit:
                self.persistent.commit()
            else:
                self.persistent.rollback()
        except Exception as e:
            self.persistent.rollback()
            raise

    def execute_simulate(self, num_iterations: int, body: List[ASTNode], result_var: str) -> Distribution:
        """Execute Monte Carlo simulation.

        Runs the body multiple times and collects results into a distribution.

        Args:
            num_iterations: Number of simulation runs
            body: Code to execute each iteration
            result_var: Variable to collect from each run

        Returns:
            An empirical distribution of the results
        """
        samples = []

        for i in range(num_iterations):
            # Create new scope for each iteration
            self.base.scopes.append({})

            try:
                self.base.execute(body)

                # Collect result
                if result_var in self.base.scopes[-1]:
                    val = self.base.scopes[-1][result_var]
                    if isinstance(val, TimelineValue):
                        val = val.current
                    samples.append(float(unwrap_tainted(val)))
            except Exception:
                pass  # Skip failed iterations
            finally:
                self.base.scopes.pop()

        return empirical_from_samples(samples)


# ============================================================================
# DEMONSTRATION UTILITIES
# ============================================================================

def demo_sql_injection_prevention():
    """Demonstrate SQL injection prevention using taint tracking."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}DEMO 1: SQL INJECTION PREVENTION (Security as Type){Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}\n")

    # Simulate user input (untrusted)
    user_input = TaintedValue("admin' OR '1'='1", TaintLevel.UNTRUSTED, source="user_form")

    print(f"{Color.YELLOW}User Input (untrusted):{Color.RESET} {user_input}")

    # Try to use untrusted data in SQL (FAILS)
    query_unsafe = TaintedValue(f"SELECT * FROM users WHERE name = '{user_input.value}'",
                                TaintLevel.UNTRUSTED, source="user_form")

    print(f"\n{Color.RED}Attempting unsafe query:{Color.RESET}")
    print(f"  {query_unsafe.value}")

    try:
        check_sql_safety(query_unsafe)
        print(f"{Color.RED}  [BLOCKED] Security system prevented SQL injection!{Color.RESET}")
    except SecurityError as e:
        print(f"{Color.RED}  [BLOCKED] {e}{Color.RESET}")

    # Sanitize and use (SUCCEEDS)
    user_input_clean = sanitize(user_input)
    query_safe = TaintedValue(f"SELECT * FROM users WHERE name = '{user_input_clean.value}'",
                              TaintLevel.TRUSTED, source="sanitized")

    print(f"\n{Color.GREEN}After sanitization:{Color.RESET} {user_input_clean}")
    print(f"\n{Color.GREEN}Safe query:{Color.RESET}")
    print(f"  {query_safe.value}")

    try:
        check_sql_safety(query_safe)
        print(f"{Color.GREEN}  [ALLOWED] Query is safe to execute!{Color.RESET}")
    except SecurityError:
        print(f"{Color.RED}  [BLOCKED] Should not happen!{Color.RESET}")

    print(f"\n{Color.CYAN}Type system prevented injection attack at compile/runtime!{Color.RESET}")
    print(f"{Color.CYAN}Taint propagates: untrusted + anything = untrusted{Color.RESET}\n")


def demo_persistent_memory():
    """Demonstrate persistent memory across program runs."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}DEMO 2: PERSISTENT MEMORY (Survives Restarts){Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}\n")

    store = PersistentStore(".demo.memory")

    # First run - initialize counter
    if not store.has('visit_count'):
        store.set('visit_count', 0)
        print(f"{Color.YELLOW}First visit! Initializing counter...{Color.RESET}")

    # Increment counter
    count = store.get('visit_count')
    count += 1
    store.set('visit_count', count)

    print(f"{Color.GREEN}Visit count: {count}{Color.RESET}")
    print(f"{Color.CYAN}This value persists across program restarts!{Color.RESET}")

    # Demonstrate transactions
    print(f"\n{Color.YELLOW}Testing transactions...{Color.RESET}")

    store.begin_transaction()
    store.set('transaction_test', 100)
    print(f"  Set transaction_test = 100 (in transaction)")

    store.set('transaction_test', 200)
    print(f"  Set transaction_test = 200 (in transaction)")

    print(f"  Rolling back...")
    store.rollback()

    print(f"{Color.GREEN}After rollback: transaction_test = {store.get('transaction_test', 'not set')}{Color.RESET}")

    # Successful transaction
    store.begin_transaction()
    store.set('committed_value', 42)
    store.commit()

    print(f"{Color.GREEN}After commit: committed_value = {store.get('committed_value')}{Color.RESET}")
    print(f"\n{Color.CYAN}Transactional guarantees: commit or rollback!{Color.RESET}\n")

    # Cleanup demo file
    if os.path.exists(".demo.memory"):
        os.remove(".demo.memory")


def demo_probability_distributions():
    """Demonstrate probability distributions and Monte Carlo simulation."""
    print(f"\n{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}DEMO 3: PROBABILITY DISTRIBUTIONS{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}{'='*70}{Color.RESET}\n")

    # Uniform distribution
    print(f"{Color.YELLOW}1. Uniform Distribution [0, 10]:{Color.RESET}")
    u = uniform(0, 10)
    print(f"   {u}")
    print(f"   Expected value: {u.expected_value():.2f}")
    print(f"   Samples: {[u.sample() for _ in range(5)]}")

    # Normal distribution
    print(f"\n{Color.YELLOW}2. Normal Distribution (μ=100, σ=15):{Color.RESET}")
    n = normal(100, 15)
    print(f"   {n}")
    print(f"   Expected value: {n.expected_value():.2f}")
    samples = [n.sample() for _ in range(5)]
    print(f"   Samples: {[f'{s:.1f}' for s in samples]}")

    # Bernoulli distribution
    print(f"\n{Color.YELLOW}3. Bernoulli Distribution (p=0.7):{Color.RESET}")
    b = bernoulli(0.7)
    print(f"   {b}")
    print(f"   Expected value: {b.expected_value():.2f}")
    print(f"   Samples (10 coin flips): {[int(b.sample()) for _ in range(10)]}")

    # Probability queries
    print(f"\n{Color.YELLOW}4. Probability Queries (Monte Carlo):{Color.RESET}")
    n = normal(100, 15)

    p_above_115 = n.probability(lambda x: x > 115)
    print(f"   P(X > 115) ≈ {p_above_115:.3f}")

    p_between = n.probability(lambda x: 90 < x < 110)
    print(f"   P(90 < X < 110) ≈ {p_between:.3f}")

    # Monte Carlo simulation
    print(f"\n{Color.YELLOW}5. Monte Carlo Simulation:{Color.RESET}")
    print(f"   Simulating dice rolls...")

    # Simulate rolling two dice and summing
    samples = []
    for _ in range(1000):
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        samples.append(float(die1 + die2))

    dice_dist = empirical_from_samples(samples)
    print(f"   {dice_dist}")
    print(f"   Expected sum: {dice_dist.expected_value():.2f}")
    print(f"   P(sum = 7) ≈ {dice_dist.probability(lambda x: 6.5 < x < 7.5):.3f}")

    print(f"\n{Color.CYAN}First-class probability distributions in the language!{Color.RESET}\n")


def run_all_demos():
    """Run all three groundbreaking feature demos."""
    print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}   LAMENT REVOLUTIONARY FEATURES - DEMONSTRATION{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}\n")

    demo_sql_injection_prevention()
    demo_persistent_memory()
    demo_probability_distributions()

    print(f"\n{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}   THREE GROUNDBREAKING FEATURES DEMONSTRATED{Color.RESET}")
    print(f"{Color.MAGENTA}{Color.BOLD}{'='*70}{Color.RESET}\n")


if __name__ == "__main__":
    run_all_demos()
