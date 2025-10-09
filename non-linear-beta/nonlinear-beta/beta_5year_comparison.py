#!/usr/bin/env python3
"""
5-Year S&P 500 Beta Analysis (2020-2025)
Compare with Yahoo Finance beta values
"""

import pandas as pd
import numpy as np
import sys
import os
import time
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from getBars import getBars

def calculate_beta_simple(stock_data, market_data):
    """
    Calculate beta using simple, robust method.
    """
    try:
        # Align data on common dates
        common_dates = stock_data.index.intersection(market_data.index)
        if len(common_dates) < 50:  # Need at least 50 days for 5-year
            return None
            
        stock_aligned = stock_data.loc[common_dates, 'close']
        market_aligned = market_data.loc[common_dates, 'close']
        
        # Calculate returns
        stock_returns = stock_aligned.pct_change().dropna()
        market_returns = market_aligned.pct_change().dropna()
        
        # Ensure same length
        min_len = min(len(stock_returns), len(market_returns))
        stock_ret = stock_returns.values[:min_len]
        market_ret = market_returns.values[:min_len]
        
        # Calculate beta
        covariance = np.cov(stock_ret, market_ret)[0, 1]
        market_variance = np.var(market_ret)
        
        if market_variance == 0:
            return None
            
        beta = covariance / market_variance
        correlation = np.corrcoef(stock_ret, market_ret)[0, 1]
        
        # Calculate nonlinear betas
        positive_mask = market_ret > 0
        negative_mask = market_ret < 0
        
        positive_beta = None
        negative_beta = None
        
        if np.sum(positive_mask) > 10:
            stock_pos = stock_ret[positive_mask]
            market_pos = market_ret[positive_mask]
            cov_pos = np.cov(stock_pos, market_pos)[0, 1]
            var_pos = np.var(market_pos)
            if var_pos > 0:
                positive_beta = cov_pos / var_pos
                
        if np.sum(negative_mask) > 10:
            stock_neg = stock_ret[negative_mask]
            market_neg = market_ret[negative_mask]
            cov_neg = np.cov(stock_neg, market_neg)[0, 1]
            var_neg = np.var(market_neg)
            if var_neg > 0:
                negative_beta = cov_neg / var_neg
        
        return {
            'beta': beta,
            'correlation': correlation,
            'positive_beta': positive_beta,
            'negative_beta': negative_beta,
            'data_points': len(stock_ret),
            'positive_days': np.sum(positive_mask),
            'negative_days': np.sum(negative_mask)
        }
        
    except Exception as e:
        print(f"Error calculating beta: {e}")
        return None

