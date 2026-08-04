"""Graze behavior.

An animal eats the grass on its cell to reduce hunger. When the cell is grazed
bare it moves to the richest neighboring patch, so herds forage across the
pasture and spread out under grazing pressure.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.movement import wander
from agents.needs import Need, clamp
from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

#: Grass eaten per tick, and how much hunger a unit of grass satisfies.
_BITE: Final[float] = 0.4
_HUNGER_PER_GRASS: Final[float] = 0.38


class GrazeBehavior(Behavior):
    """Consume grass from the pasture to restore hunger."""

    name: str = "graze"

    def execute(self, agent: BaseAgent) -> None:
        """Eat here if there is grass, otherwise step to the greenest patch.

        Args:
            agent: The grazing animal.
        """
        position = agent.position
        if position is None:
            return

        pasture = agent.model.pasture
        eaten = pasture.graze(position, _BITE)
        if eaten > 0.0:
            agent.needs[Need.HUNGER] = clamp(
                agent.needs.get(Need.HUNGER, 0.0) - eaten * _HUNGER_PER_GRASS
            )
            return

        self._seek_grass(agent, pasture)

    @staticmethod
    def _seek_grass(agent: BaseAgent, pasture: object) -> None:
        model = agent.model
        best = None
        best_level = 0.0
        for cell in model.map.neighbors(agent.position):
            if not model.is_walkable(*cell):
                continue
            level = pasture.level(cell)
            if level > best_level:
                best, best_level = cell, level
        if best is not None:
            model.map.move_agent(agent, best)
        else:
            wander(agent)
