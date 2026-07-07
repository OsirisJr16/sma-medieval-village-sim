"""Work behavior.

Generic productive-labor behavior. Concrete professions parameterize *what* is
produced (crops, ore, timber, buildings) while sharing the travel-to-workplace /
perform-task / return loop.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


class WorkBehavior(Behavior):
    """Perform the agent's profession-specific labor."""

    name: str = "work"

    def execute(self, agent: BaseAgent) -> None:
        """Do one tick of the agent's job.

        Args:
            agent: The agent performing the behavior.
        """
        # TODO: Travel to workplace, perform the profession task, store output.
        raise NotImplementedError("WorkBehavior.execute is not implemented yet.")
