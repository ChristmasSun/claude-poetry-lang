#!/usr/bin/env python3
"""Test two match statements."""

from lament.advanced import run_advanced_lament

code = """
remember x = 5
match x {
    case 0 => { confess "Zero" },
    case 5 => { confess "Found five!" },
    case _ => { confess "Something else" }
}

confess "Between matches"

remember y = 10
match y {
    case 5 => { confess "Five" },
    case 10 => { confess "Ten" },
    case _ => { confess "Other" }
}

confess "Done"
"""

try:
    run_advanced_lament(code, debug=False)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
