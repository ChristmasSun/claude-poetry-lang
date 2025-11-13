#!/usr/bin/env python3
"""Test pattern matching."""

from lament.advanced import run_advanced_lament

code = """
confess "Testing patterns"

remember x = 5
match x {
    case 0 => { confess "Zero" },
    case 5 => { confess "Found five!" },
    case _ => { confess "Something else" }
}

confess "Done"
"""

try:
    run_advanced_lament(code, debug=False)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
