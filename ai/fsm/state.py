"""FSM state interface.

:class:`State` is the abstract base for every state an agent can be in (e.g.
Idle, Working, Fleeing, Sleeping). A state encapsulates what an agent does while
in it and the transition hooks around it.

Concrete states are implemented later (often backed by an
:mod:`ai.behaviors` behavior). This module defines only the interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


class State(ABC):
    """Abstract base class for a finite-state-machine state.

    Attributes:
        name: Human-readable identifier used for debugging/telemetry.
    """

    #: Overridable, human-readable state name.
    name: str = "state"

    def on_enter(self, agent: BaseAgent) -> None:
        """Hook run once when the agent transitions *into* this state.

        Args:
            agent: The agent entering the state.
        """
        # TODO: Optional setup (e.g. pick a target, start a timer).

    @abstractmethod
    def execute(self, agent: BaseAgent) -> None:
        """Perform this state's per-tick work.

        Args:
            agent: The agent currently in this state.
        """
        raise NotImplementedError

    def on_exit(self, agent: BaseAgent) -> None:
        """Hook run once when the agent transitions *out of* this state.

        Args:
            agent: The agent leaving the state.
        """
        # TODO: Optional teardown (e.g. release a reservation).
