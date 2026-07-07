"""Patrol behavior.

Moves the agent along a route to watch for threats. Primarily used by guards to
protect the settlement.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


class PatrolBehavior(Behavior):
    """Walk a patrol route and watch for threats."""

    name: str = "patrol"

    def execute(self, agent: BaseAgent) -> None:
        """Advance along the patrol route by one tick.

        Args:
            agent: The agent performing the behavior.
        """
        # TODO: Step toward the next waypoint and scan for threats.
        raise NotImplementedError("PatrolBehavior.execute is not implemented yet.")
