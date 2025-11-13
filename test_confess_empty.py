#!/usr/bin/env python3
"""Test confess with empty string."""

from lament.advanced import run_advanced_lament

code = """
remember x = 5
match x {
    case 0 => { confess "Zero" },
    case 5 => { confess "Found five!" },
    case _ => { confess "Something else" }
}

confess ""
confess "After empty"
"""

try:
    run_advanced_lament(code, debug=False)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
