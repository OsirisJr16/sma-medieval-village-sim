"""Concrete agent states.

Each state pairs a :mod:`ai.behaviors` behavior (what the agent *does*) with the
conditions for leaving it (where the agent goes *next*). Villagers follow

    working --(tired)--> sleeping --(rested)--> working
            --(hungry)-> eating   --(fed)----> working

while wildlife prey follow the simpler

    wandering --(hungry)--> grazing --(fed)--> wandering

Thresholds are deliberately asymmetric: an agent leaves a state only once the
need is comfortably satisfied, which prevents oscillating between states.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.movement import step_away, step_toward, wander
from agents.needs import Need
from agents.perception import is_adjacent, nearest_of_type
from ai.behaviors.eat import EatBehavior
from ai.behaviors.farm import FarmBehavior
from ai.behaviors.graze import GrazeBehavior
from ai.behaviors.sleep import SleepBehavior
from ai.behaviors.trade import TradeBehavior
from ai.behaviors.work import WorkBehavior
from ai.fsm.state import State
from ai.fuzzy import choose_daily_action
from config.constants import AgentType

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


def _is_night(agent: BaseAgent) -> bool:
    """Whether it is night in the agent's world."""
    return agent.model.clock.is_night


def _alarm(agent: BaseAgent) -> tuple[int, int] | None:
    """The position of an active danger the agent has been warned about, if any."""
    getter = getattr(agent, "alarm_position", None)
    return getter() if getter is not None else None


def _daily_next(agent: BaseAgent, current: str) -> str | None:
    """Choose the next daily state via fuzzy desire arbitration.

    Danger always wins; otherwise the strongest fuzzy desire among eat / sleep /
    work decides. An empty granary vetoes eating (there is nothing to eat).
    """
    if _alarm(agent) is not None:
        return agent.THREAT_STATE
    choice = choose_daily_action(agent, current)
    if choice == EatingState.name and agent.model.granary <= 0.0:
        return agent.WORK_STATE
    return choice

#: Hunger levels bounding a prey animal's graze/wander cycle.
_PREY_HUNGRY: Final[float] = 0.55
_PREY_FED: Final[float] = 0.10

#: Cells a hunting predator covers per tick — its speed edge over fleeing prey.
_HUNT_STEPS: Final[int] = 2


