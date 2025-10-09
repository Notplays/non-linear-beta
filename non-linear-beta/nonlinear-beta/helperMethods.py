#!/usr/bin/env python3
"""
Helper methods for trading day calculations and drift analysis.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta



def load_config():
    pass  # No longer needed

def getTradingDays(start_date, end_date):
    """
    Get list of trading days between start_date and end_date.
    
    Args:
        start_date (str): Start date in 'YYYY-MM-DD' format
        end_date (str): End date in 'YYYY-MM-DD' format
    
    Returns:
        list: List of trading day dates
    """
    # Use pandas market calendar for NYSE
    import pandas_market_calendars as mcal
    nyse = mcal.get_calendar('NYSE')
    schedule = nyse.schedule(start_date=start_date, end_date=end_date)
    trading_days = schedule.index.strftime('%Y-%m-%d').tolist()
    return trading_days

def calculateDrift(df, window=20):
    """
    Calculate price drift over a rolling window.
    
    Args:
        df (pandas.DataFrame): Price data with 'close' column
        window (int): Rolling window size
    
    Returns:
        pandas.Series: Drift values
    """
    if 'close' not in df.columns:
        print("DataFrame must have 'close' column")
        return None
    
    # Calculate returns
    returns = df['close'].pct_change()
    
    # Calculate rolling mean (drift)
    drift = returns.rolling(window=window).mean()
    
    return drift

def plotDrift(df, symbol, window=20):
    """
    Plot price drift analysis.
    
    Args:
        df (pandas.DataFrame): Price data
        symbol (str): Stock symbol for title
        window (int): Rolling window size
    """
    import matplotlib.pyplot as plt
    
    drift = calculateDrift(df, window)
    
    if drift is None:
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
    
    # Price plot
    ax1.plot(df.index, df['close'], label='Price')
    ax1.set_title(f'{symbol} Price and Drift Analysis')
    ax1.set_ylabel('Price')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Drift plot
    ax2.plot(drift.index, drift, label=f'{window}-day Drift', color='red')
    ax2.axhline(y=0, color='black', linestyle='--', alpha=0.5)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Drift')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show() 