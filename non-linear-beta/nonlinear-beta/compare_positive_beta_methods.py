#!/usr/bin/env python3
"""
Compare positive_beta calculation methodologies:
1. Your original covariance/variance method
2. My linear regression method used in Yahoo Finance methodology
"""

import pandas as pd
import numpy as np
from scipy import stats
import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from getBars import getBars

def calculate_positive_beta_original_method(stock_returns, market_returns):
    """
    Your original methodology using covariance/variance
    """
    # Split by positive/negative market days
    positive_mask = market_returns > 0
    positive_days_count = np.sum(positive_mask)
    
    positive_beta = None
    if positive_days_count > 20:
        stock_pos = stock_returns[positive_mask]
        market_pos = market_returns[positive_mask]
        pos_covariance = np.cov(stock_pos, market_pos)[0, 1]
        pos_market_variance = np.var(market_pos)
        if pos_market_variance > 0:
            positive_beta = pos_covariance / pos_market_variance
    
    return positive_beta, positive_days_count

def calculate_positive_beta_regression_method(stock_returns, market_returns):
    """
    My regression methodology used in Yahoo Finance approach
    """
    positive_mask = market_returns > 0
    positive_days_count = np.sum(positive_mask)
    
    positive_beta = None
    if positive_days_count > 5:  # Lower threshold in my method
        stock_pos = stock_returns[positive_mask]
        market_pos = market_returns[positive_mask]
        if len(stock_pos) > 1:
            slope_pos, _, _, _, _ = stats.linregress(market_pos, stock_pos)
            positive_beta = slope_pos
    
    return positive_beta, positive_days_count

def test_both_methods(symbol, period_years=5):
    """
    Test both methodologies on a specific stock
    """
    print(f"\n🔍 TESTING POSITIVE BETA METHODOLOGIES FOR {symbol}")
    print("="*60)
    
    # Get data (same as Yahoo methodology)
    from datetime import datetime, timedelta
    end_date = datetime.now()
    start_date = end_date - timedelta(days=period_years*365 + 30)
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    # Get stock and market data
    stock_data = getBars(symbol, start_str, end_str)
    market_data = getBars('^GSPC', start_str, end_str)
    
    if stock_data is None or market_data is None:
        print(f"❌ Failed to get data for {symbol}")
        return None
    
    # Calculate monthly returns (Yahoo methodology)
    stock_monthly = stock_data['close'].resample('ME').last()
    market_monthly = market_data['close'].resample('ME').last()
    
    stock_returns = stock_monthly.pct_change().dropna()
    market_returns = market_monthly.pct_change().dropna()
    
    # Align data
    common_dates = stock_returns.index.intersection(market_returns.index)
    stock_aligned = stock_returns.loc[common_dates].values
    market_aligned = market_returns.loc[common_dates].values
    
    print(f"📊 Data period: {common_dates[0].strftime('%Y-%m')} to {common_dates[-1].strftime('%Y-%m')}")
    print(f"📈 Total months: {len(common_dates)}")
    print(f"📈 Market up months: {np.sum(market_aligned > 0)}")
    print(f"📉 Market down months: {np.sum(market_aligned < 0)}")
    
    # Method 1: Your original covariance/variance approach
    pos_beta_orig, pos_days_orig = calculate_positive_beta_original_method(stock_aligned, market_aligned)
    
    # Method 2: My regression approach
    pos_beta_regr, pos_days_regr = calculate_positive_beta_regression_method(stock_aligned, market_aligned)
    
    print(f"\n📈 POSITIVE BETA COMPARISON:")
    print(f"Original Method (Cov/Var): {pos_beta_orig:.4f}" if pos_beta_orig else "Original Method: N/A (need >20 positive days)")
    print(f"Regression Method:         {pos_beta_regr:.4f}" if pos_beta_regr else "Regression Method: N/A")
    
    if pos_beta_orig and pos_beta_regr:
        difference = pos_beta_regr - pos_beta_orig
        pct_diff = (difference / pos_beta_orig) * 100
        print(f"Difference: {difference:+.4f} ({pct_diff:+.1f}%)")
        
        if abs(pct_diff) < 5:
            print("✅ Methods are VERY SIMILAR")
        elif abs(pct_diff) < 15:
            print("✅ Methods are SIMILAR")
        else:
            print("⚠️  Methods show SIGNIFICANT DIFFERENCE")
    
    # Also test traditional beta for reference
    covariance = np.cov(stock_aligned, market_aligned)[0, 1]
    market_variance = np.var(market_aligned)
    traditional_beta = covariance / market_variance
    
    # Regression beta (overall)
    slope_all, _, r_value, _, _ = stats.linregress(market_aligned, stock_aligned)
    regression_beta = slope_all
    
    print(f"\n📊 OVERALL BETA COMPARISON:")
    print(f"Traditional Beta (Cov/Var): {traditional_beta:.4f}")
    print(f"Regression Beta:            {regression_beta:.4f}")
    print(f"R-squared:                  {r_value**2:.4f}")
    
    return {
        'symbol': symbol,
        'months': len(common_dates),
        'positive_months': np.sum(market_aligned > 0),
        'pos_beta_original': pos_beta_orig,
        'pos_beta_regression': pos_beta_regr,
        'traditional_beta': traditional_beta,
        'regression_beta': regression_beta,
        'r_squared': r_value**2
    }

