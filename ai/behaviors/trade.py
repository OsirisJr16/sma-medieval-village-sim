"""Trade behavior.

Buys and/or sells goods at a market, exchanging items and currency according to
prevailing prices. Primarily used by merchants but available to any agent.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ai.behaviors import Behavior

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


class TradeBehavior(Behavior):
    """Exchange goods and currency at a market."""

    name: str = "trade"

    def execute(self, agent: BaseAgent) -> None:
        """Perform one tick of trading at a market.

        Args:
            agent: The agent performing the behavior.
        """
        # TODO: Travel to a market, place buy/sell orders, settle trades.
        raise NotImplementedError("TradeBehavior.execute is not implemented yet.")
