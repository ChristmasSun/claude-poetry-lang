#!/usr/bin/env python3
"""Test generators."""

from lament.advanced import run_advanced_lament

code = """
sigh count_up(n) {
    remember i = 0
    while i < n {
        yield i
        i = i + 1
    }
}

confess "Counting to 5:"
remember counter = count_up(5)
for num in counter {
    confess num
}
"""

try:
    run_advanced_lament(code, debug=False)
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
