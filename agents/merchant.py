"""Merchant agent.

A :class:`~agents.villager.Villager` who buys and sells goods at the market,
moving resources through the economy and profiting from price differences.
"""

from __future__ import annotations

from agents.villager import Villager
from config.constants import AgentType


class Merchant(Villager):
    """A villager specialized in trade."""

    agent_type: AgentType = AgentType.MERCHANT

    # TODO: Add trading state (gold, wares, target market, price memory).
    # TODO: Override step() to drive the buy-low / sell-high trade loop.
