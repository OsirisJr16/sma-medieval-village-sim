"""Agent activation scheduler.

In Mesa 3.x the legacy ``mesa.time`` schedulers are gone; activation is expressed
directly on the model's ``AgentSet`` (e.g. ``model.agents.shuffle_do("step")``).
:class:`Scheduler` is a thin strategy wrapper over that API so the activation
*order* is a single, swappable decision rather than being hard-coded in the
model's ``step``.

Only structure and TODO markers are defined here.
"""

from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import mesa


class ActivationOrder(StrEnum):
    """Order in which agents are activated each step."""

    #: Same order every step (deterministic).
    SEQUENTIAL = "sequential"
    #: Shuffled each step (Mesa's RandomActivation equivalent).
    RANDOM = "random"
    #: All agents compute, then all apply (simultaneous update).
    SIMULTANEOUS = "simultaneous"
    #: Activate one type at a time, in a fixed order.
    BY_TYPE = "by_type"


class Scheduler:
    """Strategy wrapper around Mesa's AgentSet activation.

    Attributes:
        model: The model whose agents are activated.
        order: The activation order strategy.
    """

    def __init__(
        self,
        model: mesa.Model,
        order: ActivationOrder = ActivationOrder.RANDOM,
    ) -> None:
        """Initialize the scheduler.

        Args:
            model: The model whose ``agents`` AgentSet will be activated.
            order: The activation order strategy to apply.
        """
        self.model: mesa.Model = model
        self.order: ActivationOrder = order

    def step(self) -> None:
        """Activate all agents for one tick according to :attr:`order`.

        For example, ``RANDOM`` maps to ``self.model.agents.shuffle_do("step")``
        and ``SEQUENTIAL`` to ``self.model.agents.do("step")``.
        """
        # TODO: Dispatch to the matching AgentSet call based on self.order.
        raise NotImplementedError("Scheduler.step is not implemented yet.")
