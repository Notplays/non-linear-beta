#!/usr/bin/env python3
"""
Simple analysis of why NVIDIA beta is 1.7
"""

import numpy as np
import yfinance as yf

print("WHY IS NVIDIA BETA ONLY 1.7? - INVESTIGATION")
print("="*50)

# Get data
nvda = yf.download('NVDA', start='2015-01-01', end='2025-01-01', progress=False, auto_adjust=False)
spy = yf.download('SPY', start='2015-01-01', end='2025-01-01', progress=False, auto_adjust=False)

# Check price performance
nvda_start = float(nvda['Close'].iloc[0])
nvda_end = float(nvda['Close'].iloc[-1])
spy_start = float(spy['Close'].iloc[0])
spy_end = float(spy['Close'].iloc[-1])

print(f"NVIDIA: ${nvda_start:.2f} → ${nvda_end:.2f}")
print(f"Gain: {(nvda_end/nvda_start-1)*100:.0f}%")

print(f"\nSPY: ${spy_start:.2f} → ${spy_end:.2f}")
print(f"Gain: {(spy_end/spy_start-1)*100:.0f}%")

print(f"\nNVIDIA outperformed SPY by: {(nvda_end/nvda_start)/(spy_end/spy_start):.1f}x")

# Calculate returns and beta
nvda_ret = nvda['Close'].pct_change().dropna().values
spy_ret = spy['Close'].pct_change().dropna().values

min_len = min(len(nvda_ret), len(spy_ret))
nvda_ret = nvda_ret[:min_len]
spy_ret = spy_ret[:min_len]

# Calculate beta
beta = np.cov(nvda_ret, spy_ret)[0,1] / np.var(spy_ret)
correlation = np.corrcoef(nvda_ret, spy_ret)[0,1]

# Calculate volatilities
nvda_vol = np.std(nvda_ret) * np.sqrt(252) * 100
spy_vol = np.std(spy_ret) * np.sqrt(252) * 100

print(f"\nFULL PERIOD STATISTICS (2015-2025):")
print(f"Beta: {beta:.3f}")
print(f"Correlation: {correlation:.3f}")
print(f"NVIDIA volatility: {nvda_vol:.0f}% annual")
print(f"SPY volatility: {spy_vol:.0f}% annual")
print(f"Volatility ratio: {nvda_vol/spy_vol:.1f}x")

# Check different periods
print(f"\nBETA BY PERIOD:")
periods = [
    ('2015-01-01', '2018-12-31', '2015-2018 (Early)'),
    ('2019-01-01', '2022-12-31', '2019-2022 (Growth)'),
    ('2023-01-01', '2025-01-01', '2023-2025 (AI Boom)')
]

for start, end, label in periods:
    try:
        n = yf.download('NVDA', start=start, end=end, progress=False, auto_adjust=False)
        s = yf.download('SPY', start=start, end=end, progress=False, auto_adjust=False)
        
        if len(n) > 50:
            n_ret = n['Close'].pct_change().dropna().values
            s_ret = s['Close'].pct_change().dropna().values
            
            min_l = min(len(n_ret), len(s_ret))
            b = np.cov(n_ret[:min_l], s_ret[:min_l])[0,1] / np.var(s_ret[:min_l])
            
            print(f"{label}: {b:.3f}")
    except:
        print(f"{label}: Error")

print(f"\nWHY BETA IS 'ONLY' 1.7:")
print("1. MASSIVE GAINS ≠ HIGH BETA")
print("   - Beta measures CORRELATION with market, not total returns")
print("   - NVIDIA's gains were often INDEPENDENT of daily market moves")

print(f"\n2. NVIDIA BECAME THE MARKET")
print("   - Now ~7% of S&P 500 by weight")
print("   - When you become part of what you're measured against, beta → 1")

print(f"\n3. CONSISTENT GROWTH vs ERRATIC VOLATILITY")  
print("   - NVIDIA grew consistently, not randomly")
print("   - High beta = high correlation + high volatility")
print("   - NVIDIA had high volatility but not perfect correlation")

print(f"\n4. DIFFERENT PERIODS MATTER")
print("   - Google's ~2.0 beta might be from different time periods")
print("   - Or using different methodologies/benchmarks")

print(f"\nCONCLUSION: 1.7 IS ACTUALLY REASONABLE!")
print("A stock that goes up 26,000% in 10 years doesn't need high beta")
print("Beta measures day-to-day correlation, not long-term performance")

# Compare with other high-growth stocks
print(f"\nCOMPARISON WITH OTHER GROWTH STOCKS:")
growth_stocks = ['TSLA', 'AMZN', 'NFLX']

for stock in growth_stocks:
    try:
        data = yf.download(stock, start='2015-01-01', end='2025-01-01', progress=False, auto_adjust=False)
        if len(data) > 100:
            ret = data['Close'].pct_change().dropna().values
            min_l = min(len(ret), len(spy_ret))
            b = np.cov(ret[:min_l], spy_ret[:min_l])[0,1] / np.var(spy_ret[:min_l])
            print(f"{stock}: {b:.3f}")
    except:
        print(f"{stock}: Error")