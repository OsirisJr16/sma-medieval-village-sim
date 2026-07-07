"""Farmer agent.

A :class:`~agents.villager.Villager` who cultivates crops at a farm: sowing,
tending, and harvesting food that feeds the village and supplies the market.
"""

from __future__ import annotations

from agents.villager import Villager
from config.constants import AgentType


class Farmer(Villager):
    """A villager specialized in agriculture."""

    agent_type: AgentType = AgentType.FARMER

    # TODO: Add farming state (assigned field, crop stage, tools).
    # TODO: Override step() to drive the sow -> tend -> harvest cycle.
