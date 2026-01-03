"""
Stock Scoring Service - Professional Grade
With persistent caching and DCF integration
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from services.stock_service import (
    get_stock_data, 
    get_nifty_stocks, 
    get_stock_info,
    get_stock_data_batch,
    update_progress,
    get_cache,
    set_cache,
    PERIOD_MAP
)
from services.indicators import calculate_all_indicators, get_indicator_signals
from services.valuation import get_full_valuation_analysis



def safe_float(val, default=0.0):
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return default
    try:
        result = float(val)
        return default if np.isnan(result) else round(result, 2)
    except:
        return default


def safe_int(val, default=0):
    if val is None:
        return default
    try:
        return int(val)
    except:
        return default


def calculate_momentum_score(df: pd.DataFrame) -> float:
    if df.empty or len(df) < 5:
        return 50.0
    
    latest = df.iloc[-1]
    
    if len(df) < 20:
        if len(df) >= 5:
            try:
                short_return = ((df['Close'].iloc[-1] - df['Close'].iloc[-5]) / df['Close'].iloc[-5]) * 100
                normalized = ((short_return + 10) / 20) * 100
                return max(0, min(100, normalized))
            except:
                return 50.0
        return 50.0
    
    return_1w = safe_float(latest.get('Return_1W', 0))
    return_1m = safe_float(latest.get('Return_1M', 0))
    return_3m = safe_float(latest.get('Return_3M', 0))
    
    weighted_return = (return_1w * 0.5 + return_1m * 0.3 + return_3m * 0.2)
    normalized = ((weighted_return + 20) / 40) * 100
    return max(0, min(100, normalized))


def calculate_technical_score(df: pd.DataFrame) -> float:
    if df.empty or len(df) < 10:
        return 50.0
    
    latest = df.iloc[-1]
    score = 0
    max_score = 100
    
    rsi = safe_float(latest.get('RSI', 50), 50)
    if 30 <= rsi <= 50:
        score += 25
    elif 50 < rsi <= 70:
        score += 15
    elif rsi < 30:
        score += 20
    else:
        score += 5
    
    macd = safe_float(latest.get('MACD', 0))
    macd_signal = safe_float(latest.get('MACD_Signal', 0))
    if macd > macd_signal:
        score += 25
    else:
        score += 10
    
    price = safe_float(latest['Close'])
    sma_20 = safe_float(latest.get('SMA_20', 0))
    sma_50 = safe_float(latest.get('SMA_50', 0))
    
    if sma_20 > 0 and price > sma_20:
        score += 15
    if sma_50 > 0 and price > sma_50:
        score += 15
    
    bb_percent = safe_float(latest.get('BB_Percent', 0.5), 0.5)
    if 0.2 <= bb_percent <= 0.5:
        score += 20
    elif 0.5 < bb_percent <= 0.8:
        score += 10
    else:
        score += 5
    
    return min(100, score)


def calculate_volume_score(df: pd.DataFrame) -> float:
    if df.empty or len(df) < 5:
        return 50.0
    
    score = 50.0
    recent = df.tail(10).copy() if len(df) >= 10 else df.copy()
    
    if 'Volume_Ratio' in recent.columns:
        try:
            avg_ratio = recent['Volume_Ratio'].mean()
            if not pd.isna(avg_ratio):
                if avg_ratio > 1.5:
                    score += 25
                elif avg_ratio > 1.2:
                    score += 15
                elif avg_ratio < 0.7:
                    score -= 15
        except:
            pass
    
    return max(0, min(100, score))


def calculate_trend_score(df: pd.DataFrame) -> float:
    if df.empty or len(df) < 5:
        return 50.0
    
    try:
        latest = df.iloc[-1]
        first = df.iloc[0]
        
        score = 50.0
        trend = ((latest['Close'] - first['Close']) / first['Close']) * 100
        
        if trend > 5:
            score += 20
        elif trend > 2:
            score += 10
        elif trend < -5:
            score -= 20
        elif trend < -2:
            score -= 10
        
        sma_20 = safe_float(latest.get('SMA_20', 0))
        sma_50 = safe_float(latest.get('SMA_50', 0))
        
        if sma_20 > 0 and sma_50 > 0:
            if sma_20 > sma_50:
                score += 15
            else:
                score -= 10
        
        return max(0, min(100, score))
    except:
        return 50.0


def calculate_composite_score(symbol: str, df: pd.DataFrame = None, period: str = "6mo", interval: str = "1d") -> Optional[Dict]:
    """Calculate comprehensive stock score with DCF visualization data"""
    if df is None:
        df = get_stock_data(symbol, period=period, interval=interval)
    
    if df is None or df.empty:
        return None
    
    try:
        df = calculate_all_indicators(df)
        valuation = get_full_valuation_analysis(symbol, df)
        
        momentum_score = calculate_momentum_score(df)
        technical_score = calculate_technical_score(df)
        volume_score = calculate_volume_score(df)
        trend_score = calculate_trend_score(df)
        valuation_score = safe_float(valuation.get('valuation', {}).get('score', 50), 50)
        pe_score = safe_float(valuation.get('pe_score', 50), 50)
        
        composite = (
            momentum_score * 0.25 +
            technical_score * 0.30 +
            volume_score * 0.15 +
            trend_score * 0.15 +
            ((valuation_score + pe_score) / 2) * 0.15
        )
        
        info = get_stock_info(symbol)
        latest = df.iloc[-1]
        
        if len(df) >= 2:
            change_pct = ((latest['Close'] - df.iloc[-2]['Close']) / df.iloc[-2]['Close']) * 100
        else:
            change_pct = info.get('changePercent', 0) if info else 0
        
        # Get DCF data
        dcf = valuation.get('dcf', {})
        targets = valuation.get('targets', {})
        hurdle = valuation.get('hurdle_rate', {})
        
        # Calculate upside/downside visualization data
        current_price = safe_float(latest['Close'])
        dcf_value = safe_float(dcf.get('intrinsic_value', 0))
        buy_target = safe_float(targets.get('buy_targets', {}).get('conservative', 0))
        sell_target = safe_float(targets.get('sell_targets', {}).get('conservative', 0))
        
        price_range = {
            "current": current_price,
            "dcf_value": dcf_value,
            "buy_target": buy_target,
            "sell_target": sell_target,
            "dcf_upside": safe_float(((dcf_value - current_price) / current_price) * 100) if current_price > 0 else 0,
            "target_upside": safe_float(targets.get('upside_potential', {}).get('conservative', 0)),
            "target_downside": safe_float(targets.get('downside_risk', 0)),
            "52w_high": safe_float(info.get('fiftyTwoWeekHigh', 0)) if info else 0,
            "52w_low": safe_float(info.get('fiftyTwoWeekLow', 0)) if info else 0,
        }
        
        # Generate recommendation
        rec = generate_recommendation(composite, valuation, targets, dcf)
        
        return {
            "symbol": str(symbol),
            "name": str(info.get('name', symbol) if info else symbol),
            "sector": str(info.get('sector', 'Unknown') if info else 'Unknown'),
            "price": current_price,
            "change_percent": safe_float(change_pct),
            "scores": {
                "composite": safe_float(composite),
                "momentum": safe_float(momentum_score),
                "technical": safe_float(technical_score),
                "volume": safe_float(volume_score),
                "trend": safe_float(trend_score),
                "valuation": safe_float(valuation_score),
                "pe_score": safe_float(pe_score)
            },
            "returns": {
                "1w": safe_float(latest.get('Return_1W', 0)),
                "1m": safe_float(latest.get('Return_1M', 0)),
                "3m": safe_float(latest.get('Return_3M', 0))
            },
            "rsi": safe_float(latest.get('RSI', 50), 50),
            "macd_signal": "Bullish" if safe_float(latest.get('MACD', 0)) > safe_float(latest.get('MACD_Signal', 0)) else "Bearish",
            "valuation_status": str(valuation.get('valuation', {}).get('status', 'Unknown')),
            "market_cap_category": str(valuation.get('market_cap_category', 'Unknown')),
            "market_cap": safe_int(valuation.get('market_cap', 0)),
            "fundamentals": valuation.get('fundamentals', {}),
            "targets": targets,
            "dcf": {
                "intrinsic_value": dcf_value,
                "margin_of_safety": safe_float(dcf.get('margin_of_safety', 0)),
                "valuation": str(dcf.get('valuation', 'Unknown')),
                "assumptions": dcf.get('assumptions', {})
            },
            "hurdle_rate": hurdle,
            "price_range": price_range,
            "recommendation": rec
        }
    except Exception as e:
        print(f"Error scoring {symbol}: {e}")
        return None


def generate_recommendation(composite: float, valuation: dict, targets: dict, dcf: dict) -> Dict:
    """Generate professional recommendation"""
    val_status = valuation.get('valuation', {}).get('status', 'Unknown')
    dcf_margin = safe_float(dcf.get('margin_of_safety', 0))
    
    # Score-based action
    if composite >= 70 and dcf_margin > 20:
        action, color, conf = "STRONG BUY", "#10b981", min(95, composite)
    elif composite >= 60 or (composite >= 50 and dcf_margin > 15):
        action, color, conf = "BUY", "#34d399", composite
    elif composite >= 45:
        action, color, conf = "HOLD", "#f59e0b", 50
    elif composite >= 35:
        action, color, conf = "SELL", "#f87171", 100 - composite
    else:
        action, color, conf = "STRONG SELL", "#ef4444", min(95, 100 - composite)
    
    return {
        "action": action,
        "color": color,
        "confidence": safe_float(conf),
        "dcf_margin": dcf_margin,
        "upside": safe_float(targets.get('upside_potential', {}).get('conservative', 0)),
        "risk_reward": safe_float(targets.get('risk_reward_ratio', 0)),
        "buy_target": safe_float(targets.get('buy_targets', {}).get('conservative', 0)),
        "sell_target": safe_float(targets.get('sell_targets', {}).get('conservative', 0))
    }


def get_all_scored_stocks(period: str = "6mo", interval: str = "1d", timeframe: str = "weekly") -> List[Dict]:
    """Get all stocks with scores - uses persistent cache"""
    
    # Check cache first
    cached = get_cache(timeframe, "scored")
    if cached:
        update_progress(45, 45, f"✓ Using cached {timeframe} scores", "done", timeframe)
        return cached
    
    stocks = get_nifty_stocks()
    symbols = list(stocks.keys())
    
    stock_data = get_stock_data_batch(symbols, period=period, interval=interval, timeframe=timeframe)
    
    scored_stocks = []
    total = len(stock_data)
    
    for i, (symbol, df) in enumerate(stock_data.items()):
        try:
            result = calculate_composite_score(symbol, df, period=period, interval=interval)
            if result:
                scored_stocks.append(result)
            update_progress(i + 1, total, f"Scoring {symbol}", "loading", timeframe)
        except Exception as e:
            continue
    
    scored_stocks.sort(key=lambda x: x['scores']['composite'], reverse=True)
    
    for i, stock in enumerate(scored_stocks):
        stock['rank'] = i + 1
    
    # Cache the results
    set_cache(timeframe, "scored", scored_stocks)
    
    update_progress(total, total, f"✓ {timeframe.title()}: {len(scored_stocks)} stocks analyzed", "done", timeframe)
    return scored_stocks


def get_recommendations(period: str = "6mo", interval: str = "1d", timeframe: str = "weekly") -> Dict:
    """Get actionable recommendations"""
    all_stocks = get_all_scored_stocks(period=period, interval=interval, timeframe=timeframe)
    
    strong_buys = [s for s in all_stocks if s.get('recommendation', {}).get('action') == 'STRONG BUY']
    buys = [s for s in all_stocks if s.get('recommendation', {}).get('action') == 'BUY']
    holds = [s for s in all_stocks if s.get('recommendation', {}).get('action') == 'HOLD']
    sells = [s for s in all_stocks if s.get('recommendation', {}).get('action') == 'SELL']
    strong_sells = [s for s in all_stocks if s.get('recommendation', {}).get('action') == 'STRONG SELL']
    
    top_picks = sorted(
        [s for s in all_stocks if s.get('recommendation', {}).get('action') in ['STRONG BUY', 'BUY']],
        key=lambda x: x.get('recommendation', {}).get('confidence', 0),
        reverse=True
    )[:5]
    
    avoid_list = sorted(
        [s for s in all_stocks if s.get('recommendation', {}).get('action') in ['STRONG SELL', 'SELL']],
        key=lambda x: x.get('recommendation', {}).get('confidence', 0),
        reverse=True
    )[:5]
    
    return {
        "summary": {
            "strong_buy": len(strong_buys),
            "buy": len(buys),
            "hold": len(holds),
            "sell": len(sells),
            "strong_sell": len(strong_sells),
            "total": len(all_stocks)
        },
        "top_picks": top_picks,
        "avoid_list": avoid_list,
        "all_recommendations": all_stocks
    }


def screen_stocks(
    min_score: float = 0,
    max_rsi: float = 100,
    min_rsi: float = 0,
    sectors: List[str] = None,
    macd_signal: str = None,
    valuation_status: str = None,
    min_upside: float = None,
    max_pe: float = None,
    period: str = "6mo",
    interval: str = "1d",
    timeframe: str = "weekly"
) -> List[Dict]:
    """Screen stocks with advanced filters"""
    all_stocks = get_all_scored_stocks(period=period, interval=interval, timeframe=timeframe)
    
    filtered = []
    for stock in all_stocks:
        if stock['scores']['composite'] < min_score:
            continue
        if stock['rsi'] < min_rsi or stock['rsi'] > max_rsi:
            continue
        if sectors and stock['sector'] not in sectors:
            continue
        if macd_signal and stock['macd_signal'] != macd_signal:
            continue
        if valuation_status and stock['valuation_status'] != valuation_status:
            continue
        if min_upside is not None:
            upside = stock.get('recommendation', {}).get('upside', 0)
            if upside < min_upside:
                continue
        if max_pe is not None:
            pe = stock.get('fundamentals', {}).get('pe_ratio', 0)
            if pe > max_pe:
                continue
        filtered.append(stock)
    
    return filtered
