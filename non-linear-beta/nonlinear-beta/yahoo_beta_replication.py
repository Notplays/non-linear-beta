#!/usr/bin/env python3
"""
Yahoo Finance Beta Replication - NVIDIA Focus
Trying to match Yahoo Finance's exact 5Y Monthly Beta of 2.12 for NVIDIA
"""

import pandas as pd
import numpy as np
import sys
import os
import time
from datetime import datetime, timedelta

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from getBars import getBars

def get_yahoo_style_beta(symbol, market_symbol='^GSPC', years=5):
    """
    Try to replicate Yahoo Finance beta calculation exactly.
    """
    print(f"\n🔍 ANALYZING {symbol} - Yahoo Finance Style")
    print("="*60)
    
    # Calculate exact 5-year period (60 months back from now)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years*365 + 30)  # Add buffer
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    print(f"Period: {start_str} to {end_str}")
    
    # Get data
    print(f"Fetching {symbol} data...")
    stock_data = getBars(symbol, start_str, end_str)
    print(f"Fetching market data ({market_symbol})...")
    market_data = getBars(market_symbol, start_str, end_str)
    
    if stock_data is None or market_data is None:
        print("❌ Failed to get data")
        return None
    
    print(f"Stock data: {len(stock_data)} days")
    print(f"Market data: {len(market_data)} days")
    
    # Method 1: Last trading day of each month (Yahoo style)
    stock_monthly_eom = stock_data['close'].resample('M').last()
    market_monthly_eom = market_data['close'].resample('M').last()
    
    # Method 2: Business month end
    stock_monthly_bm = stock_data['close'].resample('BM').last()
    market_monthly_bm = market_data['close'].resample('BM').last()
    
    # Method 3: Calendar month end with forward fill
    stock_monthly_cal = stock_data['close'].resample('M').last().fillna(method='ffill')
    market_monthly_cal = market_data['close'].resample('M').last().fillna(method='ffill')
    
    methods = [
        ("End of Month", stock_monthly_eom, market_monthly_eom),
        ("Business Month End", stock_monthly_bm, market_monthly_bm),
        ("Calendar Month End", stock_monthly_cal, market_monthly_cal)
    ]
    
    results = []
    
    for method_name, stock_monthly, market_monthly in methods:
        print(f"\n📊 METHOD: {method_name}")
        
        # Calculate monthly returns
        stock_returns = stock_monthly.pct_change().dropna()
        market_returns = market_monthly.pct_change().dropna()
        
        # Align data
        common_dates = stock_returns.index.intersection(market_returns.index)
        if len(common_dates) < 12:
            print(f"❌ Insufficient data: {len(common_dates)} months")
            continue
            
        stock_aligned = stock_returns.loc[common_dates]
        market_aligned = market_returns.loc[common_dates]
        
        # Limit to exactly 60 months if we have more
        if len(stock_aligned) > 60:
            stock_aligned = stock_aligned.tail(60)
            market_aligned = market_aligned.tail(60)
        
        print(f"Monthly returns: {len(stock_aligned)} months")
        print(f"Date range: {stock_aligned.index[0].strftime('%Y-%m')} to {stock_aligned.index[-1].strftime('%Y-%m')}")
        
        # Calculate beta
        stock_ret = stock_aligned.values
        market_ret = market_aligned.values
        
        # Method A: Standard covariance/variance
        covariance = np.cov(stock_ret, market_ret)[0, 1]
        market_variance = np.var(market_ret, ddof=1)  # Sample variance
        beta_a = covariance / market_variance
        
        # Method B: Linear regression (slope)
        from scipy import stats
        slope, intercept, r_value, p_value, std_err = stats.linregress(market_ret, stock_ret)
        beta_b = slope
        
        # Method C: Using pandas corr and std
        correlation = stock_aligned.corr(market_aligned)
        beta_c = correlation * (stock_aligned.std() / market_aligned.std())
        
        r_squared = r_value ** 2
        
        print(f"Beta (Cov/Var): {beta_a:.3f}")
        print(f"Beta (Regression): {beta_b:.3f}")
        print(f"Beta (Corr*Vol): {beta_c:.3f}")
        print(f"R-squared: {r_squared:.3f}")
        print(f"Correlation: {correlation:.3f}")
        
        results.append({
            'Method': method_name,
            'Beta_CovVar': beta_a,
            'Beta_Regression': beta_b,
            'Beta_CorrVol': beta_c,
            'R_Squared': r_squared,
            'Correlation': correlation,
            'Months': len(stock_aligned),
            'Start_Date': stock_aligned.index[0],
            'End_Date': stock_aligned.index[-1]
        })
    
    return results

