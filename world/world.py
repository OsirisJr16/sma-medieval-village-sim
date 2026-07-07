"""World aggregate — the environment the simulation takes place in.

:class:`World` is a facade/aggregate that owns the environmental subsystems
(map, terrain, weather, seasons, and resource nodes) and exposes a cohesive API
to the model. Keeping these behind one aggregate lets the model stay agnostic
about how the environment is structured internally.

No environmental logic is implemented yet — only structure and TODO markers.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.map import Map
    from world.resources import ResourceField
    from world.season import Season
    from world.terrain import Terrain
    from world.weather import Weather


class World:
    """Aggregate root for the simulated environment.

    Attributes:
        width: Environment width in cells.
        height: Environment height in cells.
        map: Spatial grid abstraction.
        terrain: Terrain layer.
        weather: Weather subsystem.
        season: Seasonal cycle.
        resources: World resource nodes.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize the world with empty subsystems.

        Args:
            width: Environment width in cells.
            height: Environment height in cells.
        """
        self.width: int = width
        self.height: int = height

        # TODO: Construct each subsystem and generate the initial environment.
        self.map: Map | None = None
        self.terrain: Terrain | None = None
        self.weather: Weather | None = None
        self.season: Season | None = None
        self.resources: ResourceField | None = None

    def generate(self) -> None:
        """Procedurally generate the environment.

        Should populate terrain, place resource nodes, and set the initial
        climate state.
        """
        # TODO: Implement world generation (noise-based terrain, biomes, ...).
        raise NotImplementedError("World.generate is not implemented yet.")

    def step(self) -> None:
        """Advance environmental state by one tick (weather, season, regrowth)."""
        # TODO: Tick weather/season and regenerate renewable resources.
        raise NotImplementedError("World.step is not implemented yet.")
