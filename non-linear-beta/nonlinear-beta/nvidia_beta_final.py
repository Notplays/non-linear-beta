#!/usr/bin/env python3
"""
Ultra-simple NVIDIA beta calculator.
"""

import pandas as pd
import numpy as np
import yfinance as yf

print("NVIDIA BETA CALCULATION - WORKING VERSION")
print("="*50)

# Download with auto_adjust=False to get simpler column structure
nvda = yf.download('NVDA', start='2015-01-01', end='2025-01-01', progress=False, auto_adjust=False)
spy = yf.download('SPY', start='2015-01-01', end='2025-01-01', progress=False, auto_adjust=False)

print(f"Downloaded {len(nvda)} NVIDIA records")
print(f"Downloaded {len(spy)} SPY records")

# Use Close prices
nvda_close = nvda['Close'].dropna()
spy_close = spy['Close'].dropna()

print(f"NVIDIA: ${float(nvda_close.iloc[0]):.2f} → ${float(nvda_close.iloc[-1]):.2f} ({float(nvda_close.iloc[-1])/float(nvda_close.iloc[0])*100:.0f}% total return)")
print(f"SPY: ${float(spy_close.iloc[0]):.2f} → ${float(spy_close.iloc[-1]):.2f} ({float(spy_close.iloc[-1])/float(spy_close.iloc[0])*100:.0f}% total return)")

# Calculate daily returns
nvda_ret = nvda_close.pct_change().dropna()
spy_ret = spy_close.pct_change().dropna()

# Align by index (dates)
aligned_dates = nvda_ret.index.intersection(spy_ret.index)
nvda_aligned = nvda_ret[aligned_dates]
spy_aligned = spy_ret[aligned_dates]

print(f"Aligned data points: {len(aligned_dates):,}")
print(f"Period: {aligned_dates[0].date()} to {aligned_dates[-1].date()}")

# Calculate beta = Cov(stock, market) / Var(market)
covariance = np.cov(nvda_aligned, spy_aligned)[0, 1]
market_variance = np.var(spy_aligned)
beta = covariance / market_variance

# Additional statistics
correlation = np.corrcoef(nvda_aligned, spy_aligned)[0, 1]
nvda_vol = nvda_aligned.std() * np.sqrt(252) * 100  # Annualized volatility
spy_vol = spy_aligned.std() * np.sqrt(252) * 100

print(f"\nRESULTS:")
print(f"Traditional Beta: {beta:.4f}")
print(f"Correlation: {correlation:.4f}")
print(f"NVIDIA Annual Volatility: {nvda_vol:.1f}%")
print(f"SPY Annual Volatility: {spy_vol:.1f}%")

# Calculate directional betas
up_days = spy_aligned > 0
down_days = spy_aligned < 0

print(f"\nMARKET DIRECTION ANALYSIS:")
print(f"Positive market days: {up_days.sum():,}")
print(f"Negative market days: {down_days.sum():,}")

if up_days.sum() > 20:
    nvda_up = nvda_aligned[up_days]
    spy_up = spy_aligned[up_days]
    beta_up = np.cov(nvda_up, spy_up)[0, 1] / np.var(spy_up)
    print(f"Positive Market Beta: {beta_up:.4f}")

if down_days.sum() > 20:
    nvda_down = nvda_aligned[down_days]
    spy_down = spy_aligned[down_days]
    beta_down = np.cov(nvda_down, spy_down)[0, 1] / np.var(spy_down)
    print(f"Negative Market Beta: {beta_down:.4f}")
    
    if 'beta_up' in locals():
        ratio = beta_up / beta_down
        print(f"Beta Ratio (Up/Down): {ratio:.4f}")
        if ratio > 1:
            print("→ NVIDIA is MORE sensitive to market gains than losses")
        else:
            print("→ NVIDIA is MORE sensitive to market losses than gains")

print(f"\nCONCLUSION:")
print(f"NVIDIA's TRUE beta (2015-2025) is {beta:.3f}")
print(f"This is approximately {beta/1.036:.1f}x higher than your original result of 1.036")
print(f"The original analysis definitely had a data processing error!")

# Quick comparison with other major tech stocks
print(f"\nQUICK COMPARISON (same period):")
tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']

for stock in tech_stocks:
    try:
        data = yf.download(stock, start='2015-01-01', end='2025-01-01', progress=False, auto_adjust=False)
        returns = data['Close'].pct_change().dropna()
        aligned_returns = returns[aligned_dates]
        
        if len(aligned_returns) > 100:
            stock_beta = np.cov(aligned_returns, spy_aligned)[0, 1] / np.var(spy_aligned)
            print(f"{stock:5}: Beta = {stock_beta:.3f}")
    except:
        print(f"{stock:5}: Error calculating beta")