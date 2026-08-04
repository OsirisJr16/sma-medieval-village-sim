"""World clock.

The simulation's sense of time. One tick is one in-game hour
(``STEPS_PER_DAY`` hours per day), so the clock derives the hour of day, the
day count, and the seasonal calendar from a single tick counter — the source of
truth the rest of the world reads.

Daytime spans ``[_DAY_START, _NIGHT_START)``; :attr:`daylight` ramps up at dawn
and down at dusk so the renderer can tint the world smoothly.
"""

from __future__ import annotations

from typing import Final

from config.constants import STEPS_PER_DAY
from world.season import Season

# Hour boundaries of daylight (24-hour clock).
_DAY_START: Final[int] = 6
_NIGHT_START: Final[int] = 20
# Hours over which light fades in at dawn and out at dusk.
_TWILIGHT: Final[int] = 2


class WorldClock:
    """Tracks in-game time and the seasonal calendar.

    Attributes:
        tick: Total elapsed hours since the start.
        season: The seasonal calendar, advanced on each new day.
    """

    def __init__(self) -> None:
        """Start the clock at day 0, midnight, in the season's default."""
        self.tick: int = 0
        self.season: Season = Season()

    def advance(self) -> None:
        """Advance time by one hour, rolling the calendar over each new day."""
        self.tick += 1
        if self.hour == 0:
            self.season.advance_day()

    @property
    def hour(self) -> int:
        """The hour of the current day, ``0``–``23``."""
        return self.tick % STEPS_PER_DAY

    @property
    def day(self) -> int:
        """The number of whole days elapsed."""
        return self.tick // STEPS_PER_DAY

    @property
    def is_night(self) -> bool:
        """Whether it is currently night (agents sleep)."""
        return not (_DAY_START <= self.hour < _NIGHT_START)

    @property
    def daylight(self) -> float:
        """Ambient light level, ``0.0`` (night) to ``1.0`` (full day)."""
        hour = self.hour
        if _DAY_START + _TWILIGHT <= hour < _NIGHT_START - _TWILIGHT:
            return 1.0
        if _DAY_START <= hour < _DAY_START + _TWILIGHT:
            return (hour - _DAY_START) / _TWILIGHT
        if _NIGHT_START - _TWILIGHT <= hour < _NIGHT_START:
            return (_NIGHT_START - hour) / _TWILIGHT
        return 0.0
