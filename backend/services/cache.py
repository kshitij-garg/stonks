"""
Caching Service with LRU + TTL Support
Provides in-memory caching for expensive operations
"""

import time
import threading
import hashlib
import json
from collections import OrderedDict
from typing import Any, Optional, Callable
from functools import wraps


class TTLCache:
    """Thread-safe LRU cache with TTL (Time To Live) support"""
    
    def __init__(self, maxsize: int = 1000, default_ttl: int = 300):
        """
        Args:
            maxsize: Maximum number of items in cache
            default_ttl: Default time-to-live in seconds (default 5 min)
        """
        self._cache = OrderedDict()
        self._ttls = {}
        self._maxsize = maxsize
        self._default_ttl = default_ttl
        self._lock = threading.RLock()
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache, returns None if expired or not found"""
        with self._lock:
            if key not in self._cache:
                self._misses += 1
                return None
            
            # Check if expired
            if time.time() > self._ttls.get(key, 0):
                self._delete(key)
                self._misses += 1
                return None
            
            # Move to end (most recently used)
            self._cache.move_to_end(key)
            self._hits += 1
            return self._cache[key]
    
    def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set item in cache with optional custom TTL"""
        with self._lock:
            # Evict oldest if at capacity
            while len(self._cache) >= self._maxsize:
                oldest_key = next(iter(self._cache))
                self._delete(oldest_key)
            
            self._cache[key] = value
            self._ttls[key] = time.time() + (ttl or self._default_ttl)
            self._cache.move_to_end(key)
    
    def _delete(self, key: str) -> None:
        """Internal delete without lock"""
        self._cache.pop(key, None)
        self._ttls.pop(key, None)
    
    def delete(self, key: str) -> None:
        """Delete item from cache"""
        with self._lock:
            self._delete(key)
    
    def clear(self) -> None:
        """Clear entire cache"""
        with self._lock:
            self._cache.clear()
            self._ttls.clear()
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching pattern (contains)"""
        with self._lock:
            keys_to_delete = [k for k in self._cache if pattern in k]
            for key in keys_to_delete:
                self._delete(key)
            return len(keys_to_delete)
    
    def stats(self) -> dict:
        """Get cache statistics"""
        with self._lock:
            total = self._hits + self._misses
            return {
                "size": len(self._cache),
                "maxsize": self._maxsize,
                "hits": self._hits,
                "misses": self._misses,
                "hit_rate": round(self._hits / total * 100, 1) if total > 0 else 0
            }


# Global cache instances
_stock_cache = TTLCache(maxsize=500, default_ttl=300)  # 5 min for stock data
_api_cache = TTLCache(maxsize=100, default_ttl=120)   # 2 min for API responses
_indicator_cache = TTLCache(maxsize=200, default_ttl=600)  # 10 min for indicators


def get_stock_cache() -> TTLCache:
    return _stock_cache


def get_api_cache() -> TTLCache:
    return _api_cache


def get_indicator_cache() -> TTLCache:
    return _indicator_cache


def make_cache_key(*args, **kwargs) -> str:
    """Generate a unique cache key from arguments"""
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(cache: TTLCache = None, ttl: int = None, key_prefix: str = ""):
    """
    Decorator to cache function results
    
    Usage:
        @cached(cache=get_stock_cache(), ttl=300, key_prefix="stock_")
        def get_stock_info(symbol):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            target_cache = cache or _api_cache
            cache_key = f"{key_prefix}{func.__name__}_{make_cache_key(*args, **kwargs)}"
            
            # Try to get from cache
            result = target_cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            if result is not None:
                target_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


def invalidate_stock_cache(symbol: str = None) -> int:
    """Invalidate stock cache, optionally for specific symbol"""
    if symbol:
        return _stock_cache.invalidate_pattern(symbol)
    else:
        _stock_cache.clear()
        return -1


def get_all_cache_stats() -> dict:
    """Get stats for all caches"""
    return {
        "stock_cache": _stock_cache.stats(),
        "api_cache": _api_cache.stats(),
        "indicator_cache": _indicator_cache.stats()
    }