def main():
    print("🔍 POSITIVE BETA METHODOLOGY COMPARISON")
    print("="*60)
    print("Comparing two approaches:")
    print("1. Original: positive_beta = cov(stock_pos, market_pos) / var(market_pos)")
    print("2. Regression: positive_beta = slope from linear regression on positive days")
    
    # Test key stocks
    test_stocks = ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'AMZN', 'META', 'GOOGL', 'JPM', 'JNJ', 'PG']
    
    results = []
    for symbol in test_stocks:
        try:
            result = test_both_methods(symbol)
            if result:
                results.append(result)
        except Exception as e:
            print(f"❌ Error testing {symbol}: {e}")
    
    # Summary analysis
    if results:
        print(f"\n{'='*80}")
        print(f"SUMMARY ANALYSIS ({len(results)} stocks)")
        print(f"{'='*80}")
        
        valid_comparisons = [r for r in results if r['pos_beta_original'] and r['pos_beta_regression']]
        
        if valid_comparisons:
            print(f"✅ Valid comparisons: {len(valid_comparisons)}/{len(results)}")
            
            differences = []
            pct_differences = []
            
            print(f"\n{'Stock':<8} {'Original':<10} {'Regression':<11} {'Difference':<11} {'% Diff':<8}")
            print("-" * 55)
            
            for r in valid_comparisons:
                diff = r['pos_beta_regression'] - r['pos_beta_original']
                pct_diff = (diff / r['pos_beta_original']) * 100
                differences.append(diff)
                pct_differences.append(pct_diff)
                
                print(f"{r['symbol']:<8} {r['pos_beta_original']:<10.4f} {r['pos_beta_regression']:<11.4f} {diff:<+11.4f} {pct_diff:<+8.1f}%")
            
            print(f"\n📊 STATISTICAL SUMMARY:")
            print(f"Mean difference: {np.mean(differences):+.4f}")
            print(f"Mean % difference: {np.mean(pct_differences):+.1f}%")
            print(f"Std % difference: {np.std(pct_differences):.1f}%")
            print(f"Max % difference: {np.max(np.abs(pct_differences)):.1f}%")
            
            # Determine if methods are equivalent
            mean_abs_pct_diff = np.mean(np.abs(pct_differences))
            if mean_abs_pct_diff < 5:
                print(f"\n✅ CONCLUSION: Methods are HIGHLY EQUIVALENT (avg {mean_abs_pct_diff:.1f}% difference)")
            elif mean_abs_pct_diff < 15:
                print(f"\n✅ CONCLUSION: Methods are EQUIVALENT (avg {mean_abs_pct_diff:.1f}% difference)")
            else:
                print(f"\n⚠️  CONCLUSION: Methods show MATERIAL DIFFERENCES (avg {mean_abs_pct_diff:.1f}% difference)")
        
        else:
            print("❌ No valid comparisons possible (insufficient positive market days)")
    
    print(f"\n💡 METHODOLOGY NOTES:")
    print(f"• Both methods identify positive market days the same way (market_return > 0)")
    print(f"• Original method uses covariance/variance formula (your approach)")
    print(f"• Regression method uses linear regression slope (my Yahoo Finance approach)")
    print(f"• Both should theoretically give similar results for well-behaved data")
    print(f"• Regression method is more robust to outliers")
    print(f"• Your original method requires >20 positive days, mine requires >5")

if __name__ == "__main__":
    main()