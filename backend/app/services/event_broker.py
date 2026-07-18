"""Thread-safe fan-out for live automation events."""

from queue import Full, Queue
from threading import Lock
from typing import Any


class EventBroker:
    """Broadcast each event to every connected SSE client."""

    def __init__(self) -> None:
        self._subscribers: set[Queue[dict[str, Any]]] = set()
        self._lock = Lock()

    def subscribe(self) -> Queue[dict[str, Any]]:
        subscriber: Queue[dict[str, Any]] = Queue(maxsize=100)
        with self._lock:
            self._subscribers.add(subscriber)
        return subscriber

    def unsubscribe(self, subscriber: Queue[dict[str, Any]]) -> None:
        with self._lock:
            self._subscribers.discard(subscriber)

    def publish(self, event: dict[str, Any]) -> None:
        with self._lock:
            subscribers = tuple(self._subscribers)
        for subscriber in subscribers:
            try:
                subscriber.put_nowait(event)
            except Full:
                # Slow clients resume from persisted event history instead.
                self.unsubscribe(subscriber)


event_broker = EventBroker()
