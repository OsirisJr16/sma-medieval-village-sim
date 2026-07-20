"""Sprite manager.

Builds the surfaces the renderer blits and caches them so decoding and scaling
happen once per cell size. It supplies:

* villager sprites from the ``assets/villagers`` character sheets (first idle
  frame, trimmed to its opaque bounds),
* the grass ground tile and tree/decor props from the fields tileset, and
* a primitive circle marker used when villager art is unavailable.

The tileset art is authored for 32px tiles, so props scale by ``cell / 32`` to
keep their proportions relative to the ground.

Pygame is imported lazily so importing this module needs no display; loading
requires an active display mode and therefore runs on first use, after the
renderer has created the window.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from config.colors import RGB
from world.scenery import SceneryType

if TYPE_CHECKING:
    # ``pygame.Surface`` — typed loosely to avoid importing pygame at module load.
    Surface = Any

# Character sheets are 32x32-frame grids; frame 0 (top-left) is the idle pose.
_FRAME_SIZE = 32
# Native tile size the fields tileset art was drawn for.
_NATIVE_TILE = 32
# Villager height as a fraction of a cell, so agents stay readable.
_VILLAGER_SCALE = 0.9

_TILESET = Path("assets/fileds_tileset")
_OBJECTS = _TILESET / "2 Objects"
_GROUND_TILE = _TILESET / "1 Tiles" / "FieldsTile_38.png"

# Art sources per scenery type. Entries ending in ``*`` expand to every match,
# so each type draws from the full variety the tileset offers.
_SCENERY_ART: dict[SceneryType, tuple[Path, ...]] = {
    SceneryType.TREE: (_OBJECTS / "7 Decor" / "Tree1.png",),
    SceneryType.STUMP: (_OBJECTS / "7 Decor" / "Tree2.png",),
    SceneryType.BUSH: (_OBJECTS / "9 Bush" / "*.png",),
    # Stones 1-6 are pebble-sized; 7-16 are boulders.
    SceneryType.PEBBLE: tuple(_OBJECTS / "4 Stone" / f"{i}.png" for i in range(1, 7)),
    SceneryType.ROCK: tuple(_OBJECTS / "4 Stone" / f"{i}.png" for i in range(7, 17)),
    SceneryType.LOG: (_OBJECTS / "7 Decor" / "Log*.png",),
    SceneryType.BOX: (_OBJECTS / "7 Decor" / "Box*.png",),
    SceneryType.LAMP: (_OBJECTS / "7 Decor" / "Lamp*.png",),
    SceneryType.DIRT: (_OBJECTS / "7 Decor" / "Dirt*.png",),
    SceneryType.FENCE: (_OBJECTS / "2 Fence" / "*.png",),
    SceneryType.CAMP: (_OBJECTS / "8 Camp" / "*.png",),
    SceneryType.SIGN: (_OBJECTS / "3 Pointer" / "*.png",),
    SceneryType.FLOWER: (_OBJECTS / "6 Flower" / "*.png",),
    SceneryType.GRASS_TUFT: (_OBJECTS / "5 Grass" / "*.png",),
}

_MarkerKey = tuple[int, RGB]


class SpriteManager:
    """Loads and caches the surfaces used to draw the world and its agents.

    Attributes:
        villager_dir: Directory holding villager character sheets.
        markers: Circle marker surfaces keyed by ``(diameter, color)``.
    """

    def __init__(self, villager_dir: str = "assets/villagers") -> None:
        """Initialize the sprite manager.

        Args:
            villager_dir: Directory to load villager character sheets from.
        """
        self.villager_dir: Path = Path(villager_dir)
        self.markers: dict[_MarkerKey, Surface] = {}
        self._villagers: dict[int, list[Surface]] = {}
        self._ground: dict[int, Surface] = {}
        self._scenery: dict[int, dict[SceneryType, list[Surface]]] = {}

    def villager_sprites(self, cell: int) -> list[Surface]:
        """Return villager sprites sized for a cell, loading them once.

        Args:
            cell: Cell size in pixels.

        Returns:
            One trimmed, scaled sprite per character sheet (empty if none found).
        """
        sprites = self._villagers.get(cell)
        if sprites is None:
            sprites = [
                self._load_villager(path, cell)
                for path in sorted(self.villager_dir.glob("*.png"))
            ]
            self._villagers[cell] = sprites
        return sprites

    def ground_tile(self, cell: int) -> Surface | None:
        """Return the grass ground tile scaled to ``cell`` pixels."""
        if cell not in self._ground:
            self._ground[cell] = self._load_scaled(_GROUND_TILE, (cell, cell))
        return self._ground[cell]

    def scenery_sprites(self, cell: int) -> dict[SceneryType, list[Surface]]:
        """Return every scenery variant, scaled relative to a cell.

        Args:
            cell: Cell size in pixels.

        Returns:
            Mapping of scenery type to its available sprite variants.
        """
        variants = self._scenery.get(cell)
        if variants is None:
            variants = {
                kind: self._load_variants(sources, cell)
                for kind, sources in _SCENERY_ART.items()
            }
            self._scenery[cell] = variants
        return variants

    def circle(self, diameter: int, color: RGB) -> Surface:
        """Return a cached circular marker surface, creating it on first use.

        Args:
            diameter: Marker diameter in pixels.
            color: Fill color.

        Returns:
            A per-pixel-alpha surface with a centered filled circle.
        """
        key: _MarkerKey = (diameter, color)
        surface = self.markers.get(key)
        if surface is None:
            import pygame

            surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
            radius = diameter / 2
            pygame.draw.circle(surface, color, (radius, radius), radius)
            self.markers[key] = surface
        return surface

    def clear(self) -> None:
        """Drop all cached surfaces."""
        self.markers.clear()
        self._villagers.clear()
        self._ground.clear()
        self._scenery.clear()

    @classmethod
    def _load_variants(cls, sources: tuple[Path, ...], cell: int) -> list[Surface]:
        paths: list[Path] = []
        for source in sources:
            if "*" in source.name:
                paths.extend(sorted(source.parent.glob(source.name)))
            elif source.exists():
                paths.append(source)
        return [cls._load_proportional(path, cell) for path in paths]

    @staticmethod
    def _load_villager(path: Path, cell: int) -> Surface:
        import pygame

        sheet = pygame.image.load(str(path)).convert_alpha()
        frame = sheet.subsurface((0, 0, _FRAME_SIZE, _FRAME_SIZE)).copy()
        # Trim the transparent margin so the sprite's height is the character's.
        trimmed = frame.subsurface(frame.get_bounding_rect()).copy()
        scale = (cell * _VILLAGER_SCALE) / trimmed.get_height()
        size = (max(1, round(trimmed.get_width() * scale)), max(1, round(cell * _VILLAGER_SCALE)))
        return pygame.transform.scale(trimmed, size)

    @staticmethod
    def _load_scaled(path: Path, size: tuple[int, int]) -> Surface | None:
        import pygame

        if not path.exists():
            return None
        return pygame.transform.scale(
            pygame.image.load(str(path)).convert_alpha(), size
        )

    @classmethod
    def _load_proportional(cls, path: Path, cell: int) -> Surface | None:
        if not path.exists():
            return None
        import pygame

        image = pygame.image.load(str(path)).convert_alpha()
        scale = cell / _NATIVE_TILE
        size = (
            max(1, round(image.get_width() * scale)),
            max(1, round(image.get_height() * scale)),
        )
        return pygame.transform.scale(image, size)
