"""Work behavior.

Generic productive-labor behavior. Concrete professions parameterize *what* is
produced (crops, ore, timber, buildings) while sharing the travel-to-workplace /
perform-task / return loop.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.movement import wander
from agents.needs import Need, clamp
from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

#: Extra need cost per tick of labor, on top of baseline metabolism.
_ENERGY_COST: Final[float] = 0.010
_HUNGER_COST: Final[float] = 0.004


class WorkBehavior(Behavior):
    """Perform the agent's profession-specific labor."""

    name: str = "work"

    def execute(self, agent: BaseAgent) -> None:
        """Do one tick of the agent's job.

        Args:
            agent: The agent performing the behavior.
        """
        # TODO: Travel to a workplace and produce goods once buildings and the
        #       economy exist; for now labor is roaming the fields.
        wander(agent)
        agent.needs[Need.ENERGY] = clamp(
            agent.needs.get(Need.ENERGY, 0.0) - _ENERGY_COST
        )
        agent.needs[Need.HUNGER] = clamp(
            agent.needs.get(Need.HUNGER, 0.0) + _HUNGER_COST
        )
