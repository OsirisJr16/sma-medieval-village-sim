"""Behaviors subpackage.

A *behavior* is a self-contained, reusable unit of agent action (eat, sleep,
work, trade, patrol) that can be triggered by a state machine, a behavior tree,
or a planner. Defining behaviors independently of the FSM keeps them reusable
across different decision-making techniques.

This module declares the abstract :class:`Behavior` interface that every
concrete behavior implements.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


class Behavior(ABC):
    """Abstract base class for a reusable agent behavior.

    Attributes:
        name: Human-readable identifier used for debugging/telemetry.
    """

    #: Overridable, human-readable behavior name.
    name: str = "behavior"

    def can_execute(self, agent: BaseAgent) -> bool:
        """Return whether this behavior is currently applicable to the agent.

        Used by planners/selectors as a precondition check.

        Args:
            agent: The agent considering this behavior.

        Returns:
            True if the behavior may run now. Defaults to ``True``.
        """
        # TODO: Override with real preconditions where relevant.
        return True

    @abstractmethod
    def execute(self, agent: BaseAgent) -> None:
        """Perform one tick of this behavior for the agent.

        Args:
            agent: The agent performing the behavior.
        """
        raise NotImplementedError
