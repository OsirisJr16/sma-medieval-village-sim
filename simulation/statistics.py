"""Statistics & metrics collection.

:class:`Statistics` wraps Mesa's ``DataCollector`` (and any custom aggregation)
to record time series of interesting quantities — population by type, resource
totals, average needs, market prices — for later analysis or live plotting.

Only structure and TODO markers are defined here.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from core.model import GameModel


class Statistics:
    """Collects and exposes simulation metrics over time.

    Attributes:
        model: The model being measured.
    """

    def __init__(self, model: GameModel) -> None:
        """Initialize the statistics collector.

        Args:
            model: The model to gather metrics from.
        """
        self.model: GameModel = model

        # TODO: Configure a mesa.DataCollector with model- and agent-reporters.

    def collect(self) -> None:
        """Sample and record metrics for the current tick."""
        # TODO: Trigger the underlying DataCollector.collect(self.model).
        raise NotImplementedError("Statistics.collect is not implemented yet.")

    def snapshot(self) -> dict[str, Any]:
        """Return the latest recorded metrics.

        Returns:
            A mapping of metric name to its most recent value.
        """
        # TODO: Return the most recent row of collected data.
        raise NotImplementedError("Statistics.snapshot is not implemented yet.")
