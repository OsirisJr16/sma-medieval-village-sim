"""Weather subsystem.

Tracks the current atmospheric conditions, which can affect agent behavior
(e.g. seeking shelter), crop growth, and movement costs. Weather transitions are
influenced by the current :mod:`world.season`.

Only the taxonomy and structure are defined; transition logic is future work.
"""

from __future__ import annotations

from enum import StrEnum


class WeatherType(StrEnum):
    """Possible weather conditions."""

    CLEAR = "clear"
    CLOUDY = "cloudy"
    RAIN = "rain"
    STORM = "storm"
    SNOW = "snow"
    FOG = "fog"


class Weather:
    """Holds and evolves the current weather state.

    Attributes:
        current: The current weather condition.
    """

    def __init__(self, initial: WeatherType = WeatherType.CLEAR) -> None:
        """Initialize the weather subsystem.

        Args:
            initial: The starting weather condition.
        """
        self.current: WeatherType = initial

    def step(self) -> None:
        """Advance the weather by one tick.

        Should probabilistically transition ``current`` based on the season and
        the previous condition.
        """
        # TODO: Implement season-weighted stochastic weather transitions.
        raise NotImplementedError("Weather.step is not implemented yet.")
