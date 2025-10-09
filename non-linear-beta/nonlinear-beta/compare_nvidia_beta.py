#!/usr/bin/env python3
"""
Compare NVIDIA beta calculations to find the discrepancy.
"""

import numpy as np
import yfinance as yf
from getBars import getBars
from sp500_optimized_analysis import calculate_beta_clean

print("=== COMPARING NVIDIA BETA CALCULATIONS ===")
print()

# Method 1: Direct YFinance calculation
print("Method 1: Direct YFinance calculation")
nvda = yf.download('NVDA', start='2015-01-01', end='2025-01-01', progress=False, auto_adjust=False)
spy = yf.download('SPY', start='2015-01-01', end='2025-01-01', progress=False, auto_adjust=False)

print(f"YFinance NVDA shape: {nvda.shape}")
print(f"YFinance SPY shape: {spy.shape}")

nvda_close = nvda['Close'].squeeze()
spy_close = spy['Close'].squeeze()

nvda_returns = nvda_close.pct_change().dropna().values
spy_returns = spy_close.pct_change().dropna().values

min_len = min(len(nvda_returns), len(spy_returns))
nvda_returns = nvda_returns[:min_len]
spy_returns = spy_returns[:min_len]

covariance = np.cov(nvda_returns, spy_returns)[0, 1]
market_variance = np.var(spy_returns)
beta_direct = covariance / market_variance

print(f"Direct calculation beta: {beta_direct:.4f}")
print(f"Data points: {len(nvda_returns):,}")
print(f"Date range: {nvda.index[0].date()} to {nvda.index[-1].date()}")
print()

# Method 2: Using getBars function
print("Method 2: Using getBars function (pipeline approach)")
nvda_data = getBars('NVDA', '2015-01-01', '2025-01-01')
spy_data = getBars('SPY', '2015-01-01', '2025-01-01')

print(f"getBars NVDA shape: {nvda_data.shape}")
print(f"getBars SPY shape: {spy_data.shape}")

result = calculate_beta_clean(nvda_data, spy_data)
print(f"Pipeline calculation beta: {result['traditional_beta']:.4f}")
print(f"Data points: {result['data_points']:,}")
print(f"Date range: {nvda_data.index[0].date()} to {nvda_data.index[-1].date()}")
print()

# Check if the date ranges are different
print("=== DATE RANGE COMPARISON ===")
yf_dates = set(nvda.index.date)
gb_dates = set(nvda_data.index.date)

print(f"YFinance unique dates: {len(yf_dates)}")
print(f"getBars unique dates: {len(gb_dates)}")

if yf_dates != gb_dates:
    only_yf = yf_dates - gb_dates
    only_gb = gb_dates - yf_dates
    print(f"Dates only in YFinance: {len(only_yf)}")
    print(f"Dates only in getBars: {len(only_gb)}")
    if only_yf:
        print(f"Sample YF-only dates: {sorted(list(only_yf))[:5]}")
    if only_gb:
        print(f"Sample GB-only dates: {sorted(list(only_gb))[:5]}")
else:
    print("Date ranges are identical")

print()
print("=== FINAL ANALYSIS ===")
print(f"Beta difference: {abs(beta_direct - result['traditional_beta']):.4f}")
print(f"Ratio: {beta_direct / result['traditional_beta']:.2f}x")

# The correct answer
print(f"\nThe CORRECT NVIDIA beta should be: {beta_direct:.3f}")
if abs(beta_direct - 1.754) < 0.01:
    print("✓ This matches our earlier calculation of ~1.754")
else:
    print(f"Note: This differs from our earlier calculation of 1.754")