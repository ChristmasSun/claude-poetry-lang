#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lament.essentials import execute_with_essentials

with open('test_simple.lament', 'r') as f:
    source = f.read()

try:
    execute_with_essentials(source)
    print("\n✓ Test passed!")
except Exception as e:
    print(f"\n✗ Test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
