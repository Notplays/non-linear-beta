#!/usr/bin/env python3
"""
Yahoo Finance Beta Replication - 10 Years (2015-2025)
Using the same methodology that matched perfectly for 5Y but extended to 10Y
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

def get_yahoo_style_beta_10y(symbol, market_symbol='^GSPC', years=10):
    """
    Calculate 10-year beta using the exact methodology that matched Yahoo Finance 5Y.
    """
    print(f"\n🔍 ANALYZING {symbol} - 10-Year Yahoo Finance Style")
    print("="*60)
    
    # Use fixed 10-year period: 2015-01-01 to 2025-01-01
    start_str = '2015-01-01'
    end_str = '2025-01-01'
    
    print(f"Period: {start_str} to {end_str} (10 years)")
    
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
    
    # Use End of Month method (the one that matched perfectly)
    stock_monthly_eom = stock_data['close'].resample('ME').last()  # Updated to 'ME'
    market_monthly_eom = market_data['close'].resample('ME').last()
    
    print(f"\n📊 METHOD: End of Month (10 Years)")
    
    # Calculate monthly returns
    stock_returns = stock_monthly_eom.pct_change().dropna()
    market_returns = market_monthly_eom.pct_change().dropna()
    
    # Align data
    common_dates = stock_returns.index.intersection(market_returns.index)
    if len(common_dates) < 24:
        print(f"❌ Insufficient data: {len(common_dates)} months")
        return None
        
    stock_aligned = stock_returns.loc[common_dates]
    market_aligned = market_returns.loc[common_dates]
    
    print(f"Monthly returns: {len(stock_aligned)} months")
    print(f"Date range: {stock_aligned.index[0].strftime('%Y-%m')} to {stock_aligned.index[-1].strftime('%Y-%m')}")
    
    # Calculate beta using regression method (most accurate)
    stock_ret = stock_aligned.values
    market_ret = market_aligned.values
    
    from scipy import stats
    slope, intercept, r_value, p_value, std_err = stats.linregress(market_ret, stock_ret)
    beta = slope
    r_squared = r_value ** 2
    correlation = stock_aligned.corr(market_aligned)
    
    # Calculate nonlinear betas
    positive_mask = market_ret > 0
    negative_mask = market_ret < 0
    
    positive_beta = None
    negative_beta = None
    
    if np.sum(positive_mask) > 5:
        stock_pos = stock_ret[positive_mask]
        market_pos = market_ret[positive_mask]
        if len(stock_pos) > 1:
            slope_pos, _, _, _, _ = stats.linregress(market_pos, stock_pos)
            positive_beta = slope_pos
            
    if np.sum(negative_mask) > 5:
        stock_neg = stock_ret[negative_mask]
        market_neg = market_ret[negative_mask]
        if len(stock_neg) > 1:
            slope_neg, _, _, _, _ = stats.linregress(market_neg, stock_neg)
            negative_beta = slope_neg
    
    print(f"Beta (10Y): {beta:.3f}")
    print(f"R-squared: {r_squared:.3f}")
    print(f"Correlation: {correlation:.3f}")
    print(f"Standard Error: {std_err:.3f}")
    
    if positive_beta:
        print(f"Bull Market Beta: {positive_beta:.3f}")
    if negative_beta:
        print(f"Bear Market Beta: {negative_beta:.3f}")
    
    return {
        'Symbol': symbol,
        'Beta_10Y': beta,
        'R_Squared': r_squared,
        'Correlation': correlation,
        'Standard_Error': std_err,
        'Positive_Beta': positive_beta,
        'Negative_Beta': negative_beta,
        'Months': len(stock_aligned),
        'Positive_Months': np.sum(positive_mask),
        'Negative_Months': np.sum(negative_mask),
        'Start_Date': stock_aligned.index[0],
        'End_Date': stock_aligned.index[-1]
    }

def main():
    print("🎯 10-YEAR BETA ANALYSIS - Yahoo Finance Methodology")
    print("Using the exact method that matched NVDA 5Y beta (2.109 vs 2.12)")
    print("="*80)
    
    # Test key stocks including full S&P 500 representation
    test_symbols = [
        # Tech Giants
        'NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA',
        # Financials  
        'JPM', 'BAC', 'WFC', 'GS', 'MS',
        # Healthcare
        'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK',
        # Consumer
        'KO', 'PG', 'WMT', 'HD', 'MCD',
        # Energy
        'XOM', 'CVX', 'COP', 'SLB',
        # Industrials
        'BA', 'CAT', 'GE', 'MMM',
        # New listings (limited data)
        'PLTR', 'COIN', 'HOOD'
    ]
    
    results = []
    failed_stocks = []
    
    for i, symbol in enumerate(test_symbols, 1):
        print(f"\nProcessing {i}/{len(test_symbols)}: {symbol}")
        print("-" * 50)
        
        try:
            result = get_yahoo_style_beta_10y(symbol)
            
            if result is not None:
                results.append(result)
                print(f"✅ Success: {symbol} Beta = {result['Beta_10Y']:.3f}")
            else:
                failed_stocks.append(symbol)
                print(f"❌ Failed: {symbol}")
                
        except Exception as e:
            print(f"❌ Error processing {symbol}: {e}")
            failed_stocks.append(symbol)
    
    # Save and analyze results
    if results:
        df = pd.DataFrame(results)
        output_file = 'sp500_10year_yahoo_methodology.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n{'='*80}")
        print(f"10-YEAR BETA ANALYSIS COMPLETE!")
        print(f"{'='*80}")
        print(f"✅ Successfully processed: {len(results)} stocks")
        print(f"❌ Failed to process: {len(failed_stocks)} stocks")
        print(f"📊 Results saved to: {output_file}")
        
        # Summary statistics
        print(f"\n📈 10-YEAR BETA SUMMARY:")
        print(f"Average Beta: {df['Beta_10Y'].mean():.3f}")
        print(f"Beta Range: {df['Beta_10Y'].min():.3f} to {df['Beta_10Y'].max():.3f}")
        print(f"Median Beta: {df['Beta_10Y'].median():.3f}")
        print(f"Standard Deviation: {df['Beta_10Y'].std():.3f}")
        
        # Show top and bottom betas
        print(f"\n🏆 HIGHEST 10-YEAR BETAS:")
        top_betas = df.nlargest(10, 'Beta_10Y')[['Symbol', 'Beta_10Y', 'R_Squared', 'Months']]
        for _, row in top_betas.iterrows():
            print(f"  {row['Symbol']:<6} {row['Beta_10Y']:.3f} (R²={row['R_Squared']:.3f}, {row['Months']:3.0f}m)")
        
        print(f"\n📉 LOWEST 10-YEAR BETAS:")
        low_betas = df.nsmallest(10, 'Beta_10Y')[['Symbol', 'Beta_10Y', 'R_Squared', 'Months']]
        for _, row in low_betas.iterrows():
            print(f"  {row['Symbol']:<6} {row['Beta_10Y']:.3f} (R²={row['R_Squared']:.3f}, {row['Months']:3.0f}m)")
        
        # Compare with previous results for key stocks
        key_comparisons = {
            'NVDA': {'5Y': 2.109, '10Y_Daily': 1.772},
            'TSLA': {'10Y_Daily': 1.828},
            'AAPL': {'10Y_Daily': 1.244},
            'MSFT': {'10Y_Daily': 0.982}
        }
        
        print(f"\n🔄 COMPARISON WITH PREVIOUS ANALYSES:")
        print(f"{'Stock':<6} {'10Y Monthly':<12} {'5Y Monthly':<12} {'10Y Daily':<12} {'Difference':<12}")
        print("-" * 65)
        
        for _, row in df.iterrows():
            symbol = row['Symbol']
            beta_10y_monthly = row['Beta_10Y']
            
            if symbol in key_comparisons:
                comp = key_comparisons[symbol]
                beta_5y = comp.get('5Y', 'N/A')
                beta_10y_daily = comp.get('10Y_Daily', 'N/A')
                
                if beta_5y != 'N/A':
                    diff_5y = beta_10y_monthly - beta_5y
                    print(f"{symbol:<6} {beta_10y_monthly:<12.3f} {beta_5y:<12.3f} {beta_10y_daily if beta_10y_daily != 'N/A' else 'N/A':<12} {diff_5y:<+12.3f}")
                else:
                    print(f"{symbol:<6} {beta_10y_monthly:<12.3f} {'N/A':<12} {beta_10y_daily if beta_10y_daily != 'N/A' else 'N/A':<12} {'N/A':<12}")
        
        # Analyze by sector patterns
        sector_patterns = {
            'Technology': ['NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA'],
            'Financials': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK'],
            'Consumer': ['KO', 'PG', 'WMT', 'HD', 'MCD'],
            'Energy': ['XOM', 'CVX', 'COP', 'SLB']
        }
        
        print(f"\n🏢 SECTOR BETA ANALYSIS (10-Year Monthly):")
        for sector, symbols in sector_patterns.items():
            sector_betas = df[df['Symbol'].isin(symbols)]['Beta_10Y']
            if len(sector_betas) > 0:
                print(f"  {sector:<12}: Avg={sector_betas.mean():.3f}, Range={sector_betas.min():.3f}-{sector_betas.max():.3f}")
        
        # Special focus on NVIDIA
        nvda_row = df[df['Symbol'] == 'NVDA']
        if not nvda_row.empty:
            nvda = nvda_row.iloc[0]
            print(f"\n🎯 NVIDIA 10-YEAR ANALYSIS:")
            print(f"  Beta (10Y Monthly): {nvda['Beta_10Y']:.3f}")
            print(f"  R-squared: {nvda['R_Squared']:.3f} ({nvda['R_Squared']*100:.1f}% market correlation)")
            print(f"  Data Quality: {nvda['Months']} months")
            print(f"  Bull Market Beta: {nvda['Positive_Beta']:.3f if pd.notna(nvda['Positive_Beta']) else 'N/A'}")
            print(f"  Bear Market Beta: {nvda['Negative_Beta']:.3f if pd.notna(nvda['Negative_Beta']) else 'N/A'}")
            print(f"  Period: {nvda['Start_Date'].strftime('%Y-%m')} to {nvda['End_Date'].strftime('%Y-%m')}")
        
        if failed_stocks:
            print(f"\n❌ FAILED STOCKS:")
            print(f"  {', '.join(failed_stocks)}")
            print(f"  (Likely due to insufficient 10-year data or recent IPOs)")
        
        print(f"\n💡 KEY INSIGHTS:")
        print(f"  • 10-year monthly betas provide the most stable, long-term risk measures")
        print(f"  • Methodology matches Yahoo Finance 5Y calculations perfectly")
        print(f"  • Captures full market cycles: 2015-2017 growth, 2018 correction,")
        print(f"    2020 COVID crash/recovery, 2021-2022 meme stocks, 2023-2025 AI boom")
        print(f"  • Monthly returns smooth out daily noise and volatility spikes")
        print(f"  • S&P 500 index benchmark provides institutional-grade accuracy")
        
    else:
        print("❌ No successful results!")

if __name__ == "__main__":
    main()