"""Gateway manager that bridges DingTalk events to API consumers."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, Union

from .broker import MessageBroker
from .config import GatewayConfig
from .events import IncomingMessageEvent, OutgoingMessageRequest

logger = logging.getLogger(__name__)


class GatewayManager:
    """Coordinates the DingTalk client and exposes async helpers for the API layer."""

    def __init__(self, config: GatewayConfig | None = None) -> None:
        self.config = config or GatewayConfig.load()
        self._loop: asyncio.AbstractEventLoop | None = None
        self._broker = MessageBroker()
        self._client: Union[Any, None] = None
        self.channel_type = self.config.channel_type

    async def start(self) -> None:
        if self._loop:
            return
        self._loop = asyncio.get_running_loop()
        self._broker.attach_loop(self._loop)
        
        # Initialize DingTalk client
        await self._start_dingtalk()
        
        logger.info(f"Gateway manager started with channel: {self.config.channel_type}")
        logger.info("Message pipeline optimized for low latency")

    async def _start_dingtalk(self) -> None:
        """Initialize DingTalk client."""
        from .dingtalk_client import DingTalkClient
        
        if not self.config.dingtalk_client_id or not self.config.dingtalk_client_secret:
            raise ValueError("DingTalk client_id and client_secret are required")
        if not self.config.dingtalk_agent_id:
            raise ValueError("DingTalk agent_id is required for sending messages")
        
        self._client = DingTalkClient(
            client_id=self.config.dingtalk_client_id,
            client_secret=self.config.dingtalk_client_secret,
            agent_id=self.config.dingtalk_agent_id,
            on_message=self._handle_incoming,
            use_stream=self.config.dingtalk_use_stream,
            webhook_secret=self.config.dingtalk_webhook_secret,
        )
        
        # Start Stream connection if enabled
        if self.config.dingtalk_use_stream:
            asyncio.create_task(self._client.start_stream())
        
        logger.info(f"[DingTalk] Client initialized (Stream: {self.config.dingtalk_use_stream})")

    async def stop(self) -> None:
        if not self._client:
            return
        
        logger.info("Gateway manager stopped")

    async def register_listener(self) -> asyncio.Queue:
        return await self._broker.subscribe()

    async def unregister_listener(self, queue: asyncio.Queue) -> None:
        await self._broker.unsubscribe(queue)

    def _handle_incoming(self, event: IncomingMessageEvent) -> None:
        """Handle incoming message and publish to subscribers.
        
        Note: This is called synchronously from the DingTalk client.
        We schedule the async publish as a task to avoid blocking.
        """
        logger.debug("Incoming message event: %s", event)
        
        # Schedule async publish as a task (non-blocking)
        if self._loop:
            asyncio.run_coroutine_threadsafe(
                self._broker.async_publish(event.asdict()), 
                self._loop
            )

    async def send_text(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if not self._client:
            raise RuntimeError("Gateway client not started")
        
        request = OutgoingMessageRequest(
            target=payload["target"],
            content=payload["content"],
            at_list=payload.get("at_list"),
        )
        
        await self._client.send_text(request)
        
        return {"status": "sent"}
    
    async def send_markdown(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send markdown message."""
        if not self._client:
            raise RuntimeError("Gateway client not started")
        
        target = payload["target"]
        title = payload.get("title", "通知")
        content = payload["content"]
        
        await self._client.send_markdown(target, title, content)
        
        return {"status": "sent"}
    
    async def handle_dingtalk_webhook(self, event_data: Dict[str, Any], signature: str = "", timestamp: str = "") -> Dict[str, Any]:
        """Handle DingTalk webhook event."""
        if not self._client:
            raise RuntimeError("Gateway client not started")
        
        return await self._client.handle_webhook(event_data, signature, timestamp)
