"""Agent-to-agent message envelope.

Defines a directed :class:`Message` for point-to-point agent communication,
modeled loosely on FIPA ACL performatives (inform, request, propose, ...). Unlike
broadcast :class:`~communication.events.Event` objects, a message targets a
specific recipient and is delivered via that agent's
:class:`~communication.mailbox.Mailbox`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Performative(StrEnum):
    """Communicative intent of a message (FIPA-inspired)."""

    INFORM = "inform"
    REQUEST = "request"
    PROPOSE = "propose"
    ACCEPT = "accept"
    REJECT = "reject"
    QUERY = "query"

    # TODO: Add further performatives as negotiation protocols are designed.


@dataclass(slots=True)
class Message:
    """A directed message between two agents.

    Attributes:
        sender: Identifier of the sending agent.
        receiver: Identifier of the receiving agent.
        performative: The communicative intent.
        content: Arbitrary message-specific payload.
    """

    sender: Any
    receiver: Any
    performative: Performative
    content: dict[str, Any] = field(default_factory=dict)

    # TODO: Add conversation_id / reply_to fields to support multi-turn
    #       negotiation protocols (e.g. contract net).
