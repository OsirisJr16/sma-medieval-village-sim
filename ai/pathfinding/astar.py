"""A* pathfinding.

Defines the :class:`Pathfinder` interface and an :class:`AStarPathfinder`
implementation placeholder. Agents request routes through the interface so the
concrete algorithm can be replaced without touching movement logic.

Grid coordinates are ``(x, y)`` tuples. Only the interface and structure are
defined here; the search itself is future work.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from world.map import Map

# A grid coordinate.
Coord = tuple[int, int]


class Pathfinder(ABC):
    """Interface for grid pathfinding strategies."""

    @abstractmethod
    def find_path(self, start: Coord, goal: Coord) -> list[Coord]:
        """Compute a walkable path between two cells.

        Args:
            start: The starting coordinate.
            goal: The destination coordinate.

        Returns:
            An ordered list of coordinates from ``start`` to ``goal`` (empty if
            no path exists). Whether endpoints are included is implementation
            defined and should be documented by concrete classes.
        """
        raise NotImplementedError


class AStarPathfinder(Pathfinder):
    """A* search over the world grid.

    Attributes:
        world_map: The map providing passability and movement costs.
    """

    def __init__(self, world_map: Map) -> None:
        """Initialize the pathfinder.

        Args:
            world_map: The map used to query passability and terrain costs.
        """
        self.world_map: Map = world_map

    def find_path(self, start: Coord, goal: Coord) -> list[Coord]:
        """Compute a path with the A* algorithm.

        Args:
            start: The starting coordinate.
            goal: The destination coordinate.

        Returns:
            The path from ``start`` to ``goal`` (empty if unreachable).
        """
        # TODO: Implement A* using terrain cost as g() and a heuristic
        #       (Manhattan/Chebyshev depending on the neighborhood) as h().
        raise NotImplementedError("AStarPathfinder.find_path is not implemented yet.")

    def heuristic(self, a: Coord, b: Coord) -> float:
        """Estimate the cost between two cells.

        Args:
            a: First coordinate.
            b: Second coordinate.

        Returns:
            The estimated (admissible) cost from ``a`` to ``b``.
        """
        # TODO: Return an admissible heuristic matching the movement model.
        raise NotImplementedError("AStarPathfinder.heuristic is not implemented yet.")
