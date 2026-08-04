"""Global publish/subscribe event bus.

:class:`EventBus` lets subsystems communicate without direct references:
publishers emit :class:`~communication.events.Event` objects and subscribers
register callbacks per :class:`~communication.events.EventType`. This is the
backbone of the event-driven architecture.

The container structure and public API are defined here; dispatch logic is
future work.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from communication.events import EventType

if TYPE_CHECKING:
    from communication.events import Event

# A subscriber is any callable that consumes an Event.
Subscriber = Callable[["Event"], None]


class EventBus:
    """In-process publish/subscribe dispatcher.

    Attributes:
        subscribers: Registered callbacks keyed by event type.
    """

    def __init__(self) -> None:
        """Initialize an empty event bus."""
        self.subscribers: dict[EventType, list[Subscriber]] = {}

    def subscribe(self, event_type: EventType, handler: Subscriber) -> None:
        """Register a handler for an event type.

        Args:
            event_type: The event category to listen for.
            handler: The callback invoked when a matching event is published.
        """
        self.subscribers.setdefault(event_type, []).append(handler)

    def unsubscribe(self, event_type: EventType, handler: Subscriber) -> None:
        """Remove a previously registered handler.

        Args:
            event_type: The event category the handler was registered for.
            handler: The callback to remove.
        """
        handlers = self.subscribers.get(event_type)
        if handlers and handler in handlers:
            handlers.remove(handler)

    def publish(self, event: Event) -> None:
        """Broadcast an event to all matching subscribers.

        Args:
            event: The event to dispatch.
        """
        # Iterate a copy so a handler may (un)subscribe during dispatch.
        for handler in list(self.subscribers.get(event.type, ())):
            handler(event)
