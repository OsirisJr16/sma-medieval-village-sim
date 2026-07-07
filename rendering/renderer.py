"""Main renderer.

:class:`Renderer` owns the Pygame window/surface and draws the simulation each
frame: terrain tiles, buildings, agents, and UI overlays. It reads from the
model but never mutates it.

Pygame is imported lazily so importing this module does not require a display.
Only structure and TODO markers are defined here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.model import GameModel

    from rendering.camera import Camera
    from rendering.sprite_manager import SpriteManager
    from rendering.ui import UI


class Renderer:
    """Draws the simulation to a Pygame surface.

    Attributes:
        width: Window width in pixels.
        height: Window height in pixels.
        tile_size: Size of a single grid tile in pixels.
        camera: The viewport controller.
        sprites: The sprite provider.
        ui: The HUD/overlay renderer.
    """

    def __init__(
        self,
        width: int,
        height: int,
        *,
        tile_size: int = 16,
    ) -> None:
        """Initialize the renderer configuration.

        Args:
            width: Window width in pixels.
            height: Window height in pixels.
            tile_size: Pixel size of one grid tile.
        """
        self.width: int = width
        self.height: int = height
        self.tile_size: int = tile_size

        # TODO: Initialize Pygame, create the display surface and clock here.
        self.camera: Camera | None = None
        self.sprites: SpriteManager | None = None
        self.ui: UI | None = None

    def render(self, model: GameModel) -> None:
        """Draw one frame from the current model state.

        Args:
            model: The simulation model to visualize (read-only).
        """
        # TODO: Clear surface -> draw terrain -> buildings -> agents -> UI ->
        #       flip the display.
        raise NotImplementedError("Renderer.render is not implemented yet.")

    def shutdown(self) -> None:
        """Release rendering resources and quit Pygame."""
        # TODO: pygame.quit() and free cached surfaces.
        raise NotImplementedError("Renderer.shutdown is not implemented yet.")
