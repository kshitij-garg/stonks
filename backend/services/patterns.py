"""
Chart Pattern Detection
Detect common technical chart patterns for trading signals
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional


def detect_patterns(df: pd.DataFrame) -> List[Dict]:
    """Detect various chart patterns"""
    if df is None or df.empty or len(df) < 20:
        return []
    
    patterns = []
    
    # Golden Cross / Death Cross
    if 'SMA_20' in df.columns and 'SMA_50' in df.columns:
        sma20 = df['SMA_20'].iloc[-1]
        sma50 = df['SMA_50'].iloc[-1]
        sma20_prev = df['SMA_20'].iloc[-2]
        sma50_prev = df['SMA_50'].iloc[-2]
        
        if sma20_prev < sma50_prev and sma20 > sma50:
            patterns.append({
                'name': 'Golden Cross',
                'type': 'bullish',
                'strength': 'strong',
                'description': 'SMA 20 crossed above SMA 50 - bullish signal'
            })
        elif sma20_prev > sma50_prev and sma20 < sma50:
            patterns.append({
                'name': 'Death Cross',
                'type': 'bearish',
                'strength': 'strong',
                'description': 'SMA 20 crossed below SMA 50 - bearish signal'
            })
    
    # RSI Divergence
    if 'RSI' in df.columns:
        rsi = df['RSI'].iloc[-1]
        if rsi < 30:
            patterns.append({
                'name': 'Oversold',
                'type': 'bullish',
                'strength': 'moderate',
                'description': f'RSI at {rsi:.0f} indicates oversold conditions'
            })
        elif rsi > 70:
            patterns.append({
                'name': 'Overbought',
                'type': 'bearish',
                'strength': 'moderate',
                'description': f'RSI at {rsi:.0f} indicates overbought conditions'
            })
    
    # MACD Crossover
    if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
        macd = df['MACD'].iloc[-1]
        signal = df['MACD_Signal'].iloc[-1]
        macd_prev = df['MACD'].iloc[-2]
        signal_prev = df['MACD_Signal'].iloc[-2]
        
        if macd_prev < signal_prev and macd > signal:
            patterns.append({
                'name': 'MACD Bullish Crossover',
                'type': 'bullish',
                'strength': 'moderate',
                'description': 'MACD crossed above signal line'
            })
        elif macd_prev > signal_prev and macd < signal:
            patterns.append({
                'name': 'MACD Bearish Crossover',
                'type': 'bearish',
                'strength': 'moderate',
                'description': 'MACD crossed below signal line'
            })
    
    # Bollinger Band Squeeze
    if 'BB_Upper' in df.columns and 'BB_Lower' in df.columns:
        bb_width = (df['BB_Upper'].iloc[-1] - df['BB_Lower'].iloc[-1]) / df['Close'].iloc[-1]
        avg_width = ((df['BB_Upper'] - df['BB_Lower']) / df['Close']).tail(20).mean()
        
        if bb_width < avg_width * 0.7:
            patterns.append({
                'name': 'Bollinger Squeeze',
                'type': 'neutral',
                'strength': 'moderate',
                'description': 'Low volatility squeeze - breakout expected'
            })
    
    # Higher Highs / Lower Lows
    highs = df['High'].tail(10)
    lows = df['Low'].tail(10)
    
    if all(highs.iloc[i] >= highs.iloc[i-1] for i in range(1, min(5, len(highs)))):
        patterns.append({
            'name': 'Higher Highs',
            'type': 'bullish',
            'strength': 'weak',
            'description': 'Consistent higher highs - uptrend'
        })
    
    if all(lows.iloc[i] <= lows.iloc[i-1] for i in range(1, min(5, len(lows)))):
        patterns.append({
            'name': 'Lower Lows',
            'type': 'bearish',
            'strength': 'weak',
            'description': 'Consistent lower lows - downtrend'
        })
    
    # Volume Spike
    if 'Volume' in df.columns and 'Volume_Ratio' in df.columns:
        vol_ratio = df['Volume_Ratio'].iloc[-1]
        if vol_ratio > 2:
            patterns.append({
                'name': 'Volume Spike',
                'type': 'neutral',
                'strength': 'strong',
                'description': f'Volume {vol_ratio:.1f}x average - significant activity'
            })
    
    # Support/Resistance
    close = df['Close'].iloc[-1]
    recent_high = df['High'].tail(20).max()
    recent_low = df['Low'].tail(20).min()
    
    if close >= recent_high * 0.98:
        patterns.append({
            'name': 'Near Resistance',
            'type': 'bearish',
            'strength': 'weak',
            'description': f'Price near 20-day high of ₹{recent_high:.2f}'
        })
    elif close <= recent_low * 1.02:
        patterns.append({
            'name': 'Near Support',
            'type': 'bullish',
            'strength': 'weak',
            'description': f'Price near 20-day low of ₹{recent_low:.2f}'
        })
    
    return patterns


def get_pattern_summary(patterns: List[Dict]) -> Dict:
    """Summarize patterns into overall signal"""
    if not patterns:
        return {'signal': 'neutral', 'strength': 0, 'patterns_count': 0}
    
    bullish = sum(1 for p in patterns if p['type'] == 'bullish')
    bearish = sum(1 for p in patterns if p['type'] == 'bearish')
    
    strength_map = {'strong': 3, 'moderate': 2, 'weak': 1}
    bull_strength = sum(strength_map.get(p['strength'], 1) for p in patterns if p['type'] == 'bullish')
    bear_strength = sum(strength_map.get(p['strength'], 1) for p in patterns if p['type'] == 'bearish')
    
    if bull_strength > bear_strength * 1.5:
        signal = 'bullish'
    elif bear_strength > bull_strength * 1.5:
        signal = 'bearish'
    else:
        signal = 'neutral'
    
    return {
        'signal': signal,
        'bullish_count': bullish,
        'bearish_count': bearish,
        'strength': bull_strength - bear_strength,
        'patterns_count': len(patterns),
        'patterns': patterns
    }
