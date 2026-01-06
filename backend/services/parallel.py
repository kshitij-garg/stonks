"""
Parallel Processing Service
Provides thread pool for concurrent operations
"""

import concurrent.futures
from typing import List, Callable, Any, Dict, Iterable
from functools import partial
import threading
import time


# Global thread pool
_executor = None
_executor_lock = threading.Lock()


def get_executor(max_workers: int = 10) -> concurrent.futures.ThreadPoolExecutor:
    """Get or create the global thread pool executor"""
    global _executor
    with _executor_lock:
        if _executor is None:
            _executor = concurrent.futures.ThreadPoolExecutor(
                max_workers=max_workers, 
                thread_name_prefix="stonks_worker"
            )
    return _executor


def parallel_map(
    func: Callable, 
    items: Iterable, 
    max_workers: int = 10,
    timeout: float = 60.0
) -> List[Any]:
    """
    Execute function on each item in parallel
    Returns list of results in same order as input
    
    Usage:
        results = parallel_map(fetch_stock, ['RELIANCE', 'TCS', 'INFY'])
    """
    executor = get_executor(max_workers)
    futures = {executor.submit(func, item): i for i, item in enumerate(items)}
    results = [None] * len(futures)
    
    for future in concurrent.futures.as_completed(futures, timeout=timeout):
        idx = futures[future]
        try:
            results[idx] = future.result()
        except Exception as e:
            print(f"[Parallel] Error processing item {idx}: {e}")
            results[idx] = None
    
    return results


def parallel_batch(
    func: Callable,
    items: List[Any],
    batch_size: int = 20,
    max_workers: int = 10,
    delay_between_batches: float = 0.5
) -> List[Any]:
    """
    Process items in batches with parallel execution within each batch
    Useful for rate-limited APIs
    """
    results = []
    
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_results = parallel_map(func, batch, max_workers)
        results.extend(batch_results)
        
        # Rate limiting delay between batches
        if i + batch_size < len(items):
            time.sleep(delay_between_batches)
    
    return results


def parallel_dict_map(
    func: Callable,
    items: Dict[str, Any],
    max_workers: int = 10
) -> Dict[str, Any]:
    """
    Execute function on each dict value in parallel
    Returns dict with same keys and processed values
    """
    keys = list(items.keys())
    values = list(items.values())
    
    processed = parallel_map(func, values, max_workers)
    
    return dict(zip(keys, processed))


class AsyncTaskQueue:
    """Simple async task queue for background operations"""
    
    def __init__(self, max_workers: int = 5):
        self._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="async_task"
        )
        self._pending = {}
        self._lock = threading.Lock()
    
    def submit(self, task_id: str, func: Callable, *args, **kwargs) -> str:
        """Submit a task for background execution"""
        with self._lock:
            if task_id in self._pending:
                return task_id  # Task already running
            
            future = self._executor.submit(func, *args, **kwargs)
            self._pending[task_id] = future
            
            # Auto-cleanup when done
            future.add_done_callback(lambda f: self._cleanup(task_id))
            
        return task_id
    
    def _cleanup(self, task_id: str):
        with self._lock:
            self._pending.pop(task_id, None)
    
    def is_running(self, task_id: str) -> bool:
        with self._lock:
            return task_id in self._pending
    
    def get_result(self, task_id: str, timeout: float = None) -> Any:
        with self._lock:
            future = self._pending.get(task_id)
        
        if future is None:
            return None
        
        try:
            return future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            return None
    
    def cancel(self, task_id: str) -> bool:
        with self._lock:
            future = self._pending.get(task_id)
        
        if future:
            return future.cancel()
        return False


# Global async task queue
_task_queue = AsyncTaskQueue(max_workers=5)


def submit_async_task(task_id: str, func: Callable, *args, **kwargs) -> str:
    """Submit a task to the global async queue"""
    return _task_queue.submit(task_id, func, *args, **kwargs)


def is_task_running(task_id: str) -> bool:
    """Check if an async task is still running"""
    return _task_queue.is_running(task_id)
