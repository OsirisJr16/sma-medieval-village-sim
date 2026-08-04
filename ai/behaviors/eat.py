"""Eat behavior.

A villager draws a meal from the village granary to restore hunger. The granary
is stocked by farmers, so eating now depends on production: an empty granary
means the meal — and the hunger relief — simply is not there.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.needs import Need, clamp
from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

#: Food drawn from the granary per tick, and hunger removed per unit eaten.
_MEAL: Final[float] = 0.09
_HUNGER_PER_FOOD: Final[float] = 1.0


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
        model = agent.model
        served = min(_MEAL, model.granary)
        if served <= 0.0:
            return  # Empty granary: nothing to eat this tick.
        model.granary -= served
        agent.needs[Need.HUNGER] = clamp(
            agent.needs.get(Need.HUNGER, 0.0) - served * _HUNGER_PER_FOOD
        )
