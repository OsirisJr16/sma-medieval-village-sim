"""Farmer agent.

A :class:`~agents.villager.Villager` who feeds the settlement: instead of
roaming as generic labor, a farmer's workday is spent harvesting grass from the
pasture into the village granary. The rest of village life (eat, sleep, flee a
threat) is inherited unchanged.
"""

from __future__ import annotations

from agents.villager import Villager
from ai.fsm.state_machine import StateMachine
from ai.fsm.states import (
    AlarmedState,
    EatingState,
    FarmingState,
    SleepingState,
)
from config.constants import AgentType


class Farmer(Villager):
    """A villager specialized in agriculture."""

    agent_type: AgentType = AgentType.FARMER
    WORK_STATE: str = FarmingState.name

    def _build_brain(self) -> StateMachine:
        """Assemble the farmer's state machine (farms instead of roaming)."""
        brain = StateMachine(self)
        for state in (FarmingState(), SleepingState(), EatingState(), AlarmedState()):
            brain.add_state(state)
        return brain
