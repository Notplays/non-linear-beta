#!/usr/bin/env python3
"""
Quick test to see what's in the data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from getBars import getBars

print("Testing getBars output structure...")

nvda_data = getBars('NVDA', '2015-01-01', '2025-01-01')
print("NVDA data columns:", nvda_data.columns.tolist() if nvda_data is not None else "None")
print("NVDA data shape:", nvda_data.shape if nvda_data is not None else "None")
print("NVDA head:")
print(nvda_data.head() if nvda_data is not None else "None")

spy_data = getBars('SPY', '2015-01-01', '2025-01-01')
print("\nSPY data columns:", spy_data.columns.tolist() if spy_data is not None else "None")
print("SPY data shape:", spy_data.shape if spy_data is not None else "None")