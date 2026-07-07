"""Miner agent.

A :class:`~agents.villager.Villager` who extracts ore and stone from mines and
mountain deposits, supplying raw materials to the blacksmith and builders.
"""

from __future__ import annotations

from agents.villager import Villager
from config.constants import AgentType


class Miner(Villager):
    """A villager specialized in mining ore and stone."""

    agent_type: AgentType = AgentType.MINER

    # TODO: Add mining state (assigned vein/mine, carried ore, pickaxe).
    # TODO: Override step() to drive the travel -> mine -> deposit cycle.
