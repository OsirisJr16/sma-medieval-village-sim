"""Central Mesa model for the Medieval Village Simulation.

:class:`GameModel` is the heart of the simulation. It subclasses
:class:`mesa.Model` and owns the global simulation state: the spatial map and
the agent population.

Following Mesa 3.x conventions, agents auto-register with ``self.agents`` (an
``AgentSet``) on construction, and activation is expressed via AgentSet methods
(``self.agents.shuffle_do("step")``) rather than the legacy ``mesa.time``
schedulers.
"""

from __future__ import annotations

import mesa

from agents.villager import Villager
from core.logger import get_logger
from world.map import Map
from world.scenery import Scenery
from world.terrain import Terrain

_logger = get_logger(__name__)


class GameModel(mesa.Model):
    """The Mesa model that drives the whole simulation.

    Attributes:
        width: Grid width in cells.
        height: Grid height in cells.
        map: The spatial map wrapping the Mesa grid.
        running: Mesa flag consulted by the engine / batch runners.
    """

    def __init__(
        self,
        width: int,
        height: int,
        *,
        num_villagers: int,
        torus: bool = False,
        scenery_density: float = 0.35,
        seed: int | None = None,
    ) -> None:
        """Initialize and populate the model.

        Args:
            width: Grid width in cells.
            height: Grid height in cells.
            num_villagers: Number of villagers to spawn.
            torus: Whether the grid wraps around its edges.
            scenery_density: Fraction of cells carrying scenery.
            seed: Optional RNG seed for reproducible runs.
        """
        # Mesa 3.5 seeds ``self.random`` deterministically from an integer
        # ``rng`` and deprecates the ``seed`` keyword.
        super().__init__(rng=seed)

        self.width: int = width
        self.height: int = height
        self.map: Map = Map(width, height, torus=torus)
        self.terrain: Terrain = Terrain(width, height)
        self.scenery: Scenery = Scenery.generate(
            width, height, self.random, density=scenery_density
        )

        self._spawn_villagers(num_villagers)

        # Mesa consults this flag to know whether to keep stepping.
        self.running: bool = True

        _logger.info("Simulation initialized.")
        _logger.info("Grid: %d x %d", width, height)
        _logger.info("Villagers: %d", len(self.agents))

    def is_walkable(self, x: int, y: int) -> bool:
        """Return whether an agent may occupy a cell.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.

        Returns:
            True when neither the terrain nor its scenery blocks movement.
        """
        return self.terrain.is_passable(x, y) and not self.scenery.blocks(x, y)

    def _spawn_villagers(self, count: int) -> None:
        open_cells = [
            (x, y)
            for y in range(self.height)
            for x in range(self.width)
            if self.is_walkable(x, y)
        ]
        for _ in range(count):
            villager = Villager(self)
            self.map.place_agent(villager, self.random.choice(open_cells))

    def step(self) -> None:
        """Advance the simulation by a single tick by activating every agent."""
        self.agents.shuffle_do("step")
