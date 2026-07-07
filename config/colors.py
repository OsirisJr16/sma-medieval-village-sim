"""Named color palette.

Central RGB color definitions used by the rendering layer. Keeping colors in one
place makes theming and accessibility adjustments trivial and avoids magic
tuples scattered across the codebase.

A :data:`RGB` is an ``(red, green, blue)`` tuple with each channel in 0-255.
"""

from __future__ import annotations

from typing import Final

# Type alias for readability across the rendering package.
RGB = tuple[int, int, int]

# --- Base palette ------------------------------------------------------------
BLACK: Final[RGB] = (0, 0, 0)
WHITE: Final[RGB] = (255, 255, 255)
GRAY: Final[RGB] = (128, 128, 128)
LIGHT_GRAY: Final[RGB] = (200, 200, 200)
DARK_GRAY: Final[RGB] = (64, 64, 64)

# --- Terrain -----------------------------------------------------------------
GRASS_GREEN: Final[RGB] = (86, 155, 66)
FOREST_GREEN: Final[RGB] = (34, 102, 51)
WATER_BLUE: Final[RGB] = (52, 122, 183)
MOUNTAIN_GRAY: Final[RGB] = (120, 120, 120)
SAND: Final[RGB] = (214, 197, 141)
DIRT_BROWN: Final[RGB] = (120, 85, 55)
SNOW: Final[RGB] = (235, 240, 245)

# --- Agents ------------------------------------------------------------------
VILLAGER_COLOR: Final[RGB] = (222, 184, 135)
GUARD_COLOR: Final[RGB] = (70, 70, 160)
MERCHANT_COLOR: Final[RGB] = (200, 160, 40)
WOLF_COLOR: Final[RGB] = (90, 90, 90)
DEER_COLOR: Final[RGB] = (150, 111, 51)

# --- UI ----------------------------------------------------------------------
UI_BACKGROUND: Final[RGB] = (30, 30, 38)
UI_FOREGROUND: Final[RGB] = (230, 230, 230)
UI_ACCENT: Final[RGB] = (218, 165, 32)

# TODO: Provide a season-aware palette mapping so terrain tints shift with the
#       seasonal cycle (see world/season.py).
