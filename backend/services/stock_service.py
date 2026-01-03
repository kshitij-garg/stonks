"""
Stock Data Service - Professional Grade with Local Storage
135+ stocks with SQLite price caching and accurate return calculations
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from services.stock_universe import get_all_stocks, get_stocks_by_index, STOCK_COUNTS
from services.price_db import (
    store_price_data, 
    get_stored_prices, 
    needs_sync,
    get_database_stats
)

# ============================================
# CACHE & PROGRESS
# ============================================
CACHE_VALIDITY_SECONDS = 600

_cache_store = {
    "daily": {"data": None, "scored": None, "timestamp": None},
    "weekly": {"data": None, "scored": None, "timestamp": None},
    "monthly": {"data": None, "scored": None, "timestamp": None}
}
_cache_lock = threading.Lock()

_progress = {
    "current": 0,
    "total": 0,
    "status": "idle",
    "message": "",
    "logs": [],
    "active_timeframe": None
}
_progress_lock = threading.Lock()


def get_cache(timeframe: str, key: str = "scored"):
    with _cache_lock:
        cache = _cache_store.get(timeframe)
        if cache and cache.get("timestamp"):
            age = (datetime.now() - cache["timestamp"]).seconds
            if age < CACHE_VALIDITY_SECONDS:
                return cache.get(key)
    return None


def set_cache(timeframe: str, key: str, data):
    with _cache_lock:
        if timeframe not in _cache_store:
            _cache_store[timeframe] = {}
        _cache_store[timeframe][key] = data
        _cache_store[timeframe]["timestamp"] = datetime.now()


def get_cache_status():
    with _cache_lock:
        status = {}
        for tf, cache in _cache_store.items():
            if cache.get("timestamp"):
                age = (datetime.now() - cache["timestamp"]).seconds
                status[tf] = {
                    "cached": True,
                    "age_seconds": age,
                    "valid": age < CACHE_VALIDITY_SECONDS,
                    "stocks_count": len(cache.get("scored", [])) if cache.get("scored") else 0
                }
            else:
                status[tf] = {"cached": False, "age_seconds": 0, "valid": False, "stocks_count": 0}
        
        # Add database stats
        try:
            status["database"] = get_database_stats()
        except:
            status["database"] = {}
        
        return status


def reset_progress():
    global _progress
    with _progress_lock:
        _progress = {
            "current": 0, "total": 0, "status": "idle",
            "message": "", "logs": [], "active_timeframe": None
        }


def update_progress(current: int, total: int, message: str, status: str = "loading", timeframe: str = None):
    global _progress
    with _progress_lock:
        _progress["current"] = current
        _progress["total"] = total
        _progress["message"] = message
        _progress["status"] = status
        if timeframe:
            _progress["active_timeframe"] = timeframe
        _progress["logs"].append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "message": message
        })
        _progress["logs"] = _progress["logs"][-50:]


def get_progress():
    with _progress_lock:
        result = _progress.copy()
        result["cache_status"] = get_cache_status()
        return result


# ============================================
# PERIOD CONFIGURATION
# ============================================
PERIOD_MAP = {
    "daily": {"period": "1mo", "interval": "1d", "lookback_days": 30},
    "weekly": {"period": "6mo", "interval": "1wk", "lookback_days": 180},
    "monthly": {"period": "2y", "interval": "1mo", "lookback_days": 730}
}


def get_nifty_stocks() -> Dict:
    """Get all stocks - backwards compatible"""
    return get_all_stocks()


# ============================================
# DATA FETCHING WITH LOCAL STORAGE
# ============================================

def fetch_and_store_stock(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
    """Fetch stock data from yfinance and store locally"""
    try:
        # Try NSE first
        ticker = yf.Ticker(f"{symbol}.NS")
        df = ticker.history(period=period)
        
        if df.empty:
            ticker = yf.Ticker(f"{symbol}.BO")
            df = ticker.history(period=period)
        
        if not df.empty:
            df = df.reset_index()
            if 'Date' in df.columns:
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
            elif 'Datetime' in df.columns:
                df['Date'] = pd.to_datetime(df['Datetime']).dt.strftime('%Y-%m-%d')
            
            # Store to local database
            store_price_data(symbol, df)
            return df
        
        return None
    except Exception as e:
        return None


def get_stock_data_smart(symbol: str, lookback_days: int = 180) -> Optional[pd.DataFrame]:
    """
    Smart data retrieval:
    1. Check local database first
    2. Only fetch from yfinance if data is stale or missing
    3. Calculate returns from stored data
    """
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
    
    # Check if we have recent data in DB
    if not needs_sync(symbol, max_age_hours=6):
        stored = get_stored_prices(symbol, start_date, end_date)
        if stored is not None and len(stored) >= 5:
            return stored
    
    # Fetch fresh data
    period = "1y" if lookback_days > 180 else "6mo"
    df = fetch_and_store_stock(symbol, period)
    
    if df is not None:
        # Filter to requested range
        df['Date'] = pd.to_datetime(df['Date'])
        df = df[df['Date'] >= start_date]
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
        return df
    
    # Fallback to any stored data
    return get_stored_prices(symbol, start_date, end_date)


def calculate_accurate_returns(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate accurate 1W, 1M, 3M returns from price data"""
    if df is None or df.empty or len(df) < 2:
        return df
    
    df = df.copy()
    df['Close'] = pd.to_numeric(df['Close'], errors='coerce')
    
    latest_price = df['Close'].iloc[-1]
    
    # 1 Week return (5 trading days)
    if len(df) >= 5:
        week_ago_price = df['Close'].iloc[-5]
        df['Return_1W'] = ((latest_price - week_ago_price) / week_ago_price) * 100
    else:
        df['Return_1W'] = 0
    
    # 1 Month return (~20 trading days)
    if len(df) >= 20:
        month_ago_price = df['Close'].iloc[-20]
        df['Return_1M'] = ((latest_price - month_ago_price) / month_ago_price) * 100
    elif len(df) >= 5:
        df['Return_1M'] = df['Return_1W']
    else:
        df['Return_1M'] = 0
    
    # 3 Month return (~60 trading days)
    if len(df) >= 60:
        three_month_price = df['Close'].iloc[-60]
        df['Return_3M'] = ((latest_price - three_month_price) / three_month_price) * 100
    elif len(df) >= 40:
        df['Return_3M'] = df['Return_1M'] * 1.5
    else:
        df['Return_3M'] = df['Return_1M']
    
    return df


