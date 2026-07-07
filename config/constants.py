"""Immutable simulation constants.

Fixed values that never change at runtime and are not user-configurable. Unlike
:mod:`config.settings` (environment-driven, per-run tunables), constants here
describe intrinsic rules of the simulation domain.

Keep this module free of logic — declarations only.
"""

from __future__ import annotations

from enum import IntEnum, StrEnum
from typing import Final

# --- Time --------------------------------------------------------------------
# One simulation "day" is measured in discrete steps (ticks).
STEPS_PER_DAY: Final[int] = 24
DAYS_PER_SEASON: Final[int] = 30
SEASONS_PER_YEAR: Final[int] = 4
STEPS_PER_YEAR: Final[int] = STEPS_PER_DAY * DAYS_PER_SEASON * SEASONS_PER_YEAR

# --- Agent needs (0.0 = depleted, 1.0 = full) --------------------------------
NEED_MIN: Final[float] = 0.0
NEED_MAX: Final[float] = 1.0

# --- Grid --------------------------------------------------------------------
# Number of neighboring cells considered in Moore (8) vs. Von Neumann (4).
MOORE_NEIGHBORS: Final[int] = 8
VON_NEUMANN_NEIGHBORS: Final[int] = 4


class Direction(IntEnum):
    """Cardinal movement directions on the grid."""

    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3


class AgentType(StrEnum):
    """Canonical identifiers for the agent kinds in the simulation."""

    VILLAGER = "villager"
    FARMER = "farmer"
    GUARD = "guard"
    MERCHANT = "merchant"
    MINER = "miner"
    LUMBERJACK = "lumberjack"
    BUILDER = "builder"
    WOLF = "wolf"
    DEER = "deer"


class BuildingType(StrEnum):
    """Canonical identifiers for building kinds."""

    HOUSE = "house"
    FARM = "farm"
    MINE = "mine"
    MARKET = "market"
    BLACKSMITH = "blacksmith"


# TODO: Add domain constants as subsystems are implemented, e.g. base needs
#       decay rates, carrying capacities, day/night thresholds, spawn ratios.
