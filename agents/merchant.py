"""Merchant agent.

A :class:`~agents.villager.Villager` who trades for a living. A merchant carries
an inventory of food and gold and a mailbox for negotiation: its workday is
spent arbitraging the granary and haggling food-for-gold with other merchants.
Its everyday needs (eat, sleep, flee) are inherited unchanged.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agents.villager import Villager
from ai.fsm.state_machine import StateMachine
from ai.fsm.states import (
    AlarmedState,
    EatingState,
    SleepingState,
    TradingState,
)
from communication.mailbox import Mailbox
from config.constants import AgentType
from economy.inventory import Inventory
from economy.resources import ResourceType

if TYPE_CHECKING:
    import mesa

#: Cells a merchant can see other merchants from.
_VISION = 5


class Merchant(Villager):
    """A villager specialized in trade."""

    agent_type: AgentType = AgentType.MERCHANT
    WORK_STATE: str = TradingState.name

    def __init__(self, model: mesa.Model) -> None:
        """Initialize the merchant with starting stock, gold and a mailbox.

        Args:
            model: The model the merchant belongs to.
        """
        super().__init__(model)
        self.vision = _VISION
        self.inventory = Inventory()
        self.inventory.add(ResourceType.WHEAT, self.random.randint(2, 8))
        self.inventory.add(ResourceType.GOLD, self.random.randint(5, 15))
        self.mailbox = Mailbox()

    def _build_brain(self) -> StateMachine:
        """Assemble the merchant's state machine (trades instead of roaming)."""
        brain = StateMachine(self)
        for state in (TradingState(), SleepingState(), EatingState(), AlarmedState()):
            brain.add_state(state)
        return brain
