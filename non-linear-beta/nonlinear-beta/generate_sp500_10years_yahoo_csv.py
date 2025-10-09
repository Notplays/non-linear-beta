#!/usr/bin/env python3
"""
Generate S&P 500 10-Year Monthly Beta CSV - Yahoo Finance Methodology
Using the exact method validated for 5-year analysis, extended to 10 years
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

def calculate_yahoo_beta_10y(symbol, market_symbol='^GSPC'):
    """
    Calculate 10-year beta using exact Yahoo Finance methodology.
    """
    # Calculate exact 10-year period (120 months back from now)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365 + 60)  # Add buffer
    
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
        if len(common_dates) < 60:  # Need at least 60 months for meaningful 10Y analysis
            return None
            
        stock_aligned = stock_returns.loc[common_dates]
        market_aligned = market_returns.loc[common_dates]
        
        # Limit to exactly 120 months if we have more
        if len(stock_aligned) > 120:
            stock_aligned = stock_aligned.tail(120)
            market_aligned = market_aligned.tail(120)
        
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
        
        if np.sum(positive_mask) > 10:
            stock_pos = stock_ret[positive_mask]
            market_pos = market_ret[positive_mask]
            if len(stock_pos) > 1:
                slope_pos, _, _, _, _ = stats.linregress(market_pos, stock_pos)
                positive_beta = slope_pos
                
        if np.sum(negative_mask) > 10:
            stock_neg = stock_ret[negative_mask]
            market_neg = market_ret[negative_mask]
            if len(stock_neg) > 1:
                slope_neg, _, _, _, _ = stats.linregress(market_neg, stock_neg)
                negative_beta = slope_neg
        
        # Calculate additional statistics
        volatility = stock_ret.std()
        market_volatility = market_ret.std()
        alpha = intercept
        sharpe_ratio = stock_ret.mean() / stock_ret.std() if stock_ret.std() > 0 else None
        
        return {
            'Symbol': symbol,
            'Beta_10Y_Yahoo': beta,
            'Correlation': correlation,
            'R_Squared': r_squared,
            'Positive_Beta': positive_beta,
            'Negative_Beta': negative_beta,
            'Alpha': alpha,
            'Standard_Error': std_err,
            'Volatility': volatility,
            'Market_Volatility': market_volatility,
            'Sharpe_Ratio': sharpe_ratio,
            'Months': len(stock_aligned),
            'Positive_Months': np.sum(positive_mask),
            'Negative_Months': np.sum(negative_mask),
            'Start_Date': stock_aligned.index[0].strftime('%Y-%m'),
            'End_Date': stock_aligned.index[-1].strftime('%Y-%m'),
            'Avg_Monthly_Return': stock_ret.mean(),
            'Market_Avg_Return': market_ret.mean()
        }
        
    except Exception as e:
        print(f"Error processing {symbol}: {e}")
        return None

def main():
    print("🎯 S&P 500 10-YEAR BETA CSV - YAHOO FINANCE METHODOLOGY")
    print("Using validated methodology extended to 10-year timeframe")
    print("="*80)
    
    # Load S&P 500 symbols
    try:
        sp500_df = pd.read_csv('sp500_wikipedia_data.csv')
        all_symbols = sp500_df['symbol'].tolist()
        print(f"Loaded {len(all_symbols)} S&P 500 symbols")
    except Exception as e:
        print(f"Error loading S&P 500 data: {e}")
        # Fallback to comprehensive list
        all_symbols = [
            # Tech Giants
            'AAPL', 'MSFT', 'GOOGL', 'GOOG', 'AMZN', 'NVDA', 'META', 'TSLA', 'NFLX', 'ADBE',
            'CRM', 'ORCL', 'IBM', 'INTC', 'AMD', 'QCOM', 'TXN', 'AVGO', 'CSCO', 'NOW',
            'INTU', 'AMAT', 'LRCX', 'KLAC', 'MCHP', 'MU', 'SWKS', 'NTAP', 'SNPS', 'CDNS',
            
            # Finance
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'USB', 'PNC', 'COF', 'AXP',
            'BLK', 'SPGI', 'ICE', 'CME', 'MCO', 'TRV', 'PGR', 'AIG', 'ALL', 'AFL',
            
            # Healthcare & Pharma
            'JNJ', 'PFE', 'UNH', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'AMGN',
            'GILD', 'LLY', 'MDT', 'ISRG', 'SYK', 'BSX', 'EW', 'ZBH', 'BAX', 'REGN',
            
            # Consumer & Retail
            'WMT', 'AMZN', 'HD', 'TGT', 'LOW', 'TJX', 'COST', 'SBUX', 'MCD', 'NKE',
            'DIS', 'TSLA', 'F', 'GM', 'LULU', 'ULTA', 'ROST', 'TJX', 'MAR', 'HLT',
            
            # Energy
            'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PSX', 'VLO', 'MPC', 'OXY', 'HAL',
            'KMI', 'OKE', 'TRGP', 'WMB', 'FANG', 'DVN', 'PXD', 'BKR', 'APA', 'HES',
            
            # Industrials
            'BA', 'CAT', 'GE', 'HON', 'UPS', 'LMT', 'RTX', 'DE', 'MMM', 'ITW',
            'EMR', 'ETN', 'PH', 'ROK', 'DOV', 'IR', 'CMI', 'FDX', 'NSC', 'UNP',
            
            # Utilities
            'NEE', 'SO', 'DUK', 'AEP', 'SRE', 'PEG', 'EXC', 'XEL', 'WEC', 'ES',
            'AWK', 'ATO', 'CNP', 'NI', 'LNT', 'EVRG', 'AES', 'PPL', 'FE', 'ETR',
            
            # Materials
            'LIN', 'APD', 'SHW', 'FCX', 'NEM', 'DOW', 'DD', 'PPG', 'ECL', 'CF',
            'LYB', 'MLM', 'VMC', 'NUE', 'STLD', 'X', 'CLF', 'AA', 'MOS', 'FMC',
            
            # REITs & Real Estate
            'PLD', 'AMT', 'SPG', 'O', 'EQIX', 'DLR', 'PSA', 'WELL', 'AVB', 'EQR',
            'VTR', 'BXP', 'HST', 'REG', 'MAA', 'UDR', 'CPT', 'ESS', 'AIV', 'PPS',
            
            # Communication Services
            'T', 'VZ', 'CMCSA', 'DIS', 'NFLX', 'META', 'GOOGL', 'GOOG', 'CHTR', 'TMUS',
            'VIV', 'OMC', 'IPG', 'NWSA', 'NWS', 'FOXA', 'FOX', 'WBD', 'PARA', 'LYV',
            
            # High Beta / Volatile
            'PLTR', 'COIN', 'HOOD', 'NCLH', 'CCL', 'RCL', 'UAL', 'DAL', 'AAL', 'LUV',
            'MGM', 'WYNN', 'LVS', 'CZR', 'PENN', 'DKNG', 'UBER', 'LYFT', 'ABNB', 'DASH'
        ]
        all_symbols = list(set(all_symbols))  # Remove duplicates
    
    print(f"Processing {len(all_symbols)} symbols...")
    
    # Get market data once
    print("Fetching S&P 500 index data...")
    end_date = datetime.now()
    start_date = end_date - timedelta(days=10*365 + 60)
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
                result = calculate_yahoo_beta_10y(symbol)
                
                if result is not None:
                    results.append(result)
                    print(f"✅ Beta: {result['Beta_10Y_Yahoo']:.3f} (R²={result['R_Squared']:.3f}, {result['Months']}m)")
                    
                    # Special highlight for key stocks
                    if symbol in ['NVDA', 'TSLA', 'PLTR', 'COIN', 'AAPL', 'MSFT']:
                        print(f"    🎯 {symbol}: {result['Beta_10Y_Yahoo']:.3f}")
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
        output_file = 'sp500_10years_yahoo_methodology.csv'
        results_df.to_csv(output_file, index=False)
        
        print(f"\n{'='*80}")
        print(f"10-YEAR YAHOO METHODOLOGY ANALYSIS COMPLETE!")
        print(f"{'='*80}")
        print(f"✅ Successfully processed: {len(results)} stocks")
        print(f"❌ Failed to process: {len(failed_stocks)} stocks")
        print(f"📊 Results saved to: {output_file}")
        
        # Summary statistics
        print(f"\n📈 10-YEAR BETA SUMMARY (Yahoo Methodology):")
        print(f"Average Beta: {results_df['Beta_10Y_Yahoo'].mean():.3f}")
        print(f"Beta Range: {results_df['Beta_10Y_Yahoo'].min():.3f} to {results_df['Beta_10Y_Yahoo'].max():.3f}")
        print(f"Median Beta: {results_df['Beta_10Y_Yahoo'].median():.3f}")
        print(f"Stocks with Beta > 1.5: {len(results_df[results_df['Beta_10Y_Yahoo'] > 1.5])}")
        print(f"Stocks with Beta < 0.5: {len(results_df[results_df['Beta_10Y_Yahoo'] < 0.5])}")
        
        # Average months of data
        avg_months = results_df['Months'].mean()
        max_months = results_df['Months'].max()
        min_months = results_df['Months'].min()
        print(f"Data coverage: {avg_months:.1f} months average ({min_months}-{max_months} range)")
        
        # Show top betas
        print(f"\n🏆 HIGHEST 10-YEAR BETAS (Yahoo Method):")
        top_betas = results_df.nlargest(15, 'Beta_10Y_Yahoo')[['Symbol', 'Beta_10Y_Yahoo', 'R_Squared', 'Months']]
        for _, row in top_betas.iterrows():
            print(f"  {row['Symbol']:<6} {row['Beta_10Y_Yahoo']:.3f} (R²={row['R_Squared']:.3f}, {row['Months']}m)")
        
        print(f"\n📉 LOWEST 10-YEAR BETAS (Yahoo Method):")
        low_betas = results_df.nsmallest(15, 'Beta_10Y_Yahoo')[['Symbol', 'Beta_10Y_Yahoo', 'R_Squared', 'Months']]
        for _, row in low_betas.iterrows():
            print(f"  {row['Symbol']:<6} {row['Beta_10Y_Yahoo']:.3f} (R²={row['R_Squared']:.3f}, {row['Months']}m)")
        
        # Check specific stocks
        key_stocks = ['NVDA', 'AAPL', 'MSFT', 'PLTR', 'TSLA', 'COIN', 'AMZN', 'GOOGL', 'META']
        print(f"\n🎯 KEY STOCKS 10-YEAR VERIFICATION:")
        for stock in key_stocks:
            stock_row = results_df[results_df['Symbol'] == stock]
            if not stock_row.empty:
                row = stock_row.iloc[0]
                beta = row['Beta_10Y_Yahoo']
                r2 = row['R_Squared']
                months = row['Months']
                vol = row['Volatility']
                print(f"  {stock:<6} Beta: {beta:.3f}, R²: {r2:.3f}, Months: {months}, Vol: {vol:.3f}")
        
        # Sector analysis if we have enough data
        if len(results) > 50:
            print(f"\n📊 10-YEAR BETA DISTRIBUTION:")
            print(f"Very High (>2.0): {len(results_df[results_df['Beta_10Y_Yahoo'] > 2.0])}")
            print(f"High (1.5-2.0): {len(results_df[(results_df['Beta_10Y_Yahoo'] >= 1.5) & (results_df['Beta_10Y_Yahoo'] <= 2.0)])}")
            print(f"Medium-High (1.0-1.5): {len(results_df[(results_df['Beta_10Y_Yahoo'] >= 1.0) & (results_df['Beta_10Y_Yahoo'] < 1.5)])}")
            print(f"Medium-Low (0.5-1.0): {len(results_df[(results_df['Beta_10Y_Yahoo'] >= 0.5) & (results_df['Beta_10Y_Yahoo'] < 1.0)])}")
            print(f"Low (<0.5): {len(results_df[results_df['Beta_10Y_Yahoo'] < 0.5])}")
        
        if failed_stocks:
            print(f"\n❌ FAILED STOCKS ({len(failed_stocks)}):")
            failed_str = ', '.join(failed_stocks[:30])
            if len(failed_stocks) > 30:
                failed_str += f", ... and {len(failed_stocks) - 30} more"
            print(f"  {failed_str}")
        
        print(f"\n💡 METHODOLOGY NOTES:")
        print(f"  • Uses exact Yahoo Finance methodology validated for 5Y")
        print(f"  • Extended to 10-year timeframe for long-term risk assessment")
        print(f"  • S&P 500 index (^GSPC) as benchmark")
        print(f"  • Up to 120 months of data per stock")
        print(f"  • Linear regression for beta calculation")
        print(f"  • Includes alpha, volatility, and Sharpe ratio metrics")
        
        # Quality metrics
        high_quality = len(results_df[results_df['R_Squared'] > 0.3])
        full_data = len(results_df[results_df['Months'] >= 100])
        
        print(f"\n📈 DATA QUALITY METRICS:")
        print(f"High R² (>0.3): {high_quality}/{len(results)} ({high_quality/len(results)*100:.1f}%)")
        print(f"Full 10Y data (≥100m): {full_data}/{len(results)} ({full_data/len(results)*100:.1f}%)")
        
        # Compare with 5Y if available
        try:
            df_5y = pd.read_csv('sp500_5year_yahoo_methodology.csv')
            common_stocks = set(results_df['Symbol']) & set(df_5y['Symbol'])
            if common_stocks:
                print(f"\n🔄 5Y vs 10Y BETA COMPARISON (Sample):")
                for stock in list(common_stocks)[:10]:
                    row_10y = results_df[results_df['Symbol'] == stock].iloc[0]
                    row_5y = df_5y[df_5y['Symbol'] == stock].iloc[0]
                    beta_10y = row_10y['Beta_10Y_Yahoo']
                    beta_5y = row_5y['Beta_5Y_Yahoo']
                    diff = beta_5y - beta_10y
                    print(f"  {stock:<6} 10Y: {beta_10y:.3f}, 5Y: {beta_5y:.3f}, Diff: {diff:+.3f}")
        except:
            pass
    
    else:
        print("❌ No successful results!")

if __name__ == "__main__":
    main()