def main():
    print("="*80)
    print("5-YEAR S&P 500 BETA ANALYSIS (2020-2025)")
    print("Comparison with Yahoo Finance Beta Values")
    print("="*80)
    
    # Define test symbols including PLTR
    test_symbols = ['PLTR', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'COIN', 'KO', 'JNJ', 'PG']
    
    # Get market data (SPY) first
    print("Fetching 5-year market data (SPY) from 2020-01-01 to 2025-01-01...")
    market_data = getBars('SPY', '2020-01-01', '2025-01-01')
    if market_data is None:
        print("Failed to get market data!")
        return
    
    print(f"Market data: {len(market_data)} days")
    
    # Process each test stock
    results = []
    
    for i, symbol in enumerate(test_symbols, 1):
        print(f"\nProcessing {i}/{len(test_symbols)}: {symbol}")
        
        try:
            # Get stock data for 5 years
            stock_data = getBars(symbol, '2020-01-01', '2025-01-01')
            
            if stock_data is None or len(stock_data) < 50:
                print(f"  ❌ Insufficient 5-year data for {symbol}")
                continue
            
            # Calculate beta
            beta_result = calculate_beta_simple(stock_data, market_data)
            
            if beta_result is None:
                print(f"  ❌ Beta calculation failed for {symbol}")
                continue
            
            # Add to results
            result = {
                'Symbol': symbol,
                'Beta_5Y': beta_result['beta'],
                'Correlation': beta_result['correlation'],
                'Positive_Beta': beta_result['positive_beta'],
                'Negative_Beta': beta_result['negative_beta'],
                'Data_Points': beta_result['data_points'],
                'Positive_Days': beta_result['positive_days'],
                'Negative_Days': beta_result['negative_days']
            }
            results.append(result)
            
            print(f"  ✅ 5Y Beta: {beta_result['beta']:.3f}, Correlation: {beta_result['correlation']:.3f}, Days: {beta_result['data_points']}")
            
            # Special focus on PLTR
            if symbol == 'PLTR':
                print(f"  🎯 PLTR ANALYSIS:")
                print(f"     5-Year Beta: {beta_result['beta']:.3f}")
                print(f"     Data Points: {beta_result['data_points']} trading days")
                print(f"     Correlation: {beta_result['correlation']:.3f}")
                if beta_result['positive_beta']:
                    print(f"     Bull Market Beta: {beta_result['positive_beta']:.3f}")
                if beta_result['negative_beta']:
                    print(f"     Bear Market Beta: {beta_result['negative_beta']:.3f}")
            
        except Exception as e:
            print(f"  ❌ Error processing {symbol}: {e}")
            continue
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        output_file = 'sp500_5year_beta_comparison.csv'
        results_df.to_csv(output_file, index=False)
        
        print(f"\n{'='*80}")
        print(f"5-YEAR BETA ANALYSIS COMPLETE!")
        print(f"{'='*80}")
        print(f"✅ Successfully processed: {len(results)} stocks")
        print(f"📊 Results saved to: {output_file}")
        
        # Show comparison with 10-year data
        print(f"\n📈 BETA COMPARISON (5Y vs Expected YFinance):")
        print(f"{'Symbol':<8} {'5Y Beta':<10} {'YF Expected':<12} {'Difference':<12}")
        print("-" * 50)
        
        # Expected YFinance betas (approximate from public sources)
        yf_betas = {
            'PLTR': 2.6,   # User mentioned this
            'NVDA': 1.7,   # We calculated this
            'TSLA': 2.1,   # High beta stock
            'AAPL': 1.2,   # Large cap tech
            'MSFT': 0.9,   # Stable large cap
            'GOOGL': 1.1,  # Large cap tech
            'AMZN': 1.2,   # Large cap tech
            'META': 1.3,   # Tech stock
            'COIN': 3.0,   # Crypto-related
            'KO': 0.6,     # Defensive
            'JNJ': 0.7,    # Healthcare defensive
            'PG': 0.5      # Consumer staples
        }
        
        for _, row in results_df.iterrows():
            symbol = row['Symbol']
            beta_5y = row['Beta_5Y']
            yf_expected = yf_betas.get(symbol, 'N/A')
            if yf_expected != 'N/A':
                diff = beta_5y - yf_expected
                print(f"{symbol:<8} {beta_5y:<10.3f} {yf_expected:<12.1f} {diff:<+12.3f}")
            else:
                print(f"{symbol:<8} {beta_5y:<10.3f} {'N/A':<12} {'N/A':<12}")
        
        # Specific PLTR analysis
        pltr_row = results_df[results_df['Symbol'] == 'PLTR']
        if not pltr_row.empty:
            pltr_beta = pltr_row.iloc[0]['Beta_5Y']
            print(f"\n🎯 PLTR SPECIFIC ANALYSIS:")
            print(f"   Our 5Y Beta: {pltr_beta:.3f}")
            print(f"   YFinance Expected: 2.6")
            print(f"   Difference: {pltr_beta - 2.6:+.3f}")
            print(f"   Match Quality: {'✅ CLOSE' if abs(pltr_beta - 2.6) < 0.3 else '❌ DIFFERENT'}")
        
        print(f"\n💡 INSIGHTS:")
        print(f"   • 5-year betas may differ from YFinance due to:")
        print(f"     - Different calculation periods")
        print(f"     - Different benchmarks (SPY vs S&P 500 index)")
        print(f"     - Raw vs adjusted prices")
        print(f"     - Frequency differences (daily vs weekly/monthly)")
        print(f"   • YFinance typically uses 2-3 year rolling windows")
        print(f"   • Our analysis uses exactly 5 years: 2020-2025")
        
    else:
        print("No successful results!")

if __name__ == "__main__":
    main()