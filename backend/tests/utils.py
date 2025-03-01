import asyncio
import functools
from typing import Any, Callable, Coroutine


def async_to_sync(coroutine_func: Callable[..., Coroutine]) -> Callable[..., Any]:
    """
    Decorator to convert async functions to sync functions.
    Properly handles running the event loop for testing purposes.
    """

    @functools.wraps(coroutine_func)
    def wrapper(*args, **kwargs):
        # Use a new event loop to avoid "Event loop is closed" errors
        loop = asyncio.new_event_loop()
        try:
            return loop.run_until_complete(coroutine_func(*args, **kwargs))
        finally:
            loop.close()

    return wrapper


class AsyncTestClient:
    """Test utility for calling async functions safely in tests"""

    @staticmethod
    async def call_async(coroutine_func, *args, **kwargs):
        """Call an async function with proper await"""
        return await coroutine_func(*args, **kwargs)

    @staticmethod
    def call_sync(coroutine_func, *args, **kwargs):
        """Call an async function synchronously with proper event loop handling"""
        return async_to_sync(coroutine_func)(*args, **kwargs)
