"""
会话级数据缓存
为CLI工具提供单次命令执行期间的内存缓存
"""

from typing import Callable, Optional, Any
from functools import wraps
import hashlib


class SessionCache:
    """单次CLI会话数据缓存"""
    def __init__(self):
        self._cache: dict[str, Any] = {}

    def get(self, key: str) -> Optional[Any]:
        return self._cache.get(key)

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value

    def clear(self) -> None:
        self._cache.clear()

    def get_stats(self) -> dict[str, Any]:
        total_entries = len(self._cache)
        return {
            'total_entries': total_entries,
            'cache_keys': list(self._cache.keys())
        }


def _generate_cache_key(func_name: str, *args, **kwargs) -> str:
    """生成缓存键"""
    # 创建参数字符串
    args_str = str(args)
    kwargs_str = str(sorted(kwargs.items())) if kwargs else ""
    
    # 组合完整键字符串
    key_content = f"{func_name}:{args_str}:{kwargs_str}"
    
    # 使用SHA256生成哈希值，避免键过长
    hash_obj = hashlib.sha256(key_content.encode('utf-8'))
    return hash_obj.hexdigest()[:32]  # 取前32位作为键



def session_cache():
    """会话级缓存装饰器"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = _generate_cache_key(func.__name__, *args, **kwargs)
            cached_result = _session_cache.get(key)
            if cached_result is not None:
                return cached_result
            result = func(*args, **kwargs)
            _session_cache.set(key, result)
            return result
        return wrapper
    return decorator


# 全局会话缓存实例
_session_cache = SessionCache()

def clear_session_cache() -> None:
    _session_cache.clear()

def get_cache_stats() -> dict[str, Any]:
    return _session_cache.get_stats()

