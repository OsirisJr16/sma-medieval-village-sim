"""Heads-up display / UI overlays.

:class:`UI` draws on-screen information over the world view: clock/season,
population counts, selected-agent inspector, and simulation controls. Like the
rest of the rendering layer it only reads from the model.

Pygame is imported lazily. Only structure and TODO markers are defined here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.model import GameModel

    # ``pygame.Surface`` — typed loosely to avoid importing pygame at module load.
    Surface = Any


class UI:
    """Renders HUD elements and overlays.

    Attributes:
        font_dir: Directory UI fonts are loaded from.
    """

    def __init__(self, font_dir: str = "assets/fonts") -> None:
        """Initialize the UI layer.

        Args:
            font_dir: Directory to load UI fonts from.
        """
        self.font_dir: str = font_dir

        # TODO: Load fonts and prepare reusable widgets/panels.

    def draw(self, surface: Any, model: GameModel) -> None:
        """Draw the HUD onto the given surface.

        Args:
            surface: The target surface to draw onto.
            model: The simulation model to read stats from (read-only).
        """
        # TODO: Render clock/season, population, and inspector panels.
        raise NotImplementedError("UI.draw is not implemented yet.")