def try_different_benchmarks(symbol='NVDA'):
    """
    Try different market benchmarks to see which matches Yahoo Finance.
    """
    benchmarks = [
        '^GSPC',  # S&P 500 Index
        'SPY',    # SPDR S&P 500 ETF
        '^SPX',   # S&P 500 (alternative symbol)
        'VOO',    # Vanguard S&P 500 ETF
    ]
    
    print(f"🧪 TESTING DIFFERENT BENCHMARKS FOR {symbol}")
    print("="*70)
    
    all_results = []
    
    for benchmark in benchmarks:
        print(f"\n📈 BENCHMARK: {benchmark}")
        print("-" * 40)
        
        try:
            results = get_yahoo_style_beta(symbol, benchmark, years=5)
            if results:
                for result in results:
                    result['Benchmark'] = benchmark
                    all_results.append(result)
                    
                    # Find closest to Yahoo's 2.12
                    betas = [result['Beta_CovVar'], result['Beta_Regression'], result['Beta_CorrVol']]
                    closest_beta = min(betas, key=lambda x: abs(x - 2.12))
                    diff = abs(closest_beta - 2.12)
                    
                    print(f"   {result['Method']}: Closest = {closest_beta:.3f} (diff: {diff:.3f})")
            else:
                print(f"   ❌ Failed to get data for {benchmark}")
                
        except Exception as e:
            print(f"   ❌ Error with {benchmark}: {e}")
    
    return all_results

def main():
    print("🎯 YAHOO FINANCE BETA REPLICATION")
    print("Target: NVIDIA Beta (5Y Monthly) = 2.12")
    print("="*80)
    
    # Test NVIDIA with different approaches
    all_results = try_different_benchmarks('NVDA')
    
    if all_results:
        # Convert to DataFrame for analysis
        df = pd.DataFrame(all_results)
        output_file = 'yahoo_beta_replication_analysis.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n📊 SUMMARY OF ALL ATTEMPTS")
        print("="*80)
        print(f"{'Benchmark':<10} {'Method':<20} {'Beta':<8} {'Diff from 2.12':<15} {'R²':<8}")
        print("-" * 70)
        
        best_match = None
        min_diff = float('inf')
        
        for _, row in df.iterrows():
            benchmark = row['Benchmark']
            method = row['Method']
            beta = row['Beta_Regression']  # Use regression beta as standard
            diff = abs(beta - 2.12)
            r2 = row['R_Squared']
            
            print(f"{benchmark:<10} {method:<20} {beta:<8.3f} {diff:<15.3f} {r2:<8.3f}")
            
            if diff < min_diff:
                min_diff = diff
                best_match = row
        
        print(f"\n🏆 BEST MATCH TO YAHOO FINANCE 2.12:")
        if best_match is not None:
            print(f"   Benchmark: {best_match['Benchmark']}")
            print(f"   Method: {best_match['Method']}")
            print(f"   Beta: {best_match['Beta_Regression']:.3f}")
            print(f"   Difference: {min_diff:.3f}")
            print(f"   R-squared: {best_match['R_Squared']:.3f}")
            print(f"   Period: {best_match['Start_Date'].strftime('%Y-%m')} to {best_match['End_Date'].strftime('%Y-%m')}")
            print(f"   Months: {best_match['Months']}")
        
        print(f"\n💡 POSSIBLE REASONS FOR DIFFERENCES:")
        print(f"   • Yahoo may use adjusted prices differently")
        print(f"   • Different calculation periods (rolling vs fixed)")
        print(f"   • Yahoo may use weekly returns instead of monthly")
        print(f"   • Different handling of dividends/splits")
        print(f"   • Yahoo may use a proprietary benchmark")
        print(f"   • Time zone differences in month-end calculations")
        
        print(f"\n📁 Detailed results saved to: {output_file}")
        
        # Test if Yahoo uses a different time period
        print(f"\n🕐 TESTING DIFFERENT TIME PERIODS:")
        periods = [3, 4, 5, 6]
        for years in periods:
            try:
                results = get_yahoo_style_beta('NVDA', '^GSPC', years=years)
                if results and len(results) > 0:
                    beta = results[0]['Beta_Regression']
                    diff = abs(beta - 2.12)
                    print(f"   {years} years: Beta = {beta:.3f} (diff: {diff:.3f})")
            except:
                print(f"   {years} years: Failed")
    
    else:
        print("❌ No results obtained")

if __name__ == "__main__":
    main()