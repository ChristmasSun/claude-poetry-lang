#!/usr/bin/env python3
"""Test range patterns."""

from lament.advanced import run_advanced_lament

code = """
remember score = 85
match score {
    case 0..59 => { confess "Grade: F" },
    case 60..69 => { confess "Grade: D" },
    case 70..79 => { confess "Grade: C" },
    case 80..89 => { confess "Grade: B" },
    case 90..100 => { confess "Grade: A" },
    case _ => { confess "Invalid score" }
}

confess "Done"
"""

try:
    run_advanced_lament(code, debug=False)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
