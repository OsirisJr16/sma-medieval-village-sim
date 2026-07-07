"""Finite state machine.

:class:`StateMachine` drives an agent's behavior by holding a set of
:class:`~ai.fsm.state.State` objects and the transitions between them, exposing
one current state at a time and running its per-tick logic.

The container structure is defined here; transition evaluation is future work.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

    from ai.fsm.state import State


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

        Args:
            state: The state instance to register (keyed by ``state.name``).
        """
        # TODO: Store the state and optionally set it as the initial state.
        raise NotImplementedError("StateMachine.add_state is not implemented yet.")

    def transition_to(self, name: str) -> None:
        """Switch the active state, firing exit/enter hooks.

        Args:
            name: The name of the state to activate.
        """
        # TODO: Call current.on_exit, set current, call new.on_enter.
        raise NotImplementedError(
            "StateMachine.transition_to is not implemented yet."
        )

    def update(self) -> None:
        """Run the current state's per-tick logic and evaluate transitions."""
        # TODO: Delegate to self.current.execute(self.owner) and check guards.
        raise NotImplementedError("StateMachine.update is not implemented yet.")
