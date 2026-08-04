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


def navigate(agent: BaseAgent, goal: Coord) -> Coord | None:
    """Take one step toward ``goal`` along an A* path around obstacles.

    The path is cached on the agent and only recomputed when the goal changes or
    the cached route becomes stale — so this stays cheap for a fixed destination.
    Falls back to a greedy step when no path exists.

    Args:
        agent: The agent to move.
        goal: The destination cell.

    Returns:
        The destination cell stepped to, or ``None`` if the agent could not move.
    """
    origin = agent.position
    if origin is None or origin == goal:
        return None

    path = getattr(agent, "_nav_path", None)
    if getattr(agent, "_nav_goal", None) != goal or not _next_is_reachable(agent, origin, path):
        path = agent.model.pathfinder.find_path(origin, goal)
        agent._nav_goal = goal
        agent._nav_path = path

    if not path:  # Unreachable via A*: nudge greedily instead of freezing.
        return step_toward(agent, goal)

    destination = path[0]
    agent.model.map.move_agent(agent, destination)
    agent._nav_path = path[1:]
    return destination


def _next_is_reachable(agent: BaseAgent, origin: Coord, path: list[Coord] | None) -> bool:
    if not path:
        return False
    nxt = path[0]
    return (
        max(abs(origin[0] - nxt[0]), abs(origin[1] - nxt[1])) == 1
        and agent.model.is_walkable(*nxt)
    )


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
