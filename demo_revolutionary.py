#!/usr/bin/env python3
"""
Lament Revolutionary Features Demo
===================================

Run comprehensive demos of the three groundbreaking features:
1. Security as Type (Taint Tracking)
2. Persistent Memory
3. Probability Distributions
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lament.revolutionary import run_all_demos

if __name__ == "__main__":
    run_all_demos()
