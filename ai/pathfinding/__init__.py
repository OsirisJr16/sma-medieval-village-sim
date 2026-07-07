"""Pathfinding subpackage.

Navigation and route-planning for agents. Exposes a :class:`Pathfinder`
interface (in :mod:`ai.pathfinding.astar`) so movement code depends on the
abstraction rather than a concrete algorithm, allowing A\\*, JPS, flow fields,
etc. to be swapped freely.
"""
