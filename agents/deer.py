"""Deer agent.

Wildlife prey. A :class:`~agents.base_agent.BaseAgent` (not a villager) that
wanders and grazes, driven by a small state machine. It is deliberately kept
simple; fleeing from predators is added alongside the wolf.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.base_agent import BaseAgent
from agents.needs import Need, clamp
from agents.perception import count_of_type
from agents.reproduction import try_reproduce
from ai.fsm.state_machine import StateMachine
from ai.fsm.states import FleeingState, GrazingState, WanderingState
from config.constants import AgentType

if TYPE_CHECKING:
    import mesa

#: Hunger gained each tick from living and moving.
_HUNGER_PER_TICK: Final[float] = 0.012
#: How far a deer can spot a predator, in cells.
_VISION: Final[int] = 4
#: Breeding: well-fed deer calve readily so prey out-breed their predators.
#: A generous local-crowd ceiling still stops any single spot from exploding.
_BREED_HUNGER: Final[float] = 0.50
_BREED_CHANCE: Final[float] = 0.18
_BREED_COST: Final[float] = 0.12
_BREED_CROWD: Final[int] = 8
_POPULATION_CAP: Final[int] = 300


class Deer(BaseAgent):
    """A herbivorous wild animal.

    Attributes:
        agent_type: Identifier for the deer agent kind.
    """

    agent_type: AgentType = AgentType.DEER

    def __init__(self, model: mesa.Model) -> None:
        """Initialize the deer.

        Args:
            model: The model the deer belongs to.
        """
        super().__init__(model)
        self.vision = _VISION
        self.needs = {Need.HUNGER: self.random.uniform(0.0, 0.4)}
        self.brain = self._build_brain()

    def step(self) -> None:
        """Advance the deer by one tick: get hungrier, then act on its state."""
        if self.position is None:
            return

        self.needs[Need.HUNGER] = clamp(self.needs[Need.HUNGER] + _HUNGER_PER_TICK)
        if self.brain is not None:
            self.brain.update()
        self._maybe_breed()

    def _maybe_breed(self) -> None:
        # Only breed when well-fed and not currently fleeing a predator.
        if self.needs[Need.HUNGER] > _BREED_HUNGER:
            return
        if self.brain is not None and self.brain.current is not None:
            if self.brain.current.name == FleeingState.name:
                return
        if count_of_type(self, AgentType.DEER) >= _BREED_CROWD:
            return
        if try_reproduce(self, chance=_BREED_CHANCE, cap=_POPULATION_CAP):
            self.needs[Need.HUNGER] = clamp(self.needs[Need.HUNGER] + _BREED_COST)

    def _build_brain(self) -> StateMachine:
        """Assemble the prey state machine; the first state is the initial one."""
        brain = StateMachine(self)
        for state in (WanderingState(), GrazingState(), FleeingState()):
            brain.add_state(state)
        return brain
