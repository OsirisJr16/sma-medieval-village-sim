"""Guard agent.

A :class:`~agents.villager.Villager` who protects the settlement: patrolling,
detecting threats (e.g. wolves), and defending other villagers.
"""

from __future__ import annotations

from agents.villager import Villager
from config.constants import AgentType


class Guard(Villager):
    """A villager specialized in defense and patrolling."""

    agent_type: AgentType = AgentType.GUARD

    # TODO: Add guard state (patrol route, alert level, current target).
    # TODO: Override step() to drive patrol -> detect -> engage behavior.
