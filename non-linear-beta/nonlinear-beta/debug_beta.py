#!/usr/bin/env python3
"""
Debug the beta calculation to find the issue.
"""

import numpy as np
from getBars import getBars

def debug_beta_calculation():
    """Debug step by step what's happening in the beta calculation."""
    
    print("DEBUGGING BETA CALCULATION")
    print("="*40)
    
    # Get data
    print("Fetching NVIDIA data...")
    nvda_data = getBars('NVDA', '2015-01-01', '2025-01-01')
    print("Fetching SPY data...")
    spy_data = getBars('SPY', '2015-01-01', '2025-01-01')
    
    print(f"NVDA data shape: {nvda_data.shape}")
    print(f"SPY data shape: {spy_data.shape}")
    
    # Calculate returns
    print("\nCalculating returns...")
    nvda_returns = nvda_data['close'].pct_change().dropna().squeeze()
    spy_returns = spy_data['close'].pct_change().dropna().squeeze()
    
    print(f"NVDA returns shape: {nvda_returns.shape}")
    print(f"SPY returns shape: {spy_returns.shape}")
    print(f"NVDA returns type: {type(nvda_returns)}")
    print(f"SPY returns type: {type(spy_returns)}")
    
    # Alignment
    print("\nAligning data...")
    common_dates = nvda_returns.index.intersection(spy_returns.index)
    print(f"Common dates: {len(common_dates)}")
    
    nvda_aligned = nvda_returns.loc[common_dates].values
    spy_aligned = spy_returns.loc[common_dates].values
    
    print(f"NVDA aligned shape: {nvda_aligned.shape}")
    print(f"SPY aligned shape: {spy_aligned.shape}")
    
    # Check for NaN
    nvda_nan_count = np.sum(np.isnan(nvda_aligned))
    spy_nan_count = np.sum(np.isnan(spy_aligned))
    print(f"NVDA NaN count: {nvda_nan_count}")
    print(f"SPY NaN count: {spy_nan_count}")
    
    if nvda_nan_count > 0 or spy_nan_count > 0:
        print("Found NaN values - removing them...")
        valid_mask = ~(np.isnan(nvda_aligned) | np.isnan(spy_aligned))
        nvda_clean = nvda_aligned[valid_mask]
        spy_clean = spy_aligned[valid_mask]
        print(f"Clean data length: {len(nvda_clean)}")
    else:
        nvda_clean = nvda_aligned
        spy_clean = spy_aligned
    
    # Calculate beta
    print("\nCalculating beta...")
    covariance = np.cov(nvda_clean, spy_clean)[0, 1]
    market_variance = np.var(spy_clean)
    
    print(f"Covariance: {covariance}")
    print(f"Market variance: {market_variance}")
    
    if market_variance != 0:
        beta = covariance / market_variance
        print(f"Beta: {beta}")
    else:
        print("Market variance is zero!")
    
    # Check some sample values
    print(f"\nSample NVDA returns: {nvda_clean[:5]}")
    print(f"Sample SPY returns: {spy_clean[:5]}")
    print(f"NVDA std: {np.std(nvda_clean)}")
    print(f"SPY std: {np.std(spy_clean)}")

if __name__ == "__main__":
    debug_beta_calculation()