class WorkingState(State):
    """Roam the fields doing labor until tired or hungry."""

    name: str = "working"

    def __init__(self) -> None:
        """Bind the work behavior."""
        self._behavior = WorkBehavior()

    def execute(self, agent: BaseAgent) -> None:
        """Perform one tick of labor.

        Args:
            agent: The working agent.
        """
        self._behavior.execute(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Eat if urgently hungry, otherwise sleep at nightfall or when tired.

        Args:
            agent: The working agent.

        Returns:
            The next state's name, or ``None`` to keep working.
        """
        return _daily_next(agent, self.name)


class SleepingState(State):
    """Rest in place until energy is restored."""

    name: str = "sleeping"

    def __init__(self) -> None:
        """Bind the sleep behavior."""
        self._behavior = SleepBehavior()

    def execute(self, agent: BaseAgent) -> None:
        """Recover energy for one tick.

        Args:
            agent: The sleeping agent.
        """
        self._behavior.execute(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Wake at daybreak once rested; sleep through the night.

        Args:
            agent: The sleeping agent.

        Returns:
            The next state's name, or ``None`` to keep sleeping.
        """
        return _daily_next(agent, self.name)


class EatingState(State):
    """Eat in place until hunger is satisfied."""

    name: str = "eating"

    def __init__(self) -> None:
        """Bind the eat behavior."""
        self._behavior = EatBehavior()

    def execute(self, agent: BaseAgent) -> None:
        """Eat for one tick.

        Args:
            agent: The eating agent.
        """
        self._behavior.execute(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Return to work once fed, or go to sleep if exhaustion wins out.

        Args:
            agent: The eating agent.

        Returns:
            The next state's name, or ``None`` to keep eating.
        """
        return _daily_next(agent, self.name)


class AlarmedState(State):
    """Flee the last reported danger, warned by a neighbor (villager)."""

    name: str = "alarmed"

    def execute(self, agent: BaseAgent) -> None:
        """Move away from the warned danger.

        Args:
            agent: The alarmed villager.
        """
        threat = _alarm(agent)
        if threat is not None:
            step_away(agent, threat)
        else:
            wander(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Return to normal life once the danger is no longer known.

        Args:
            agent: The alarmed villager.

        Returns:
            The next state's name, or ``None`` to keep fleeing.
        """
        if _alarm(agent) is not None:
            return None
        return SleepingState.name if _is_night(agent) else agent.WORK_STATE


class DefendingState(State):
    """Advance on the reported danger and fight it (guard)."""

    name: str = "defending"

    def execute(self, agent: BaseAgent) -> None:
        """Close on the nearest wolf and strike it when adjacent.

        Args:
            agent: The defending guard.
        """
        wolf = nearest_of_type(agent, AgentType.WOLF)
        if wolf is not None and wolf.position is not None and agent.position is not None:
            if is_adjacent(agent.position, wolf.position):
                agent.attack(wolf)
            else:
                step_toward(agent, wolf.position)
            return
        # No wolf in sight yet: march toward the last reported position.
        threat = _alarm(agent)
        if threat is not None:
            step_toward(agent, threat)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Stand down once no danger is known or visible.

        Args:
            agent: The defending guard.

        Returns:
            The next state's name, or ``None`` to keep defending.
        """
        if _alarm(agent) is not None or nearest_of_type(agent, AgentType.WOLF) is not None:
            return None
        return SleepingState.name if _is_night(agent) else agent.WORK_STATE


class FarmingState(State):
    """Harvest grass into the granary as the farmer's daily labor."""

    name: str = "farming"

    def __init__(self) -> None:
        """Bind the farm behavior."""
        self._behavior = FarmBehavior()

    def execute(self, agent: BaseAgent) -> None:
        """Reap grass for one tick.

        Args:
            agent: The farming villager.
        """
        self._behavior.execute(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Break for food, rest, or danger like any other worker.

        Args:
            agent: The farming villager.

        Returns:
            The next state's name, or ``None`` to keep farming.
        """
        return _daily_next(agent, self.name)


class TradingState(State):
    """Buy, sell, and haggle food for gold as the merchant's daily labor."""

    name: str = "trading"

    def __init__(self) -> None:
        """Bind the trade behavior."""
        self._behavior = TradeBehavior()

    def execute(self, agent: BaseAgent) -> None:
        """Trade for one tick.

        Args:
            agent: The merchant.
        """
        self._behavior.execute(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Break for food, rest, or danger like any other worker.

        Args:
            agent: The merchant.

        Returns:
            The next state's name, or ``None`` to keep trading.
        """
        return _daily_next(agent, self.name)


class WanderingState(State):
    """Roam the land until hunger sets in (prey)."""

    name: str = "wandering"

    def execute(self, agent: BaseAgent) -> None:
        """Take one wandering step.

        Args:
            agent: The wandering animal.
        """
        wander(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Stop to graze once hungry.

        Args:
            agent: The wandering animal.

        Returns:
            The next state's name, or ``None`` to keep wandering.
        """
        if nearest_of_type(agent, AgentType.WOLF) is not None:
            return FleeingState.name
        if agent.needs.get(Need.HUNGER, 0.0) >= _PREY_HUNGRY:
            return GrazingState.name
        return None


class GrazingState(State):
    """Graze in place until sated (prey)."""

    name: str = "grazing"

    def __init__(self) -> None:
        """Bind the graze behavior (eats grass from the pasture)."""
        self._behavior = GrazeBehavior()

    def execute(self, agent: BaseAgent) -> None:
        """Graze for one tick.

        Args:
            agent: The grazing animal.
        """
        self._behavior.execute(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Resume wandering once fed.

        Args:
            agent: The grazing animal.

        Returns:
            The next state's name, or ``None`` to keep grazing.
        """
        if nearest_of_type(agent, AgentType.WOLF) is not None:
            return FleeingState.name
        if agent.needs.get(Need.HUNGER, 0.0) <= _PREY_FED:
            return WanderingState.name
        return None


class FleeingState(State):
    """Run from the nearest predator until it is out of sight (prey)."""

    name: str = "fleeing"

    def execute(self, agent: BaseAgent) -> None:
        """Step away from the closest wolf.

        Args:
            agent: The fleeing animal.
        """
        wolf = nearest_of_type(agent, AgentType.WOLF)
        if wolf is not None and wolf.position is not None:
            step_away(agent, wolf.position)
        else:
            wander(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Return to wandering once no predator is in sight.

        Args:
            agent: The fleeing animal.

        Returns:
            The next state's name, or ``None`` to keep fleeing.
        """
        if nearest_of_type(agent, AgentType.WOLF) is None:
            return WanderingState.name
        return None


class ProwlingState(State):
    """Roam in search of prey (predator)."""

    name: str = "prowling"

    def execute(self, agent: BaseAgent) -> None:
        """Take one searching step.

        Args:
            agent: The prowling predator.
        """
        wander(agent)

    def next_state(self, agent: BaseAgent) -> str | None:
        """Give chase once prey is spotted.

        Args:
            agent: The prowling predator.

        Returns:
            The next state's name, or ``None`` to keep prowling.
        """
        if nearest_of_type(agent, AgentType.DEER) is not None:
            return HuntingState.name
        return None


class HuntingState(State):
    """Chase and catch the nearest prey (predator)."""

    name: str = "hunting"

    def execute(self, agent: BaseAgent) -> None:
        """Close on the nearest prey, catching it when adjacent.

        Args:
            agent: The hunting predator.
        """
        prey = nearest_of_type(agent, AgentType.DEER)
        if prey is None:
            return
        # A short burst lets the predator close on same-speed fleeing prey.
        for _ in range(_HUNT_STEPS):
            if prey.position is None or agent.position is None:
                return
            if is_adjacent(agent.position, prey.position):
                agent.eat(prey)
                return
            if step_toward(agent, prey.position) is None:
                return

    def next_state(self, agent: BaseAgent) -> str | None:
        """Give up the chase when no prey remains in sight.

        Args:
            agent: The hunting predator.

        Returns:
            The next state's name, or ``None`` to keep hunting.
        """
        if nearest_of_type(agent, AgentType.DEER) is None:
            return ProwlingState.name
        return None
