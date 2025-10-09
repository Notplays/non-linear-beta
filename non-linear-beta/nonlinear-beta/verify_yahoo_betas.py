#!/usr/bin/env python3
"""
Yahoo Finance Beta Verification Script
Compare our calculated 5Y betas with Yahoo Finance website values
"""

import pandas as pd
import yfinance as yf
import time
import requests
from bs4 import BeautifulSoup
import re

def get_yahoo_beta_web(symbol):
    """
    Get beta from Yahoo Finance website using web scraping
    """
    try:
        url = f"https://finance.yahoo.com/quote/{symbol}/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return None
            
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Look for beta in various possible locations
        beta_patterns = [
            r'Beta.*?(\d+\.\d+)',
            r'beta.*?(\d+\.\d+)', 
            r'Beta \(5Y Monthly\).*?(\d+\.\d+)',
            r'"beta".*?(\d+\.\d+)'
        ]
        
        page_text = soup.get_text()
        
        for pattern in beta_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                try:
                    beta = float(matches[0])
                    if 0.01 <= beta <= 10.0:  # Reasonable beta range
                        return beta
                except:
                    continue
        
        # Try yfinance as backup
        ticker = yf.Ticker(symbol)
        info = ticker.info
        if 'beta' in info and info['beta'] is not None:
            return float(info['beta'])
            
        return None
        
    except Exception as e:
        print(f"Error getting beta for {symbol}: {e}")
        return None

