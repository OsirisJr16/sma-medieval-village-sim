"""Per-agent mailbox.

Each agent owns a :class:`Mailbox` that buffers incoming and outgoing
:class:`~communication.message.Message` objects. Buffering decouples send-time
from process-time: an agent posts messages during its step and reads its inbox
on its own schedule.

The container structure and public API are defined here; delivery logic is
future work.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from communication.message import Message


class Mailbox:
    """An agent's inbox/outbox buffers.

    Attributes:
        inbox: Received messages awaiting processing.
        outbox: Messages queued for delivery.
    """

    def __init__(self) -> None:
        """Initialize empty inbox and outbox queues."""
        self.inbox: deque[Message] = deque()
        self.outbox: deque[Message] = deque()

    def post(self, message: Message) -> None:
        """Queue an outgoing message for later delivery.

        Args:
            message: The message to send.
        """
        # TODO: Append to the outbox (delivery handled by the messaging system).
        raise NotImplementedError("Mailbox.post is not implemented yet.")

    def deliver(self, message: Message) -> None:
        """Place an incoming message into the inbox.

        Args:
            message: The message being delivered to this agent.
        """
        # TODO: Append to the inbox.
        raise NotImplementedError("Mailbox.deliver is not implemented yet.")

    def read(self) -> Message | None:
        """Pop and return the next incoming message, if any.

        Returns:
            The next message, or ``None`` when the inbox is empty.
        """
        # TODO: Pop from the inbox (FIFO).
        raise NotImplementedError("Mailbox.read is not implemented yet.")
