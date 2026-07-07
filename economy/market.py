"""Marketplace.

The :class:`Market` is where agents buy and sell goods. It collects buy/sell
orders, matches them using the current :class:`~economy.prices.PriceTable`, and
transfers resources and currency between participants' inventories.

The container structure and public API are defined here; order matching is
future work.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from economy.prices import PriceTable
    from economy.resources import ResourceType


class Market:
    """A resource exchange that matches buyers and sellers.

    Attributes:
        prices: The price table governing trade values.
    """

    def __init__(self, prices: PriceTable) -> None:
        """Initialize the market.

        Args:
            prices: The price table used to value trades.
        """
        self.prices: PriceTable = prices

        # TODO: Add order books (buy/sell) per resource type.

    def place_order(
        self,
        agent: object,
        resource: ResourceType,
        quantity: int,
        *,
        is_buy: bool,
    ) -> None:
        """Submit a buy or sell order.

        Args:
            agent: The ordering agent (must expose an inventory).
            resource: The resource type to trade.
            quantity: The number of units to trade.
            is_buy: True for a buy order, False for a sell order.
        """
        # TODO: Record the order and attempt to match it.
        raise NotImplementedError("Market.place_order is not implemented yet.")

    def clear(self) -> None:
        """Match outstanding orders and settle trades for this tick."""
        # TODO: Match compatible orders, transfer goods/currency, update prices.
        raise NotImplementedError("Market.clear is not implemented yet.")
