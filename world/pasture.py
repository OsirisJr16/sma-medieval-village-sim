"""Grazing pasture.

A continuous per-cell field of edible grass — the simulation's renewable food
resource. Grass grows only on fertile (walkable) cells, is consumed when grazed,
and regrows over time at a season-dependent rate. This is the finite resource
prey compete for; overgrazed cells deplete and must recover.

Levels are fractions in ``[0.0, 1.0]`` (0 = bare ground, 1 = lush).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from random import Random

Coord = tuple[int, int]


class Pasture:
    """Per-cell grass levels for the whole map.

    Attributes:
        width: Field width in cells.
        height: Field height in cells.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize a bare, wholly infertile pasture.

        Args:
            width: Field width in cells.
            height: Field height in cells.
        """
        self.width: int = width
        self.height: int = height
        self._level: list[list[float]] = [[0.0] * width for _ in range(height)]
        self._fertile: list[list[bool]] = [[False] * width for _ in range(height)]
        # Cells a farmer has worked; cleared once the grass fully reclaims them.
        self._tilled: list[list[bool]] = [[False] * width for _ in range(height)]

    @classmethod
    def generate(
        cls,
        width: int,
        height: int,
        is_fertile: Callable[[int, int], bool],
        rng: Random,
    ) -> Pasture:
        """Build a pasture, seeding fertile cells with lush starting grass.

        Args:
            width: Field width in cells.
            height: Field height in cells.
            is_fertile: Predicate marking cells where grass may grow.
            rng: Random source, injected so seeding follows the model seed.

        Returns:
            The generated pasture.
        """
        pasture = cls(width, height)
        for y in range(height):
            for x in range(width):
                if is_fertile(x, y):
                    pasture._fertile[y][x] = True
                    pasture._level[y][x] = rng.uniform(0.5, 1.0)
        return pasture

    def is_fertile(self, coord: Coord) -> bool:
        """Return whether grass can grow at a cell."""
        x, y = coord
        return self._fertile[y][x]

    def level(self, coord: Coord) -> float:
        """Return the grass level at a cell (``0.0``–``1.0``)."""
        x, y = coord
        return self._level[y][x]

    def till(self, coord: Coord) -> None:
        """Mark a cell as worked farmland (shown as a plowed plot)."""
        x, y = coord
        if self._fertile[y][x]:
            self._tilled[y][x] = True

    def is_tilled(self, coord: Coord) -> bool:
        """Return whether a cell is currently worked farmland."""
        x, y = coord
        return self._tilled[y][x]

    def graze(self, coord: Coord, bite: float) -> float:
        """Consume up to ``bite`` of grass at a cell.

        Args:
            coord: The cell being grazed.
            bite: The maximum amount to eat.

        Returns:
            The amount actually eaten (bounded by what is there).
        """
        x, y = coord
        eaten = min(bite, self._level[y][x])
        self._level[y][x] -= eaten
        return eaten

    def regrow(self, rate: float) -> None:
        """Grow every fertile cell toward full by ``rate``.

        Args:
            rate: Grass regained per fertile cell this tick.
        """
        if rate <= 0.0:
            return
        for y in range(self.height):
            row = self._level[y]
            fertile = self._fertile[y]
            tilled = self._tilled[y]
            for x in range(self.width):
                if fertile[x] and row[x] < 1.0:
                    row[x] = min(1.0, row[x] + rate)
                    # Grass has reclaimed the plot; it is no longer farmland.
                    if tilled[x] and row[x] >= 0.85:
                        tilled[x] = False

    def average(self) -> float:
        """Return the mean grass level over fertile cells (``0`` if none)."""
        total = 0.0
        count = 0
        for y in range(self.height):
            for x in range(self.width):
                if self._fertile[y][x]:
                    total += self._level[y][x]
                    count += 1
        return total / count if count else 0.0
