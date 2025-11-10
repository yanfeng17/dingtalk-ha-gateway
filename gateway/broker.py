"""Simple asyncio-based pub/sub broker for message fanout."""

from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator, Dict, Set


class MessageBroker:
    """Fan out events to multiple asyncio subscribers."""

    def __init__(self) -> None:
        self._subscribers: Set[asyncio.Queue] = set()
        self._lock = asyncio.Lock()
        self._loop: asyncio.AbstractEventLoop | None = None

    def attach_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def subscribe(self, max_queue: int = 100) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=max_queue)
        async with self._lock:
            self._subscribers.add(queue)
        return queue

    async def unsubscribe(self, queue: asyncio.Queue) -> None:
        async with self._lock:
            self._subscribers.discard(queue)

    def publish(self, event: Dict[str, Any]) -> None:
        """Publish event to all subscribers (sync version for backward compatibility)."""
        if not self._subscribers:
            return
        if self._loop is None:
            raise RuntimeError("Event loop not attached")

        for queue in list(self._subscribers):
            asyncio.run_coroutine_threadsafe(self._safe_put(queue, event), self._loop)
    
    async def async_publish(self, event: Dict[str, Any]) -> None:
        """Publish event to all subscribers asynchronously (faster)."""
        if not self._subscribers:
            return
        
        # Use asyncio.gather for parallel puts (faster than sequential)
        await asyncio.gather(
            *[self._safe_put(queue, event) for queue in list(self._subscribers)],
            return_exceptions=True
        )

    async def _safe_put(self, queue: asyncio.Queue, event: Dict[str, Any]) -> None:
        try:
            await queue.put(event)
        except asyncio.QueueFull:
            await queue.get()
            await queue.put(event)
