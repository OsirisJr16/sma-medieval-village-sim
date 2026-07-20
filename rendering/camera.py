"""Camera / viewport.

:class:`Camera` maps between world (pixel) coordinates and screen (pixel)
coordinates, applying a pan offset and a zoom factor so large maps can be
explored within a fixed window in later phases.

The camera is deliberately unit-agnostic: callers convert grid cells to world
pixels, and the camera only applies pan/zoom. This keeps tile sizing out of the
camera (Single Responsibility).
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
        wx, wy = world
        return ((wx - self.x) * self.zoom, (wy - self.y) * self.zoom)

    def screen_to_world(self, screen: Vec2) -> Vec2:
        """Convert a screen coordinate to a world coordinate.

        Args:
            screen: The screen-space coordinate.

        Returns:
            The corresponding world-space coordinate.
        """
        sx, sy = screen
        return (sx / self.zoom + self.x, sy / self.zoom + self.y)

    def pan(self, dx: float, dy: float) -> None:
        """Move the camera by a world-space delta.

        Args:
            dx: Horizontal delta.
            dy: Vertical delta.
        """
        self.x += dx
        self.y += dy
