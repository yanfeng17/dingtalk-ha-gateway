"""DingTalk client for interacting with DingTalk Open Platform."""

from __future__ import annotations

import asyncio
import json
import logging
import time
import hmac
import hashlib
import base64
from typing import Any, Callable, Dict, Optional
from dataclasses import asdict

import aiohttp
import requests

from .events import IncomingMessageEvent, OutgoingMessageRequest

logger = logging.getLogger(__name__)


class DingTalkClientError(Exception):
    """Base exception for DingTalk client failures."""


class DingTalkClient:
    """Encapsulates the DingTalk client lifecycle and API interactions."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        agent_id: str,
        on_message: Callable[[IncomingMessageEvent], None],
        use_stream: bool = True,
        webhook_secret: Optional[str] = None,
    ) -> None:
        """
        Initialize DingTalk client.
        
        Args:
            client_id: DingTalk application Client ID (新版)
            client_secret: DingTalk application Client Secret (新版)
            agent_id: DingTalk Agent ID (发送消息时需要)
            on_message: Callback function for incoming messages
            use_stream: Use Stream mode (True) or Webhook mode (False)
            webhook_secret: Secret for webhook signature verification (Webhook mode only)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.agent_id = agent_id
        self._on_message = on_message
        self.use_stream = use_stream
        self.webhook_secret = webhook_secret
        
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
        self._contact_cache: Dict[str, str] = {}
        self._stream_task: Optional[asyncio.Task] = None
        
        logger.info(f"[DingTalk] Client initialized with client_id: {client_id[:10]}... (Stream mode: {use_stream})")

    async def start_stream(self) -> None:
        """Start Stream connection for receiving messages."""
        if not self.use_stream:
            logger.warning("[DingTalk] Stream mode is disabled")
            return
        
        try:
            # Import dingtalk-stream SDK
            from dingtalk_stream import AckMessage, ChatbotHandler, ChatbotMessage, DingTalkStreamClient, Credential
            
            class MessageHandler(ChatbotHandler):
                def __init__(self, parent: DingTalkClient):
                    super().__init__()
                    self.parent = parent
                
                async def process(self, callback_message):
                    """Process incoming message from Stream."""
                    try:
                        # Parse message - ChatbotMessage 已经帮我们处理好了
                        incoming_message = ChatbotMessage.from_dict(callback_message.data)
                        await self.parent._handle_stream_message(incoming_message)
                        return AckMessage.STATUS_OK, "OK"
                    except Exception as e:
                        logger.error(f"[DingTalk] Error processing stream message: {e}", exc_info=True)
                        return AckMessage.STATUS_SYSTEM_EXCEPTION, str(e)
            
            # Create credential
            credential = Credential(self.client_id, self.client_secret)
            
            # Create stream client
            stream_client = DingTalkStreamClient(credential)
            
            # Register chatbot handler with the correct topic
            stream_client.register_callback_handler(ChatbotMessage.TOPIC, MessageHandler(self))
            
            # Start stream connection in background
            logger.info("[DingTalk] Starting Stream connection...")
            await stream_client.start()
            
        except ImportError:
            logger.error("[DingTalk] dingtalk-stream package not installed. Please install: pip install dingtalk-stream")
            raise DingTalkClientError("dingtalk-stream package required for Stream mode")
        except Exception as e:
            logger.error(f"[DingTalk] Failed to start Stream connection: {e}", exc_info=True)
            raise DingTalkClientError(f"Stream connection failed: {e}")

    async def _handle_stream_message(self, incoming_message) -> None:
        """Handle incoming message from Stream connection.
        
        Args:
            incoming_message: ChatbotMessage object from dingtalk-stream SDK
        """
        try:
            # Extract message fields from ChatbotMessage object
            conversation_type = incoming_message.conversation_type
            sender_id = incoming_message.sender_staff_id or incoming_message.sender_id
            sender_nick = incoming_message.sender_nick or sender_id
            msg_id = incoming_message.message_id
            conversation_id = incoming_message.conversation_id
            
            # 保存 session_webhook 用于回复到聊天框
            session_webhook = incoming_message.session_webhook
            webhook_expired_time = incoming_message.session_webhook_expired_time
            
            # Get text content
            if incoming_message.text and hasattr(incoming_message.text, 'content'):
                content_text = incoming_message.text.content or ""
            else:
                content_text = ""
            
            is_group = conversation_type == "2"
            
            # Check if bot is mentioned
            at_me = incoming_message.is_in_at_list or False
            
            # Skip group messages without mention
            if is_group and not at_me:
                logger.debug("[DingTalk] Group message without mention, skipping")
                return
            
            # 缓存 session_webhook 供后续使用
            if session_webhook:
                self._contact_cache[sender_id] = {
                    'webhook': session_webhook,
                    'expired_at': webhook_expired_time,
                    'conversation_id': conversation_id
                }
                logger.debug(f"[DingTalk] Cached session_webhook for {sender_id}")
            
            # Build incoming message event
            incoming_event = IncomingMessageEvent(
                msg_id=msg_id,
                sender=sender_id,
                sender_name=sender_nick,
                receiver=self.client_id,
                content=content_text,
                is_group=is_group,
                timestamp=int(time.time() * 1000),
                room_id=conversation_id if is_group else None,
                room_name=incoming_message.conversation_title,
                at_me=at_me if is_group else None,
            )
            
            # 记录接收时间用于性能分析
            receive_time = time.time()
            logger.info(f"[DingTalk] Received message from {sender_nick}: {content_text[:50]}")
            
            # Trigger callback (同步调用，避免额外延迟)
            self._on_message(incoming_event)
            
            # 记录处理耗时
            process_time = (time.time() - receive_time) * 1000
            logger.debug(f"[DingTalk] Message processing time: {process_time:.2f}ms")
            
        except Exception as e:
            logger.error(f"[DingTalk] Error handling stream message: {e}", exc_info=True)

    async def handle_webhook(self, event_data: Dict[str, Any], signature: str = "", timestamp: str = "") -> Dict[str, Any]:
        """
        Handle incoming webhook event from DingTalk.
        
        Args:
            event_data: Raw event data from DingTalk
            signature: Request signature for verification
            timestamp: Request timestamp
            
        Returns:
            Response dict for DingTalk server
        """
        if self.use_stream:
            logger.warning("[DingTalk] Received webhook request but Stream mode is enabled")
            return {"success": False, "error": "webhook_disabled"}
        
        # Verify signature
        if self.webhook_secret:
            if not self._verify_webhook_signature(timestamp, signature):
                logger.warning("[DingTalk] Invalid webhook signature")
                return {"success": False, "error": "invalid_signature"}
        
        try:
            await self._handle_webhook_message(event_data)
            return {"success": True}
        except Exception as e:
            logger.error(f"[DingTalk] Error handling webhook: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def _verify_webhook_signature(self, timestamp: str, signature: str) -> bool:
        """Verify webhook request signature."""
        if not self.webhook_secret:
            return True
        
        string_to_sign = f"{timestamp}\n{self.webhook_secret}"
        hmac_code = hmac.new(
            self.webhook_secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        expected_signature = base64.b64encode(hmac_code).decode('utf-8')
        
        return signature == expected_signature

    async def _handle_webhook_message(self, event_data: Dict[str, Any]) -> None:
        """Process incoming message from webhook."""
        # Similar to stream message handling
        # Implementation depends on DingTalk webhook payload structure
        logger.info("[DingTalk] Processing webhook message")
        # TODO: Implement based on actual webhook payload format

    async def send_text(self, request: OutgoingMessageRequest) -> None:
        """
        Send text message to DingTalk.
        优先使用 session_webhook（显示在聊天框），否则使用工作通知API
        
        Args:
            request: Outgoing message request
        """
        # 先尝试使用 session_webhook（聊天框回复）
        if request.target in self._contact_cache:
            webhook_info = self._contact_cache.get(request.target)
            if isinstance(webhook_info, dict):
                webhook_url = webhook_info.get('webhook')
                expired_at = webhook_info.get('expired_at', 0)
                
                # 检查是否过期（webhook有效期通常2小时）
                if webhook_url and time.time() * 1000 < expired_at:
                    try:
                        await self._send_via_webhook(webhook_url, request.content)
                        logger.info(f"[DingTalk] ✅ Message sent to chat via webhook: {request.target}")
                        return
                    except Exception as e:
                        logger.warning(f"[DingTalk] Webhook send failed, fallback to work notification: {e}")
                        # 如果webhook失败，继续使用工作通知方式
        
        # 如果没有webhook或已过期，使用工作通知API
        logger.info(f"[DingTalk] 📢 Sending via work notification (no active webhook for {request.target})")
        await self._send_via_work_notification(request)
    
    async def _send_via_webhook(self, webhook_url: str, content: str) -> None:
        """通过 session_webhook 发送消息（显示在聊天框）"""
        data = {
            "msgtype": "text",
            "text": {
                "content": content
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(webhook_url, json=data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                result = await response.json()
                if result.get("errcode") != 0:
                    raise DingTalkClientError(f"Webhook send failed: {result.get('errmsg')}")
    
    async def _send_via_work_notification(self, request: OutgoingMessageRequest) -> None:
        """通过工作通知API发送消息（显示在工作通知中）"""
        access_token = await self._get_access_token()
        
        url = "https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2"
        params = {"access_token": access_token}
        
        msg_content = {"content": request.content}
        
        data = {
            "agent_id": self.agent_id,
            "userid_list": request.target,
            "msg": {
                "msgtype": "text",
                "text": msg_content
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params, json=data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    result = await response.json()
                    
                    if result.get("errcode") == 0:
                        logger.info(f"[DingTalk] Work notification sent to {request.target}")
                    else:
                        logger.error(f"[DingTalk] Failed to send message: {result.get('errmsg')}")
                        raise DingTalkClientError(f"Send message failed: {result.get('errmsg')}")
        except Exception as e:
            logger.error(f"[DingTalk] Error sending message: {e}")
            raise DingTalkClientError(f"Failed to send message: {e}")

    async def send_markdown(self, target: str, title: str, content: str) -> None:
        """
        Send markdown message to DingTalk.
        
        Args:
            target: Target user or chat ID
            title: Message title
            content: Markdown content
        """
        access_token = await self._get_access_token()
        
        url = "https://oapi.dingtalk.com/topapi/message/corpconversation/asyncsend_v2"
        params = {"access_token": access_token}
        
        data = {
            "agent_id": self.agent_id,
            "userid_list": target,
            "msg": {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": content
                }
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, params=params, json=data, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    result = await response.json()
                    
                    if result.get("errcode") == 0:
                        logger.info(f"[DingTalk] Markdown message sent to {target}")
                    else:
                        logger.error(f"[DingTalk] Failed to send markdown: {result.get('errmsg')}")
                        raise DingTalkClientError(f"Send markdown failed: {result.get('errmsg')}")
        except Exception as e:
            logger.error(f"[DingTalk] Error sending markdown: {e}")
            raise

    async def _get_access_token(self) -> str:
        """Get or refresh access token."""
        # Check if token is still valid
        if self._access_token and time.time() < self._token_expires_at:
            return self._access_token
        
        # Fetch new token (新版API)
        url = "https://oapi.dingtalk.com/gettoken"
        params = {
            "appkey": self.client_id,
            "appsecret": self.client_secret,
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    result = await response.json()
                    
                    if result.get("errcode") != 0:
                        raise DingTalkClientError(f"Get access token failed: {result.get('errmsg')}")
                    
                    self._access_token = result.get("access_token")
                    expires_in = result.get("expires_in", 7200)
                    self._token_expires_at = time.time() + expires_in - 300  # Refresh 5 minutes early
                    
                    logger.info("[DingTalk] Access token refreshed successfully")
                    return self._access_token
        except Exception as e:
            logger.error(f"[DingTalk] Failed to get access token: {e}")
            raise DingTalkClientError(f"Failed to get access token: {e}")
