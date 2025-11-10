"""Entry point for the DingTalk gateway API service."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict

from fastapi import Depends, FastAPI, Header, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from gateway import GatewayManager
from gateway.config import GatewayConfig


logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(name)s: %(message)s")

app = FastAPI(title="DingTalk HA Gateway", version="0.1.0")
config = GatewayConfig.load()
manager = GatewayManager(config=config)

logger = logging.getLogger(__name__)


class SendMessageSchema(BaseModel):
    target: str
    content: str
    at_list: list[str] | None = None


class SendMarkdownSchema(BaseModel):
    target: str
    title: str | None = "通知"
    content: str


async def token_guard(x_access_token: str | None = Header(default=None)):
    if config.access_token and x_access_token != config.access_token:
        raise HTTPException(status_code=401, detail="Invalid access token")
    return True


@app.on_event("startup")
async def on_startup() -> None:
    await manager.start()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await manager.stop()


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    return {"status": "ok", "channel": "dingtalk"}


@app.post("/send_message")
async def send_message(payload: SendMessageSchema, guard: bool = Depends(token_guard)) -> JSONResponse:
    result = await manager.send_text(payload.model_dump())
    return JSONResponse(result)


@app.post("/send_markdown")
async def send_markdown(payload: SendMarkdownSchema, guard: bool = Depends(token_guard)) -> JSONResponse:
    """Send markdown message."""
    result = await manager.send_markdown(payload.model_dump())
    return JSONResponse(result)


@app.post("/dingtalk/webhook")
async def dingtalk_webhook(request: Request) -> Dict[str, Any]:
    """
    DingTalk event subscription webhook endpoint.
    Handles message events from DingTalk.
    """
    try:
        # Get signature headers
        signature = request.headers.get("sign", "")
        timestamp = request.headers.get("timestamp", "")
        
        event_data = await request.json()
        logger.debug(f"[DingTalk] Received webhook event")
        
        result = await manager.handle_dingtalk_webhook(event_data, signature, timestamp)
        return result
    except Exception as e:
        logger.error(f"[DingTalk] Error handling webhook: {e}", exc_info=True)
        return {"success": False, "error": str(e)}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    token = websocket.headers.get("X-Access-Token")
    if config.access_token and token != config.access_token:
        await websocket.close(code=4403)
        return
    await websocket.accept()
    queue = await manager.register_listener()
    try:
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        await manager.unregister_listener(queue)


def run():  # pragma: no cover - helper for uvicorn
    import uvicorn

    uvicorn.run(
        "app:app",
        host=config.listen_host,
        port=config.listen_port,
        reload=False,
    )


if __name__ == "__main__":
    run()
