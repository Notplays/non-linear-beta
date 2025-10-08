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
    Fetch historical bar data from Alpaca Markets API.
    
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
        df = yf.download(
            symbol,
            start=start_date,
            end=end_date,
            interval=interval,
            progress=False
        )
        if df.empty:
            print(f"No data found for {symbol}")
            return None
        # Rename columns to match expected format
        df.rename(columns={
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume'
        }, inplace=True)
        # Only keep expected columns
        df = df[['open', 'high', 'low', 'close', 'volume']]
        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
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