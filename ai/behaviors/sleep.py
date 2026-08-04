"""Sleep behavior.

Restores the agent's energy need, typically at its home and during night-time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.needs import Need, clamp
from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

#: Energy regained per tick spent asleep.
_RECOVER_PER_TICK: Final[float] = 0.05


class SleepBehavior(Behavior):
    """Restore the energy need by resting."""

    name: str = "sleep"

    def execute(self, agent: BaseAgent) -> None:
        """Rest to recover energy.

        Args:
            agent: The agent performing the behavior.
        """
        # TODO: Require the agent to be at its home once buildings exist.
        agent.needs[Need.ENERGY] = clamp(
            agent.needs.get(Need.ENERGY, 0.0) + _RECOVER_PER_TICK
        )
