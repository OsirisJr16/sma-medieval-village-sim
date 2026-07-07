"""Wolf agent.

Wildlife predator. A :class:`~agents.base_agent.BaseAgent` (not a villager) that
hunts prey such as deer and may threaten villagers, giving guards something to
defend against. Part of a simple predator-prey dynamic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent
from config.constants import AgentType

if TYPE_CHECKING:
    import mesa


class Wolf(BaseAgent):
    """A predatory wild animal.

    Attributes:
        agent_type: Identifier for the wolf agent kind.
    """

    agent_type: AgentType = AgentType.WOLF

    def __init__(self, model: mesa.Model) -> None:
        """Initialize the wolf.

        Args:
            model: The model the wolf belongs to.
        """
        super().__init__(model)
        # TODO: Seed predator needs/state (hunger, current prey target).

    def step(self) -> None:
        """Advance the wolf by one tick."""
        # TODO: wander -> detect prey -> chase -> attack; starve without food.
        raise NotImplementedError("Wolf.step is not implemented yet.")
