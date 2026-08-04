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

from config.colors import (
    DARK_GRAY,
    GUARD_COLOR,
    UI_ACCENT,
    UI_BACKGROUND,
    UI_FOREGROUND,
    VILLAGER_COLOR,
    WATER_BLUE,
    WOLF_COLOR,
)
from config.constants import AgentType
from rendering.camera import Camera
from rendering.sprite_manager import SpriteManager
from rendering.ui import UI

if TYPE_CHECKING:
    from core.model import GameModel

    Surface = Any

_CAPTION = "Medieval Village Simulation"
# Selectable cell sizes, smallest to largest.
_ZOOM_LEVELS: tuple[int, ...] = (8, 12, 16, 24, 32, 48, 64)
# Extra rows drawn above the viewport so tall props (trees) scroll in smoothly.
_OVERDRAW_ROWS = 3
# Below this cell size, per-agent state badges are more clutter than signal.
_BADGE_MIN_CELL = 16
# Night tint: color and the opacity it reaches at full darkness.
_NIGHT_COLOR = (10, 14, 44)
_MAX_NIGHT_ALPHA = 165
# Bare-earth tint shown on grazed-down pasture cells.
_DIRT_COLOR = (120, 90, 58)
_FOOD_MAX_ALPHA = 150
# Badge letter and color per agent state.
_STATE_BADGES: dict[str, tuple[str, tuple[int, int, int]]] = {
    "working": ("W", UI_FOREGROUND),
    "eating": ("E", UI_ACCENT),
    "sleeping": ("Z", WATER_BLUE),
    "alarmed": ("!", (235, 110, 90)),
    "defending": ("D", (150, 175, 240)),
    "farming": ("F", (176, 208, 104)),
    "trading": ("$", (224, 190, 96)),
}
# Ring colors marking villager roles on the map.
_ROLE_RINGS: dict[AgentType, tuple[int, int, int]] = {
    AgentType.GUARD: GUARD_COLOR,
    AgentType.FARMER: (150, 200, 96),
    AgentType.MERCHANT: (224, 190, 96),
}


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
        show_sidebar: bool = True,
    ) -> None:
        """Initialize the renderer configuration and helpers.

        No Pygame call happens here; the window is created in :meth:`setup`
        after the engine has initialized Pygame.

        Args:
            width: Initial window width in pixels.
            height: Initial window height in pixels.
            max_tile_size: Largest selectable cell size, in pixels.
            show_grid: Whether to overlay cell grid lines.
            show_sidebar: Whether to reserve and draw the stats sidebar.
        """
        self.width: int = width
        self.height: int = height
        self.max_tile_size: int = max_tile_size
        self.show_grid: bool = show_grid
        self.camera: Camera = Camera(width, height)
        self.sprites: SpriteManager = SpriteManager()
        self.ui: UI | None = UI() if show_sidebar else None
        self.cell_size: int = 0
        self.selected: Any = None
        self.paused: bool = False
        self.sim_fps: int = 0
        self.show_food: bool = True
        self._surface: Surface | None = None
        self._overlay: Surface | None = None
        self._food_tile_cache: Surface | None = None
        self._hud_font: Any = None

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

    def handle_event(self, event: Any, model: GameModel) -> None:
        """Apply a window event affecting the view (zoom, agent selection).

        Args:
            event: A Pygame event.
            model: The model, used to resolve a clicked cell to an agent.
        """
        import pygame

        if event.type == pygame.MOUSEWHEEL:
            self.zoom(1 if event.y > 0 else -1)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._select_at(event.pos, model)

    def handle_key(self, key: int) -> None:
        """Apply a view-related key press (toggle graph scale or food overlay)."""
        import pygame

        if key == pygame.K_l and self.ui is not None:
            self.ui.toggle_scale()
        elif key == pygame.K_f:
            self.show_food = not self.show_food

    def _select_at(self, pos: tuple[int, int], model: GameModel) -> None:
        view_w, _ = self._viewport_size()
        if pos[0] >= view_w or not self.cell_size:
            return  # A click in the sidebar clears nothing.
        cell = (
            int((pos[0] + self.camera.x) / self.cell_size),
            int((pos[1] + self.camera.y) / self.cell_size),
        )
        agents = model.map.agents_at(cell)
        self.selected = agents[0] if agents else None

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

        win_w, win_h = self._viewport_size()
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
        # Drop a selection whose agent has since died.
        if self.selected is not None and getattr(self.selected, "pos", None) is None:
            self.selected = None
        self._clamp_camera(model)

        self._surface.fill(UI_BACKGROUND)
        self._draw_world(model)
        if self.show_grid:
            self._draw_grid(model)
        self._draw_agents(model)
        self._draw_night(model)
        self._draw_path(model)
        self._draw_selection(model)
        if self.ui is not None:
            self.ui.draw(
                self._surface,
                model,
                self._viewport_size()[0],
                selected=self.selected,
                paused=self.paused,
                sim_fps=self.sim_fps,
            )
        else:
            self._draw_clock(model)
        pygame.display.flip()

    def _draw_path(self, model: GameModel) -> None:
        """Trace the selected agent's cached A* route, if it has one."""
        path = getattr(self.selected, "_nav_path", None)
        if not path:
            return
        import pygame

        cell = self.cell_size
        for cx, cy in path:
            ox, oy = self.camera.world_to_screen((cx * cell, cy * cell))
            centre = (int(ox + cell / 2), int(oy + cell / 2))
            pygame.draw.circle(self._surface, UI_ACCENT, centre, max(2, cell // 8))

    def _draw_selection(self, model: GameModel) -> None:
        """Ring the selected agent so it stands out (drawn above the night tint)."""
        if self.selected is None:
            return
        position = getattr(self.selected, "position", None)
        if position is None:
            return
        x0, y0, x1, y1 = self._visible_cells(model)
        if not (x0 <= position[0] < x1 and y0 <= position[1] < y1):
            return
        import pygame

        cell = self.cell_size
        ox, oy = self.camera.world_to_screen((position[0] * cell, position[1] * cell))
        centre = (int(ox + cell / 2), int(oy + cell / 2))
        pygame.draw.circle(self._surface, UI_ACCENT, centre, int(cell * 0.6), 2)

    def shutdown(self) -> None:
        """Release rendering resources and quit Pygame."""
        import pygame

        self.sprites.clear()
        self._overlay = None
        self._hud_font = None
        pygame.quit()

    def _draw_night(self, model: GameModel) -> None:
        """Darken the world according to the world clock's daylight level."""
        alpha = round((1.0 - model.clock.daylight) * _MAX_NIGHT_ALPHA)
        if alpha <= 0:
            return
        import pygame

        # Cover only the world view so the sidebar stays legible at night.
        view_w, _ = self._viewport_size()
        size = (view_w, self._surface.get_height())
        if self._overlay is None or self._overlay.get_size() != size:
            self._overlay = pygame.Surface(size)
            self._overlay.fill(_NIGHT_COLOR)
        self._overlay.set_alpha(alpha)
        self._surface.blit(self._overlay, (0, 0))

    def _draw_clock(self, model: GameModel) -> None:
        """Draw the date and time of day in the top-left corner."""
        import pygame

        if self._hud_font is None:
            self._hud_font = pygame.font.Font(None, 26)
        clock = model.clock
        text = (
            f"{clock.season.current.value.title()}  ·  "
            f"Day {clock.day + 1}  ·  {clock.hour:02d}:00"
        )
        label = self._hud_font.render(text, True, UI_FOREGROUND)
        pad = 6
        backing = pygame.Surface(
            (label.get_width() + pad * 2, label.get_height() + pad * 2)
        )
        backing.set_alpha(160)
        backing.fill(UI_BACKGROUND)
        self._surface.blit(backing, (8, 8))
        self._surface.blit(label, (8 + pad, 8 + pad))

    def _viewport_size(self) -> tuple[int, int]:
        """Size of the world view: the window minus the stats sidebar."""
        win_w, win_h = self._surface.get_size()
        sidebar = self.ui.width if self.ui is not None else 0
        return max(1, win_w - sidebar), win_h

    def _zoom_levels(self) -> tuple[int, ...]:
        levels = tuple(z for z in _ZOOM_LEVELS if z <= self.max_tile_size)
        return levels or (_ZOOM_LEVELS[0],)

    def _initial_cell_size(self, model: GameModel) -> int:
        """Pick the largest zoom level that shows the whole world, if any."""
        win_w, win_h = self._viewport_size()
        levels = self._zoom_levels()
        fitting = [
            z
            for z in levels
            if model.width * z <= win_w and model.height * z <= win_h
        ]
        return max(fitting) if fitting else levels[0]

    def _clamp_camera(self, model: GameModel) -> None:
        """Centre each axis when the world fits, otherwise keep it in view."""
        win_w, win_h = self._viewport_size()
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
        win_w, win_h = self._viewport_size()
        cell = self.cell_size
        x0 = max(0, int(self.camera.x // cell))
        y0 = max(0, int(self.camera.y // cell) - _OVERDRAW_ROWS)
        x1 = min(model.width, int((self.camera.x + win_w) // cell) + 1)
        y1 = min(model.height, int((self.camera.y + win_h) // cell) + 1)
        return x0, y0, x1, y1

    def _draw_world(self, model: GameModel) -> None:
        cell = self.cell_size
        ground = self.sprites.ground_tile(cell)
        field = self.sprites.field_tile(cell)
        scenery = self.sprites.scenery_sprites(cell)
        dirt = self._food_tile(cell) if self.show_food else None
        pasture = model.pasture
        x0, y0, x1, y1 = self._visible_cells(model)

        # Rows are drawn top-to-bottom so nearer scenery overlaps what's behind.
        for y in range(y0, y1):
            for x in range(x0, x1):
                ox, oy = self.camera.world_to_screen((x * cell, y * cell))
                if ground is not None:
                    self._surface.blit(ground, (int(ox), int(oy)))
                if pasture.is_tilled((x, y)):
                    # A farmer's plowed plot reads as an actual field.
                    self._surface.blit(field, (int(ox), int(oy)))
                elif dirt is not None and pasture.is_fertile((x, y)):
                    # Tint grazed-down grass toward bare earth so depletion shows.
                    alpha = int((1.0 - pasture.level((x, y))) * _FOOD_MAX_ALPHA)
                    if alpha > 8:
                        dirt.set_alpha(alpha)
                        self._surface.blit(dirt, (int(ox), int(oy)))
                kind = model.scenery.get(x, y)
                if kind is None:
                    continue
                variants = scenery.get(kind)
                if variants:
                    prop = variants[_cell_hash(x, y, 0xC0FFEE) % len(variants)]
                    self._blit_standing(prop, ox, oy, cell)

    def _food_tile(self, cell: int) -> Surface:
        """A reusable bare-earth tile whose alpha the caller sets per cell."""
        import pygame

        if self._food_tile_cache is None or self._food_tile_cache.get_width() != cell:
            self._food_tile_cache = pygame.Surface((cell, cell))
            self._food_tile_cache.fill(_DIRT_COLOR)
        return self._food_tile_cache

    def _blit_standing(self, prop: Surface, ox: float, oy: float, cell: int) -> None:
        """Blit a prop centred on its cell and resting on the cell's base."""
        px = ox + (cell - prop.get_width()) // 2
        py = oy + cell - prop.get_height()
        self._surface.blit(prop, (int(px), int(py)))

    def _blit_centered(self, prop: Surface, ox: float, oy: float, cell: int) -> None:
        """Blit a prop centred within its cell."""
        px = ox + (cell - prop.get_width()) // 2
        py = oy + (cell - prop.get_height()) // 2
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

    def _draw_agents(self, model: GameModel) -> None:
        cell = self.cell_size
        villagers = self.sprites.villager_sprites(cell)
        prey = self.sprites.prey_sprites(cell)
        wolf = self.sprites.circle(max(6, round(cell * 0.7)), WOLF_COLOR)
        fallback = self.sprites.circle(cell, VILLAGER_COLOR)
        x0, y0, x1, y1 = self._visible_cells(model)
        for agent in model.agents:
            position = getattr(agent, "position", None)
            if position is None or not (x0 <= position[0] < x1 and y0 <= position[1] < y1):
                continue

            kind = getattr(agent, "agent_type", None)
            ox, oy = self.camera.world_to_screen(
                (position[0] * cell, position[1] * cell)
            )
            if kind is AgentType.WOLF:
                self._blit_centered(wolf, ox, oy, cell)
                continue

            # A stable per-agent sprite keeps identities consistent frame to
            # frame without storing presentation state on the model.
            roster = prey if kind is AgentType.DEER else villagers
            image = roster[agent.unique_id % len(roster)] if roster else fallback
            self._blit_standing(image, ox, oy, cell)
            ring = _ROLE_RINGS.get(kind)
            if ring is not None:
                import pygame

                centre = (int(ox + cell / 2), int(oy + cell / 2))
                pygame.draw.circle(self._surface, ring, centre, int(cell * 0.5), 2)
            if kind is not AgentType.DEER and cell >= _BADGE_MIN_CELL:
                self._draw_state_badge(agent, ox, oy, cell)

    def _draw_state_badge(self, agent: Any, ox: float, oy: float, cell: int) -> None:
        """Annotate an agent with a letter showing what it is currently doing."""
        brain = getattr(agent, "brain", None)
        state = getattr(brain, "current", None)
        entry = _STATE_BADGES.get(getattr(state, "name", ""))
        if entry is None:
            return

        label, color = entry
        badge = self.sprites.badge(label, cell, color)
        px = ox + (cell - badge.get_width()) // 2
        self._surface.blit(badge, (int(px), int(oy - badge.get_height() * 0.35)))