def verify_betas():
    """
    Verify our calculated betas against Yahoo Finance
    """
    print("🔍 YAHOO FINANCE BETA VERIFICATION")
    print("="*80)
    
    # Load our calculated betas
    try:
        our_df = pd.read_csv('sp500_5year_yahoo_methodology.csv')
        print(f"Loaded {len(our_df)} calculated betas")
    except Exception as e:
        print(f"Error loading our results: {e}")
        return
    
    # Test stocks - mix of high profile and various beta ranges
    test_stocks = [
        # High profile tech
        'NVDA', 'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA',
        # High beta stocks from our results
        'PLTR', 'COIN', 'HOOD', 'NCLH', 'CCL',
        # Medium beta stocks
        'JPM', 'JNJ', 'PG', 'KO', 'WMT', 'V', 'MA',
        # Low beta stocks
        'NEE', 'SO', 'VZ', 'PFE', 'MRK',
        # Various sectors
        'XOM', 'CVX', 'GS', 'BAC', 'UNH', 'HD', 'DIS', 'NFLX'
    ]
    
    results = []
    
    print(f"\nTesting {len(test_stocks)} representative stocks...")
    print("-" * 80)
    
    for i, symbol in enumerate(test_stocks):
        print(f"{i+1:2d}/{len(test_stocks)}: {symbol:<6}", end=" ")
        
        # Get our calculated beta
        our_row = our_df[our_df['Symbol'] == symbol]
        if our_row.empty:
            print("❌ Not in our data")
            continue
            
        our_beta = our_row.iloc[0]['Beta_5Y_Yahoo']
        
        # Get Yahoo Finance beta
        yahoo_beta = get_yahoo_beta_web(symbol)
        
        if yahoo_beta is None:
            print(f"❌ Yahoo data unavailable (Our: {our_beta:.3f})")
            continue
        
        # Calculate deviation
        deviation = abs(our_beta - yahoo_beta)
        deviation_pct = (deviation / yahoo_beta) * 100 if yahoo_beta != 0 else 999
        
        # Status
        if deviation <= 0.05:
            status = "✅ EXCELLENT"
        elif deviation <= 0.15:
            status = "✅ GOOD"
        elif deviation <= 0.30:
            status = "⚠️  FAIR"
        else:
            status = "❌ POOR"
        
        print(f"Our: {our_beta:.3f}, Yahoo: {yahoo_beta:.3f}, Diff: {deviation:.3f} ({deviation_pct:.1f}%) {status}")
        
        results.append({
            'Symbol': symbol,
            'Our_Beta': our_beta,
            'Yahoo_Beta': yahoo_beta,
            'Deviation': deviation,
            'Deviation_Pct': deviation_pct,
            'Status': status
        })
        
        # Small delay to be respectful
        time.sleep(0.5)
    
    # Analysis
    if results:
        results_df = pd.DataFrame(results)
        
        print(f"\n{'='*80}")
        print(f"VERIFICATION RESULTS SUMMARY")
        print(f"{'='*80}")
        
        print(f"📊 Stocks Tested: {len(results)}")
        
        # Quality distribution
        excellent = len(results_df[results_df['Deviation'] <= 0.05])
        good = len(results_df[(results_df['Deviation'] > 0.05) & (results_df['Deviation'] <= 0.15)])
        fair = len(results_df[(results_df['Deviation'] > 0.15) & (results_df['Deviation'] <= 0.30)])
        poor = len(results_df[results_df['Deviation'] > 0.30])
        
        print(f"✅ Excellent (≤0.05): {excellent} ({excellent/len(results)*100:.1f}%)")
        print(f"✅ Good (≤0.15): {good} ({good/len(results)*100:.1f}%)")
        print(f"⚠️  Fair (≤0.30): {fair} ({fair/len(results)*100:.1f}%)")
        print(f"❌ Poor (>0.30): {poor} ({poor/len(results)*100:.1f}%)")
        
        # Statistics
        mean_dev = results_df['Deviation'].mean()
        median_dev = results_df['Deviation'].median()
        max_dev = results_df['Deviation'].max()
        min_dev = results_df['Deviation'].min()
        
        print(f"\n📈 DEVIATION STATISTICS:")
        print(f"Mean Deviation: {mean_dev:.3f}")
        print(f"Median Deviation: {median_dev:.3f}")
        print(f"Max Deviation: {max_dev:.3f}")
        print(f"Min Deviation: {min_dev:.3f}")
        
        mean_dev_pct = results_df['Deviation_Pct'].mean()
        median_dev_pct = results_df['Deviation_Pct'].median()
        
        print(f"Mean % Deviation: {mean_dev_pct:.1f}%")
        print(f"Median % Deviation: {median_dev_pct:.1f}%")
        
        # Best matches
        print(f"\n🎯 BEST MATCHES (Lowest Deviation):")
        best_matches = results_df.nsmallest(5, 'Deviation')
        for _, row in best_matches.iterrows():
            print(f"  {row['Symbol']:<6} Our: {row['Our_Beta']:.3f}, Yahoo: {row['Yahoo_Beta']:.3f}, Diff: {row['Deviation']:.3f}")
        
        # Worst matches
        print(f"\n❌ WORST MATCHES (Highest Deviation):")
        worst_matches = results_df.nlargest(5, 'Deviation')
        for _, row in worst_matches.iterrows():
            print(f"  {row['Symbol']:<6} Our: {row['Our_Beta']:.3f}, Yahoo: {row['Yahoo_Beta']:.3f}, Diff: {row['Deviation']:.3f}")
        
        # Key stocks verification
        key_stocks = ['NVDA', 'AAPL', 'MSFT', 'TSLA', 'AMZN']
        print(f"\n🔑 KEY STOCKS VERIFICATION:")
        for stock in key_stocks:
            stock_row = results_df[results_df['Symbol'] == stock]
            if not stock_row.empty:
                row = stock_row.iloc[0]
                print(f"  {row['Symbol']:<6} Our: {row['Our_Beta']:.3f}, Yahoo: {row['Yahoo_Beta']:.3f}, Diff: {row['Deviation']:.3f} ({row['Deviation_Pct']:.1f}%)")
        
        # Save detailed results
        results_df.to_csv('yahoo_beta_verification.csv', index=False)
        print(f"\n💾 Detailed results saved to: yahoo_beta_verification.csv")
        
        # Overall assessment
        accuracy_score = (excellent + good) / len(results) * 100
        print(f"\n🎯 OVERALL ACCURACY ASSESSMENT:")
        print(f"Accuracy Score: {accuracy_score:.1f}% (Excellent + Good matches)")
        
        if accuracy_score >= 90:
            print("🟢 OUTSTANDING - Methodology is highly accurate")
        elif accuracy_score >= 80:
            print("🟡 GOOD - Methodology is reliable with minor deviations")
        elif accuracy_score >= 70:
            print("🟠 FAIR - Methodology has some accuracy issues")
        else:
            print("🔴 POOR - Methodology needs significant improvement")
    
    else:
        print("❌ No successful verifications!")

if __name__ == "__main__":
    verify_betas()