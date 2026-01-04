"""
Fundamentals Service
Quarterly results, balance sheet, and financial ratios
"""

import yfinance as yf
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


def safe_float(val, default=0.0):
    if val is None or pd.isna(val):
        return default
    try:
        return float(val)
    except:
        return default


def get_quarterly_results(symbol: str) -> Dict:
    """Get quarterly financial results"""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        
        # Quarterly financials
        quarterly = ticker.quarterly_financials
        if quarterly is None or quarterly.empty:
            return {"error": "No quarterly data available"}
        
        results = []
        for col in quarterly.columns[:8]:  # Last 8 quarters
            quarter_data = {
                "quarter": col.strftime("%b %Y") if hasattr(col, 'strftime') else str(col),
                "revenue": safe_float(quarterly.loc['Total Revenue', col]) if 'Total Revenue' in quarterly.index else 0,
                "net_income": safe_float(quarterly.loc['Net Income', col]) if 'Net Income' in quarterly.index else 0,
                "operating_income": safe_float(quarterly.loc['Operating Income', col]) if 'Operating Income' in quarterly.index else 0,
                "gross_profit": safe_float(quarterly.loc['Gross Profit', col]) if 'Gross Profit' in quarterly.index else 0,
            }
            
            # Calculate margins
            if quarter_data['revenue'] > 0:
                quarter_data['net_margin'] = round((quarter_data['net_income'] / quarter_data['revenue']) * 100, 2)
                quarter_data['operating_margin'] = round((quarter_data['operating_income'] / quarter_data['revenue']) * 100, 2)
            else:
                quarter_data['net_margin'] = 0
                quarter_data['operating_margin'] = 0
            
            results.append(quarter_data)
        
        # QoQ and YoY growth
        if len(results) >= 2:
            results[0]['revenue_qoq'] = round(
                ((results[0]['revenue'] - results[1]['revenue']) / results[1]['revenue']) * 100, 2
            ) if results[1]['revenue'] > 0 else 0
        
        if len(results) >= 5:
            results[0]['revenue_yoy'] = round(
                ((results[0]['revenue'] - results[4]['revenue']) / results[4]['revenue']) * 100, 2
            ) if results[4]['revenue'] > 0 else 0
        
        return {
            "symbol": symbol,
            "quarters": results,
            "latest": results[0] if results else None
        }
        
    except Exception as e:
        return {"error": str(e)}


def get_balance_sheet(symbol: str) -> Dict:
    """Get balance sheet data"""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        
        bs = ticker.quarterly_balance_sheet
        if bs is None or bs.empty:
            return {"error": "No balance sheet data"}
        
        latest = bs.iloc[:, 0]  # Most recent
        previous = bs.iloc[:, 1] if len(bs.columns) > 1 else latest
        
        def get_item(name, df):
            return safe_float(df.get(name, 0))
        
        data = {
            "symbol": symbol,
            "date": bs.columns[0].strftime("%Y-%m-%d") if hasattr(bs.columns[0], 'strftime') else str(bs.columns[0]),
            "current": {
                "total_assets": get_item('Total Assets', latest),
                "total_liabilities": get_item('Total Liabilities Net Minority Interest', latest),
                "total_equity": get_item('Stockholders Equity', latest),
                "cash": get_item('Cash And Cash Equivalents', latest),
                "total_debt": get_item('Total Debt', latest),
                "current_assets": get_item('Current Assets', latest),
                "current_liabilities": get_item('Current Liabilities', latest),
            },
            "previous": {
                "total_assets": get_item('Total Assets', previous),
                "total_equity": get_item('Stockholders Equity', previous),
            }
        }
        
        # Calculate ratios
        ca = data['current']['current_assets']
        cl = data['current']['current_liabilities']
        ta = data['current']['total_assets']
        te = data['current']['total_equity']
        td = data['current']['total_debt']
        
        data['ratios'] = {
            "current_ratio": round(ca / cl, 2) if cl > 0 else 0,
            "debt_to_equity": round(td / te, 2) if te > 0 else 0,
            "debt_to_assets": round(td / ta, 2) if ta > 0 else 0,
            "equity_ratio": round(te / ta, 2) if ta > 0 else 0,
        }
        
        return data
        
    except Exception as e:
        return {"error": str(e)}


