"""Finite state machine.

:class:`StateMachine` drives an agent's behavior by holding a set of
:class:`~ai.fsm.state.State` objects and the transitions between them, exposing
one current state at a time and running its per-tick logic.

The container structure is defined here; transition evaluation is future work.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.logger import get_logger

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

    from ai.fsm.state import State

_logger = get_logger(__name__)


class StateMachine:
    """A simple finite state machine bound to an owning agent.

    Attributes:
        owner: The agent this machine controls.
        states: Registered states keyed by name.
        current: The currently active state, if any.
    """

    def __init__(self, owner: BaseAgent) -> None:
        """Initialize an empty state machine.

        Args:
            owner: The agent whose behavior this machine drives.
        """
        self.owner: BaseAgent = owner
        self.states: dict[str, State] = {}
        self.current: State | None = None

    def add_state(self, state: State) -> None:
        """Register a state with the machine.

        The first state registered becomes the initial state.

        Args:
            state: The state instance to register (keyed by ``state.name``).
        """
        self.states[state.name] = state
        if self.current is None:
            self.current = state
            state.on_enter(self.owner)

    def transition_to(self, name: str) -> None:
        """Switch the active state, firing exit/enter hooks.

        Args:
            name: The name of the state to activate.

        Raises:
            KeyError: If no state is registered under ``name``.
        """
        state = self.states.get(name)
        if state is None:
            raise KeyError(f"Unknown state: {name!r}")
        if state is self.current:
            return

        previous = self.current
        if previous is not None:
            previous.on_exit(self.owner)
        self.current = state
        state.on_enter(self.owner)

        _logger.info(
            "%s %d: %s -> %s",
            type(self.owner).__name__,
            self.owner.unique_id,
            previous.name if previous else "-",
            state.name,
        )

    def update(self) -> None:
        """Evaluate the current state's transition, then run its per-tick logic."""
        if self.current is None:
            return

        target = self.current.next_state(self.owner)
        if target is not None and target != self.current.name:
            self.transition_to(target)
        self.current.execute(self.owner)
