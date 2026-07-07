"""Camera / viewport.

:class:`Camera` maps between world (grid) coordinates and screen (pixel)
coordinates, supporting panning and zooming so large maps can be explored within
a fixed window.

Only structure and TODO markers are defined here.
"""

from __future__ import annotations

# A pixel or world coordinate pair.
Vec2 = tuple[float, float]


class Camera:
    """Controls the visible region of the world.

    Attributes:
        x: World-space x of the camera's top-left corner.
        y: World-space y of the camera's top-left corner.
        zoom: Zoom factor (1.0 = no scaling).
        viewport_width: Viewport width in pixels.
        viewport_height: Viewport height in pixels.
    """

    def __init__(self, viewport_width: int, viewport_height: int) -> None:
        """Initialize the camera at the origin.

        Args:
            viewport_width: Viewport width in pixels.
            viewport_height: Viewport height in pixels.
        """
        self.x: float = 0.0
        self.y: float = 0.0
        self.zoom: float = 1.0
        self.viewport_width: int = viewport_width
        self.viewport_height: int = viewport_height

    def world_to_screen(self, world: Vec2) -> Vec2:
        """Convert a world coordinate to a screen coordinate.

        Args:
            world: The world-space coordinate.

        Returns:
            The corresponding screen-space coordinate.
        """
        # TODO: Apply pan (x, y) and zoom.
        raise NotImplementedError("Camera.world_to_screen is not implemented yet.")

    def screen_to_world(self, screen: Vec2) -> Vec2:
        """Convert a screen coordinate to a world coordinate.

        Args:
            screen: The screen-space coordinate.

        Returns:
            The corresponding world-space coordinate.
        """
        # TODO: Invert pan (x, y) and zoom.
        raise NotImplementedError("Camera.screen_to_world is not implemented yet.")

    def pan(self, dx: float, dy: float) -> None:
        """Move the camera by a world-space delta.

        Args:
            dx: Horizontal delta.
            dy: Vertical delta.
        """
        # TODO: Offset x/y, clamped to world bounds.
        raise NotImplementedError("Camera.pan is not implemented yet.")
