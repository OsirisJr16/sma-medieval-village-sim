"""Agents package.

Defines the Mesa agents that inhabit the simulation: an abstract
:class:`agents.base_agent.BaseAgent`, a :class:`agents.villager.Villager` base
for the human population, role-specialized villagers (farmer, guard, merchant,
miner, lumberjack, builder), and wildlife (wolf, deer).

Agents depend on AI subsystems (state machines, behaviors, pathfinding) through
their interfaces, so new decision-making strategies can be introduced without
modifying agent classes.
"""
