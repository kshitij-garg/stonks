"""
Backtesting Service with SQLite Persistence
Tracks recommendation history and calculates returns
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import os

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'backtest.db')
_db_lock = threading.Lock()


def get_db_connection():
    """Get database connection, create db if needed"""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize database tables"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Recommendations history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                confidence REAL,
                price_at_rec REAL,
                dcf_value REAL,
                upside_target REAL,
                composite_score REAL,
                sector TEXT,
                UNIQUE(timestamp, symbol, timeframe)
            )
        ''')
        
        # Price tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                UNIQUE(timestamp, symbol)
            )
        ''')
        
        # Backtest results table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS backtest_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_date TEXT NOT NULL,
                period_days INTEGER,
                total_return REAL,
                buy_return REAL,
                strong_buy_return REAL,
                benchmark_return REAL,
                win_rate REAL,
                recommendations_count INTEGER
            )
        ''')
        
        conn.commit()
        conn.close()


def save_recommendations(stocks: List[Dict], timeframe: str):
    """Save current recommendations to database"""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for stock in stocks:
            rec = stock.get('recommendation', {})
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO recommendations 
                    (timestamp, timeframe, symbol, action, confidence, price_at_rec, 
                     dcf_value, upside_target, composite_score, sector)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    timestamp,
                    timeframe,
                    stock.get('symbol', ''),
                    rec.get('action', 'HOLD'),
                    rec.get('confidence', 0),
                    stock.get('price', 0),
                    stock.get('dcf', {}).get('intrinsic_value', 0),
                    rec.get('upside', 0),
                    stock.get('scores', {}).get('composite', 0),
                    stock.get('sector', '')
                ))
            except Exception as e:
                print(f"Error saving {stock.get('symbol')}: {e}")
        
        conn.commit()
        conn.close()


def save_current_prices(stocks: List[Dict]):
    """Save current prices for tracking"""
    timestamp = datetime.now().strftime('%Y-%m-%d')
    
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for stock in stocks:
            try:
                cursor.execute('''
                    INSERT OR REPLACE INTO price_history (timestamp, symbol, price)
                    VALUES (?, ?, ?)
                ''', (timestamp, stock.get('symbol', ''), stock.get('price', 0)))
            except:
                pass
        
        conn.commit()
        conn.close()


def get_recommendation_history(days: int = 30, symbol: str = None) -> List[Dict]:
    """Get recommendation history"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        if symbol:
            cursor.execute('''
                SELECT * FROM recommendations 
                WHERE timestamp >= ? AND symbol = ?
                ORDER BY timestamp DESC
            ''', (start_date, symbol))
        else:
            cursor.execute('''
                SELECT * FROM recommendations 
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (start_date,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]


def calculate_backtest_returns(days: int = 30) -> Dict:
    """Calculate returns for recommendations over a period"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Get recommendations from start date
        cursor.execute('''
            SELECT r.*, 
                   p1.price as start_price,
                   p2.price as end_price
            FROM recommendations r
            LEFT JOIN price_history p1 ON r.symbol = p1.symbol AND p1.timestamp = r.timestamp
            LEFT JOIN price_history p2 ON r.symbol = p2.symbol AND p2.timestamp = ?
            WHERE r.timestamp = ?
        ''', (end_date, start_date))
        
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return {
                "period_days": days,
                "no_data": True,
                "message": "No historical data available yet. Recommendations are being tracked."
            }
        
        # Calculate returns by action type
        results = {
            "period_days": days,
            "start_date": start_date,
            "end_date": end_date,
            "by_action": {},
            "total_recommendations": 0,
            "profitable_count": 0,
            "loss_count": 0,
            "avg_return": 0,
            "best_pick": None,
            "worst_pick": None,
            "detail": []
        }
        
        total_return = 0
        returns_list = []
        
        for row in rows:
            row_dict = dict(row)
            start_price = row_dict.get('start_price') or row_dict.get('price_at_rec')
            end_price = row_dict.get('end_price')
            
            if not start_price or not end_price:
                continue
            
            pct_return = ((end_price - start_price) / start_price) * 100
            action = row_dict.get('action', 'HOLD')
            
            if action not in results["by_action"]:
                results["by_action"][action] = {"count": 0, "total_return": 0, "returns": []}
            
            results["by_action"][action]["count"] += 1
            results["by_action"][action]["total_return"] += pct_return
            results["by_action"][action]["returns"].append(pct_return)
            
            results["total_recommendations"] += 1
            total_return += pct_return
            returns_list.append({
                "symbol": row_dict.get('symbol'),
                "action": action,
                "return": round(pct_return, 2),
                "start_price": round(start_price, 2),
                "end_price": round(end_price, 2)
            })
            
            if pct_return > 0:
                results["profitable_count"] += 1
            else:
                results["loss_count"] += 1
            
            if results["best_pick"] is None or pct_return > results["best_pick"]["return"]:
                results["best_pick"] = {"symbol": row_dict.get('symbol'), "return": round(pct_return, 2)}
            
            if results["worst_pick"] is None or pct_return < results["worst_pick"]["return"]:
                results["worst_pick"] = {"symbol": row_dict.get('symbol'), "return": round(pct_return, 2)}
        
        # Calculate averages
        if results["total_recommendations"] > 0:
            results["avg_return"] = round(total_return / results["total_recommendations"], 2)
            results["win_rate"] = round((results["profitable_count"] / results["total_recommendations"]) * 100, 1)
        
        for action in results["by_action"]:
            if results["by_action"][action]["count"] > 0:
                results["by_action"][action]["avg_return"] = round(
                    results["by_action"][action]["total_return"] / results["by_action"][action]["count"], 2
                )
        
        # Sort detail by return
        results["detail"] = sorted(returns_list, key=lambda x: x["return"], reverse=True)
        
        return results


def get_tracking_stats() -> Dict:
    """Get general tracking statistics"""
    with _db_lock:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Total recommendations
        cursor.execute('SELECT COUNT(*) as count FROM recommendations')
        total_recs = cursor.fetchone()['count']
        
        # Unique dates
        cursor.execute('SELECT COUNT(DISTINCT timestamp) as count FROM recommendations')
        unique_dates = cursor.fetchone()['count']
        
        # Latest recommendation date
        cursor.execute('SELECT MAX(timestamp) as latest FROM recommendations')
        latest = cursor.fetchone()['latest']
        
        # Actions breakdown
        cursor.execute('''
            SELECT action, COUNT(*) as count 
            FROM recommendations 
            GROUP BY action
        ''')
        action_breakdown = {row['action']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "total_recommendations": total_recs,
            "tracking_days": unique_dates,
            "latest_date": latest,
            "action_breakdown": action_breakdown
        }


# Initialize database on module load
init_database()
