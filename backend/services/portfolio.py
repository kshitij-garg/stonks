"""
Portfolio Tracking Service
Track holdings, calculate P&L, and analyze portfolio performance
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import os
import threading

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'portfolio.db')
_db_lock = threading.Lock()


def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_price REAL NOT NULL,
                buy_date TEXT,
                notes TEXT,
                UNIQUE(symbol)
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                type TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL,
                notes TEXT
            )
        ''')
        
        conn.commit()
        conn.close()


def add_holding(symbol: str, quantity: float, avg_price: float, buy_date: str = None) -> bool:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT OR REPLACE INTO holdings (symbol, quantity, avg_price, buy_date)
                VALUES (?, ?, ?, ?)
            ''', (symbol.upper(), quantity, avg_price, buy_date or datetime.now().strftime('%Y-%m-%d')))
            
            c.execute('''
                INSERT INTO transactions (symbol, type, quantity, price, date)
                VALUES (?, 'BUY', ?, ?, ?)
            ''', (symbol.upper(), quantity, avg_price, datetime.now().isoformat()))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding holding: {e}")
            return False
        finally:
            conn.close()


def update_holding(symbol: str, quantity: float, avg_price: float) -> bool:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            UPDATE holdings SET quantity = ?, avg_price = ? WHERE symbol = ?
        ''', (quantity, avg_price, symbol.upper()))
        conn.commit()
        conn.close()
        return True


def remove_holding(symbol: str) -> bool:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('DELETE FROM holdings WHERE symbol = ?', (symbol.upper(),))
        conn.commit()
        conn.close()
        return True


def get_holdings() -> List[Dict]:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM holdings ORDER BY symbol')
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_transactions(symbol: str = None, limit: int = 50) -> List[Dict]:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        
        if symbol:
            c.execute('SELECT * FROM transactions WHERE symbol = ? ORDER BY date DESC LIMIT ?', 
                      (symbol.upper(), limit))
        else:
            c.execute('SELECT * FROM transactions ORDER BY date DESC LIMIT ?', (limit,))
        
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_portfolio_summary(current_prices: Dict[str, float]) -> Dict:
    """Calculate portfolio summary with current prices"""
    holdings = get_holdings()
    
    total_invested = 0
    total_current = 0
    holdings_data = []
    
    for h in holdings:
        symbol = h['symbol']
        qty = h['quantity']
        avg = h['avg_price']
        current = current_prices.get(symbol, avg)
        
        invested = qty * avg
        current_val = qty * current
        pnl = current_val - invested
        pnl_pct = ((current - avg) / avg) * 100 if avg > 0 else 0
        
        total_invested += invested
        total_current += current_val
        
        holdings_data.append({
            **h,
            'current_price': current,
            'current_value': round(current_val, 2),
            'invested_value': round(invested, 2),
            'pnl': round(pnl, 2),
            'pnl_percent': round(pnl_pct, 2)
        })
    
    total_pnl = total_current - total_invested
    total_pnl_pct = ((total_current - total_invested) / total_invested) * 100 if total_invested > 0 else 0
    
    return {
        'holdings': holdings_data,
        'total_invested': round(total_invested, 2),
        'total_current': round(total_current, 2),
        'total_pnl': round(total_pnl, 2),
        'total_pnl_percent': round(total_pnl_pct, 2),
        'holdings_count': len(holdings_data)
    }


def get_portfolio_analytics(stock_data: Dict[str, Dict]) -> Dict:
    """
    Get advanced portfolio analytics including:
    - Sector allocation
    - Upside predictions based on recommendations
    - Risk assessment
    - Top gainers/losers
    """
    from services.stock_universe import get_all_stocks
    
    holdings = get_holdings()
    stock_universe = get_all_stocks()
    
    if not holdings:
        return {"error": "No holdings found"}
    
    # Calculate totals
    total_invested = 0
    total_current = 0
    holdings_with_data = []
    sector_allocation = {}
    
    for h in holdings:
        symbol = h['symbol']
        qty = h['quantity']
        avg = h['avg_price']
        
        # Get stock data from recommendation engine
        stock_info = stock_data.get(symbol, {})
        current = stock_info.get('price', avg)
        sector = stock_info.get('sector') or stock_universe.get(symbol, {}).get('sector', 'Unknown')
        
        invested = qty * avg
        current_val = qty * current
        pnl = current_val - invested
        pnl_pct = ((current - avg) / avg) * 100 if avg > 0 else 0
        
        total_invested += invested
        total_current += current_val
        
        # Recommendation-based upside
        recommendation = stock_info.get('recommendation', {})
        upside = recommendation.get('upside', 0) if isinstance(recommendation, dict) else 0
        action = recommendation.get('action', 'HOLD') if isinstance(recommendation, dict) else 'HOLD'
        confidence = recommendation.get('confidence', 50) if isinstance(recommendation, dict) else 50
        
        # Week prediction based on momentum
        week_return_hist = stock_info.get('returns', {}).get('1W', 0)
        momentum_score = stock_info.get('scores', {}).get('momentum', 50) if isinstance(stock_info.get('scores'), dict) else 50
        predicted_1w = round(upside * 0.15, 2)  # ~15% of total upside in 1 week
        
        holding_data = {
            **h,
            'current_price': round(current, 2),
            'current_value': round(current_val, 2),
            'invested_value': round(invested, 2),
            'pnl': round(pnl, 2),
            'pnl_percent': round(pnl_pct, 2),
            'sector': sector,
            'recommendation': action,
            'upside': round(upside, 2),
            'confidence': round(confidence, 0),
            'predicted_1w': predicted_1w,
            'predicted_1w_value': round(current_val * (1 + predicted_1w / 100), 2),
            'rsi': stock_info.get('rsi', 50),
            'macd_signal': stock_info.get('macd_signal', 'Neutral'),
            'score': stock_info.get('scores', {}).get('composite', 50) if isinstance(stock_info.get('scores'), dict) else 50
        }
        
        holdings_with_data.append(holding_data)
        
        # Sector allocation
        if sector not in sector_allocation:
            sector_allocation[sector] = {'value': 0, 'count': 0, 'stocks': []}
        sector_allocation[sector]['value'] += current_val
        sector_allocation[sector]['count'] += 1
        sector_allocation[sector]['stocks'].append(symbol)
    
    # Calculate sector percentages
    for sector in sector_allocation:
        sector_allocation[sector]['percentage'] = round(
            (sector_allocation[sector]['value'] / total_current) * 100, 2
        ) if total_current > 0 else 0
        sector_allocation[sector]['value'] = round(sector_allocation[sector]['value'], 2)
    
    # Sort holdings by various metrics
    top_gainers = sorted(holdings_with_data, key=lambda x: x['pnl_percent'], reverse=True)[:5]
    top_losers = sorted(holdings_with_data, key=lambda x: x['pnl_percent'])[:5]
    highest_upside = sorted(holdings_with_data, key=lambda x: x['upside'], reverse=True)[:5]
    best_recommendations = [h for h in holdings_with_data if h['recommendation'] in ['STRONG BUY', 'BUY']]
    sells_recommended = [h for h in holdings_with_data if h['recommendation'] in ['SELL', 'STRONG SELL']]
    
    # Calculate predicted portfolio value (1 week)
    predicted_1w_total = sum(h['predicted_1w_value'] for h in holdings_with_data)
    predicted_gain = predicted_1w_total - total_current
    predicted_gain_pct = ((predicted_1w_total - total_current) / total_current) * 100 if total_current > 0 else 0
    
    # Risk metrics
    high_rsi_stocks = [h for h in holdings_with_data if h['rsi'] > 70]
    low_rsi_stocks = [h for h in holdings_with_data if h['rsi'] < 30]
    
    # Concentration risk
    max_holding_pct = max((h['current_value'] / total_current) * 100 for h in holdings_with_data) if holdings_with_data else 0
    concentration_warning = max_holding_pct > 25
    
    return {
        'summary': {
            'total_invested': round(total_invested, 2),
            'total_current': round(total_current, 2),
            'total_pnl': round(total_current - total_invested, 2),
            'total_pnl_percent': round(((total_current - total_invested) / total_invested) * 100, 2) if total_invested > 0 else 0,
            'holdings_count': len(holdings_with_data)
        },
        'predictions': {
            'predicted_1w_value': round(predicted_1w_total, 2),
            'predicted_1w_gain': round(predicted_gain, 2),
            'predicted_1w_gain_percent': round(predicted_gain_pct, 2)
        },
        'sector_allocation': sector_allocation,
        'insights': {
            'top_gainers': top_gainers,
            'top_losers': top_losers,
            'highest_upside': highest_upside,
            'buy_recommendations': len(best_recommendations),
            'sell_recommendations': len(sells_recommended),
            'stocks_to_buy': [h['symbol'] for h in best_recommendations[:3]],
            'stocks_to_sell': [h['symbol'] for h in sells_recommended[:3]]
        },
        'risk': {
            'overbought_stocks': [h['symbol'] for h in high_rsi_stocks],
            'oversold_stocks': [h['symbol'] for h in low_rsi_stocks],
            'concentration_risk': concentration_warning,
            'max_holding_percent': round(max_holding_pct, 2)
        },
        'holdings': holdings_with_data
    }


def clear_all_holdings() -> bool:
    """Clear all holdings from portfolio"""
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('DELETE FROM holdings')
        conn.commit()
        conn.close()
        return True


init_db()

