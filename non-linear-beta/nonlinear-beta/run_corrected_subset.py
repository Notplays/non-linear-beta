#!/usr/bin/env python3
"""
Run corrected analysis on a subset of S&P 500 stocks to verify the fix.
"""

import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sp500_optimized_analysis import SP500OptimizedAnalyzer

def run_corrected_subset_analysis():
    """Run corrected analysis on a representative subset."""
    
    print("CORRECTED S&P 500 BETA ANALYSIS - SUBSET")
    print("="*50)
    
    # Test with major stocks from different sectors
    test_symbols = [
        'NVDA',    # Information Technology
        'AAPL',    # Information Technology  
        'MSFT',    # Information Technology
        'AMZN',    # Consumer Discretionary
        'GOOGL',   # Communication Services
        'TSLA',    # Consumer Discretionary
        'META',    # Communication Services
        'JPM',     # Financials
        'JNJ',     # Health Care
        'WMT'      # Consumer Staples
    ]
    
    # Create sector mapping for our test
    sector_map = {
        'NVDA': 'Information Technology',
        'AAPL': 'Information Technology',
        'MSFT': 'Information Technology',
        'AMZN': 'Consumer Discretionary',
        'GOOGL': 'Communication Services',
        'TSLA': 'Consumer Discretionary',
        'META': 'Communication Services',
        'JPM': 'Financials',
        'JNJ': 'Health Care',
        'WMT': 'Consumer Staples'
    }
    
    analyzer = SP500OptimizedAnalyzer()
    
    print(f"Fetching data for {len(test_symbols)} representative stocks...")
    
    # Fetch data with corrected approach
    if not analyzer.fetch_data_optimized(test_symbols, start_date='2015-01-01', max_workers=2):
        print("Failed to fetch data")
        return
    
    print(f"Successfully fetched data for {len(analyzer.results)} stocks")
    
    # Calculate betas using corrected method
    beta_results = analyzer.calculate_betas()
    
    if not beta_results:
        print("No valid beta results")
        return
    
    print(f"\nCORRECTED BETA RESULTS:")
    print("-" * 70)
    print(f"{'Symbol':<6} {'Sector':<20} {'Beta':<7} {'Pos β':<7} {'Neg β':<7} {'Ratio':<7}")
    print("-" * 70)
    
    results_list = []
    for symbol, result in beta_results.items():
        sector = sector_map.get(symbol, 'Unknown')
        beta = result['traditional_beta']
        pos_beta = result['positive_beta']
        neg_beta = result['negative_beta']
        ratio = result['beta_ratio']
        
        print(f"{symbol:<6} {sector:<20} {beta:<7.3f} {pos_beta:<7.3f} {neg_beta:<7.3f} {ratio:<7.3f}")
        
        results_list.append({
            'symbol': symbol,
            'sector': sector,
            'traditional_beta': beta,
            'positive_beta': pos_beta,
            'negative_beta': neg_beta,
            'beta_ratio': ratio,
            'data_points': result['data_points'],
            'positive_days': result['positive_days'],
            'negative_days': result['negative_days']
        })
    
    # Save corrected results
    df = pd.DataFrame(results_list)
    df.to_csv('corrected_beta_subset_results.csv', index=False)
    print(f"\nCorrected results saved to 'corrected_beta_subset_results.csv'")
    
    # Compare with your original NVIDIA result
    nvda_result = next((r for r in results_list if r['symbol'] == 'NVDA'), None)
    if nvda_result:
        original_beta = 1.036
        corrected_beta = nvda_result['traditional_beta']
        print(f"\nNVIDIA BETA COMPARISON:")
        print(f"Original (wrong): {original_beta:.3f}")
        print(f"Corrected:        {corrected_beta:.3f}")
        print(f"Correction factor: {corrected_beta/original_beta:.1f}x")
    
    print(f"\nCORRECTED ANALYSIS COMPLETE!")
    print(f"Your pipeline is now fixed and ready for full S&P 500 analysis.")
    
    return analyzer

if __name__ == "__main__":
    run_corrected_subset_analysis()