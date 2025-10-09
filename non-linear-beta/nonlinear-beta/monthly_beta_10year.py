#!/usr/bin/env python3
"""
Monthly S&P 500 Beta Analysis (10 Years) - Yahoo Finance Style
Using monthly returns and S&P 500 index (^GSPC) over 10 years (2015-2025)
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
    monthly_prices = data['close'].resample('ME').last()  # Updated to 'ME' to avoid deprecation
    
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
    print("MONTHLY S&P 500 BETA ANALYSIS (10 YEARS) - Yahoo Finance Style")
    print("Using Monthly Returns & S&P 500 Index (^GSPC) 2015-2025")
    print("="*80)
    
    # Define test symbols including PLTR and some key stocks
    test_symbols = ['PLTR', 'NVDA', 'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'COIN', 'KO', 'JNJ', 'PG', 'BRK.A', 'V', 'JPM']
    
    # Get S&P 500 index data (^GSPC) for 10 years
    print("Fetching 10-year S&P 500 index data (^GSPC) from 2015-01-01 to 2025-01-01...")
    market_data = getBars('^GSPC', '2015-01-01', '2025-01-01')
    if market_data is None:
        print("Failed to get S&P 500 index data! Trying SPY as fallback...")
        market_data = getBars('SPY', '2015-01-01', '2025-01-01')
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
            # Get stock data for 10 years
            stock_data = getBars(symbol, '2015-01-01', '2025-01-01')
            
            if stock_data is None or len(stock_data) < 500:  # Need decent amount of data
                print(f"  ❌ Insufficient 10-year data for {symbol}")
                continue
            
            # Calculate monthly beta
            beta_result = calculate_beta_monthly(stock_data, market_data)
            
            if beta_result is None:
                print(f"  ❌ Monthly beta calculation failed for {symbol}")
                continue
            
            # Add to results
            result = {
                'Symbol': symbol,
                'Beta_Monthly_10Y': beta_result['beta'],
                'Correlation': beta_result['correlation'],
                'R_Squared': beta_result['r_squared'],
                'Positive_Beta': beta_result['positive_beta'],
                'Negative_Beta': beta_result['negative_beta'],
                'Months': beta_result['months'],
                'Positive_Months': beta_result['positive_months'],
                'Negative_Months': beta_result['negative_months']
            }
            results.append(result)
            
            print(f"  ✅ Monthly Beta (10Y): {beta_result['beta']:.3f}, R²: {beta_result['r_squared']:.3f}, Months: {beta_result['months']}")
            
            # Special focus on key stocks
            if symbol in ['PLTR', 'NVDA']:
                print(f"  🎯 {symbol} MONTHLY ANALYSIS (10Y):")
                print(f"     Monthly Beta: {beta_result['beta']:.3f}")
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
        output_file = 'sp500_monthly_beta_10year.csv'
        results_df.to_csv(output_file, index=False)
        
        print(f"\n{'='*80}")
        print(f"10-YEAR MONTHLY BETA ANALYSIS COMPLETE!")
        print(f"{'='*80}")
        print(f"✅ Successfully processed: {len(results)} stocks")
        print(f"📊 Results saved to: {output_file}")
        print(f"🎯 Market Benchmark: {market_symbol}")
        print(f"📅 Period: 2015-2025 (10 years)")
        
        # Show comparison with previous analyses
        print(f"\n📈 10-YEAR MONTHLY BETA RESULTS:")
        print(f"{'Symbol':<8} {'10Y Beta':<10} {'R²':<8} {'Months':<8} {'Bull β':<8} {'Bear β':<8}")
        print("-" * 70)
        
        for _, row in results_df.iterrows():
            symbol = row['Symbol']
            beta = row['Beta_Monthly_10Y']
            r2 = row['R_Squared']
            months = row['Months']
            pos_beta = row['Positive_Beta'] if pd.notna(row['Positive_Beta']) else 0
            neg_beta = row['Negative_Beta'] if pd.notna(row['Negative_Beta']) else 0
            print(f"{symbol:<8} {beta:<10.3f} {r2:<8.3f} {months:<8.0f} {pos_beta:<8.3f} {neg_beta:<8.3f}")
        
        # Compare 10Y vs 5Y for key stocks
        key_stocks_5y = {
            'PLTR': 2.871,
            'NVDA': 1.665,
            'TSLA': 2.385,
            'AAPL': 1.232,
            'MSFT': 0.917
        }
        
        print(f"\n📊 COMPARISON: 10-Year vs 5-Year Monthly Betas:")
        print(f"{'Stock':<8} {'10Y Beta':<10} {'5Y Beta':<10} {'Difference':<12}")
        print("-" * 45)
        
        for _, row in results_df.iterrows():
            symbol = row['Symbol']
            beta_10y = row['Beta_Monthly_10Y']
            if symbol in key_stocks_5y:
                beta_5y = key_stocks_5y[symbol]
                diff = beta_10y - beta_5y
                print(f"{symbol:<8} {beta_10y:<10.3f} {beta_5y:<10.3f} {diff:<+12.3f}")
        
        # Specific analysis for key stocks
        key_results = results_df[results_df['Symbol'].isin(['PLTR', 'NVDA', 'TSLA'])]
        if not key_results.empty:
            print(f"\n🎯 KEY INSIGHTS (10-Year Monthly Analysis):")
            for _, row in key_results.iterrows():
                symbol = row['Symbol']
                beta = row['Beta_Monthly_10Y']
                r2 = row['R_Squared']
                months = row['Months']
                print(f"\n   {symbol}:")
                print(f"   • 10-Year Beta: {beta:.3f}")
                print(f"   • Market Correlation: {r2*100:.1f}%")
                print(f"   • Data Quality: {months} months of data")
                
                if symbol == 'PLTR' and months < 60:
                    print(f"   • Note: PLTR only has {months} months (IPO Sept 2020)")
                elif symbol == 'NVDA':
                    print(f"   • NVIDIA: Full 10-year dataset, reliable beta")
        
        print(f"\n💡 10-YEAR vs 5-YEAR INSIGHTS:")
        print(f"   • 10-year betas include more market cycles")
        print(f"   • Captures 2015-2017 growth, 2018 correction, 2020 COVID, 2021-2022 meme stocks")
        print(f"   • More stable and representative of long-term risk")
        print(f"   • PLTR still limited by IPO date (only ~4.3 years of data)")
        
        # Show market regime breakdown
        total_months = len(market_monthly)
        positive_months = len(market_monthly[market_monthly > 0])
        negative_months = total_months - positive_months
        
        print(f"\n📈 MARKET REGIME BREAKDOWN (10 Years):")
        print(f"   • Total Months: {total_months}")
        print(f"   • Positive Months: {positive_months} ({positive_months/total_months*100:.1f}%)")
        print(f"   • Negative Months: {negative_months} ({negative_months/total_months*100:.1f}%)")
        print(f"   • Covers major market cycles: 2015-2017 bull, 2018 correction, 2020 crash/recovery, 2021-2022 growth/correction")
        
    else:
        print("No successful results!")

if __name__ == "__main__":
    main()