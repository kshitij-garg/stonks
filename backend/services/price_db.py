"""
Historical Price Database
SQLite storage for historical prices - no refetching of past data
"""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'prices.db')
_db_lock = threading.Lock()


def get_db_connection():
    """Get database connection"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_price_database():
    """Initialize price database tables"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Historical OHLCV data
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                date TEXT NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                UNIQUE(symbol, date)
            )
        ''')
        
        # Index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_symbol_date ON price_history(symbol, date)
        ''')
        
        # Last update tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_status (
                symbol TEXT PRIMARY KEY,
                last_sync TEXT,
                earliest_date TEXT,
                latest_date TEXT
            )
        ''')
        
        conn.commit()
        conn.close()


def store_price_data(symbol: str, df: pd.DataFrame):
    """Store price data to database"""
    if df is None or df.empty:
        return False
    
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            for _, row in df.iterrows():
                date_str = row.get('Date', str(row.name))
                if isinstance(date_str, pd.Timestamp):
                    date_str = date_str.strftime('%Y-%m-%d')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO price_history 
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    str(date_str),
                    float(row.get('Open', 0)),
                    float(row.get('High', 0)),
                    float(row.get('Low', 0)),
                    float(row.get('Close', 0)),
                    int(row.get('Volume', 0))
                ))
            
            # Update sync status
            cursor.execute('''
                INSERT OR REPLACE INTO sync_status (symbol, last_sync, earliest_date, latest_date)
                VALUES (?, ?, ?, ?)
            ''', (
                symbol,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                df['Date'].min() if 'Date' in df.columns else str(df.index.min()),
                df['Date'].max() if 'Date' in df.columns else str(df.index.max())
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error storing {symbol}: {e}")
            return False
        finally:
            conn.close()


def get_stored_prices(symbol: str, start_date: str = None, end_date: str = None) -> Optional[pd.DataFrame]:
    """Get stored price data for a symbol"""
    with _db_lock:
        conn = get_db_connection()
        
        query = "SELECT date, open, high, low, close, volume FROM price_history WHERE symbol = ?"
        params = [symbol]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        
        query += " ORDER BY date ASC"
        
        try:
            df = pd.read_sql_query(query, conn, params=params)
            conn.close()
            
            if df.empty:
                return None
            
            df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
            return df
        except Exception as e:
            print(f"Error reading {symbol}: {e}")
            conn.close()
            return None


def get_sync_status(symbol: str = None) -> Dict:
    """Get sync status for one or all symbols"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if symbol:
            cursor.execute("SELECT * FROM sync_status WHERE symbol = ?", (symbol,))
            row = cursor.fetchone()
            conn.close()
            return dict(row) if row else None
        else:
            cursor.execute("SELECT * FROM sync_status")
            rows = cursor.fetchall()
            conn.close()
            return {row['symbol']: dict(row) for row in rows}


def needs_sync(symbol: str, max_age_hours: int = 12) -> bool:
    """Check if symbol needs data sync"""
    status = get_sync_status(symbol)
    if not status:
        return True
    
    last_sync = datetime.strptime(status['last_sync'], '%Y-%m-%d %H:%M:%S')
    age = (datetime.now() - last_sync).total_seconds() / 3600
    return age > max_age_hours


def get_database_stats() -> Dict:
    """Get statistics about stored data"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(DISTINCT symbol) as symbols FROM price_history")
        symbols = cursor.fetchone()['symbols']
        
        cursor.execute("SELECT COUNT(*) as records FROM price_history")
        records = cursor.fetchone()['records']
        
        cursor.execute("SELECT MIN(date) as earliest, MAX(date) as latest FROM price_history")
        dates = cursor.fetchone()
        
        conn.close()
        
        return {
            "symbols_stored": symbols,
            "total_records": records,
            "earliest_date": dates['earliest'],
            "latest_date": dates['latest']
        }


# Initialize database on module load
init_price_database()
