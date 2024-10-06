from functools import wraps
from hashlib import sha256
import json
from diskcache import Cache


cache = Cache('cache_dir')  # Initialize the disk cache

def cache_decorator(expire=3600):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key based on function name and parameters
            key = sha256(json.dumps((func.__name__, args, kwargs), sort_keys=True).encode()).hexdigest()
            data = cache.get(key)
            if not data:
                data = func(*args, **kwargs)
                cache.set(key, data, expire=expire)
            return data
        return wrapper
    return decorator


def delete_cache_decorator():
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = sha256(json.dumps((func.__name__, args, kwargs), sort_keys=True).encode()).hexdigest()
            cache.delete(key)
            return func(*args, **kwargs)
        return wrapper
    return decorator
