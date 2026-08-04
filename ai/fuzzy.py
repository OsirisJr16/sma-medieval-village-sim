"""Fuzzy decision helpers.

The FSM used to pick a daily action with hard thresholds (hunger >= 0.70 →
eat, energy <= 0.25 → sleep). This module replaces those crisp cut-offs with
**graded desires**: each candidate action gets a strength from fuzzy membership
functions of the agent's needs and the time of day, and the strongest desire
wins. A stickiness bonus for the current activity provides hysteresis so agents
don't dither on the boundary between two comparable desires.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agents.needs import Need

if TYPE_CHECKING:
    from agents.base_agent import BaseAgent

# Extra desire the current activity keeps, to avoid flip-flopping.
_STICKINESS = 0.15


def ramp_up(x: float, lo: float, hi: float) -> float:
    """Rising membership: ``0`` below ``lo``, ``1`` above ``hi``, linear between."""
    if x <= lo:
        return 0.0
    if x >= hi:
        return 1.0
    return (x - lo) / (hi - lo)


def ramp_down(x: float, lo: float, hi: float) -> float:
    """Falling membership: ``1`` below ``lo``, ``0`` above ``hi``."""
    return 1.0 - ramp_up(x, lo, hi)


def daily_desires(agent: BaseAgent) -> dict[str, float]:
    """Return the fuzzy desire for each daily action, keyed by state name.

    Args:
        agent: The villager-kind agent deciding what to do.

    Returns:
        Desire strengths for eating, sleeping and this agent's work activity.
    """
    hunger = agent.needs.get(Need.HUNGER, 0.0)
    energy = agent.needs.get(Need.ENERGY, 1.0)
    night = agent.model.clock.is_night

    eat = ramp_up(hunger, 0.45, 0.9)
    # Sleepy when tired, and strongly so at night.
    sleep = max(ramp_down(energy, 0.2, 0.6), 0.85 if night else 0.0)
    # A steady wish to be productive, all but suppressed after dark.
    work = 0.35 * (0.15 if night else 1.0)

    return {"eating": eat, "sleeping": sleep, agent.WORK_STATE: work}


def choose_daily_action(agent: BaseAgent, current: str) -> str:
    """Return the state name of the strongest desire (current activity is sticky).

    Args:
        agent: The deciding agent.
        current: The name of the agent's current state.

    Returns:
        The chosen action's state name.
    """
    desires = daily_desires(agent)

    def score(action: str) -> float:
        return desires[action] + (_STICKINESS if action == current else 0.0)

    return max(desires, key=score)
