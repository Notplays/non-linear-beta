#!/usr/bin/env python3
"""
Test script to diagnose and fix NVIDIA beta calculation.
"""

import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

def calculate_beta_corrected(stock_symbol, market_symbol='SPY', start_date='2015-01-01', end_date='2025-01-01'):
    """
    Calculate beta with proper error handling and diagnostics.
    """
    print(f"Calculating beta for {stock_symbol} vs {market_symbol}")
    print(f"Period: {start_date} to {end_date}")
    print("-" * 50)
    
    try:
        # Download data with explicit column handling
        print("Downloading stock data...")
        stock_data = yf.download(stock_symbol, start=start_date, end=end_date, progress=False)
        
        print("Downloading market data...")
        market_data = yf.download(market_symbol, start=start_date, end=end_date, progress=False)
        
        # Check if data is empty
        if stock_data.empty or market_data.empty:
            print("ERROR: No data downloaded")
            return None
            
        print(f"Stock data shape: {stock_data.shape}")
        print(f"Market data shape: {market_data.shape}")
        
        # Use Adjusted Close for proper split/dividend handling
        if 'Adj Close' in stock_data.columns:
            stock_prices = stock_data['Adj Close']
            market_prices = market_data['Adj Close']
        else:
            stock_prices = stock_data['Close']
            market_prices = market_data['Close']
            
        print(f"Stock price range: {float(stock_prices.iloc[0]):.2f} to {float(stock_prices.iloc[-1]):.2f}")
        print(f"Market price range: {float(market_prices.iloc[0]):.2f} to {float(market_prices.iloc[-1]):.2f}")
        
        # Calculate returns
        stock_returns = stock_prices.pct_change().dropna()
        market_returns = market_prices.pct_change().dropna()
        
        print(f"Stock returns shape: {stock_returns.shape}")
        print(f"Market returns shape: {market_returns.shape}")
        
        # Align data
        aligned_data = pd.DataFrame({
            'stock': stock_returns,
            'market': market_returns
        }).dropna()
        
        print(f"Aligned data shape: {aligned_data.shape}")
        print(f"Date range: {aligned_data.index[0].date()} to {aligned_data.index[-1].date()}")
        
        if len(aligned_data) < 50:
            print("ERROR: Insufficient data points")
            return None
            
        # Calculate traditional beta
        covariance = np.cov(aligned_data['stock'], aligned_data['market'])[0, 1]
        market_variance = np.var(aligned_data['market'])
        
        if market_variance == 0:
            print("ERROR: Market variance is zero")
            return None
            
        traditional_beta = covariance / market_variance
        
        # Split by market direction
        positive_days = aligned_data[aligned_data['market'] > 0]
        negative_days = aligned_data[aligned_data['market'] < 0]
        
        print(f"Positive market days: {len(positive_days)}")
        print(f"Negative market days: {len(negative_days)}")
        
        # Calculate directional betas
        positive_beta = None
        negative_beta = None
        
        if len(positive_days) > 20:
            pos_cov = np.cov(positive_days['stock'], positive_days['market'])[0, 1]
            pos_var = np.var(positive_days['market'])
            if pos_var > 0:
                positive_beta = pos_cov / pos_var
                
        if len(negative_days) > 20:
            neg_cov = np.cov(negative_days['stock'], negative_days['market'])[0, 1]
            neg_var = np.var(negative_days['market'])
            if neg_var > 0:
                negative_beta = neg_cov / neg_var
        
        # Calculate statistics
        stock_std = aligned_data['stock'].std()
        market_std = aligned_data['market'].std()
        correlation = aligned_data['stock'].corr(aligned_data['market'])
        
        results = {
            'symbol': stock_symbol,
            'traditional_beta': traditional_beta,
            'positive_beta': positive_beta,
            'negative_beta': negative_beta,
            'beta_ratio': positive_beta / negative_beta if positive_beta and negative_beta and negative_beta != 0 else None,
            'data_points': len(aligned_data),
            'positive_days': len(positive_days),
            'negative_days': len(negative_days),
            'correlation': correlation,
            'stock_volatility': stock_std * 100,  # As percentage
            'market_volatility': market_std * 100,  # As percentage
            'start_date': aligned_data.index[0].date(),
            'end_date': aligned_data.index[-1].date()
        }
        
        return results
        
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def print_results(results):
    """Print beta calculation results in a formatted way."""
    if not results:
        print("No results to display")
        return
        
    print("\n" + "="*60)
    print(f"BETA ANALYSIS RESULTS FOR {results['symbol']}")
    print("="*60)
    print(f"Period: {results['start_date']} to {results['end_date']}")
    print(f"Data Points: {results['data_points']:,}")
    print(f"Positive Market Days: {results['positive_days']:,}")
    print(f"Negative Market Days: {results['negative_days']:,}")
    print()
    print("BETA CALCULATIONS:")
    print(f"  Traditional Beta: {results['traditional_beta']:.4f}")
    print(f"  Positive Beta:    {results['positive_beta']:.4f}" if results['positive_beta'] else "  Positive Beta:    N/A")
    print(f"  Negative Beta:    {results['negative_beta']:.4f}" if results['negative_beta'] else "  Negative Beta:    N/A")
    print(f"  Beta Ratio:       {results['beta_ratio']:.4f}" if results['beta_ratio'] else "  Beta Ratio:       N/A")
    print()
    print("RISK METRICS:")
    print(f"  Correlation:      {results['correlation']:.4f}")
    print(f"  Stock Volatility: {results['stock_volatility']:.2f}%")
    print(f"  Market Volatility: {results['market_volatility']:.2f}%")
    print()
    
    # Interpretation
    beta = results['traditional_beta']
    if beta > 1.5:
        risk_level = "HIGH RISK - Very volatile relative to market"
    elif beta > 1.1:
        risk_level = "MODERATE-HIGH RISK - More volatile than market"
    elif beta > 0.9:
        risk_level = "MODERATE RISK - Similar volatility to market"
    else:
        risk_level = "LOW RISK - Less volatile than market"
        
    print(f"INTERPRETATION: {risk_level}")

