"""Seasonal cycle.

Tracks the passage of in-game seasons, which modulate weather probabilities,
crop yields, resource regrowth, and agent needs. The season advances
deterministically based on elapsed steps (see :mod:`config.constants`).

Only the taxonomy and structure are defined; advancement logic is future work.
"""

from __future__ import annotations

from enum import StrEnum


class SeasonType(StrEnum):
    """The four seasons, in cyclic order."""

    SPRING = "spring"
    SUMMER = "summer"
    AUTUMN = "autumn"
    WINTER = "winter"


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

    def step(self) -> None:
        """Advance the seasonal clock by one tick.

        Should roll over to the next season after ``DAYS_PER_SEASON`` days.
        """
        # TODO: Advance day_of_season and cycle `current` on rollover.
        raise NotImplementedError("Season.step is not implemented yet.")
