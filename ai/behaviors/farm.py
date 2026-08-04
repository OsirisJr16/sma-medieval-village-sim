"""Farm behavior.

A farmer harvests grass from the pasture and stores it in the village granary —
turning the shared food resource into a stockpile the whole settlement eats
from. Like a grazing animal, a farmer moves to the greenest neighboring patch
when the current cell is bare, so farmers and herds compete for the same land.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.movement import wander
from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

#: Grass harvested per tick, and food yielded per unit of grass.
_HARVEST: Final[float] = 0.4
_YIELD: Final[float] = 3.0


class FarmBehavior(Behavior):
    """Harvest grass into the village granary."""

    name: str = "farm"

    def execute(self, agent: BaseAgent) -> None:
        """Reap grass here, or move toward the greenest patch when bare.

        Args:
            agent: The farming villager.
        """
        position = agent.position
        if position is None:
            return

        model = agent.model
        reaped = model.pasture.graze(position, _HARVEST)
        if reaped > 0.0:
            model.granary = min(model.granary_capacity, model.granary + reaped * _YIELD)
            model.pasture.till(position)  # leave a visible plowed plot
            return

        best = None
        best_level = 0.0
        for cell in model.map.neighbors(position):
            if not model.is_walkable(*cell):
                continue
            level = model.pasture.level(cell)
            if level > best_level:
                best, best_level = cell, level
        if best is not None:
            model.map.move_agent(agent, best)
        else:
            wander(agent)
