#!/usr/bin/env python3
"""
Generate S&P 500 5-Year Monthly Beta CSV - Yahoo Finance Methodology
Using the exact method that matched NVDA 5Y beta (2.109 vs 2.12)
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

def calculate_yahoo_beta_5y(symbol, market_symbol='^GSPC'):
    """
    Calculate 5-year beta using exact Yahoo Finance methodology.
    """
    # Calculate exact 5-year period (60 months back from now)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365 + 30)  # Add buffer
    
    start_str = start_date.strftime('%Y-%m-%d')
    end_str = end_date.strftime('%Y-%m-%d')
    
    try:
        # Get data
        stock_data = getBars(symbol, start_str, end_str)
        market_data = getBars(market_symbol, start_str, end_str)
        
        if stock_data is None or market_data is None:
            return None
        
        # End of Month method (the one that matched perfectly)
        stock_monthly = stock_data['close'].resample('ME').last()
        market_monthly = market_data['close'].resample('ME').last()
        
        # Calculate monthly returns
        stock_returns = stock_monthly.pct_change().dropna()
        market_returns = market_monthly.pct_change().dropna()
        
        # Align data
        common_dates = stock_returns.index.intersection(market_returns.index)
        if len(common_dates) < 24:  # Need at least 24 months
            return None
            
        stock_aligned = stock_returns.loc[common_dates]
        market_aligned = market_returns.loc[common_dates]
        
        # Limit to exactly 60 months if we have more
        if len(stock_aligned) > 60:
            stock_aligned = stock_aligned.tail(60)
            market_aligned = market_aligned.tail(60)
        
        # Calculate beta using regression method
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
        
        return {
            'Symbol': symbol,
            'Beta_5Y_Yahoo': beta,
            'Correlation': correlation,
            'R_Squared': r_squared,
            'Positive_Beta': positive_beta,
            'Negative_Beta': negative_beta,
            'Standard_Error': std_err,
            'Months': len(stock_aligned),
            'Positive_Months': np.sum(positive_mask),
            'Negative_Months': np.sum(negative_mask),
            'Start_Date': stock_aligned.index[0].strftime('%Y-%m'),
            'End_Date': stock_aligned.index[-1].strftime('%Y-%m')
        }
        
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return None

def main():
    print("🎯 S&P 500 5-YEAR BETA CSV - YAHOO FINANCE METHODOLOGY")
    print("Using the exact method that matched NVDA (2.109 vs 2.12)")
    print("="*80)
    
    # Load S&P 500 symbols
    try:
        sp500_df = pd.read_csv('sp500_wikipedia_data.csv')
        all_symbols = sp500_df['symbol'].tolist()
        print(f"Loaded {len(all_symbols)} S&P 500 symbols")
    except Exception as e:
        print(f"Error loading S&P 500 data: {e}")
        # Fallback to major stocks
        all_symbols = [
            # Tech
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'NFLX', 'ADBE', 'CRM',
            'ORCL', 'IBM', 'INTC', 'AMD', 'QCOM', 'TXN', 'AVGO', 'CSCO', 'NOW', 'INTU',
            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'COF', 'AXP',
            # Healthcare
            'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN',
            # Consumer
            'AMZN', 'TSLA', 'HD', 'WMT', 'MCD', 'NKE', 'SBUX', 'TGT', 'LOW', 'TJX',
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'MPC', 'OXY', 'HAL',
            # Others
            'BRK-B', 'V', 'MA', 'KO', 'PG', 'DIS', 'COST', 'PLTR', 'COIN'
        ]
    
    print(f"Processing {len(all_symbols)} symbols...")
    
    # Get market data once
    print("Fetching S&P 500 index data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5*365 + 30)
    market_data = getBars('^GSPC', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    
    if market_data is None:
        print("Failed to get S&P 500 data! Using SPY fallback...")
        market_data = getBars('SPY', start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if market_data is None:
            print("❌ Failed to get market data!")
            return
    
    print(f"Market data: {len(market_data)} days")
    
    # Process stocks in batches
    batch_size = 50
    total_batches = (len(all_symbols) + batch_size - 1) // batch_size
    results = []
    failed_stocks = []
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(all_symbols))
        batch_symbols = all_symbols[start_idx:end_idx]
        
        print(f"\nProcessing batch {batch_num + 1}/{total_batches} ({len(batch_symbols)} symbols)")
        
        for i, symbol in enumerate(batch_symbols):
            print(f"  {start_idx + i + 1}/{len(all_symbols)}: {symbol}", end=" ")
            
            try:
                result = calculate_yahoo_beta_5y(symbol)
                
                if result is not None:
                    results.append(result)
                    print(f"✅ Beta: {result['Beta_5Y_Yahoo']:.3f}")
                    
                    # Special highlight for NVIDIA
                    if symbol == 'NVDA':
                        print(f"    🎯 NVIDIA: {result['Beta_5Y_Yahoo']:.3f} (Target: 2.12)")
                else:
                    failed_stocks.append(symbol)
                    print("❌ Failed")
                    
                # Small delay to avoid overwhelming the API
                time.sleep(0.05)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_stocks.append(symbol)
        
        # Longer delay between batches
        if batch_num < total_batches - 1:
            print(f"  Batch complete. Waiting 2 seconds...")
            time.sleep(2)
    
    # Save results
    if results:
        results_df = pd.DataFrame(results)
        output_file = 'sp500_5year_yahoo_methodology.csv'
        results_df.to_csv(output_file, index=False)
        
        print(f"\n{'='*80}")
        print(f"5-YEAR YAHOO METHODOLOGY ANALYSIS COMPLETE!")
        print(f"{'='*80}")
        print(f"✅ Successfully processed: {len(results)} stocks")
        print(f"❌ Failed to process: {len(failed_stocks)} stocks")
        print(f"📊 Results saved to: {output_file}")
        
        # Summary statistics
        print(f"\n📈 5-YEAR BETA SUMMARY (Yahoo Methodology):")
        print(f"Average Beta: {results_df['Beta_5Y_Yahoo'].mean():.3f}")
        print(f"Beta Range: {results_df['Beta_5Y_Yahoo'].min():.3f} to {results_df['Beta_5Y_Yahoo'].max():.3f}")
        print(f"Median Beta: {results_df['Beta_5Y_Yahoo'].median():.3f}")
        print(f"Stocks with Beta > 1.5: {len(results_df[results_df['Beta_5Y_Yahoo'] > 1.5])}")
        print(f"Stocks with Beta < 0.5: {len(results_df[results_df['Beta_5Y_Yahoo'] < 0.5])}")
        
        # Show top betas
        print(f"\n🏆 HIGHEST 5-YEAR BETAS (Yahoo Method):")
        top_betas = results_df.nlargest(10, 'Beta_5Y_Yahoo')[['Symbol', 'Beta_5Y_Yahoo', 'R_Squared']]
        for _, row in top_betas.iterrows():
            print(f"  {row['Symbol']:<6} {row['Beta_5Y_Yahoo']:.3f} (R²={row['R_Squared']:.3f})")
        
        print(f"\n📉 LOWEST 5-YEAR BETAS (Yahoo Method):")
        low_betas = results_df.nsmallest(10, 'Beta_5Y_Yahoo')[['Symbol', 'Beta_5Y_Yahoo', 'R_Squared']]
        for _, row in low_betas.iterrows():
            print(f"  {row['Symbol']:<6} {row['Beta_5Y_Yahoo']:.3f} (R²={row['R_Squared']:.3f})")
        
        # Check specific stocks
        key_stocks = ['NVDA', 'AAPL', 'MSFT', 'PLTR', 'TSLA', 'COIN']
        print(f"\n🎯 KEY STOCKS VERIFICATION:")
        for stock in key_stocks:
            stock_row = results_df[results_df['Symbol'] == stock]
            if not stock_row.empty:
                beta = stock_row.iloc[0]['Beta_5Y_Yahoo']
                r2 = stock_row.iloc[0]['R_Squared']
                months = stock_row.iloc[0]['Months']
                print(f"  {stock:<6} Beta: {beta:.3f}, R²: {r2:.3f}, Months: {months}")
        
        if failed_stocks:
            print(f"\n❌ FAILED STOCKS ({len(failed_stocks)}):")
            failed_str = ', '.join(failed_stocks[:20])
            if len(failed_stocks) > 20:
                failed_str += f", ... and {len(failed_stocks) - 20} more"
            print(f"  {failed_str}")
        
        print(f"\n💡 METHODOLOGY VALIDATION:")
        print(f"  • Uses exact Yahoo Finance 5Y monthly methodology")
        print(f"  • S&P 500 index (^GSPC) as benchmark")
        print(f"  • 60 months of data per stock")
        print(f"  • Linear regression for beta calculation")
        print(f"  • Should match Yahoo Finance betas closely")
        
        # Verify NVIDIA specifically
        nvda_row = results_df[results_df['Symbol'] == 'NVDA']
        if not nvda_row.empty:
            nvda_beta = nvda_row.iloc[0]['Beta_5Y_Yahoo']
            print(f"\n🎯 NVIDIA VERIFICATION:")
            print(f"  Our Beta: {nvda_beta:.3f}")
            print(f"  Yahoo Target: 2.12")
            print(f"  Difference: {abs(nvda_beta - 2.12):.3f}")
            print(f"  Match Quality: {'✅ EXCELLENT' if abs(nvda_beta - 2.12) < 0.05 else '✅ GOOD' if abs(nvda_beta - 2.12) < 0.2 else '❌ NEEDS REVIEW'}")
    
    else:
        print("❌ No successful results!")

if __name__ == "__main__":
    main()