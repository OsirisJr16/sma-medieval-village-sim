"""Main renderer.

:class:`Renderer` owns the Pygame window surface and draws the simulation each
frame: the ground tiles, the scenery standing on them, then one sprite per
villager. It is a **read-only observer** of the model — it never mutates
simulation state.

The world may be larger than the window, so only the visible cells are drawn
and the camera can be panned and zoomed. Zoom is expressed as a discrete cell
size, which keeps the pixel art crisp and the sprite cache small.

Pygame is imported lazily so importing this module does not require a display.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from config.colors import DARK_GRAY, UI_BACKGROUND, VILLAGER_COLOR
from rendering.camera import Camera
from rendering.sprite_manager import SpriteManager

if TYPE_CHECKING:
    from core.model import GameModel

    Surface = Any

_CAPTION = "Medieval Village Simulation"
# Selectable cell sizes, smallest to largest.
_ZOOM_LEVELS: tuple[int, ...] = (8, 12, 16, 24, 32, 48, 64)
# Extra rows drawn above the viewport so tall props (trees) scroll in smoothly.
_OVERDRAW_ROWS = 3


def _cell_hash(x: int, y: int, salt: int) -> int:
    """Stable per-cell pseudo-random value, so scenery variants never flicker."""
    return (x * 73856093 ^ y * 19349663 ^ salt) & 0x7FFFFFFF


class Renderer:
    """Draws the simulation to a Pygame surface.

    Attributes:
        width: Initial window width in pixels.
        height: Initial window height in pixels.
        max_tile_size: Largest selectable cell size in pixels.
        show_grid: Whether to overlay cell grid lines.
        camera: The viewport controller.
        sprites: The sprite provider.
        cell_size: Current cell size in pixels (the zoom level).
    """

    def __init__(
        self,
        width: int,
        height: int,
        *,
        max_tile_size: int = 64,
        show_grid: bool = False,
    ) -> None:
        """Initialize the renderer configuration and helpers.

        No Pygame call happens here; the window is created in :meth:`setup`
        after the engine has initialized Pygame.

        Args:
            width: Initial window width in pixels.
            height: Initial window height in pixels.
            max_tile_size: Largest selectable cell size, in pixels.
            show_grid: Whether to overlay cell grid lines.
        """
        self.width: int = width
        self.height: int = height
        self.max_tile_size: int = max_tile_size
        self.show_grid: bool = show_grid
        self.camera: Camera = Camera(width, height)
        self.sprites: SpriteManager = SpriteManager()
        self.cell_size: int = 0
        self._surface: Surface | None = None

    def setup(self) -> None:
        """Create the resizable display window (requires Pygame initialized)."""
        import pygame

        self._surface = pygame.display.set_mode(
            (self.width, self.height), pygame.RESIZABLE
        )
        pygame.display.set_caption(_CAPTION)

    def resize(self, size: tuple[int, int]) -> None:
        """Recreate the display surface at a new window size.

        Args:
            size: The new ``(width, height)`` in pixels.
        """
        import pygame

        self._surface = pygame.display.set_mode(size, pygame.RESIZABLE)

    def handle_event(self, event: Any) -> None:
        """Apply a window event that affects the view (mouse-wheel zoom).

        Args:
            event: A Pygame event.
        """
        import pygame

        if event.type == pygame.MOUSEWHEEL:
            self.zoom(1 if event.y > 0 else -1)

    def handle_input(self) -> None:
        """Pan the camera from the currently held arrow/WASD keys."""
        import pygame

        keys = pygame.key.get_pressed()
        speed = max(6, self.cell_size // 2)
        dx = (keys[pygame.K_RIGHT] or keys[pygame.K_d]) - (
            keys[pygame.K_LEFT] or keys[pygame.K_a]
        )
        dy = (keys[pygame.K_DOWN] or keys[pygame.K_s]) - (
            keys[pygame.K_UP] or keys[pygame.K_w]
        )
        if dx or dy:
            self.camera.pan(dx * speed, dy * speed)

    def zoom(self, direction: int) -> None:
        """Step the zoom level, keeping the viewport centre fixed.

        Args:
            direction: ``+1`` to zoom in, ``-1`` to zoom out.
        """
        # The zoom level is only known once the first frame has sized the world.
        if not self.cell_size or self._surface is None:
            return

        levels = self._zoom_levels()
        current = levels.index(self.cell_size) if self.cell_size in levels else 0
        target = min(max(current + direction, 0), len(levels) - 1)
        if target == current:
            return

        win_w, win_h = self._surface.get_size()
        centre_x = (self.camera.x + win_w / 2) / self.cell_size
        centre_y = (self.camera.y + win_h / 2) / self.cell_size
        self.cell_size = levels[target]
        self.camera.x = centre_x * self.cell_size - win_w / 2
        self.camera.y = centre_y * self.cell_size - win_h / 2

    def render(self, model: GameModel) -> None:
        """Draw one frame from the current model state.

        Args:
            model: The simulation model to visualize (read-only).
        """
        import pygame

        if self._surface is None:
            raise RuntimeError("Renderer.setup() must be called before render().")

        if not self.cell_size:
            self.cell_size = self._initial_cell_size(model)
        self._clamp_camera(model)

        self._surface.fill(UI_BACKGROUND)
        self._draw_world(model)
        if self.show_grid:
            self._draw_grid(model)
        self._draw_villagers(model)
        pygame.display.flip()

    def shutdown(self) -> None:
        """Release rendering resources and quit Pygame."""
        import pygame

        self.sprites.clear()
        pygame.quit()

    def _zoom_levels(self) -> tuple[int, ...]:
        levels = tuple(z for z in _ZOOM_LEVELS if z <= self.max_tile_size)
        return levels or (_ZOOM_LEVELS[0],)

    def _initial_cell_size(self, model: GameModel) -> int:
        """Pick the largest zoom level that shows the whole world, if any."""
        win_w, win_h = self._surface.get_size()
        levels = self._zoom_levels()
        fitting = [
            z
            for z in levels
            if model.width * z <= win_w and model.height * z <= win_h
        ]
        return max(fitting) if fitting else levels[0]

    def _clamp_camera(self, model: GameModel) -> None:
        """Centre each axis when the world fits, otherwise keep it in view."""
        win_w, win_h = self._surface.get_size()
        world_w = model.width * self.cell_size
        world_h = model.height * self.cell_size
        self.camera.x = (
            -((win_w - world_w) // 2)
            if world_w <= win_w
            else min(max(self.camera.x, 0), world_w - win_w)
        )
        self.camera.y = (
            -((win_h - world_h) // 2)
            if world_h <= win_h
            else min(max(self.camera.y, 0), world_h - win_h)
        )

    def _visible_cells(self, model: GameModel) -> tuple[int, int, int, int]:
        """Return the ``(x0, y0, x1, y1)`` cell range covering the viewport."""
        win_w, win_h = self._surface.get_size()
        cell = self.cell_size
        x0 = max(0, int(self.camera.x // cell))
        y0 = max(0, int(self.camera.y // cell) - _OVERDRAW_ROWS)
        x1 = min(model.width, int((self.camera.x + win_w) // cell) + 1)
        y1 = min(model.height, int((self.camera.y + win_h) // cell) + 1)
        return x0, y0, x1, y1

    def _draw_world(self, model: GameModel) -> None:
        cell = self.cell_size
        ground = self.sprites.ground_tile(cell)
        scenery = self.sprites.scenery_sprites(cell)
        x0, y0, x1, y1 = self._visible_cells(model)

        # Rows are drawn top-to-bottom so nearer scenery overlaps what's behind.
        for y in range(y0, y1):
            for x in range(x0, x1):
                ox, oy = self.camera.world_to_screen((x * cell, y * cell))
                if ground is not None:
                    self._surface.blit(ground, (int(ox), int(oy)))
                kind = model.scenery.get(x, y)
                if kind is None:
                    continue
                variants = scenery.get(kind)
                if variants:
                    prop = variants[_cell_hash(x, y, 0xC0FFEE) % len(variants)]
                    self._blit_standing(prop, ox, oy, cell)

    def _blit_standing(self, prop: Surface, ox: float, oy: float, cell: int) -> None:
        """Blit a prop centred on its cell and resting on the cell's base."""
        px = ox + (cell - prop.get_width()) // 2
        py = oy + cell - prop.get_height()
        self._surface.blit(prop, (int(px), int(py)))

    def _draw_grid(self, model: GameModel) -> None:
        import pygame

        cell = self.cell_size
        x0, y0, x1, y1 = self._visible_cells(model)
        top = self.camera.world_to_screen((0, y0 * cell))[1]
        bottom = self.camera.world_to_screen((0, y1 * cell))[1]
        left = self.camera.world_to_screen((x0 * cell, 0))[0]
        right = self.camera.world_to_screen((x1 * cell, 0))[0]
        for x in range(x0, x1 + 1):
            sx = self.camera.world_to_screen((x * cell, 0))[0]
            pygame.draw.line(self._surface, DARK_GRAY, (sx, top), (sx, bottom))
        for y in range(y0, y1 + 1):
            sy = self.camera.world_to_screen((0, y * cell))[1]
            pygame.draw.line(self._surface, DARK_GRAY, (left, sy), (right, sy))

    def _draw_villagers(self, model: GameModel) -> None:
        cell = self.cell_size
        sprites = self.sprites.villager_sprites(cell)
        marker = None if sprites else self.sprites.circle(cell, VILLAGER_COLOR)
        for agent in model.agents:
            position = getattr(agent, "position", None)
            if position is None:
                continue
            # A stable per-villager sprite keeps identities consistent frame to
            # frame without storing presentation state on the model.
            image = sprites[agent.unique_id % len(sprites)] if sprites else marker
            if image is None:
                continue
            ox, oy = self.camera.world_to_screen(
                (position[0] * cell, position[1] * cell)
            )
            self._blit_standing(image, ox, oy, cell)
