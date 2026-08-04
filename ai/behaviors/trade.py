"""Trade behavior.

A merchant's commercial day, built around directed, negotiated communication:

1. **Settle its mailbox** — answer barter offers from other merchants, executing
   the food-for-gold swap on acceptance (:class:`~communication.message.Message`
   round-trips through each :class:`~communication.mailbox.Mailbox`).
2. **Restock** — take surplus food off the village granary to trade with.
3. **Seek and haggle** — move toward the nearest merchant and, when adjacent and
   holding more food than that neighbor, propose selling a unit for gold.

Food therefore flows from the granary's surplus out to whichever merchant is
short, and gold flows the other way — a small circulating economy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Final

from agents.movement import navigate, step_toward
from agents.perception import nearest_of_type
from ai.behaviors import Behavior
from communication.events import Event, EventType
from communication.message import Message, Performative
from config.constants import AgentType
from economy.resources import ResourceType

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

_FOOD = ResourceType.WHEAT
_GOLD = ResourceType.GOLD

# Granary fill above which merchants may take a unit of surplus food to trade.
_SURPLUS: Final[float] = 0.55
# A merchant offers to sell when it holds this many more units than a neighbor.
_SURPLUS_GAP: Final[int] = 2
# Most food a merchant will hoard.
_STOCK_CAP: Final[int] = 10
# Price of one unit of food, in gold.
_PRICE: Final[int] = 1


class TradeBehavior(Behavior):
    """Exchange food and gold with the granary and with other merchants."""

    name: str = "trade"

    def execute(self, agent: BaseAgent) -> None:
        """Perform one tick of trading.

        Args:
            agent: The merchant.
        """
        self._settle_inbox(agent)
        self._restock(agent)
        self._haggle_with_neighbor(agent)
        self._reposition(agent)

    # --- Directed, negotiated trade ------------------------------------------

    def _settle_inbox(self, agent: BaseAgent) -> None:
        while True:
            message = agent.mailbox.read()
            if message is None:
                return
            if message.performative is Performative.PROPOSE:
                self._consider_offer(agent, message)

    def _consider_offer(self, buyer: BaseAgent, message: Message) -> None:
        seller = message.sender
        food = int(message.content.get("food", 0))
        gold = int(message.content.get("gold", 0))
        can_pay = buyer.inventory.quantity_of(_GOLD) >= gold
        seller_has = seller.alive and seller.inventory.quantity_of(_FOOD) >= food

        if can_pay and seller_has:
            seller.inventory.remove(_FOOD, food)
            buyer.inventory.add(_FOOD, food)
            buyer.inventory.remove(_GOLD, gold)
            seller.inventory.add(_GOLD, gold)
            buyer.model.events.publish(
                Event(
                    EventType.TRADE_COMPLETED,
                    source=buyer.unique_id,
                    payload={"food": food, "gold": gold},
                )
            )
            self._reply(buyer, seller, Performative.ACCEPT)
        else:
            self._reply(buyer, seller, Performative.REJECT)

    @staticmethod
    def _reply(sender: BaseAgent, receiver: BaseAgent, performative: Performative) -> None:
        receiver.mailbox.deliver(
            Message(sender=sender, receiver=receiver, performative=performative)
        )

    # --- Supply and haggling --------------------------------------------------

    def _restock(self, agent: BaseAgent) -> None:
        model = agent.model
        level = model.granary / max(1.0, model.granary_capacity)
        if level > _SURPLUS and agent.inventory.quantity_of(_FOOD) < _STOCK_CAP:
            if model.granary >= 1.0:
                model.granary -= 1.0
                agent.inventory.add(_FOOD, 1)

    def _haggle_with_neighbor(self, agent: BaseAgent) -> None:
        other = nearest_of_type(agent, AgentType.MERCHANT)
        if other is None or other.position is None or agent.position is None:
            return
        # Within reach = same cell or an adjacent one (merchants pile up to trade).
        (ax, ay), (ox, oy) = agent.position, other.position
        if max(abs(ax - ox), abs(ay - oy)) > 1:
            return
        # Sell to a neighbor who is clearly shorter of food and able to pay.
        my_food = agent.inventory.quantity_of(_FOOD)
        if my_food - other.inventory.quantity_of(_FOOD) >= _SURPLUS_GAP:
            if other.inventory.quantity_of(_GOLD) >= _PRICE:
                other.mailbox.deliver(
                    Message(
                        sender=agent,
                        receiver=other,
                        performative=Performative.PROPOSE,
                        content={"food": 1, "gold": _PRICE},
                    )
                )

    def _reposition(self, agent: BaseAgent) -> None:
        other = nearest_of_type(agent, AgentType.MERCHANT)
        if other is not None and other.position is not None:
            step_toward(agent, other.position)  # greedy chase of a moving peer
        else:
            # No peer in sight: A*-route to the market square (map centre), so
            # merchants navigate around forests and rocks to converge there.
            model = agent.model
            navigate(agent, (model.width // 2, model.height // 2))
