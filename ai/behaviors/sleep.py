"""Sleep behavior.

Restores the agent's energy need, typically at its home and during night-time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


class SleepBehavior(Behavior):
    """Restore the energy need by resting."""

    name: str = "sleep"

    def execute(self, agent: BaseAgent) -> None:
        """Rest to recover energy.

        Args:
            agent: The agent performing the behavior.
        """
        # TODO: Advance rest and raise the agent's energy need.
        raise NotImplementedError("SleepBehavior.execute is not implemented yet.")
