"""Scenery layer.

Objects that sit *on top* of the terrain: trees, bushes, rocks, fences, camps
and ground clutter such as flowers and grass tufts. Terrain describes the
ground; scenery describes what stands on it.

Each cell holds at most one :class:`SceneryType` (or ``None``). Bulky scenery
blocks movement; ground clutter does not. This is simulation state — the
rendering layer only reads it.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from random import Random


class SceneryType(StrEnum):
    """Kinds of object that can occupy a cell."""

    TREE = "tree"
    STUMP = "stump"
    BUSH = "bush"
    ROCK = "rock"
    LOG = "log"
    FENCE = "fence"
    CAMP = "camp"
    BOX = "box"
    LAMP = "lamp"
    SIGN = "sign"
    PEBBLE = "pebble"
    FLOWER = "flower"
    GRASS_TUFT = "grass_tuft"
    DIRT = "dirt"


# Business rule: bulky scenery blocks movement; flat clutter is walked over.
_BLOCKING: Final[frozenset[SceneryType]] = frozenset(
    {
        SceneryType.TREE,
        SceneryType.STUMP,
        SceneryType.BUSH,
        SceneryType.ROCK,
        SceneryType.LOG,
        SceneryType.FENCE,
        SceneryType.CAMP,
        SceneryType.BOX,
        SceneryType.LAMP,
        SceneryType.SIGN,
    }
)

# Relative spawn frequency of each type when a cell receives scenery.
_WEIGHTS: Final[dict[SceneryType, int]] = {
    SceneryType.GRASS_TUFT: 24,
    SceneryType.FLOWER: 20,
    SceneryType.TREE: 16,
    SceneryType.PEBBLE: 10,
    SceneryType.BUSH: 8,
    SceneryType.DIRT: 6,
    SceneryType.ROCK: 5,
    SceneryType.STUMP: 3,
    SceneryType.LOG: 3,
    SceneryType.FENCE: 2,
    SceneryType.BOX: 1,
    SceneryType.LAMP: 1,
    SceneryType.SIGN: 1,
    SceneryType.CAMP: 1,
}


class Scenery:
    """The scenery layer for the whole map.

    Attributes:
        width: Layer width in cells.
        height: Layer height in cells.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize an empty scenery layer.

        Args:
            width: Layer width in cells.
            height: Layer height in cells.
        """
        self.width: int = width
        self.height: int = height
        self._cells: list[list[SceneryType | None]] = [
            [None] * width for _ in range(height)
        ]

    @classmethod
    def generate(
        cls,
        width: int,
        height: int,
        rng: Random,
        *,
        density: float = 0.35,
    ) -> Scenery:
        """Scatter scenery across an empty layer.

        Args:
            width: Layer width in cells.
            height: Layer height in cells.
            rng: Random source, injected so generation follows the model seed.
            density: Fraction of cells that receive some scenery.

        Returns:
            The generated scenery layer.
        """
        scenery = cls(width, height)
        kinds = list(_WEIGHTS)
        weights = [_WEIGHTS[kind] for kind in kinds]
        for y in range(height):
            for x in range(width):
                if rng.random() < density:
                    scenery.set(x, y, rng.choices(kinds, weights)[0])
        return scenery

    def get(self, x: int, y: int) -> SceneryType | None:
        """Return the scenery at a cell, or ``None`` if empty.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.

        Returns:
            The scenery type occupying ``(x, y)``.
        """
        return self._cells[y][x]

    def set(self, x: int, y: int, scenery_type: SceneryType | None) -> None:
        """Place (or clear) scenery at a cell.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.
            scenery_type: The type to store, or ``None`` to clear.
        """
        self._cells[y][x] = scenery_type

    def blocks(self, x: int, y: int) -> bool:
        """Return whether the scenery at a cell blocks movement.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.

        Returns:
            True if a bulky object occupies ``(x, y)``.
        """
        return self._cells[y][x] in _BLOCKING