def get_cash_flow(symbol: str) -> Dict:
    """Get cash flow statement"""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        
        cf = ticker.quarterly_cashflow
        if cf is None or cf.empty:
            return {"error": "No cash flow data"}
        
        results = []
        for col in cf.columns[:4]:  # Last 4 quarters
            quarter_data = {
                "quarter": col.strftime("%b %Y") if hasattr(col, 'strftime') else str(col),
                "operating_cash_flow": safe_float(cf.loc['Operating Cash Flow', col]) if 'Operating Cash Flow' in cf.index else 0,
                "investing_cash_flow": safe_float(cf.loc['Investing Cash Flow', col]) if 'Investing Cash Flow' in cf.index else 0,
                "financing_cash_flow": safe_float(cf.loc['Financing Cash Flow', col]) if 'Financing Cash Flow' in cf.index else 0,
                "free_cash_flow": safe_float(cf.loc['Free Cash Flow', col]) if 'Free Cash Flow' in cf.index else 0,
                "capex": safe_float(cf.loc['Capital Expenditure', col]) if 'Capital Expenditure' in cf.index else 0,
            }
            results.append(quarter_data)
        
        return {
            "symbol": symbol,
            "quarters": results,
            "latest": results[0] if results else None
        }
        
    except Exception as e:
        return {"error": str(e)}


def get_peer_comparison(symbol: str, peers: List[str] = None) -> Dict:
    """Compare stock with its peers"""
    from services.stock_universe import get_all_stocks
    
    all_stocks = get_all_stocks()
    stock_info = all_stocks.get(symbol.upper())
    
    if not stock_info:
        return {"error": "Stock not found"}
    
    sector = stock_info.get('sector', 'Unknown')
    
    # Find peers in same sector
    if not peers:
        peers = [s for s, info in all_stocks.items() 
                 if info.get('sector') == sector and s != symbol.upper()][:5]
    
    comparison = []
    symbols_to_compare = [symbol.upper()] + peers[:5]
    
    for sym in symbols_to_compare:
        try:
            ticker = yf.Ticker(f"{sym}.NS")
            info = ticker.info
            
            comparison.append({
                "symbol": sym,
                "name": all_stocks.get(sym, {}).get('name', sym),
                "price": safe_float(info.get('regularMarketPrice', 0)),
                "pe_ratio": safe_float(info.get('trailingPE', 0)),
                "pb_ratio": safe_float(info.get('priceToBook', 0)),
                "market_cap": safe_float(info.get('marketCap', 0)),
                "dividend_yield": safe_float(info.get('dividendYield', 0)) * 100,
                "roe": safe_float(info.get('returnOnEquity', 0)) * 100,
                "debt_to_equity": safe_float(info.get('debtToEquity', 0)),
                "is_target": sym == symbol.upper()
            })
        except:
            continue
    
    # Calculate sector averages
    if len(comparison) > 1:
        metrics = ['pe_ratio', 'pb_ratio', 'dividend_yield', 'roe', 'debt_to_equity']
        averages = {}
        for metric in metrics:
            values = [c[metric] for c in comparison if c[metric] > 0]
            averages[metric] = round(sum(values) / len(values), 2) if values else 0
    else:
        averages = {}
    
    return {
        "symbol": symbol,
        "sector": sector,
        "peers": comparison,
        "sector_averages": averages
    }


def get_full_fundamentals(symbol: str) -> Dict:
    """Get comprehensive fundamental analysis"""
    return {
        "quarterly_results": get_quarterly_results(symbol),
        "balance_sheet": get_balance_sheet(symbol),
        "cash_flow": get_cash_flow(symbol),
        "peer_comparison": get_peer_comparison(symbol)
    }
