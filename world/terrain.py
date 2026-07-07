"""Terrain layer.

Describes the immovable ground beneath every cell — the terrain type, its
traversal cost (for pathfinding), and whether it blocks movement. A
:class:`Terrain` owns a per-cell grid of :class:`TerrainType` values.

Only the type taxonomy and structure are defined here; generation and per-cell
population are future work.
"""

from __future__ import annotations

from enum import StrEnum


class TerrainType(StrEnum):
    """Kinds of terrain a cell can have."""

    GRASS = "grass"
    FOREST = "forest"
    WATER = "water"
    MOUNTAIN = "mountain"
    SAND = "sand"
    DIRT = "dirt"
    SNOW = "snow"

    # TODO: Expose per-type traversal cost and passability, e.g. via a mapping
    #       or a small dataclass, so pathfinding and movement can consult it.


class Terrain:
    """The terrain layer for the whole map.

    Attributes:
        width: Layer width in cells.
        height: Layer height in cells.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize an (empty) terrain layer.

        Args:
            width: Layer width in cells.
            height: Layer height in cells.
        """
        self.width: int = width
        self.height: int = height

        # TODO: Back this with an efficient 2D store (e.g. a numpy array of
        #       TerrainType codes) rather than nested Python lists.

    def get(self, x: int, y: int) -> TerrainType:
        """Return the terrain type at a cell.

        Args:
            x: Cell x-coordinate.
            y: Cell y-coordinate.

        Returns:
            The terrain type at ``(x, y)``.
        """
        # TODO: Read from the backing store.
        raise NotImplementedError("Terrain.get is not implemented yet.")
