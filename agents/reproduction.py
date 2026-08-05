"""Agent reproduction.

A shared mechanism for agents that breed: place a fresh agent of the same class
on a nearby free cell. The *decision* to breed (being well-fed, not in danger)
stays with each agent; this module only performs the birth and enforces a
population cap so a run cannot explode.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from communication.events import Event, EventType

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent


def _birth_cell(agent: BaseAgent) -> tuple[int, int] | None:
    origin = agent.position
    if origin is None:
        return None
    model = agent.model
    walkable = [cell for cell in model.map.neighbors(origin) if model.is_walkable(*cell)]
    # Prefer an empty cell so newborns spread out; fall back to any walkable one.
    empty = [cell for cell in walkable if model.map.is_empty(cell)]
    candidates = empty or walkable
    return agent.random.choice(candidates) if candidates else None


def try_reproduce(agent: BaseAgent, *, chance: float, cap: int) -> BaseAgent | None:
    """Possibly spawn one offspring of ``agent``'s class beside it.

    Args:
        agent: The parent agent.
        chance: Per-call probability of giving birth.
        cap: Maximum number of agents of this class allowed alive.

    Returns:
        The newborn agent, or ``None`` if no birth happened.
    """
    model = agent.model
    if len(model.agents_by_type.get(type(agent), ())) >= cap:
        return None
    if agent.random.random() >= chance:
        return None

    cell = _birth_cell(agent)
    if cell is None:
        return None

    child = type(agent)(model)
    model.map.place_agent(child, cell)
    model.events.publish(
        Event(EventType.AGENT_SPAWNED, source=agent.unique_id,
              payload={"kind": getattr(child, "agent_type", None)})
    )
    return child
