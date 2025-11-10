"""Configuration helpers for the DingTalk gateway service."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Literal
from pathlib import Path

# Load .env file if exists
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
except ImportError:
    pass  # python-dotenv not installed


@dataclass(frozen=True)
class GatewayConfig:
    """Runtime configuration loaded from environment variables."""

    # Gateway settings
    channel_type: Literal["dingtalk"] = "dingtalk"
    listen_host: str = "0.0.0.0"
    listen_port: int = 8099
    access_token: str | None = None
    
    # DingTalk settings (新版Stream模式使用ClientId和ClientSecret)
    dingtalk_client_id: str | None = None
    dingtalk_client_secret: str | None = None
    dingtalk_agent_id: str | None = None  # 发送消息时需要
    
    # DingTalk connection mode
    dingtalk_use_stream: bool = True  # True for Stream mode, False for Webhook
    dingtalk_webhook_secret: str | None = None  # Only for Webhook mode

    @classmethod
    def load(cls) -> "GatewayConfig":
        channel_type = os.getenv("CHANNEL_TYPE", "dingtalk")
        host = os.getenv("GATEWAY_HOST", "0.0.0.0")
        port = int(os.getenv("GATEWAY_PORT", "8099"))
        token = os.getenv("GATEWAY_TOKEN")
        
        # DingTalk configuration (新版Stream模式)
        dingtalk_client_id = os.getenv("DINGTALK_CLIENT_ID")
        dingtalk_client_secret = os.getenv("DINGTALK_CLIENT_SECRET")
        dingtalk_agent_id = os.getenv("DINGTALK_AGENT_ID")  # 发送消息需要
        dingtalk_use_stream = os.getenv("DINGTALK_USE_STREAM", "true").lower() == "true"
        dingtalk_webhook_secret = os.getenv("DINGTALK_WEBHOOK_SECRET")
        
        return cls(
            channel_type=channel_type,
            listen_host=host,
            listen_port=port,
            access_token=token,
            dingtalk_client_id=dingtalk_client_id,
            dingtalk_client_secret=dingtalk_client_secret,
            dingtalk_agent_id=dingtalk_agent_id,
            dingtalk_use_stream=dingtalk_use_stream,
            dingtalk_webhook_secret=dingtalk_webhook_secret,
        )
