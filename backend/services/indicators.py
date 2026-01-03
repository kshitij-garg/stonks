"""
Technical Indicators Service
Calculates technical analysis indicators for stock data
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional


def calculate_sma(df: pd.DataFrame, periods: list = [20, 50, 200]) -> pd.DataFrame:
    """Calculate Simple Moving Averages"""
    for period in periods:
        df[f'SMA_{period}'] = df['Close'].rolling(window=period).mean()
    return df


def calculate_ema(df: pd.DataFrame, periods: list = [9, 21, 50]) -> pd.DataFrame:
    """Calculate Exponential Moving Averages"""
    for period in periods:
        df[f'EMA_{period}'] = df['Close'].ewm(span=period, adjust=False).mean()
    return df


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate Relative Strength Index
    RSI = 100 - (100 / (1 + RS))
    where RS = Average Gain / Average Loss
    """
    delta = df['Close'].diff()
    
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    
    avg_gain = gain.rolling(window=period).mean()
    avg_loss = loss.rolling(window=period).mean()
    
    # Avoid division by zero
    rs = avg_gain / avg_loss.replace(0, np.nan)
    
    df['RSI'] = 100 - (100 / (1 + rs))
    df['RSI'] = df['RSI'].fillna(50)  # Default to neutral
    
    return df


