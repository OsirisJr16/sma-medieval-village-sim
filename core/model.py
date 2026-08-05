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

from collections import Counter
from typing import TYPE_CHECKING

import mesa

from agents.deer import Deer
from agents.farmer import Farmer
from agents.guard import Guard
from agents.merchant import Merchant
from agents.villager import Villager
from agents.wolf import Wolf
from ai.pathfinding.astar import AStarPathfinder
from communication.events import Event, EventType
from core.logger import get_logger
from communication.event_bus import EventBus
from world.clock import WorldClock
from world.map import Map
from world.pasture import Pasture
from world.scenery import Scenery
from world.season import SeasonType
from world.terrain import Terrain

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

_logger = get_logger(__name__)

# Base grass regrowth per tick, and the seasonal multiplier applied to it.
_REGROW_BASE = 0.015
_SEASON_GROWTH = {
    SeasonType.SPRING: 1.3,
    SeasonType.SUMMER: 1.0,
    SeasonType.AUTUMN: 0.6,
    SeasonType.WINTER: 0.15,
}


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
        num_guards: int = 0,
        num_farmers: int = 0,
        num_merchants: int = 0,
        num_prey: int = 0,
        num_predators: int = 0,
        torus: bool = False,
        scenery_density: float = 0.35,
        seed: int | None = None,
    ) -> None:
        """Initialize and populate the model.

        Args:
            width: Grid width in cells.
            height: Grid height in cells.
            num_villagers: Number of villagers to spawn.
            num_guards: Number of guards to spawn.
            num_farmers: Number of farmers to spawn.
            num_merchants: Number of merchants to spawn.
            num_prey: Number of prey animals to spawn.
            num_predators: Number of predators (wolves) to spawn.
            torus: Whether the grid wraps around its edges.
            scenery_density: Fraction of cells carrying scenery.
            seed: Optional RNG seed for reproducible runs.
        """
        # Mesa 3.5 seeds ``self.random`` deterministically from an integer
        # ``rng`` and deprecates the ``seed`` keyword.
        super().__init__(rng=seed)

        self.width: int = width
        self.height: int = height
        self.clock: WorldClock = WorldClock()
        self.events: EventBus = EventBus()
        self.map: Map = Map(width, height, torus=torus)
        self.pathfinder: AStarPathfinder = AStarPathfinder(self.map, self.is_walkable)
        self.terrain: Terrain = Terrain(width, height)
        self.scenery: Scenery = Scenery.generate(
            width, height, self.random, density=scenery_density
        )
        # Grass grows only where agents can stand (open, walkable ground).
        self.pasture: Pasture = Pasture.generate(
            width, height, self.is_walkable, self.random
        )
        # Shared village food store, stocked by farmers and eaten by all.
        _mouths = num_villagers + num_guards + num_farmers + num_merchants
        self.granary_capacity: float = float(max(1, _mouths) * 3)
        self.granary: float = self.granary_capacity * 0.5

        # Vital statistics, tallied off the event bus.
        self.trades: int = 0
        self.births: int = 0
        self.deaths: Counter[str] = Counter()
        self.events.subscribe(EventType.TRADE_COMPLETED, self._on_trade)
        self.events.subscribe(EventType.AGENT_SPAWNED, self._on_birth)
        self.events.subscribe(EventType.AGENT_DIED, self._on_death)

        self._spawn(Villager, num_villagers)
        self._spawn(Guard, num_guards)
        self._spawn(Farmer, num_farmers)
        # Merchants start clustered at the market square (map centre).
        self._spawn(Merchant, num_merchants, near=(width // 2, height // 2), radius=6)
        self._spawn(Deer, num_prey)
        self._spawn(Wolf, num_predators)

        # Mesa consults this flag to know whether to keep stepping.
        self.running: bool = True

        _logger.info("Simulation initialized.")
        _logger.info("Grid: %d x %d", width, height)
        _logger.info(
            "Villagers: %d  Guards: %d  Farmers: %d  Merchants: %d",
            num_villagers, num_guards, num_farmers, num_merchants,
        )
        _logger.info("Prey: %d  Predators: %d", num_prey, num_predators)

    def _on_trade(self, event: object) -> None:
        self.trades += 1

    def _on_birth(self, event: object) -> None:
        self.births += 1

    def _on_death(self, event: Event) -> None:
        self.deaths[event.payload.get("cause", "natural")] += 1

    def is_walkable(self, x: int, y: int) -> bool:
        """Return whether an agent may occupy a cell.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.

        Returns:
            True when neither the terrain nor its scenery blocks movement.
        """
        return self.terrain.is_passable(x, y) and not self.scenery.blocks(x, y)

    def _spawn(
        self,
        agent_class: type[BaseAgent],
        count: int,
        *,
        near: tuple[int, int] | None = None,
        radius: int | None = None,
    ) -> None:
        if count <= 0:
            return
        if near is not None and radius is not None:
            cx, cy = near
            xs = range(max(0, cx - radius), min(self.width, cx + radius + 1))
            ys = range(max(0, cy - radius), min(self.height, cy + radius + 1))
        else:
            xs, ys = range(self.width), range(self.height)
        open_cells = [(x, y) for y in ys for x in xs if self.is_walkable(x, y)]
        if not open_cells:  # A tight cluster region may be fully blocked.
            open_cells = [
                (x, y)
                for y in range(self.height)
                for x in range(self.width)
                if self.is_walkable(x, y)
            ]
        for _ in range(count):
            agent = agent_class(self)
            self.map.place_agent(agent, self.random.choice(open_cells))

    def step(self) -> None:
        """Advance time, regrow grass by the season, then activate every agent."""
        self.clock.advance()
        if self.clock.hour == 0:
            _logger.info("Day %d dawns (%s).", self.clock.day + 1, self.clock.season.current.value)
        self.pasture.regrow(_REGROW_BASE * _SEASON_GROWTH[self.clock.season.current])
        self.agents.shuffle_do("step")
