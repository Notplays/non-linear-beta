#!/usr/bin/env python3
"""
Test the corrected pipeline with a few stocks to verify it's working.
"""

import sys
import os

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sp500_optimized_analysis import calculate_beta_clean
from getBars import getBars

def test_corrected_pipeline():
    """Test the corrected beta calculation with a few known stocks."""
    
    print("TESTING CORRECTED PIPELINE")
    print("="*50)
    
    # Test with a few representative stocks
    test_stocks = ['NVDA', 'AAPL', 'MSFT', 'SPY']
    
    print("Fetching market data (SPY)...")
    market_data = getBars('SPY', '2015-01-01', '2025-01-01')
    
    if market_data is None:
        print("Failed to fetch market data")
        return
        
    print(f"Market data: {len(market_data)} records")
    
    results = {}
    
    for symbol in test_stocks:
        if symbol == 'SPY':
            continue  # Skip SPY as it's our market proxy
            
        print(f"\nTesting {symbol}...")
        
        # Fetch stock data
        stock_data = getBars(symbol, '2015-01-01', '2025-01-01')
        
        if stock_data is None:
            print(f"  Failed to fetch {symbol} data")
            continue
            
        print(f"  Stock data: {len(stock_data)} records")
        
        # Calculate beta using corrected function
        beta_result = calculate_beta_clean(stock_data, market_data)
        
        if beta_result is None:
            print(f"  Failed to calculate beta for {symbol}")
            continue
            
        results[symbol] = beta_result
        
        print(f"  Traditional Beta: {beta_result['traditional_beta']:.4f}")
        print(f"  Positive Beta: {beta_result['positive_beta']:.4f}")
        print(f"  Negative Beta: {beta_result['negative_beta']:.4f}")
        print(f"  Beta Ratio: {beta_result['beta_ratio']:.4f}")
        print(f"  Data Points: {beta_result['data_points']:,}")
    
    print(f"\nSUMMARY:")
    print("-" * 30)
    for symbol, result in results.items():
        beta = result['traditional_beta']
        print(f"{symbol:4}: Beta = {beta:6.3f}")
        
        # Verify NVIDIA is much higher than before
        if symbol == 'NVDA':
            if beta > 1.5:
                print(f"      ✓ NVIDIA beta looks correct (was 1.036 before)")
            else:
                print(f"      ✗ NVIDIA beta still too low")
    
    print(f"\nPIPELINE TEST COMPLETE")
    return results

if __name__ == "__main__":
    test_corrected_pipeline()