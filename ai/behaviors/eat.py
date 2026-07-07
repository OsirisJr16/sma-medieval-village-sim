"""Eat behavior.

Consumes food from the agent's inventory (or a nearby source) to restore the
hunger need. Applicable to villagers and wildlife alike.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


class EatBehavior(Behavior):
    """Restore the hunger need by consuming food."""

    name: str = "eat"

    def execute(self, agent: BaseAgent) -> None:
        """Consume available food to reduce hunger.

        Args:
            agent: The agent performing the behavior.
        """
        # TODO: Locate/consume food and raise the agent's hunger need.
        raise NotImplementedError("EatBehavior.execute is not implemented yet.")
