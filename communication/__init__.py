"""Communication package.

Decoupled, event-driven messaging for the multi-agent system:

* :mod:`communication.event_bus` — global publish/subscribe bus.
* :mod:`communication.events` — event taxonomy and payloads.
* :mod:`communication.message` — direct agent-to-agent message envelopes.
* :mod:`communication.mailbox` — per-agent inbox/outbox.

Agents interact through these abstractions rather than calling each other
directly, keeping them loosely coupled.
"""
