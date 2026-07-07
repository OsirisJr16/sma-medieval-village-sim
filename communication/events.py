"""Event taxonomy and payloads.

Defines the :class:`Event` base and the :class:`EventType` enumeration used by
the :class:`~communication.event_bus.EventBus`. Events are broadcast facts about
the world ("a wolf appeared", "a trade completed") that any interested subscriber
can react to — distinct from directed :class:`~communication.message.Message`
envelopes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class EventType(StrEnum):
    """Categories of broadcast events."""

    # Lifecycle
    AGENT_SPAWNED = "agent_spawned"
    AGENT_DIED = "agent_died"

    # World
    SEASON_CHANGED = "season_changed"
    WEATHER_CHANGED = "weather_changed"

    # Economy
    TRADE_COMPLETED = "trade_completed"
    RESOURCE_DEPLETED = "resource_depleted"

    # Threat
    THREAT_DETECTED = "threat_detected"

    # TODO: Extend as subsystems introduce new broadcast-worthy occurrences.


@dataclass(slots=True)
class Event:
    """A broadcast event published on the event bus.

    Attributes:
        type: The event category.
        source: Optional identifier of the emitter (e.g. an agent's unique_id).
        payload: Arbitrary event-specific data.
    """

    type: EventType
    source: Any | None = None
    payload: dict[str, Any] = field(default_factory=dict)

    # TODO: Add a monotonic tick/sequence stamp once the model clock exists
    #       (Date/time helpers are avoided here to keep events pure data).
