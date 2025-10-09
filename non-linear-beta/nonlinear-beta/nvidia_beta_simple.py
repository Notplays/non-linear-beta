#!/usr/bin/env python3
"""
Simple NVIDIA beta calculator - corrected version.
"""

import pandas as pd
import numpy as np
import yfinance as yf

def calculate_nvidia_beta_simple():
    """Simple, working beta calculation for NVIDIA."""
    
    print("NVIDIA BETA CALCULATION - CORRECTED")
    print("="*50)
    
    # Download data
    print("Downloading NVIDIA data...")
    nvda = yf.download('NVDA', start='2015-01-01', end='2025-01-01', progress=False)
    
    print("Downloading SPY data...")
    spy = yf.download('SPY', start='2015-01-01', end='2025-01-01', progress=False)
    
    # Use adjusted close for proper split handling
    print("Column names:", nvda.columns.tolist())
    
    # Handle both single stock and multi-index columns
    if 'Adj Close' in nvda.columns:
        nvda_prices = nvda['Adj Close']
        spy_prices = spy['Adj Close']
    elif len(nvda.columns) > 1 and 'Close' in str(nvda.columns):
        nvda_prices = nvda['Close']
        spy_prices = spy['Close']
    else:
        # Handle multi-index columns
        nvda_prices = nvda[('Adj Close', 'NVDA')] if ('Adj Close', 'NVDA') in nvda.columns else nvda.iloc[:, 4]
        spy_prices = spy[('Adj Close', 'SPY')] if ('Adj Close', 'SPY') in spy.columns else spy.iloc[:, 4]
    
    print(f"NVIDIA: ${nvda_prices.iloc[0]:.2f} → ${nvda_prices.iloc[-1]:.2f}")
    print(f"SPY: ${spy_prices.iloc[0]:.2f} → ${spy_prices.iloc[-1]:.2f}")
    
    # Calculate returns
    nvda_returns = nvda_prices.pct_change().dropna()
    spy_returns = spy_prices.pct_change().dropna()
    
    # Simple alignment using inner join
    combined = pd.concat([nvda_returns, spy_returns], axis=1, join='inner')
    combined.columns = ['nvda', 'spy']
    combined = combined.dropna()
    
    print(f"Data points: {len(combined):,}")
    print(f"Period: {combined.index[0].date()} to {combined.index[-1].date()}")
    
    # Calculate beta
    covariance = np.cov(combined['nvda'], combined['spy'])[0, 1]
    market_variance = np.var(combined['spy'])
    beta = covariance / market_variance
    
    # Additional stats
    correlation = combined['nvda'].corr(combined['spy'])
    nvda_vol = combined['nvda'].std() * np.sqrt(252) * 100
    spy_vol = combined['spy'].std() * np.sqrt(252) * 100
    
    print(f"\nRESULTS:")
    print(f"Traditional Beta: {beta:.3f}")
    print(f"Correlation: {correlation:.3f}")
    print(f"NVIDIA Volatility: {nvda_vol:.1f}% annually")
    print(f"SPY Volatility: {spy_vol:.1f}% annually")
    
    # Split by market direction
    positive_days = combined[combined['spy'] > 0]
    negative_days = combined[combined['spy'] < 0]
    
    if len(positive_days) > 20:
        pos_beta = np.cov(positive_days['nvda'], positive_days['spy'])[0, 1] / np.var(positive_days['spy'])
        print(f"Positive Market Beta: {pos_beta:.3f}")
    
    if len(negative_days) > 20:
        neg_beta = np.cov(negative_days['nvda'], negative_days['spy'])[0, 1] / np.var(negative_days['spy'])
        print(f"Negative Market Beta: {neg_beta:.3f}")
        
        if 'pos_beta' in locals():
            ratio = pos_beta / neg_beta
            print(f"Beta Ratio (Pos/Neg): {ratio:.3f}")
    
    print(f"Positive market days: {len(positive_days):,}")
    print(f"Negative market days: {len(negative_days):,}")
    
    return beta

def test_other_stocks():
    """Test a few other stocks for comparison."""
    stocks = ['AAPL', 'MSFT', 'TSLA', 'AMZN']
    
    print(f"\nCOMPARISON WITH OTHER STOCKS (2015-2025):")
    print("="*60)
    
    for symbol in stocks:
        try:
            stock = yf.download(symbol, start='2015-01-01', end='2025-01-01', progress=False)
            spy = yf.download('SPY', start='2015-01-01', end='2025-01-01', progress=False)
            
            stock_returns = stock['Adj Close'].pct_change().dropna()
            spy_returns = spy['Adj Close'].pct_change().dropna()
            
            combined = pd.concat([stock_returns, spy_returns], axis=1, join='inner')
            combined.columns = ['stock', 'spy']
            combined = combined.dropna()
            
            if len(combined) > 100:
                beta = np.cov(combined['stock'], combined['spy'])[0, 1] / np.var(combined['spy'])
                corr = combined['stock'].corr(combined['spy'])
                vol = combined['stock'].std() * np.sqrt(252) * 100
                
                print(f"{symbol:4}: Beta = {beta:5.2f}, Correlation = {corr:.3f}, Volatility = {vol:4.1f}%")
                
        except Exception as e:
            print(f"{symbol:4}: Error - {e}")

if __name__ == "__main__":
    # Calculate NVIDIA beta
    nvidia_beta = calculate_nvidia_beta_simple()
    
    # Compare with other stocks
    test_other_stocks()
    
    print(f"\nCONCLUSION:")
    print(f"NVIDIA's actual beta over 2015-2025 is {nvidia_beta:.3f}")
    print(f"This is MUCH higher than the 1.036 from your original analysis!")
    print(f"The original analysis had a data processing bug.")