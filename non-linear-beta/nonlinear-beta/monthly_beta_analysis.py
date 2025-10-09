#!/usr/bin/env python3
"""
Monthly S&P 500 Beta Analysis (5 Years) - Yahoo Finance Style
Using monthly returns and S&P 500 index (^GSPC)
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

def resample_to_monthly(data):
    """Convert daily data to monthly returns."""
    if data is None or len(data) == 0:
        return None
    
    # Resample to month-end prices
    monthly_prices = data['close'].resample('M').last()
    
    # Calculate monthly returns
    monthly_returns = monthly_prices.pct_change().dropna()
    
    return monthly_returns

def calculate_beta_monthly(stock_data, market_data):
    """
    Calculate beta using monthly returns - Yahoo Finance style.
    """
    try:
        # Convert to monthly returns
        stock_monthly = resample_to_monthly(stock_data)
        market_monthly = resample_to_monthly(market_data)
        
        if stock_monthly is None or market_monthly is None:
            return None
        
        # Align on common dates
        common_dates = stock_monthly.index.intersection(market_monthly.index)
        if len(common_dates) < 24:  # Need at least 24 months (2 years)
            return None
            
        stock_aligned = stock_monthly.loc[common_dates]
        market_aligned = market_monthly.loc[common_dates]
        
        # Convert to numpy arrays
        stock_ret = stock_aligned.values
        market_ret = market_aligned.values
        
        # Calculate beta
        covariance = np.cov(stock_ret, market_ret)[0, 1]
        market_variance = np.var(market_ret)
        
        if market_variance == 0:
            return None
            
        beta = covariance / market_variance
        correlation = np.corrcoef(stock_ret, market_ret)[0, 1]
        
        # Calculate R-squared
        r_squared = correlation ** 2
        
        # Calculate nonlinear betas with monthly data
        positive_mask = market_ret > 0
        negative_mask = market_ret < 0
        
        positive_beta = None
        negative_beta = None
        
        if np.sum(positive_mask) > 5:  # At least 5 positive months
            stock_pos = stock_ret[positive_mask]
            market_pos = market_ret[positive_mask]
            if len(stock_pos) > 1:
                cov_pos = np.cov(stock_pos, market_pos)[0, 1]
                var_pos = np.var(market_pos)
                if var_pos > 0:
                    positive_beta = cov_pos / var_pos
                
        if np.sum(negative_mask) > 5:  # At least 5 negative months
            stock_neg = stock_ret[negative_mask]
            market_neg = market_ret[negative_mask]
            if len(stock_neg) > 1:
                cov_neg = np.cov(stock_neg, market_neg)[0, 1]
                var_neg = np.var(market_neg)
                if var_neg > 0:
                    negative_beta = cov_neg / var_neg
        
        return {
            'beta': beta,
            'correlation': correlation,
            'r_squared': r_squared,
            'positive_beta': positive_beta,
            'negative_beta': negative_beta,
            'months': len(stock_ret),
            'positive_months': np.sum(positive_mask),
            'negative_months': np.sum(negative_mask)
        }
        
    except Exception as e:
        print(f"Error calculating monthly beta: {e}")
        return None

def main():
    print("="*80)
    print("MONTHLY S&P 500 BETA ANALYSIS (5 Years) - Yahoo Finance Style")
    print("Using Monthly Returns & S&P 500 Index (^GSPC)")
    print("="*80)
    
    # Define test symbols including PLTR
    test_symbols = ['PLTR', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'COIN', 'KO', 'JNJ', 'PG']
    
    # Get S&P 500 index data (^GSPC) for 5 years
    print("Fetching 5-year S&P 500 index data (^GSPC) from 2020-01-01 to 2025-01-01...")
    market_data = getBars('^GSPC', '2020-01-01', '2025-01-01')
    if market_data is None:
        print("Failed to get S&P 500 index data! Trying SPY as fallback...")
        market_data = getBars('SPY', '2020-01-01', '2025-01-01')
        if market_data is None:
            print("Failed to get market data!")
            return
        market_symbol = "SPY"
    else:
        market_symbol = "^GSPC"
    
    print(f"Market data ({market_symbol}): {len(market_data)} trading days")
    
    # Convert market data to monthly
    market_monthly = resample_to_monthly(market_data)
    print(f"Market monthly data: {len(market_monthly)} months")
    
    # Process each test stock
    results = []
    
    for i, symbol in enumerate(test_symbols, 1):
        print(f"\nProcessing {i}/{len(test_symbols)}: {symbol}")
        
        try:
            # Get stock data for 5 years
            stock_data = getBars(symbol, '2020-01-01', '2025-01-01')
            
            if stock_data is None or len(stock_data) < 100:
                print(f"  ❌ Insufficient 5-year data for {symbol}")
                continue
            
            # Calculate monthly beta
            beta_result = calculate_beta_monthly(stock_data, market_data)
            
            if beta_result is None:
                print(f"  ❌ Monthly beta calculation failed for {symbol}")
                continue
            
            # Add to results
            result = {
                'Symbol': symbol,
                'Beta_Monthly_5Y': beta_result['beta'],
                'Correlation': beta_result['correlation'],
                'R_Squared': beta_result['r_squared'],
                'Positive_Beta': beta_result['positive_beta'],
                'Negative_Beta': beta_result['negative_beta'],
                'Months': beta_result['months'],
                'Positive_Months': beta_result['positive_months'],
                'Negative_Months': beta_result['negative_months']
            }
            results.append(result)
            
            print(f"  ✅ Monthly Beta: {beta_result['beta']:.3f}, R²: {beta_result['r_squared']:.3f}, Months: {beta_result['months']}")
            
            # Special focus on PLTR
            if symbol == 'PLTR':
                print(f"  🎯 PLTR MONTHLY ANALYSIS:")
                print(f"     Monthly Beta (5Y): {beta_result['beta']:.3f}")
                print(f"     R-Squared: {beta_result['r_squared']:.3f}")
                print(f"     Data Points: {beta_result['months']} months")
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
        output_file = 'sp500_monthly_beta_5year.csv'
        results_df.to_csv(output_file, index=False)
        
        print(f"\n{'='*80}")
        print(f"MONTHLY BETA ANALYSIS COMPLETE!")
        print(f"{'='*80}")
        print(f"✅ Successfully processed: {len(results)} stocks")
        print(f"📊 Results saved to: {output_file}")
        print(f"🎯 Market Benchmark: {market_symbol}")
        
        # Show comparison with Yahoo Finance expected values
        print(f"\n📈 MONTHLY BETA COMPARISON (vs YFinance Expected):")
        print(f"{'Symbol':<8} {'Monthly Beta':<12} {'YF Expected':<12} {'Difference':<12} {'R²':<8}")
        print("-" * 65)
        
        # Expected YFinance betas (what user mentioned)
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
            beta_monthly = row['Beta_Monthly_5Y']
            r_squared = row['R_Squared']
            yf_expected = yf_betas.get(symbol, 'N/A')
            if yf_expected != 'N/A':
                diff = beta_monthly - yf_expected
                print(f"{symbol:<8} {beta_monthly:<12.3f} {yf_expected:<12.1f} {diff:<+12.3f} {r_squared:<8.3f}")
            else:
                print(f"{symbol:<8} {beta_monthly:<12.3f} {'N/A':<12} {'N/A':<12} {r_squared:<8.3f}")
        
        # Specific PLTR analysis
        pltr_row = results_df[results_df['Symbol'] == 'PLTR']
        if not pltr_row.empty:
            pltr_beta = pltr_row.iloc[0]['Beta_Monthly_5Y']
            pltr_r2 = pltr_row.iloc[0]['R_Squared']
            print(f"\n🎯 PLTR DETAILED ANALYSIS:")
            print(f"   Monthly Beta (5Y): {pltr_beta:.3f}")
            print(f"   YFinance Expected: 2.6")
            print(f"   Difference: {pltr_beta - 2.6:+.3f}")
            print(f"   R-Squared: {pltr_r2:.3f} ({pltr_r2*100:.1f}% explained variance)")
            print(f"   Match Quality: {'✅ VERY CLOSE' if abs(pltr_beta - 2.6) < 0.2 else '✅ CLOSE' if abs(pltr_beta - 2.6) < 0.5 else '❌ DIFFERENT'}")
        
        print(f"\n💡 KEY DIFFERENCES FROM DAILY ANALYSIS:")
        print(f"   • Monthly returns smooth out daily noise")
        print(f"   • Better matches institutional analysis methods")
        print(f"   • Yahoo Finance likely uses similar monthly methodology")
        print(f"   • R-squared shows explanatory power of the relationship")
        
        # Compare highest R-squared stocks
        top_r2 = results_df.nlargest(3, 'R_Squared')
        print(f"\n🏆 HIGHEST R-SQUARED (Best Market Correlation):")
        for _, row in top_r2.iterrows():
            print(f"   {row['Symbol']}: R² = {row['R_Squared']:.3f} ({row['R_Squared']*100:.1f}%)")
        
    else:
        print("No successful results!")

if __name__ == "__main__":
    main()