def test_multiple_periods():
    """Test NVIDIA beta across different periods to identify changes."""
    periods = [
        ('2015-01-01', '2018-12-31', 'Pre-AI Era'),
        ('2019-01-01', '2022-12-31', 'AI Development'),
        ('2023-01-01', '2025-01-01', 'AI Boom'),
        ('2015-01-01', '2025-01-01', 'Full Period')
    ]
    
    print("NVIDIA BETA ANALYSIS ACROSS TIME PERIODS")
    print("="*80)
    
    for start, end, label in periods:
        print(f"\n{label} ({start} to {end}):")
        print("-" * 40)
        results = calculate_beta_corrected('NVDA', start_date=start, end_date=end)
        if results:
            print(f"Beta: {results['traditional_beta']:.3f} | "
                  f"Pos: {results['positive_beta']:.3f} | "
                  f"Neg: {results['negative_beta']:.3f} | "
                  f"Days: {results['data_points']:,}")

if __name__ == "__main__":
    # Test NVIDIA specifically
    print("TESTING NVIDIA BETA CALCULATION")
    print("="*50)
    
    # Full period test
    nvda_results = calculate_beta_corrected('NVDA', start_date='2015-01-01', end_date='2025-01-01')
    print_results(nvda_results)
    
    # Test across different periods
    test_multiple_periods()
    
    # Compare with a few other tech stocks for sanity check
    print("\n\nCOMPARISON WITH OTHER TECH STOCKS (2015-2025):")
    print("="*60)
    
    tech_stocks = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    for stock in tech_stocks:
        print(f"\nTesting {stock}...")
        results = calculate_beta_corrected(stock, start_date='2015-01-01', end_date='2025-01-01')
        if results:
            print(f"{stock}: Beta = {results['traditional_beta']:.3f}, "
                  f"Correlation = {results['correlation']:.3f}, "
                  f"Volatility = {results['stock_volatility']:.1f}%")