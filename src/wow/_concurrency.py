"""Lock and sleep primitives under names that ``scripts/unasync.py`` can swap.

Async code imports ``AsyncLock`` and ``async_sleep``; the generated sync code imports ``Lock`` and ``sleep``.
"""

import threading
import time

import anyio

__all__ = ["AsyncLock", "Lock", "async_sleep", "sleep"]

AsyncLock = anyio.Lock
Lock = threading.Lock
sleep = time.sleep


async def async_sleep(seconds: float) -> None:
    """Sleep without blocking the event loop, under asyncio or trio."""
    await anyio.sleep(seconds)
