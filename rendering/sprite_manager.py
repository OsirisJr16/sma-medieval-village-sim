"""Sprite manager.

Loads image assets from :mod:`assets` and caches them so surfaces are decoded
once and reused across frames. Provides lookup by logical key (e.g. an agent
type or terrain type) rather than by file path.

Pygame is imported lazily. Only structure and TODO markers are defined here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # ``pygame.Surface`` — typed loosely to avoid importing pygame at module load.
    Surface = Any


class SpriteManager:
    """Loads and caches sprite surfaces.

    Attributes:
        asset_dir: Root directory sprites are loaded from.
        cache: Loaded surfaces keyed by logical name.
    """

    def __init__(self, asset_dir: str = "assets/sprites") -> None:
        """Initialize the sprite manager.

        Args:
            asset_dir: Directory to load sprite images from.
        """
        self.asset_dir: str = asset_dir
        self.cache: dict[str, Any] = {}

    def load(self, key: str, filename: str) -> None:
        """Load a sprite from disk and cache it under ``key``.

        Args:
            key: Logical name to store the sprite under.
            filename: Image filename relative to ``asset_dir``.
        """
        # TODO: pygame.image.load(...).convert_alpha() and store in cache.
        raise NotImplementedError("SpriteManager.load is not implemented yet.")

    def get(self, key: str) -> Any:
        """Return a previously loaded sprite.

        Args:
            key: The logical name the sprite was cached under.

        Returns:
            The cached surface.
        """
        # TODO: Return cache[key], raising a clear error if missing.
        raise NotImplementedError("SpriteManager.get is not implemented yet.")
