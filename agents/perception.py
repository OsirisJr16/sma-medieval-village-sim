"""Perception queries over an agent's local view.

Helpers that turn the raw list from :meth:`agents.base_agent.BaseAgent.perceive`
into the specific facts a decision needs, e.g. "the nearest wolf". Keeping these
here lets states and behaviors stay declarative.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent
    from config.constants import AgentType


def _squared_distance(a: tuple[int, int], b: tuple[int, int]) -> int:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def nearest_of_type(agent: BaseAgent, kind: AgentType) -> BaseAgent | None:
    """Return the closest perceived agent of a given kind, if any.

    Args:
        agent: The perceiving agent.
        kind: The agent type to look for.

    Returns:
        The nearest matching agent within vision, or ``None``.
    """
    origin = agent.position
    if origin is None:
        return None

    best: BaseAgent | None = None
    best_distance: int | None = None
    for other in agent.perceive():
        if getattr(other, "agent_type", None) is not kind or other.position is None:
            continue
        distance = _squared_distance(origin, other.position)
        if best_distance is None or distance < best_distance:
            best, best_distance = other, distance
    return best


def count_of_type(agent: BaseAgent, kind: AgentType) -> int:
    """Count perceived agents of a given kind (local crowding).

    Args:
        agent: The perceiving agent.
        kind: The agent type to count.

    Returns:
        How many agents of that kind are within vision.
    """
    return sum(
        1 for other in agent.perceive() if getattr(other, "agent_type", None) is kind
    )


def is_adjacent(a: tuple[int, int], b: tuple[int, int]) -> bool:
    """Return whether two cells touch (including diagonally)."""
    return max(abs(a[0] - b[0]), abs(a[1] - b[1])) == 1
