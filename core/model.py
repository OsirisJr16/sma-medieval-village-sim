"""Central Mesa model for the Medieval Village Simulation.

:class:`GameModel` is the heart of the simulation. It subclasses
:class:`mesa.Model` and owns the global simulation state: the spatial grid, the
agent population, the world environment, and data collection.

Following Mesa 3.x conventions, agents auto-register with ``self.agents`` (an
``AgentSet``) on construction, and activation is expressed via AgentSet methods
(e.g. ``self.agents.shuffle_do("step")``) rather than the legacy ``mesa.time``
schedulers.

This module contains **no** simulation logic yet — only the structural
placeholders and TODO markers for future development.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import mesa

if TYPE_CHECKING:  # Imported only for type hints to avoid import cycles.
    from world.world import World


class GameModel(mesa.Model):
    """The Mesa model that drives the whole simulation.

    Responsibilities (to be implemented):
        * Create and hold the spatial grid (``mesa.space.MultiGrid``).
        * Populate the world with agents and buildings.
        * Advance the simulation one tick per :meth:`step`.
        * Collect statistics via a ``mesa.DataCollector``.

    Attributes:
        width: Grid width in cells.
        height: Grid height in cells.
        grid: The Mesa spatial grid (assigned during setup).
        world: The :class:`~world.world.World` environment aggregate.
        running: Mesa flag consulted by batch runners / visualizers.
    """

    def __init__(
        self,
        width: int,
        height: int,
        *,
        seed: int | None = None,
    ) -> None:
        """Initialize the model.

        Args:
            width: Grid width in cells.
            height: Grid height in cells.
            seed: Optional RNG seed for reproducible runs.
        """
        super().__init__(seed=seed)

        self.width: int = width
        self.height: int = height

        # TODO: Instantiate the spatial grid, e.g.:
        #   self.grid = mesa.space.MultiGrid(width, height, torus=False)
        self.grid: mesa.space.MultiGrid | None = None

        # TODO: Build the world environment (terrain, weather, seasons, ...).
        self.world: World | None = None

        # TODO: Spawn initial agents and buildings.
        # TODO: Configure a mesa.DataCollector for metrics.

        # Mesa consults this flag to know whether to keep stepping.
        self.running: bool = True

    def step(self) -> None:
        """Advance the simulation by a single tick.

        Called once per scheduler activation. Implementations should update the
        world, then activate agents (e.g. ``self.agents.shuffle_do("step")``),
        then collect data.
        """
        # TODO: Advance world time (season/weather), activate agents, collect
        #       data, and evaluate stopping conditions.
        raise NotImplementedError("GameModel.step is not implemented yet.")

    def setup(self) -> None:
        """Populate the model with its initial state.

        Kept separate from ``__init__`` so the model can be reset/reseeded
        without reconstruction.
        """
        # TODO: Create grid, world, agents, buildings, and data collectors.
        raise NotImplementedError("GameModel.setup is not implemented yet.")
