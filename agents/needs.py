"""Agent need taxonomy.

Needs are the drives that make agents act. Each is a level in ``[0.0, 1.0]``
stored in :attr:`agents.base_agent.BaseAgent.needs`.

Conventions differ per need and are deliberate: ``HUNGER`` rises toward 1.0 as
the agent gets hungrier, while ``ENERGY`` falls toward 0.0 as it tires. In both
cases the *uncomfortable* end is the one that triggers a behavior.
"""

from __future__ import annotations

from enum import StrEnum


class Need(StrEnum):
    """Drives that agents try to satisfy."""

    HUNGER = "hunger"
    ENERGY = "energy"


def clamp(level: float) -> float:
    """Clamp a need level into the valid ``[0.0, 1.0]`` range.

    Args:
        level: The raw level.

    Returns:
        The level constrained to the unit interval.
    """
    return min(1.0, max(0.0, level))