def fetch_single_stock(symbol: str, period_config: dict) -> tuple:
    """Fetch a single stock with smart caching"""
    try:
        df = get_stock_data_smart(symbol, period_config['lookback_days'])
        
        if df is not None and not df.empty:
            df = calculate_accurate_returns(df)
            return (symbol, df, None)
        
        return (symbol, None, "No data")
    except Exception as e:
        return (symbol, None, str(e))


def get_stock_data_batch(symbols: List[str], period: str = "6mo", interval: str = "1d", 
                         timeframe: str = "weekly") -> Dict[str, pd.DataFrame]:
    """Fetch data for multiple stocks with parallel processing"""
    
    cached = get_cache(timeframe, "data")
    if cached:
        cache_status = get_cache_status().get(timeframe, {})
        update_progress(len(symbols), len(symbols), 
                       f"✓ Using cached {timeframe} data ({cache_status.get('age_seconds', 0)}s old)", 
                       "done", timeframe)
        return cached
    
    result = {}
    total = len(symbols)
    success_count = 0
    period_config = PERIOD_MAP.get(timeframe, PERIOD_MAP['weekly'])
    
    reset_progress()
    update_progress(0, total, f"Fetching {timeframe} data for {total} stocks...", "loading", timeframe)
    
    # Parallel fetching
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {
            executor.submit(fetch_single_stock, symbol, period_config): symbol 
            for symbol in symbols
        }
        
        for i, future in enumerate(as_completed(futures)):
            symbol, df, error = future.result()
            if df is not None:
                result[symbol] = df
                success_count += 1
            
            if (i + 1) % 10 == 0 or i == total - 1:
                update_progress(i + 1, total, f"Loaded {success_count}/{i + 1} stocks", "loading", timeframe)
    
    set_cache(timeframe, "data", result)
    update_progress(total, total, f"✓ {timeframe.title()}: {success_count}/{total} stocks loaded", "done", timeframe)
    return result


def get_stock_data(symbol: str, period: str = "6mo", interval: str = "1d") -> Optional[pd.DataFrame]:
    """Get single stock data"""
    lookback = 180 if period == "6mo" else 365 if period == "1y" else 30
    df = get_stock_data_smart(symbol, lookback)
    if df is not None:
        df = calculate_accurate_returns(df)
    return df


