"""Abstract base agent.

:class:`BaseAgent` is the common ancestor of every agent in the simulation. It
subclasses :class:`mesa.Agent` and adds the cross-cutting scaffolding shared by
all agents: a position, a set of needs, an inventory, a decision-making brain
(state machine / behavior), and a mailbox for message-based communication.

Following Mesa 3.x, ``mesa.Agent`` assigns ``unique_id`` automatically and
registers the agent with ``model.agents``; subclasses call ``super().__init__``
with just the model.

This is an abstract class: concrete agents must implement :meth:`step`. No
behavior is implemented here — only structure, type hints, and TODO markers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

import mesa

if TYPE_CHECKING:
    from ai.fsm.state_machine import StateMachine
    from communication.mailbox import Mailbox
    from economy.inventory import Inventory

# A grid coordinate.
Coord = tuple[int, int]


class BaseAgent(mesa.Agent, ABC):
    """Abstract base class for all simulation agents.

    Attributes:
        position: The agent's current ``(x, y)`` cell, or ``None`` if unplaced.
        needs: Mapping of need name -> level in ``[0.0, 1.0]`` (e.g. hunger,
            energy, safety). Populated by subclasses.
        inventory: The agent's carried items.
        brain: The agent's decision-making state machine.
        mailbox: The agent's inbox/outbox for communication.
        alive: Whether the agent is still active in the simulation.
    """

    def __init__(self, model: mesa.Model) -> None:
        """Initialize the base agent.

        Args:
            model: The model the agent belongs to (Mesa assigns unique_id).
        """
        super().__init__(model)

        self.position: Coord | None = None

        # TODO: Define per-role needs and their decay in subclasses.
        self.needs: dict[str, float] = {}

        # TODO: Attach an Inventory, StateMachine, and Mailbox during setup.
        self.inventory: Inventory | None = None
        self.brain: StateMachine | None = None
        self.mailbox: Mailbox | None = None

        self.alive: bool = True

    @abstractmethod
    def step(self) -> None:
        """Advance the agent by one tick.

        Called by the scheduler each activation. Concrete agents should update
        needs, consult their brain/behaviors, act on the world, and process
        their mailbox.
        """
        raise NotImplementedError

    def perceive(self) -> None:
        """Gather information about the local environment.

        Sense-phase hook, kept separate from :meth:`step` so a perceive → decide
        → act pipeline can be composed uniformly across agent types.
        """
        # TODO: Populate a perception snapshot (neighbors, threats, resources).
        raise NotImplementedError("BaseAgent.perceive is not implemented yet.")
