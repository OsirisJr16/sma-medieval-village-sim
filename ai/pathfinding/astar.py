"""A* pathfinding.

Defines the :class:`Pathfinder` interface and an :class:`AStarPathfinder`
implementation placeholder. Agents request routes through the interface so the
concrete algorithm can be replaced without touching movement logic.

Grid coordinates are ``(x, y)`` tuples. Only the interface and structure are
defined here; the search itself is future work.
"""

from __future__ import annotations

import heapq
from abc import ABC, abstractmethod
from math import sqrt
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from world.map import Map

# A grid coordinate.
Coord = tuple[int, int]

_DIAGONAL = sqrt(2.0)


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

    def __init__(self, world_map: Map, is_passable: Callable[[int, int], bool]) -> None:
        """Initialize the pathfinder.

        Args:
            world_map: The map used for neighbor iteration and bounds.
            is_passable: Predicate returning whether an ``(x, y)`` cell can be
                walked through (terrain and scenery).
        """
        self.world_map: Map = world_map
        self._is_passable = is_passable

    def find_path(self, start: Coord, goal: Coord) -> list[Coord]:
        """Compute a path with the A* algorithm over the 8-connected grid.

        Args:
            start: The starting coordinate.
            goal: The destination coordinate.

        Returns:
            The cells to step through from just after ``start`` up to and
            including ``goal`` (empty if ``goal`` is unreachable or is ``start``).
        """
        if start == goal or not self._is_passable(*goal):
            return []

        open_heap: list[tuple[float, Coord]] = [(self.heuristic(start, goal), start)]
        came_from: dict[Coord, Coord] = {}
        g_score: dict[Coord, float] = {start: 0.0}
        closed: set[Coord] = set()

        while open_heap:
            _, current = heapq.heappop(open_heap)
            if current == goal:
                return self._reconstruct(came_from, current)
            if current in closed:
                continue
            closed.add(current)
            for neighbor in self.world_map.neighbors(current, moore=True):
                if neighbor in closed or not self._is_passable(*neighbor):
                    continue
                diagonal = neighbor[0] != current[0] and neighbor[1] != current[1]
                tentative = g_score[current] + (_DIAGONAL if diagonal else 1.0)
                if tentative < g_score.get(neighbor, float("inf")):
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative
                    heapq.heappush(
                        open_heap, (tentative + self.heuristic(neighbor, goal), neighbor)
                    )
        return []

    def heuristic(self, a: Coord, b: Coord) -> float:
        """Octile distance — admissible for 8-connected movement.

        Args:
            a: First coordinate.
            b: Second coordinate.

        Returns:
            The estimated cost from ``a`` to ``b``.
        """
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        return (dx + dy) + (_DIAGONAL - 2.0) * min(dx, dy)

    @staticmethod
    def _reconstruct(came_from: dict[Coord, Coord], current: Coord) -> list[Coord]:
        path = [current]
        while current in came_from:
            current = came_from[current]
            path.append(current)
        path.reverse()
        return path[1:]  # Exclude the start cell.
