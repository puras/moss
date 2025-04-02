from asgiref.sync import async_to_sync
from functools import wraps
import asyncio

def async_route(f):
    """异步路由装饰器，用于包装异步视图函数"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        return async_to_sync(f)(*args, **kwargs)
    return wrapper

def run_async(func):
    """异步执行装饰器，用于包装异步服务函数"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(func(*args, **kwargs))
        finally:
            loop.close()
    return wrapper