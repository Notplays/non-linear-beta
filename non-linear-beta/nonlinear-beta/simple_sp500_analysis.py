#!/usr/bin/env python3
"""
Simple S&P 500 Beta Analysis - Fixed Version
No parallel processing to avoid DataFrame column issues
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
        if len(common_dates) < 100:  # Need at least 100 days
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
        
        if np.sum(positive_mask) > 20:
            stock_pos = stock_ret[positive_mask]
            market_pos = market_ret[positive_mask]
            cov_pos = np.cov(stock_pos, market_pos)[0, 1]
            var_pos = np.var(market_pos)
            if var_pos > 0:
                positive_beta = cov_pos / var_pos
                
        if np.sum(negative_mask) > 20:
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
    print("SIMPLE S&P 500 BETA ANALYSIS - ROBUST VERSION")
    print("="*80)
    
    # Load S&P 500 symbols
    try:
        sp500_df = pd.read_csv('sp500_wikipedia_data.csv')
        symbols = sp500_df['symbol'].tolist()  # lowercase 'symbol'
        print(f"Loaded {len(symbols)} S&P 500 symbols")
    except Exception as e:
        print(f"Error loading S&P 500 data: {e}")
        return
    
    # Get market data (SPY) first
    print("Fetching market data (SPY)...")
    market_data = getBars('SPY', '2015-01-01', '2025-01-01')
    if market_data is None:
        print("Failed to get market data!")
        return
    
    print(f"Market data: {len(market_data)} days")
    
    # Process each stock individually
    results = []
    failed_stocks = []
    
    for i, symbol in enumerate(symbols, 1):
        print(f"\nProcessing {i}/{len(symbols)}: {symbol}")
        
        try:
            # Get stock data
            stock_data = getBars(symbol, '2015-01-01', '2025-01-01')
            
            if stock_data is None or len(stock_data) < 100:
                print(f"  ❌ Insufficient data for {symbol}")
                failed_stocks.append(symbol)
                continue
            
            # Calculate beta
            beta_result = calculate_beta_simple(stock_data, market_data)
            
            if beta_result is None:
                print(f"  ❌ Beta calculation failed for {symbol}")
                failed_stocks.append(symbol)
                continue
            
            # Add to results
            result = {
                'Symbol': symbol,
                'Beta': beta_result['beta'],
                'Correlation': beta_result['correlation'],
                'Positive_Beta': beta_result['positive_beta'],
                'Negative_Beta': beta_result['negative_beta'],
                'Data_Points': beta_result['data_points'],
                'Positive_Days': beta_result['positive_days'],
                'Negative_Days': beta_result['negative_days']
            }
            results.append(result)
            
            print(f"  ✅ Beta: {beta_result['beta']:.3f}, Correlation: {beta_result['correlation']:.3f}")
            
            # Small delay to avoid overwhelming the API
            time.sleep(0.1)
            
        except Exception as e:
            print(f"  ❌ Error processing {symbol}: {e}")
            failed_stocks.append(symbol)
            continue
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        output_file = 'sp500_optimized_results.csv'
        results_df.to_csv(output_file, index=False)
        
        print(f"\n{'='*80}")
        print(f"ANALYSIS COMPLETE!")
        print(f"{'='*80}")
        print(f"✅ Successfully processed: {len(results)} stocks")
        print(f"❌ Failed to process: {len(failed_stocks)} stocks")
        print(f"📊 Results saved to: {output_file}")
        
        # Show some statistics
        print(f"\nBETA STATISTICS:")
        print(f"Average Beta: {results_df['Beta'].mean():.3f}")
        print(f"Beta Range: {results_df['Beta'].min():.3f} to {results_df['Beta'].max():.3f}")
        print(f"Stocks with Beta > 1.5: {len(results_df[results_df['Beta'] > 1.5])}")
        print(f"Stocks with Beta < 0.5: {len(results_df[results_df['Beta'] < 0.5])}")
        
        # Show highest and lowest betas
        print(f"\nHIGHEST BETAS:")
        top_betas = results_df.nlargest(5, 'Beta')[['Symbol', 'Beta']]
        for _, row in top_betas.iterrows():
            print(f"  {row['Symbol']}: {row['Beta']:.3f}")
            
        print(f"\nLOWEST BETAS:")
        low_betas = results_df.nsmallest(5, 'Beta')[['Symbol', 'Beta']]
        for _, row in low_betas.iterrows():
            print(f"  {row['Symbol']}: {row['Beta']:.3f}")
        
        if failed_stocks:
            print(f"\nFAILED STOCKS:")
            print(", ".join(failed_stocks[:20]))
            if len(failed_stocks) > 20:
                print(f"... and {len(failed_stocks) - 20} more")
    
    else:
        print("No successful results!")

if __name__ == "__main__":
    main()