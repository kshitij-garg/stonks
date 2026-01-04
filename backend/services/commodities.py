"""
Commodities Service - Gold, Silver, Crude Oil
Fetches MCX commodity prices and historical data
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional


# Commodity tickers
COMMODITIES = {
    "GOLD": {
        "yahoo_ticker": "GC=F",  # Gold Futures
        "mcx_ticker": "GOLD",
        "name": "Gold",
        "unit": "per 10g",
        "category": "Precious Metals"
    },
    "SILVER": {
        "yahoo_ticker": "SI=F",  # Silver Futures  
        "mcx_ticker": "SILVER",
        "name": "Silver",
        "unit": "per kg",
        "category": "Precious Metals"
    },
    "CRUDEOIL": {
        "yahoo_ticker": "CL=F",  # Crude Oil Futures
        "mcx_ticker": "CRUDEOIL",
        "name": "Crude Oil",
        "unit": "per barrel",
        "category": "Energy"
    },
    "NATURALGAS": {
        "yahoo_ticker": "NG=F",
        "mcx_ticker": "NATURALGAS",
        "name": "Natural Gas",
        "unit": "per mmBtu",
        "category": "Energy"
    },
    "COPPER": {
        "yahoo_ticker": "HG=F",
        "mcx_ticker": "COPPER",
        "name": "Copper",
        "unit": "per kg",
        "category": "Base Metals"
    }
}

# USD to INR approximate rate (updated when fetching)
USD_INR_RATE = 83.0


def get_usd_inr_rate() -> float:
    """Get current USD/INR exchange rate"""
    global USD_INR_RATE
    try:
        ticker = yf.Ticker("USDINR=X")
        hist = ticker.history(period="1d")
        if not hist.empty:
            USD_INR_RATE = float(hist['Close'].iloc[-1])
    except:
        pass
    return USD_INR_RATE


def fetch_commodity_data(symbol: str, period: str = "6mo") -> Optional[Dict]:
    """Fetch commodity price and history"""
    
    commodity = COMMODITIES.get(symbol.upper())
    if not commodity:
        return None
    
    try:
        ticker = yf.Ticker(commodity['yahoo_ticker'])
        hist = ticker.history(period=period)
        
        if hist.empty:
            return None
        
        # Get USD/INR rate for conversion
        usd_inr = get_usd_inr_rate()
        
        # Current price
        current_usd = float(hist['Close'].iloc[-1])
        prev_usd = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_usd
        
        # Convert to INR (approximate - MCX prices differ slightly)
        current_inr = current_usd * usd_inr
        prev_inr = prev_usd * usd_inr
        
        # Gold/Silver specific conversions
        if symbol.upper() == "GOLD":
            # Yahoo gives per oz, MCX is per 10g
            # 1 oz = 31.1g, so 10g = oz * (10/31.1)
            current_inr = current_inr * (10 / 31.1)
            prev_inr = prev_inr * (10 / 31.1)
        elif symbol.upper() == "SILVER":
            # Yahoo gives per oz, MCX is per kg
            # 1 oz = 31.1g, so 1kg = oz * (1000/31.1)
            current_inr = current_inr * (1000 / 31.1)
            prev_inr = prev_inr * (1000 / 31.1)
        
        change = current_inr - prev_inr
        change_pct = ((current_inr - prev_inr) / prev_inr) * 100 if prev_inr else 0
        
        # Calculate returns
        returns = {}
        if len(hist) >= 5:
            week_ago = float(hist['Close'].iloc[-5])
            returns['1W'] = ((current_usd - week_ago) / week_ago) * 100
        if len(hist) >= 22:
            month_ago = float(hist['Close'].iloc[-22])
            returns['1M'] = ((current_usd - month_ago) / month_ago) * 100
        if len(hist) >= 66:
            three_month = float(hist['Close'].iloc[-66])
            returns['3M'] = ((current_usd - three_month) / three_month) * 100
        
        # Historical data for charts
        chart_data = []
        for idx, row in hist.iterrows():
            price = float(row['Close'])
            if symbol.upper() == "GOLD":
                price = price * usd_inr * (10 / 31.1)
            elif symbol.upper() == "SILVER":
                price = price * usd_inr * (1000 / 31.1)
            else:
                price = price * usd_inr
            
            chart_data.append({
                "date": idx.strftime("%Y-%m-%d"),
                "open": round(float(row['Open']) * usd_inr, 2),
                "high": round(float(row['High']) * usd_inr, 2),
                "low": round(float(row['Low']) * usd_inr, 2),
                "close": round(price, 2),
                "volume": int(row['Volume']) if not pd.isna(row['Volume']) else 0
            })
        
        return {
            "symbol": symbol.upper(),
            "name": commodity['name'],
            "category": commodity['category'],
            "unit": commodity['unit'],
            "price": round(current_inr, 2),
            "price_usd": round(current_usd, 2),
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "returns": returns,
            "high_52w": round(hist['High'].max() * usd_inr, 2),
            "low_52w": round(hist['Low'].min() * usd_inr, 2),
            "chart_data": chart_data[-90:],  # Last 90 days for chart
            "usd_inr_rate": round(usd_inr, 2)
        }
        
    except Exception as e:
        print(f"Commodity error {symbol}: {e}")
        return None


def get_all_commodities() -> List[Dict]:
    """Get all commodity prices"""
    results = []
    for symbol in COMMODITIES.keys():
        data = fetch_commodity_data(symbol, period="3mo")
        if data:
            results.append(data)
    return results


def get_market_summary() -> Dict:
    """Get market summary including indices and commodities"""
    summary = {
        "indices": {},
        "commodities": {},
        "currency": {}
    }
    
    # Indices
    for name, ticker in [("NIFTY50", "^NSEI"), ("SENSEX", "^BSESN"), ("BANKNIFTY", "^NSEBANK")]:
        try:
            t = yf.Ticker(ticker)
            hist = t.history(period="5d")
            if not hist.empty and len(hist) >= 2:
                current = float(hist['Close'].iloc[-1])
                prev = float(hist['Close'].iloc[-2])
                summary["indices"][name] = {
                    "value": round(current, 2),
                    "change": round(current - prev, 2),
                    "change_percent": round(((current - prev) / prev) * 100, 2)
                }
        except:
            pass
    
    # Key commodities
    for symbol in ["GOLD", "SILVER", "CRUDEOIL"]:
        data = fetch_commodity_data(symbol, "1mo")
        if data:
            summary["commodities"][symbol] = {
                "name": data['name'],
                "price": data['price'],
                "unit": data['unit'],
                "change_percent": data['change_percent']
            }
    
    # USD/INR
    try:
        t = yf.Ticker("USDINR=X")
        hist = t.history(period="5d")
        if not hist.empty and len(hist) >= 2:
            current = float(hist['Close'].iloc[-1])
            prev = float(hist['Close'].iloc[-2])
            summary["currency"]["USDINR"] = {
                "value": round(current, 4),
                "change": round(current - prev, 4),
                "change_percent": round(((current - prev) / prev) * 100, 2)
            }
    except:
        pass
    
    return summary
