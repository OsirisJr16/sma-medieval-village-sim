"""Pricing model.

Tracks the current unit price of each :class:`~economy.resources.ResourceType`.
A price table can be static or evolve with supply and demand as trades occur,
giving merchants meaningful arbitrage opportunities.

The container structure and public API are defined here; the pricing dynamics
are future work.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from economy.resources import ResourceType


class PriceTable:
    """Holds and updates market prices per resource type.

    Attributes:
        prices: Current unit price keyed by resource type.
    """

    def __init__(self) -> None:
        """Initialize an empty price table."""
        self.prices: dict[ResourceType, float] = {}

    def get_price(self, resource: ResourceType) -> float:
        """Return the current unit price of a resource.

        Args:
            resource: The resource type to price.

        Returns:
            The current unit price.
        """
        # TODO: Return the stored price (with a sensible default/base price).
        raise NotImplementedError("PriceTable.get_price is not implemented yet.")

    def update(self, resource: ResourceType, supply: int, demand: int) -> None:
        """Adjust a resource's price from supply and demand.

        Args:
            resource: The resource type to reprice.
            supply: Units available.
            demand: Units sought.
        """
        # TODO: Move price toward equilibrium based on supply/demand pressure.
        raise NotImplementedError("PriceTable.update is not implemented yet.")
