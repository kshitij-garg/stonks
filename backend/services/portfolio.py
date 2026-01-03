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


init_db()
