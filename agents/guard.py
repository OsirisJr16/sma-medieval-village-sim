"""Guard agent.

A :class:`~agents.villager.Villager` who protects the settlement. Guards share
the villager's daily life (work, eat, sleep, breed) but respond to a threat
alert by *advancing* on the danger and fighting it, rather than fleeing. Guards
and wolves trade blows until one dies; guards recover slowly when at peace.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.villager import Villager
from ai.fsm.state_machine import StateMachine
from ai.fsm.states import (
    DefendingState,
    EatingState,
    SleepingState,
    WorkingState,
)
from config.constants import AgentType

if TYPE_CHECKING:
    import mesa

    from agents.base_agent import BaseAgent

_DAMAGE: Final[float] = 30.0
#: Guards see farther than ordinary villagers, to close on threats.
_VISION: Final[int] = 5


class Guard(Villager):
    """A villager specialized in defense.

    Attributes:
        hp: Current hit points; the guard dies at zero.
    """

    agent_type: AgentType = AgentType.GUARD
    THREAT_STATE: str = DefendingState.name
    #: Guards are far sturdier than ordinary villagers.
    MAX_HP: float = 120.0

    def __init__(self, model: mesa.Model) -> None:
        """Initialize the guard.

        Args:
            model: The model the guard belongs to.
        """
        super().__init__(model)
        self.vision = _VISION

    def attack(self, target: BaseAgent) -> None:
        """Strike a target, killing it if its hit points reach zero.

        Args:
            target: The agent (a wolf) being struck.
        """
        target.hp -= _DAMAGE
        if target.hp <= 0:
            target.die(cause="slain")

    def _build_brain(self) -> StateMachine:
        """Assemble the guard's state machine (defends instead of fleeing)."""
        brain = StateMachine(self)
        for state in (WorkingState(), SleepingState(), EatingState(), DefendingState()):
            brain.add_state(state)
        return brain
