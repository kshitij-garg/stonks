"""
Price Alerts Service
Create, manage, and trigger price alerts with notifications
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import os
import threading

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'alerts.db')
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
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                target_price REAL NOT NULL,
                condition TEXT NOT NULL,
                created_at TEXT,
                triggered_at TEXT,
                is_active INTEGER DEFAULT 1,
                notes TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS alert_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_id INTEGER,
                symbol TEXT,
                triggered_price REAL,
                target_price REAL,
                condition TEXT,
                triggered_at TEXT,
                FOREIGN KEY (alert_id) REFERENCES alerts(id)
            )
        ''')
        
        conn.commit()
        conn.close()


def create_alert(symbol: str, target_price: float, condition: str = 'above', 
                 alert_type: str = 'price', notes: str = None) -> int:
    """
    Create a new price alert
    
    Args:
        symbol: Stock symbol
        target_price: Price to trigger alert
        condition: 'above' or 'below'
        alert_type: 'price', 'percent_change', 'volume'
        notes: Optional notes
    
    Returns:
        Alert ID
    """
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO alerts (symbol, alert_type, target_price, condition, created_at, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (symbol.upper(), alert_type, target_price, condition, 
              datetime.now().isoformat(), notes))
        
        conn.commit()
        alert_id = c.lastrowid
        conn.close()
        
        return alert_id


def get_active_alerts(symbol: str = None) -> List[Dict]:
    """Get all active alerts, optionally filtered by symbol"""
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        
        if symbol:
            c.execute('SELECT * FROM alerts WHERE is_active = 1 AND symbol = ? ORDER BY created_at DESC', 
                      (symbol.upper(),))
        else:
            c.execute('SELECT * FROM alerts WHERE is_active = 1 ORDER BY created_at DESC')
        
        rows = c.fetchall()
        conn.close()
        
        return [dict(r) for r in rows]


def delete_alert(alert_id: int) -> bool:
    """Delete an alert"""
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
        conn.commit()
        conn.close()
        return True


def deactivate_alert(alert_id: int) -> bool:
    """Deactivate an alert"""
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('UPDATE alerts SET is_active = 0, triggered_at = ? WHERE id = ?',
                  (datetime.now().isoformat(), alert_id))
        conn.commit()
        conn.close()
        return True


def check_alerts(current_prices: Dict[str, float]) -> List[Dict]:
    """
    Check all active alerts against current prices
    Returns list of triggered alerts
    """
    triggered = []
    alerts = get_active_alerts()
    
    for alert in alerts:
        symbol = alert['symbol']
        target = alert['target_price']
        condition = alert['condition']
        
        current = current_prices.get(symbol)
        if current is None:
            continue
        
        is_triggered = False
        if condition == 'above' and current >= target:
            is_triggered = True
        elif condition == 'below' and current <= target:
            is_triggered = True
        
        if is_triggered:
            # Record trigger
            with _db_lock:
                conn = get_db()
                c = conn.cursor()
                
                c.execute('''
                    INSERT INTO alert_history (alert_id, symbol, triggered_price, target_price, condition, triggered_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (alert['id'], symbol, current, target, condition, datetime.now().isoformat()))
                
                conn.commit()
                conn.close()
            
            # Deactivate alert
            deactivate_alert(alert['id'])
            
            triggered.append({
                **alert,
                'triggered_price': current,
                'triggered_at': datetime.now().isoformat()
            })
    
    return triggered


def get_alert_history(limit: int = 50) -> List[Dict]:
    """Get history of triggered alerts"""
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('SELECT * FROM alert_history ORDER BY triggered_at DESC LIMIT ?', (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


init_db()
