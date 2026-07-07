"""Deer agent.

Wildlife prey. A :class:`~agents.base_agent.BaseAgent` (not a villager) that
grazes, wanders, and flees from predators such as wolves. Part of a simple
predator-prey dynamic and a potential hunting resource for villagers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent
from config.constants import AgentType

if TYPE_CHECKING:
    import mesa


class Deer(BaseAgent):
    """A herbivorous wild animal.

    Attributes:
        agent_type: Identifier for the deer agent kind.
    """

    agent_type: AgentType = AgentType.DEER

    def __init__(self, model: mesa.Model) -> None:
        """Initialize the deer.

        Args:
            model: The model the deer belongs to.
        """
        super().__init__(model)
        # TODO: Seed prey needs/state (hunger, fear, flee target).

    def step(self) -> None:
        """Advance the deer by one tick."""
        # TODO: graze/wander -> detect predators -> flee to safety.
        raise NotImplementedError("Deer.step is not implemented yet.")
