#!/usr/bin/env python3

"""
YFinance functions for fetching historical bar data.
"""


import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf


def load_config():
    pass  # No longer needed

def getBars(symbol, start_date, end_date, timeframe='1Day'):
    """
    Fetch historical bar data from yfinance.
    
    Args:
        symbol (str): Stock symbol (e.g., 'AAPL')
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
        timeframe (str): Bar timeframe ('1Min', '5Min', '15Min', '30Min', '1Hour', '1Day')
    
    Returns:
        pandas.DataFrame: Historical bar data with columns [open, high, low, close, volume]
    """
    # Map timeframe to yfinance interval
    interval_map = {
        '1Min': '1m',
        '5Min': '5m',
        '15Min': '15m',
        '30Min': '30m',
        '1Hour': '60m',
        '1Day': '1d'
    }
    interval = interval_map.get(timeframe, '1d')
    
    try:
        # Ensure we download only one symbol to avoid multi-index
        df = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False,
            auto_adjust=False,
            threads=False  # Prevent multi-threading issues
        )
        
        if df.empty:
            print(f"No data found for {symbol}")
            return None
            
        # Force single-level columns by ensuring symbol is passed as string, not list
        if isinstance(df.columns, pd.MultiIndex):
            # If we still get multi-index, flatten it
            df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        
        # Standardize column names
        df.columns = df.columns.str.strip()  # Remove any whitespace
        
        # Use Adj Close if available, otherwise use Close
        if 'Adj Close' in df.columns:
            df['close'] = df['Adj Close']
        elif 'Close' in df.columns:
            df['close'] = df['Close']
        else:
            print(f"No close price column found for {symbol}. Available columns: {df.columns.tolist()}")
            return None
        
        # Rename other columns to match expected format
        column_mapping = {
            'Open': 'open',
            'High': 'high', 
            'Low': 'low',
            'Volume': 'volume'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Ensure we have the expected columns
        expected_cols = ['open', 'high', 'low', 'close', 'volume']
        available_cols = [col for col in expected_cols if col in df.columns]
        
        if 'close' not in available_cols:
            print(f"No close price data available for {symbol}")
            return None
            
        # Only keep expected columns that exist
        df = df[available_cols]
        
        # Remove any rows with NaN in close price
        df = df.dropna(subset=['close'])
        
        # Ensure numeric data types
        for col in ['open', 'high', 'low', 'close']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        if 'volume' in df.columns:
            df['volume'] = pd.to_numeric(df['volume'], errors='coerce')
        
        # Final check for valid data
        if df['close'].isna().all():
            print(f"All close prices are NaN for {symbol}")
            return None
            
        print(f"Successfully fetched {len(df)} rows for {symbol}")
        return df
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return None

def getBars5Min(symbol, start_date, end_date):
    """Fetch 5-minute bars."""
    return getBars(symbol, start_date, end_date, '5Min')

def getBars15Min(symbol, start_date, end_date):
    """Fetch 15-minute bars."""
    return getBars(symbol, start_date, end_date, '15Min')

def getBars30Min(symbol, start_date, end_date):
    """Fetch 30-minute bars."""
    return getBars(symbol, start_date, end_date, '30Min')

def getBars1Day(symbol, start_date, end_date):
    """Fetch daily bars."""
    return getBars(symbol, start_date, end_date, '1Day') 