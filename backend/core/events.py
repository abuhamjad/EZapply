import asyncio
import json
import time
from typing import Any, Dict, List, Optional
from fastapi import WebSocket
from backend.core.logger import get_logger

log = get_logger("events")


class EventBus:
    """Central event bus for real-time communication with frontend."""

    def __init__(self):
        self._connections: List[WebSocket] = []
        self._history: List[Dict] = []
        self._max_history = 500

    async def connect(self, ws: WebSocket):
        await ws.accept()
        self._connections.append(ws)
        log.info(f"WebSocket connected. Active: {len(self._connections)}")

    def disconnect(self, ws: WebSocket):
        if ws in self._connections:
            self._connections.remove(ws)
        log.info(f"WebSocket disconnected. Active: {len(self._connections)}")

    async def emit(self, event_type: str, message: str, data: Optional[Dict] = None):
        """Broadcast event to all connected clients."""
        event = {
            "type": event_type,
            "message": message,
            "data": data or {},
            "timestamp": time.strftime("%H:%M:%S"),
        }
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        dead: List[WebSocket] = []
        for ws in self._connections:
            try:
                await ws.send_json(event)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws)

    def emit_sync(self, event_type: str, message: str, data: Optional[Dict] = None):
        """Synchronous emit — creates event loop task if possible."""
        event = {
            "type": event_type,
            "message": message,
            "data": data or {},
            "timestamp": time.strftime("%H:%M:%S"),
        }
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        for ws in list(self._connections):
            try:
                loop = asyncio.get_running_loop()
                asyncio.run_coroutine_threadsafe(ws.send_json(event), loop)
            except RuntimeError:
                # No running event loop in this thread
                pass
            except Exception:
                pass

    @property
    def history(self) -> List[Dict]:
        return self._history[-100:]


# Global event bus singleton
event_bus = EventBus()
