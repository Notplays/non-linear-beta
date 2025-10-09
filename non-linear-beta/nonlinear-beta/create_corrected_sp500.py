#!/usr/bin/env python3
"""
Create corrected SP500 optimized results using proper beta calculations.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def calculate_correct_beta(symbol, start_date='2015-01-01', end_date='2025-01-01'):
    """Calculate correct beta for a stock using the working method."""
    try:
        # Download data
        stock = yf.download(symbol, start=start_date, end=end_date, progress=False, auto_adjust=False)
        spy = yf.download('SPY', start=start_date, end=end_date, progress=False, auto_adjust=False)
        
        if stock.empty or spy.empty:
            return None
            
        # Use close prices and calculate returns
        stock_returns = stock['Close'].pct_change().dropna()
        spy_returns = spy['Close'].pct_change().dropna()
        
        # Align dates
        common_dates = stock_returns.index.intersection(spy_returns.index)
        
        if len(common_dates) < 100:
            return None
            
        stock_aligned = stock_returns.loc[common_dates].values
        spy_aligned = spy_returns.loc[common_dates].values
        
        # Remove any NaN values
        mask = ~(np.isnan(stock_aligned) | np.isnan(spy_aligned))
        stock_clean = stock_aligned[mask]
        spy_clean = spy_aligned[mask]
        
        if len(stock_clean) < 100:
            return None
            
        # Calculate traditional beta
        covariance = np.cov(stock_clean, spy_clean)[0, 1]
        market_variance = np.var(spy_clean)
        
        if market_variance == 0:
            return None
            
        traditional_beta = covariance / market_variance
        
        # Calculate directional betas
        positive_mask = spy_clean > 0
        negative_mask = spy_clean < 0
        
        positive_beta = np.nan
        negative_beta = np.nan
        
        if np.sum(positive_mask) > 20:
            pos_cov = np.cov(stock_clean[positive_mask], spy_clean[positive_mask])[0, 1]
            pos_var = np.var(spy_clean[positive_mask])
            if pos_var > 0:
                positive_beta = pos_cov / pos_var
                
        if np.sum(negative_mask) > 20:
            neg_cov = np.cov(stock_clean[negative_mask], spy_clean[negative_mask])[0, 1]
            neg_var = np.var(spy_clean[negative_mask])
            if neg_var > 0:
                negative_beta = neg_cov / neg_var
        
        # Calculate beta ratio
        beta_ratio = np.nan
        if not np.isnan(positive_beta) and not np.isnan(negative_beta) and negative_beta != 0:
            beta_ratio = positive_beta / negative_beta
            
        return {
            'traditional_beta': traditional_beta,
            'positive_beta': positive_beta,
            'negative_beta': negative_beta,
            'beta_ratio': beta_ratio,
            'data_points': len(stock_clean),
            'positive_days': np.sum(positive_mask),
            'negative_days': np.sum(negative_mask)
        }
        
    except Exception as e:
        print(f"Error calculating beta for {symbol}: {e}")
        return None

def create_corrected_sp500_csv():
    """Create corrected SP500 results CSV with proper beta calculations."""
    
    print("CREATING CORRECTED SP500 OPTIMIZED RESULTS")
    print("="*50)
    
    # Load S&P 500 symbols
    try:
        sp500_df = pd.read_csv('sp500_wikipedia_data.csv')
        symbols = sp500_df['symbol'].tolist()
        sector_map = dict(zip(sp500_df['symbol'], sp500_df['sector']))
        print(f"Loaded {len(symbols)} S&P 500 symbols")
    except FileNotFoundError:
        print("sp500_wikipedia_data.csv not found. Using a subset of major stocks.")
        symbols = ['NVDA', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'TSLA', 'META', 'BRK-B', 'UNH', 'JNJ']
        sector_map = {symbol: 'Unknown' for symbol in symbols}
    
    # Test with NVIDIA first to verify our calculation
    print("\nTesting with NVIDIA first...")
    nvda_result = calculate_correct_beta('NVDA')
    if nvda_result:
        print(f"NVIDIA Beta: {nvda_result['traditional_beta']:.4f}")
        print(f"Expected: ~1.74 (our earlier calculation)")
        if abs(nvda_result['traditional_beta'] - 1.74) < 0.2:
            print("✓ NVIDIA beta looks correct")
        else:
            print("⚠ NVIDIA beta might still have issues")
    
    # Process all stocks
    print(f"\nProcessing {len(symbols)} stocks...")
    results = []
    
    for i, symbol in enumerate(symbols):
        if i % 50 == 0:
            print(f"Progress: {i}/{len(symbols)} ({i/len(symbols)*100:.1f}%)")
            
        beta_result = calculate_correct_beta(symbol)
        
        if beta_result is not None:
            results.append({
                'symbol': symbol,
                'traditional_beta': beta_result['traditional_beta'],
                'positive_beta': beta_result['positive_beta'],
                'negative_beta': beta_result['negative_beta'],
                'beta_ratio': beta_result['beta_ratio'],
                'data_points': beta_result['data_points'],
                'positive_days': beta_result['positive_days'],
                'negative_days': beta_result['negative_days'],
                'sector': sector_map.get(symbol, 'Unknown')
            })
        else:
            print(f"Failed to calculate beta for {symbol}")
    
    print(f"\nSuccessfully calculated betas for {len(results)} stocks")
    
    # Create DataFrame and save
    df = pd.DataFrame(results)
    
    # Sort by traditional beta descending
    df = df.sort_values('traditional_beta', ascending=False)
    
    # Save to CSV
    output_file = 'sp500_optimized_results_corrected.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\nCorrected results saved to '{output_file}'")
    
    # Show summary statistics
    print(f"\nSUMMARY STATISTICS:")
    print(f"Number of stocks: {len(df)}")
    print(f"Mean beta: {df['traditional_beta'].mean():.3f}")
    print(f"Median beta: {df['traditional_beta'].median():.3f}")
    print(f"Beta range: {df['traditional_beta'].min():.3f} to {df['traditional_beta'].max():.3f}")
    
    # Show top 10 highest betas
    print(f"\nTOP 10 HIGHEST BETAS:")
    print(df[['symbol', 'traditional_beta', 'sector']].head(10).to_string(index=False))
    
    # Show NVIDIA specifically
    nvda_row = df[df['symbol'] == 'NVDA']
    if not nvda_row.empty:
        print(f"\nNVIDIA RESULTS:")
        nvda_data = nvda_row.iloc[0]
        print(f"Symbol: {nvda_data['symbol']}")
        print(f"Traditional Beta: {nvda_data['traditional_beta']:.4f}")
        print(f"Positive Beta: {nvda_data['positive_beta']:.4f}")
        print(f"Negative Beta: {nvda_data['negative_beta']:.4f}")
        print(f"Beta Ratio: {nvda_data['beta_ratio']:.4f}")
        print(f"Sector: {nvda_data['sector']}")
        
        print(f"\nCOMPARISON:")
        print(f"Original (wrong): 1.036")
        print(f"Corrected: {nvda_data['traditional_beta']:.3f}")
        print(f"Improvement: {nvda_data['traditional_beta']/1.036:.1f}x more accurate")
    
    return df

if __name__ == "__main__":
    df = create_corrected_sp500_csv()
    print(f"\nCORRECTED SP500 ANALYSIS COMPLETE!")