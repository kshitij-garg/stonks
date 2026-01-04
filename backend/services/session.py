"""
Session Management Service
Provides simple token-based session for portfolio isolation
"""

import sqlite3
from datetime import datetime, timedelta
import os
import secrets
import threading

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'sessions.db')
_db_lock = threading.Lock()

# Session lifetime in days
SESSION_LIFETIME_DAYS = 30


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
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_token TEXT UNIQUE NOT NULL,
                created_at TEXT,
                last_access TEXT,
                expires_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()


def create_session() -> str:
    """Create a new session and return the token"""
    token = secrets.token_urlsafe(32)
    now = datetime.now()
    expires = now + timedelta(days=SESSION_LIFETIME_DAYS)
    
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO sessions (session_token, created_at, last_access, expires_at)
            VALUES (?, ?, ?, ?)
        ''', (token, now.isoformat(), now.isoformat(), expires.isoformat()))
        
        conn.commit()
        conn.close()
    
    return token


def validate_session(token: str) -> bool:
    """Validate a session token"""
    if not token:
        return False
    
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        
        c.execute('''
            SELECT * FROM sessions 
            WHERE session_token = ? AND expires_at > ?
        ''', (token, datetime.now().isoformat()))
        
        row = c.fetchone()
        
        if row:
            # Update last access
            c.execute('''
                UPDATE sessions SET last_access = ? WHERE session_token = ?
            ''', (datetime.now().isoformat(), token))
            conn.commit()
        
        conn.close()
        return row is not None


def get_or_create_session(token: str = None) -> str:
    """Get existing session or create new one"""
    if token and validate_session(token):
        return token
    return create_session()


def cleanup_expired_sessions():
    """Remove expired sessions"""
    with _db_lock:
        conn = get_db()
        c = conn.cursor()
        c.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now().isoformat(),))
        conn.commit()
        conn.close()


init_db()
