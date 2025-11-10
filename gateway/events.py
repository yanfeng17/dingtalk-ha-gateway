"""Event definitions shared across the gateway service."""

from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import Any, Dict


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class IncomingMessageEvent:
    """Represents a message received from DingTalk."""

    msg_id: str
    sender: str
    sender_name: str
    receiver: str
    content: str
    is_group: bool
    timestamp: int
    event_time: str = field(default_factory=utc_now_iso)
    room_id: str | None = None
    room_name: str | None = None
    at_me: bool | None = None

    def asdict(self) -> Dict[str, Any]:
        data = asdict(self)
        data.setdefault("event_type", "incoming_message")
        return data


@dataclass
class OutgoingMessageRequest:
    """Payload required to send a DingTalk message."""

    target: str
    content: str
    at_list: list[str] | None = None
    msg_type: str = "text"  # text, markdown, actionCard

    def normalized(self) -> Dict[str, Any]:
        payload: Dict[str, Any] = {
            "target": self.target,
            "content": self.content,
            "msg_type": self.msg_type,
        }
        if self.at_list:
            payload["at_list"] = self.at_list
        return payload
