"""Terrain layer.

Describes the immovable ground beneath every cell — the terrain type and
whether it blocks movement. A :class:`Terrain` owns a per-cell grid of
:class:`TerrainType` values and is the simulation's source of truth for the
ground; the rendering layer only reads it.

Objects standing *on* the ground (trees, rocks, fences) live in the scenery
layer, not here.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Final


class TerrainType(StrEnum):
    """Kinds of terrain a cell can have."""

    GRASS = "grass"
    FOREST = "forest"
    WATER = "water"
    MOUNTAIN = "mountain"
    SAND = "sand"
    DIRT = "dirt"
    SNOW = "snow"


# Business rule: agents cannot walk through these terrain types.
_IMPASSABLE: Final[frozenset[TerrainType]] = frozenset(
    {TerrainType.FOREST, TerrainType.WATER, TerrainType.MOUNTAIN}
)


class Terrain:
    """The terrain layer for the whole map.

    Attributes:
        width: Layer width in cells.
        height: Layer height in cells.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize a terrain layer filled with grass.

        Args:
            width: Layer width in cells.
            height: Layer height in cells.
        """
        self.width: int = width
        self.height: int = height
        # TODO: Back this with a numpy array of codes if maps grow large.
        self._cells: list[list[TerrainType]] = [
            [TerrainType.GRASS] * width for _ in range(height)
        ]

    def get(self, x: int, y: int) -> TerrainType:
        """Return the terrain type at a cell.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.

        Returns:
            The terrain type at ``(x, y)``.
        """
        return self._cells[y][x]

    def set(self, x: int, y: int, terrain_type: TerrainType) -> None:
        """Set the terrain type at a cell.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.
            terrain_type: The type to store.
        """
        self._cells[y][x] = terrain_type

    def is_passable(self, x: int, y: int) -> bool:
        """Return whether agents may occupy a cell.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.

        Returns:
            True if the cell's terrain does not block movement.
        """
        return self._cells[y][x] not in _IMPASSABLE
