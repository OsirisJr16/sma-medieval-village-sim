"""Shared agent movement helpers.

Small, reusable spatial actions that several behaviors need. Keeping them here
avoids duplicating the "pick a random walkable neighbor and move there" logic
across villager labor and wildlife wandering.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent, Coord


def wander(agent: BaseAgent) -> Coord | None:
    """Move an agent to a random walkable neighboring cell.

    Args:
        agent: The agent to move (must already be placed).

    Returns:
        The destination cell, or ``None`` if the agent could not move.
    """
    origin = agent.position
    if origin is None:
        return None

    model = agent.model
    options = [cell for cell in model.map.neighbors(origin) if model.is_walkable(*cell)]
    if not options:
        return None

    destination = agent.random.choice(options)
    model.map.move_agent(agent, destination)
    return destination


def step_toward(agent: BaseAgent, target: Coord) -> Coord | None:
    """Take one walkable step that minimizes distance to ``target``.

    Args:
        agent: The agent to move.
        target: The cell to approach.

    Returns:
        The destination cell, or ``None`` if the agent could not move.
    """
    return _greedy_step(agent, target, toward=True)


def step_away(agent: BaseAgent, threat: Coord) -> Coord | None:
    """Take one walkable step that maximizes distance from ``threat``.

    Args:
        agent: The agent to move.
        threat: The cell to flee.

    Returns:
        The destination cell, or ``None`` if the agent could not move.
    """
    return _greedy_step(agent, threat, toward=False)


def _greedy_step(agent: BaseAgent, reference: Coord, *, toward: bool) -> Coord | None:
    origin = agent.position
    if origin is None:
        return None

    model = agent.model
    options = [cell for cell in model.map.neighbors(origin) if model.is_walkable(*cell)]
    if not options:
        return None

    def distance(cell: Coord) -> int:
        return (cell[0] - reference[0]) ** 2 + (cell[1] - reference[1]) ** 2

    destination = min(options, key=distance) if toward else max(options, key=distance)
    model.map.move_agent(agent, destination)
    return destination