def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal: int = 9) -> pd.DataFrame:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    MACD Line = 12-EMA - 26-EMA
    Signal Line = 9-EMA of MACD Line
    Histogram = MACD Line - Signal Line
    """
    ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
    ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()
    
    df['MACD'] = ema_fast - ema_slow
    df['MACD_Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
    df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']
    
    return df


def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, std_dev: float = 2.0) -> pd.DataFrame:
    """
    Calculate Bollinger Bands
    Middle Band = 20-SMA
    Upper Band = Middle + (2 * std)
    Lower Band = Middle - (2 * std)
    """
    df['BB_Middle'] = df['Close'].rolling(window=period).mean()
    rolling_std = df['Close'].rolling(window=period).std()
    
    df['BB_Upper'] = df['BB_Middle'] + (std_dev * rolling_std)
    df['BB_Lower'] = df['BB_Middle'] - (std_dev * rolling_std)
    
    # %B indicator (position within bands)
    df['BB_Percent'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
    
    return df


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate Average True Range (volatility indicator)
    """
    high_low = df['High'] - df['Low']
    high_close = abs(df['High'] - df['Close'].shift())
    low_close = abs(df['Low'] - df['Close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['ATR'] = true_range.rolling(window=period).mean()
    
    return df


def calculate_volume_analysis(df: pd.DataFrame, period: int = 20) -> pd.DataFrame:
    """
    Calculate volume-based indicators
    """
    df['Volume_SMA'] = df['Volume'].rolling(window=period).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
    
    # On-Balance Volume (OBV)
    df['OBV'] = (np.sign(df['Close'].diff()) * df['Volume']).fillna(0).cumsum()
    
    return df


def calculate_momentum(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate momentum indicators
    """
    # Rate of Change
    df['ROC_5'] = ((df['Close'] - df['Close'].shift(5)) / df['Close'].shift(5)) * 100
    df['ROC_10'] = ((df['Close'] - df['Close'].shift(10)) / df['Close'].shift(10)) * 100
    df['ROC_20'] = ((df['Close'] - df['Close'].shift(20)) / df['Close'].shift(20)) * 100
    
    # Weekly and Monthly returns
    df['Return_1W'] = df['Close'].pct_change(periods=5) * 100
    df['Return_1M'] = df['Close'].pct_change(periods=21) * 100
    df['Return_3M'] = df['Close'].pct_change(periods=63) * 100
    
    return df


def calculate_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate all technical indicators
    """
    df = calculate_sma(df)
    df = calculate_ema(df)
    df = calculate_rsi(df)
    df = calculate_macd(df)
    df = calculate_bollinger_bands(df)
    df = calculate_atr(df)
    df = calculate_volume_analysis(df)
    df = calculate_momentum(df)
    
    return df


def get_indicator_signals(df: pd.DataFrame) -> Dict:
    """
    Generate trading signals based on indicators
    Returns a summary of signals
    """
    if df.empty or len(df) < 2:
        return {}
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    signals = {
        'rsi': {
            'value': round(latest.get('RSI', 50), 2),
            'signal': 'Oversold' if latest.get('RSI', 50) < 30 else 
                     'Overbought' if latest.get('RSI', 50) > 70 else 'Neutral',
            'color': 'green' if latest.get('RSI', 50) < 30 else 
                    'red' if latest.get('RSI', 50) > 70 else 'gray'
        },
        'macd': {
            'value': round(latest.get('MACD', 0), 2),
            'signal_line': round(latest.get('MACD_Signal', 0), 2),
            'histogram': round(latest.get('MACD_Histogram', 0), 2),
            'signal': 'Bullish' if latest.get('MACD', 0) > latest.get('MACD_Signal', 0) else 'Bearish',
            'crossover': 'Golden Cross' if (prev.get('MACD', 0) <= prev.get('MACD_Signal', 0) and 
                                           latest.get('MACD', 0) > latest.get('MACD_Signal', 0)) else
                        'Death Cross' if (prev.get('MACD', 0) >= prev.get('MACD_Signal', 0) and 
                                         latest.get('MACD', 0) < latest.get('MACD_Signal', 0)) else None
        },
        'moving_averages': {
            'sma_20': round(latest.get('SMA_20', 0), 2),
            'sma_50': round(latest.get('SMA_50', 0), 2),
            'sma_200': round(latest.get('SMA_200', 0), 2),
            'price_vs_sma20': 'Above' if latest['Close'] > latest.get('SMA_20', 0) else 'Below',
            'price_vs_sma50': 'Above' if latest['Close'] > latest.get('SMA_50', 0) else 'Below',
            'price_vs_sma200': 'Above' if latest['Close'] > latest.get('SMA_200', 0) else 'Below',
            'trend': 'Strong Uptrend' if (latest.get('SMA_20', 0) > latest.get('SMA_50', 0) > latest.get('SMA_200', 0)) else
                    'Strong Downtrend' if (latest.get('SMA_20', 0) < latest.get('SMA_50', 0) < latest.get('SMA_200', 0)) else
                    'Mixed'
        },
        'bollinger': {
            'upper': round(latest.get('BB_Upper', 0), 2),
            'middle': round(latest.get('BB_Middle', 0), 2),
            'lower': round(latest.get('BB_Lower', 0), 2),
            'percent_b': round(latest.get('BB_Percent', 0.5), 2),
            'position': 'Near Upper' if latest.get('BB_Percent', 0.5) > 0.8 else
                       'Near Lower' if latest.get('BB_Percent', 0.5) < 0.2 else 'Middle'
        },
        'volume': {
            'current': int(latest.get('Volume', 0)),
            'average': int(latest.get('Volume_SMA', 0)),
            'ratio': round(latest.get('Volume_Ratio', 1), 2),
            'signal': 'High Volume' if latest.get('Volume_Ratio', 1) > 1.5 else
                     'Low Volume' if latest.get('Volume_Ratio', 1) < 0.5 else 'Normal'
        },
        'momentum': {
            'roc_5': round(latest.get('ROC_5', 0), 2),
            'roc_10': round(latest.get('ROC_10', 0), 2),
            'return_1w': round(latest.get('Return_1W', 0), 2),
            'return_1m': round(latest.get('Return_1M', 0), 2),
            'return_3m': round(latest.get('Return_3M', 0), 2)
        },
        'atr': {
            'value': round(latest.get('ATR', 0), 2),
            'percent': round((latest.get('ATR', 0) / latest['Close']) * 100, 2) if latest['Close'] > 0 else 0
        }
    }
    
    return signals
