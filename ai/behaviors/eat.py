"""Eat behavior.

Consumes food from the agent's inventory (or a nearby source) to restore the
hunger need. Applicable to villagers and wildlife alike.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.needs import Need, clamp
from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

#: Hunger removed per tick spent eating.
_RESTORE_PER_TICK: Final[float] = 0.06


class EatBehavior(Behavior):
    """Restore the hunger need by consuming food."""

    name: str = "eat"

    def can_execute(self, agent: BaseAgent) -> bool:
        """Return whether the agent is hungry enough to bother eating.

        Args:
            agent: The agent considering this behavior.

        Returns:
            True while any hunger remains.
        """
        return agent.needs.get(Need.HUNGER, 0.0) > 0.0

    def execute(self, agent: BaseAgent) -> None:
        """Consume available food to reduce hunger.

        Args:
            agent: The agent performing the behavior.
        """
        # TODO: Draw the meal from an inventory/food source once the economy
        #       exists; for now eating is simply available wherever the agent is.
        agent.needs[Need.HUNGER] = clamp(
            agent.needs.get(Need.HUNGER, 0.0) - _RESTORE_PER_TICK
        )
