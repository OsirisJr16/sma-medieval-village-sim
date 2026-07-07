"""AI package.

Decision-making subsystems for agents, each behind a stable interface so they
can evolve or be swapped independently:

* :mod:`ai.fsm` — finite state machines.
* :mod:`ai.behaviors` — reusable, composable behaviors.
* :mod:`ai.pathfinding` — navigation / route planning.

The architecture is intentionally open to additional techniques (Behavior Trees,
GOAP, Reinforcement Learning, Genetic Algorithms) added as sibling subpackages.
"""
