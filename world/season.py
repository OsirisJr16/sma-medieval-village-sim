"""Seasonal cycle.

Tracks the passage of in-game seasons, which modulate weather probabilities,
crop yields, resource regrowth, and agent needs. The season advances
deterministically based on elapsed steps (see :mod:`config.constants`).

Only the taxonomy and structure are defined; advancement logic is future work.
"""

from __future__ import annotations

from enum import StrEnum

from config.constants import DAYS_PER_SEASON


class SeasonType(StrEnum):
    """The four seasons, in cyclic order."""

    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"

    def next(self) -> SeasonType:
        """Return the season that follows this one, wrapping after winter."""
        order = list(SeasonType)
        return order[(order.index(self) + 1) % len(order)]


class Season:
    """Tracks and advances the current season.

    Attributes:
        current: The current season.
        day_of_season: Elapsed days within the current season.
    """

    def __init__(self, initial: SeasonType = SeasonType.SPRING) -> None:
        """Initialize the seasonal cycle.

        Args:
            initial: The starting season.
        """
        self.current: SeasonType = initial
        self.day_of_season: int = 0

    def advance_day(self) -> None:
        """Advance the calendar by one day, cycling season on rollover."""
        self.day_of_season += 1
        if self.day_of_season >= DAYS_PER_SEASON:
            self.day_of_season = 0
            self.current = self.current.next()
