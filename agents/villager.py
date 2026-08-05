"""Villager agent — base for the human population.

:class:`Villager` is the concrete base class for all human townsfolk. It owns
the human-specific state (needs, home, workplace) and delegates its per-tick
decisions to a finite state machine. Role-specific villagers (farmer, guard,
...) subclass it.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.base_agent import BaseAgent
from agents.needs import Need, clamp
from agents.perception import nearest_of_type
from agents.reproduction import try_reproduce
from ai.fsm.state_machine import StateMachine
from ai.fsm.states import AlarmedState, EatingState, SleepingState, WorkingState
from config.constants import AgentType
from communication.events import Event, EventType

if TYPE_CHECKING:
    import mesa

    from agents.base_agent import Coord
    from buildings.building import BaseBuilding

#: Baseline metabolism applied every tick, regardless of what the villager does.
_HUNGER_PER_TICK: Final[float] = 0.010
_ENERGY_PER_TICK: Final[float] = 0.006
#: Breeding: content, rested villagers occasionally start a family, up to a cap.
_BREED_HUNGER: Final[float] = 0.30
_BREED_ENERGY: Final[float] = 0.60
_BREED_CHANCE: Final[float] = 0.01
_POPULATION_CAP: Final[int] = 150
#: How far a villager can personally spot a wolf (short; they rely on alerts).
_VISION: Final[int] = 3
#: A villager reacts to a warned threat within this many cells...
_ALARM_RADIUS: Final[int] = 9
#: ...and stays wary of it for this many ticks after the last sighting.
_ALARM_MEMORY: Final[int] = 5
#: Survival: hunger at which a villager starves, and the wounds it costs.
_STARVE_HUNGER: Final[float] = 0.97
_STARVE_DAMAGE: Final[float] = 4.0
#: Hit points recovered per safe, fed tick; no healing while hungry or fighting.
_HP_REGEN: Final[float] = 1.0
_REGEN_MAX_HUNGER: Final[float] = 0.7
_NO_REGEN_STATES: frozenset[str] = frozenset({"defending", "alarmed"})


class Villager(BaseAgent):
    """A human inhabitant of the village.

    Attributes:
        agent_type: The villager's role identifier.
        home: The building the villager lives in, if any.
        workplace: The building the villager works at, if any.
    """

    #: Role identifier; overridden by specialized subclasses.
    agent_type: AgentType = AgentType.VILLAGER

    #: FSM state to enter on a threat alert; guards override this to fight.
    THREAT_STATE: str = AlarmedState.name

    #: Daytime labor state; farmers override this to harvest instead of roam.
    WORK_STATE: str = WorkingState.name

    #: Maximum hit points; guards override this to be sturdier fighters.
    MAX_HP: float = 45.0

    def __init__(self, model: mesa.Model) -> None:
        """Initialize the villager.

        Args:
            model: The model the villager belongs to.
        """
        super().__init__(model)
        self.vision = _VISION
        self.hp: float = self.MAX_HP

        # Staggered starting needs so the population does not eat and sleep in
        # lockstep.
        self.needs = {
            Need.HUNGER: self.random.uniform(0.0, 0.4),
            Need.ENERGY: self.random.uniform(0.6, 1.0),
        }

        self.home: BaseBuilding | None = None
        self.workplace: BaseBuilding | None = None
        # Last danger this villager knows of: (position, tick). Populated by the
        # threat handler — either from its own sighting or a neighbor's alert.
        self._alarm: tuple[Coord, int] | None = None
        self.brain = self._build_brain()

        self.model.events.subscribe(EventType.THREAT_DETECTED, self._on_threat)

    def on_remove(self) -> None:
        """Unsubscribe from the event bus when this villager dies."""
        self.model.events.unsubscribe(EventType.THREAT_DETECTED, self._on_threat)

    def step(self) -> None:
        """Advance the villager by one tick: sense danger, metabolize, then act."""
        if self.position is None:
            return

        self._raise_alarm()
        self._metabolize()
        if self.brain is not None:
            self.brain.update()
        self._survive()
        if self.alive:
            self._maybe_breed()

    def _survive(self) -> None:
        """Starve when famished, heal when safe and fed, die at zero HP."""
        if self.needs[Need.HUNGER] >= _STARVE_HUNGER:
            self.hp -= _STARVE_DAMAGE
        elif self.hp < self.MAX_HP and self._can_heal():
            self.hp = min(self.MAX_HP, self.hp + _HP_REGEN)
        if self.hp <= 0:
            self.die(cause="starved")

    def _can_heal(self) -> bool:
        state = self.brain.current.name if self.brain and self.brain.current else ""
        return state not in _NO_REGEN_STATES and self.needs[Need.HUNGER] < _REGEN_MAX_HUNGER

    def alarm_position(self) -> Coord | None:
        """Return the position of an active danger, or ``None`` once it lapses."""
        if self._alarm is None:
            return None
        position, seen = self._alarm
        if self.model.clock.tick - seen > _ALARM_MEMORY:
            return None
        return position

    def _raise_alarm(self) -> None:
        # Personally spotting a wolf broadcasts its position to every villager.
        wolf = nearest_of_type(self, AgentType.WOLF)
        if wolf is not None and wolf.position is not None:
            self.model.events.publish(
                Event(
                    EventType.THREAT_DETECTED,
                    source=self.unique_id,
                    payload={"position": wolf.position},
                )
            )

    def _on_threat(self, event: Event) -> None:
        # React only to dangers close enough to matter; keep the most recent.
        position = event.payload.get("position")
        if position is None or self.position is None:
            return
        if _chebyshev(self.position, position) <= _ALARM_RADIUS:
            self._alarm = (position, self.model.clock.tick)

    def _maybe_breed(self) -> None:
        # Content, rested villagers raise families during the day — not in a panic.
        if self.model.clock.is_night or self.alarm_position() is not None:
            return
        if self.needs[Need.HUNGER] > _BREED_HUNGER or self.needs[Need.ENERGY] < _BREED_ENERGY:
            return
        try_reproduce(self, chance=_BREED_CHANCE, cap=_POPULATION_CAP)

    def _build_brain(self) -> StateMachine:
        """Assemble the villager's state machine; the first state is the initial one."""
        brain = StateMachine(self)
        for state in (WorkingState(), SleepingState(), EatingState(), AlarmedState()):
            brain.add_state(state)
        return brain

    def _metabolize(self) -> None:
        """Apply the constant drift of needs that living costs."""
        self.needs[Need.HUNGER] = clamp(self.needs[Need.HUNGER] + _HUNGER_PER_TICK)
        self.needs[Need.ENERGY] = clamp(self.needs[Need.ENERGY] - _ENERGY_PER_TICK)


def _chebyshev(a: Coord, b: Coord) -> int:
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))
