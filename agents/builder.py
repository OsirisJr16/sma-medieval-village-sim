"""Builder agent.

A :class:`~agents.villager.Villager` who constructs and repairs buildings using
wood and stone, expanding the village over time.
"""

from __future__ import annotations

from agents.villager import Villager
from config.constants import AgentType


class Builder(Villager):
    """A villager specialized in construction."""

    agent_type: AgentType = AgentType.BUILDER

    # TODO: Add construction state (active build site, progress, materials).
    # TODO: Override step() to drive the gather -> build -> repair cycle.
