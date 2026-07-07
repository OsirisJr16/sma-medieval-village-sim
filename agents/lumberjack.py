"""Lumberjack agent.

A :class:`~agents.villager.Villager` who fells trees for timber, supplying wood
to builders and the market and clearing forest tiles.
"""

from __future__ import annotations

from agents.villager import Villager
from config.constants import AgentType


class Lumberjack(Villager):
    """A villager specialized in logging."""

    agent_type: AgentType = AgentType.LUMBERJACK

    # TODO: Add logging state (target tree, carried logs, axe).
    # TODO: Override step() to drive the travel -> chop -> haul cycle.
