"""Wolf agent.

Wildlife predator. A :class:`~agents.base_agent.BaseAgent` (not a villager) that
prowls, hunts prey such as deer, and starves without food — closing a simple
predator-prey loop. Its decisions run through a small state machine.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.base_agent import BaseAgent
from agents.needs import Need, clamp
from agents.perception import count_of_type, is_adjacent, nearest_of_type
from agents.reproduction import try_reproduce
from ai.fsm.state_machine import StateMachine
from ai.fsm.states import HuntingState, ProwlingState
from config.constants import AgentType

if TYPE_CHECKING:
    import mesa

    from agents.base_agent import BaseAgent as _BaseAgent

#: Hunger gained each tick; a wolf that reaches full hunger starves.
_HUNGER_PER_TICK: Final[float] = 0.02
#: Hunger removed by eating one prey.
_MEAL: Final[float] = 0.7
#: How far a wolf can spot prey, in cells (keener than its prey).
_VISION: Final[int] = 6
#: Combat: wolves are tough but bite for less than a guard strikes.
_MAX_HP: Final[float] = 100.0
_DAMAGE: Final[float] = 25.0
#: Breeding: efficient hunters, so wolves must stay rare to coexist with prey —
#: they whelp seldom and only when no other wolf is near.
_BREED_HUNGER: Final[float] = 0.20
_BREED_CHANCE: Final[float] = 0.08
_BREED_CROWD: Final[int] = 1
_POPULATION_CAP: Final[int] = 60


class Wolf(BaseAgent):
    """A predatory wild animal.

    Attributes:
        agent_type: Identifier for the wolf agent kind.
    """

    agent_type: AgentType = AgentType.WOLF

    def __init__(self, model: mesa.Model) -> None:
        """Initialize the wolf.

        Args:
            model: The model the wolf belongs to.
        """
        super().__init__(model)
        self.vision = _VISION
        self.hp: float = _MAX_HP
        self.needs = {Need.HUNGER: self.random.uniform(0.2, 0.5)}
        self.brain = self._build_brain()

    def step(self) -> None:
        """Advance the wolf by one tick: get hungrier, starve, fight, or hunt."""
        if not self.alive or self.position is None:
            return

        self.needs[Need.HUNGER] = clamp(self.needs[Need.HUNGER] + _HUNGER_PER_TICK)
        if self.needs[Need.HUNGER] >= 1.0:
            self.die()
            return
        # An adjacent guard is fought before anything else (self-defense).
        guard = nearest_of_type(self, AgentType.GUARD)
        if guard is not None and guard.position is not None:
            if is_adjacent(self.position, guard.position):
                self.attack(guard)
                return
        if self.brain is not None:
            self.brain.update()

    def attack(self, target: _BaseAgent) -> None:
        """Bite a target, killing it if its hit points reach zero.

        Args:
            target: The agent (a guard) being bitten.
        """
        target.hp -= _DAMAGE
        if target.hp <= 0:
            target.die()

    def eat(self, prey: BaseAgent) -> None:
        """Kill a prey animal and sate hunger.

        Args:
            prey: The prey to consume.
        """
        prey.die()
        self.needs[Need.HUNGER] = clamp(self.needs[Need.HUNGER] - _MEAL)
        # A well-fed wolf in a sparse territory may whelp after a hunt.
        if self.needs[Need.HUNGER] <= _BREED_HUNGER:
            if count_of_type(self, AgentType.WOLF) < _BREED_CROWD:
                try_reproduce(self, chance=_BREED_CHANCE, cap=_POPULATION_CAP)

    def _build_brain(self) -> StateMachine:
        """Assemble the predator state machine; the first state is the initial one."""
        brain = StateMachine(self)
        for state in (ProwlingState(), HuntingState()):
            brain.add_state(state)
        return brain