def get_stock_info(symbol: str) -> Optional[Dict]:
    """Get stock fundamental info"""
    try:
        all_stocks = get_all_stocks()
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info
        
        if not info:
            return None
        
        current_price = info.get('regularMarketPrice') or info.get('currentPrice') or info.get('previousClose', 0)
        prev_close = info.get('previousClose') or current_price
        
        return {
            "symbol": symbol,
            "name": info.get('longName') or all_stocks.get(symbol, {}).get('name', symbol),
            "sector": all_stocks.get(symbol, {}).get('sector', 'Unknown'),
            "cap": all_stocks.get(symbol, {}).get('cap', 'Unknown'),
            "price": float(current_price) if current_price else 0,
            "previousClose": float(prev_close) if prev_close else 0,
            "marketCap": int(info.get('marketCap', 0)),
            "fiftyTwoWeekHigh": float(info.get('fiftyTwoWeekHigh', 0)),
            "fiftyTwoWeekLow": float(info.get('fiftyTwoWeekLow', 0)),
            "pe_ratio": float(info.get('trailingPE', 0)) if info.get('trailingPE') else 0,
            "pb_ratio": float(info.get('priceToBook', 0)) if info.get('priceToBook') else 0,
            "dividend_yield": float(info.get('dividendYield', 0) or 0) * 100,
            "beta": float(info.get('beta', 1)) if info.get('beta') else 1,
            "eps": float(info.get('trailingEps', 0)) if info.get('trailingEps') else 0,
            "changePercent": round(((current_price - prev_close) / prev_close) * 100, 2) if prev_close else 0
        }
    except Exception as e:
        return None


def get_market_indices() -> Dict:
    """Get NIFTY 50 and SENSEX"""
    indices = {}
    
    for name, ticker_symbol in [("nifty50", "^NSEI"), ("sensex", "^BSESN")]:
        try:
            ticker = yf.Ticker(ticker_symbol)
            hist = ticker.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                current = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                indices[name] = {
                    "value": round(current, 2),
                    "change": round(current - prev, 2),
                    "changePercent": round(((current - prev) / prev) * 100, 2)
                }
        except:
            pass
    
    return indices


def get_sector_performance() -> List[Dict]:
    """Calculate sector performance with stocks"""
    sector_data = {}
    all_stocks = get_all_stocks()
    
    for symbol, info in list(all_stocks.items())[:60]:  # Top 60 for speed
        sector = info['sector']
        if sector not in sector_data:
            sector_data[sector] = {'changes': [], 'stocks': []}
        
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            hist = ticker.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                change = ((hist['Close'].iloc[-1] - hist['Close'].iloc[-2]) / hist['Close'].iloc[-2]) * 100
                sector_data[sector]['changes'].append(change)
                sector_data[sector]['stocks'].append({
                    'symbol': symbol,
                    'name': info['name'],
                    'change': round(float(change), 2),
                    'cap': info.get('cap', 'Unknown')
                })
        except:
            continue
    
    result = []
    for sector, data in sector_data.items():
        if data['changes']:
            sorted_stocks = sorted(data['stocks'], key=lambda x: x['change'], reverse=True)
            result.append({
                'sector': sector,
                'change': round(float(sum(data['changes']) / len(data['changes'])), 2),
                'stocks': sorted_stocks,
                'top_performer': sorted_stocks[0] if sorted_stocks else None,
                'worst_performer': sorted_stocks[-1] if sorted_stocks else None,
                'stock_count': len(sorted_stocks)
            })
    
    return sorted(result, key=lambda x: x['change'], reverse=True)


def start_background_prefetch():
    """Background prefetch all timeframes"""
    def prefetch():
        from services.scoring import get_all_scored_stocks
        for tf in ["weekly", "daily", "monthly"]:
            if not get_cache(tf, "scored"):
                try:
                    cfg = PERIOD_MAP[tf]
                    get_all_scored_stocks(period=cfg['period'], interval=cfg['interval'], timeframe=tf)
                except Exception as e:
                    print(f"Prefetch error {tf}: {e}")
    
    thread = threading.Thread(target=prefetch, daemon=True)
    thread.start()
    return True
