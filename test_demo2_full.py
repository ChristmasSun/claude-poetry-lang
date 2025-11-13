#!/usr/bin/env python3
"""Test full demo 2 code."""

from lament.advanced import run_advanced_lament

code = """
confess "=== Testing Literal Patterns ==="

remember x = 5
match x {
    case 0 => { confess "Zero" },
    case 5 => { confess "Found five!" },
    case _ => { confess "Something else" }
}

confess ""
confess "=== Testing Range Patterns ==="

remember score = 85
match score {
    case 0..59 => { confess "Grade: F" },
    case 60..69 => { confess "Grade: D" },
    case 70..79 => { confess "Grade: C" },
    case 80..89 => { confess "Grade: B" },
    case 90..100 => { confess "Grade: A" },
    case _ => { confess "Invalid score" }
}

confess ""
confess "=== Testing List Destructuring ==="

remember coords = [10, 20, 30]
match coords {
    case [x, y, z] => {
        confess "3D Point:"
        confess x
        confess y
        confess z
    },
    case [x, y] => {
        confess "2D Point"
    },
    case _ => {
        confess "Unknown structure"
    }
}

confess ""
confess "=== Testing Guard Clauses ==="

remember age = 25
match age {
    case n when n < 0 => { confess "Invalid age" },
    case n when n < 18 => { confess "Minor" },
    case n when n < 65 => { confess "Adult" },
    case _ => { confess "Senior" }
}

confess ""
confess "=== Testing Complex Patterns ==="

remember data = [1, 2, 3, 4, 5]
match data {
    case [] => { confess "Empty list" },
    case [a] => { confess "Single element" },
    case [first, second, ..rest] => {
        confess "First:"
        confess first
        confess "Second:"
        confess second
        confess "Rest:"
        confess rest
    }
}
"""

try:
    run_advanced_lament(code, debug=False)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
