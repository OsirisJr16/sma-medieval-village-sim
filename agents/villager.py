"""Villager agent — base for the human population.

:class:`Villager` is the concrete base class for all human townsfolk. It fills in
the human-specific scaffolding on top of :class:`~agents.base_agent.BaseAgent`
(home, workplace, profession) and provides a concrete — but not yet implemented
— :meth:`step`. Role-specific villagers (farmer, guard, ...) subclass it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agents.base_agent import BaseAgent
from config.constants import AgentType
from core.logger import get_logger

if TYPE_CHECKING:
    import mesa

    from buildings.building import BaseBuilding

_logger = get_logger(__name__)


class Villager(BaseAgent):
    """A human inhabitant of the village.

    Attributes:
        agent_type: The villager's role identifier.
        home: The building the villager lives in, if any.
        workplace: The building the villager works at, if any.
    """

    #: Role identifier; overridden by specialized subclasses.
    agent_type: AgentType = AgentType.VILLAGER

    def __init__(self, model: mesa.Model) -> None:
        """Initialize the villager.

        Args:
            model: The model the villager belongs to.
        """
        super().__init__(model)

        # TODO: Seed human-specific needs (hunger, energy, social, safety).
        self.home: BaseBuilding | None = None
        self.workplace: BaseBuilding | None = None

    def step(self) -> None:
        """Advance the villager by one tick: move to a random adjacent cell."""
        if self.position is None:
            return

        origin = self.position
        options = [
            cell
            for cell in self.model.map.neighbors(origin)
            if self.model.is_walkable(*cell)
        ]
        if not options:
            return

        destination = self.random.choice(options)
        self.model.map.move_agent(self, destination)

        _logger.info(
            "Villager %d moved from (%d,%d) to (%d,%d)",
            self.unique_id,
            *origin,
            *destination,
        )
