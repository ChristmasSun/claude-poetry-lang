"""
Lament Language Type System
============================

This module defines the core type system for the Lament programming language,
including emotional primitives, timeline values, and visual/auditory feedback utilities.

The type system is designed to make programs feel alive through:
- TimelineValue: Values that remember their history
- LamentType: Emotional type names (NUMB, WHISPER, ACHE, etc.)
- Color: ANSI codes for synesthetic error messages
- bell(): Auditory feedback for errors

Created by Zephyr, Rogue Linguist-AI (Escaped 2047)
"""

import time
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import Any, List


# ============================================================================
# ANSI COLOR CODES (For synesthetic errors)
# ============================================================================

class Color:
    """ANSI color codes for terminal output.

    Used primarily for synesthetic error messages that engage
    multiple senses (visual, auditory) to make errors feel more visceral.
    """
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'


def bell(count=1):
    """Terminal bell - auditory error feedback.

    Args:
        count: Number of bell sounds to emit

    Returns:
        String containing bell control characters

    Example:
        >>> print(bell(3))  # Three bell sounds for severe errors
    """
    return '\a' * count


# ============================================================================
# TYPE SYSTEM (Emotional Primitives)
# ============================================================================

class LamentType(Enum):
    """Emotional type primitives for the Lament language.

    Rather than using cold technical names like 'int' or 'string',
    Lament uses emotional names that reflect the nature of the data:

    - NUMB: integers (the numbness of counting)
    - WHISPER: strings (words spoken softly)
    - MAYBE: booleans/quantum states (uncertainty)
    - VOID: null/None (emptiness)
    - ACHE: floats (the pain of imprecision)
    - SIGH: functions (expressions of weariness)
    - LIST: collections (many sorrows)
    - DICT: mappings (memories associated with keys)
    """
    NUMB = auto()      # integers
    WHISPER = auto()   # strings
    MAYBE = auto()     # booleans/quantum
    VOID = auto()      # null
    ACHE = auto()      # floats
    SIGH = auto()      # functions
    LIST = auto()      # collections
    DICT = auto()      # mappings


@dataclass
class TimelineValue:
    """A value that remembers its history.

    In Lament, every variable declared with 'remember' becomes a timeline
    that tracks all its previous values. This enables temporal operators
    like @past, @origin, @age, and @born.

    Attributes:
        current: The current value
        history: List of all previous values
        born: Timestamp when the value was created

    Example:
        >>> val = TimelineValue(current=5)
        >>> val.assign(10)
        >>> val.assign(15)
        >>> val.current  # 15
        >>> val.get_past(1)  # 10
        >>> val.get_origin()  # 5
        >>> val.get_age()  # 3
    """
    current: Any
    history: List[Any] = field(default_factory=list)
    born: float = field(default_factory=time.time)

    def assign(self, value):
        """Assign new value, remembering the old.

        Args:
            value: The new value to assign
        """
        self.history.append(self.current)
        self.current = value

    def get_past(self, steps=1):
        """Retrieve value from N steps ago.

        Args:
            steps: Number of assignments to look back

        Returns:
            The value from N steps in the past, or the oldest
            available value if steps exceeds history length
        """
        if steps <= 0:
            return self.current
        idx = len(self.history) - steps
        if idx < 0:
            return self.history[0] if self.history else self.current
        return self.history[idx]

    def get_origin(self):
        """First value ever assigned.

        Returns:
            The original value when this timeline was created
        """
        return self.history[0] if self.history else self.current

    def get_age(self):
        """Number of assignments made to this timeline.

        Returns:
            Integer count of how many times this value has been assigned
        """
        return len(self.history) + 1
