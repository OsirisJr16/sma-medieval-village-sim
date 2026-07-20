"""Spatial map abstraction.

:class:`Map` wraps Mesa's spatial grid (``mesa.space.MultiGrid``) and provides
domain-oriented spatial queries (neighbors, cell placement, movement) so the
rest of the code does not couple directly to Mesa's grid API. This indirection
makes it possible to swap grid implementations (hex, continuous space) later.

Coordinates are ``(x, y)`` tuples; the origin is the bottom-left cell.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import mesa

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

# A grid coordinate.
Coord = tuple[int, int]


class Map:
    """Domain wrapper around the Mesa spatial grid.

    Attributes:
        width: Grid width in cells.
        height: Grid height in cells.
        torus: Whether the grid wraps around its edges.
        grid: The underlying Mesa grid.
    """

    def __init__(self, width: int, height: int, *, torus: bool = False) -> None:
        """Initialize the map.

        Args:
            width: Grid width in cells.
            height: Grid height in cells.
            torus: Whether opposite edges are connected.
        """
        self.width: int = width
        self.height: int = height
        self.torus: bool = torus
        self.grid: mesa.space.MultiGrid = mesa.space.MultiGrid(width, height, torus)

    def in_bounds(self, coord: Coord) -> bool:
        """Return whether a coordinate lies within the map.

        Args:
            coord: The ``(x, y)`` coordinate to test.

        Returns:
            True if the coordinate is inside the grid.
        """
        x, y = coord
        return 0 <= x < self.width and 0 <= y < self.height

    def place_agent(self, agent: BaseAgent, coord: Coord) -> None:
        """Place an agent on a cell and record its position.

        Args:
            agent: The agent to place.
            coord: The target ``(x, y)`` cell.
        """
        self.grid.place_agent(agent, coord)
        agent.position = coord

    def move_agent(self, agent: BaseAgent, coord: Coord) -> None:
        """Move an agent to a new cell and update its position.

        Args:
            agent: The agent to move.
            coord: The destination ``(x, y)`` cell.
        """
        self.grid.move_agent(agent, coord)
        agent.position = coord

    def neighbors(self, coord: Coord, *, moore: bool = True) -> list[Coord]:
        """Return the neighboring coordinates of a cell.

        Args:
            coord: The center coordinate.
            moore: Use Moore (8) neighborhood if True, else Von Neumann (4).

        Returns:
            The list of neighboring coordinates.
        """
        return list(
            self.grid.get_neighborhood(coord, moore=moore, include_center=False)
        )
