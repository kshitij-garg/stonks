"""
Watchlist Service - User stock watchlists with SQLite persistence
"""

import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import os
import threading

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'watchlist.db')
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
            CREATE TABLE IF NOT EXISTS watchlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS watchlist_stocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                watchlist_id INTEGER,
                symbol TEXT NOT NULL,
                added_at TEXT,
                added_price REAL,
                notes TEXT,
                FOREIGN KEY (watchlist_id) REFERENCES watchlists(id),
                UNIQUE(watchlist_id, symbol)
            )
        ''')
        
        # Default watchlist
        c.execute("INSERT OR IGNORE INTO watchlists (id, name, created_at) VALUES (1, 'Default', ?)", 
                  (datetime.now().isoformat(),))
        
        conn.commit()
        conn.close()


def get_watchlists() -> List[Dict]:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            SELECT w.*, COUNT(ws.id) as stock_count 
            FROM watchlists w 
            LEFT JOIN watchlist_stocks ws ON w.id = ws.watchlist_id
            GROUP BY w.id
        ''')
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def get_watchlist_stocks(watchlist_id: int = 1) -> List[Dict]:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('''
            SELECT * FROM watchlist_stocks WHERE watchlist_id = ? ORDER BY added_at DESC
        ''', (watchlist_id,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]


def add_to_watchlist(symbol: str, watchlist_id: int = 1, price: float = None, notes: str = None) -> bool:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        try:
            c.execute('''
                INSERT OR REPLACE INTO watchlist_stocks (watchlist_id, symbol, added_at, added_price, notes)
                VALUES (?, ?, ?, ?, ?)
            ''', (watchlist_id, symbol.upper(), datetime.now().isoformat(), price, notes))
            conn.commit()
            return True
        except:
            return False
        finally:
            conn.close()


def remove_from_watchlist(symbol: str, watchlist_id: int = 1) -> bool:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('DELETE FROM watchlist_stocks WHERE watchlist_id = ? AND symbol = ?', 
                  (watchlist_id, symbol.upper()))
        conn.commit()
        conn.close()
        return True


def create_watchlist(name: str) -> int:
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('INSERT INTO watchlists (name, created_at) VALUES (?, ?)', 
                  (name, datetime.now().isoformat()))
        conn.commit()
        id = c.lastrowid
        conn.close()
        return id


init_db()
