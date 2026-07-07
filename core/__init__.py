"""Application core.

Houses the composition root (:mod:`core.bootstrap`), the central Mesa model
(:mod:`core.model`), the loop orchestrator (:mod:`core.engine`), and logging
setup (:mod:`core.logger`). This is the layer that wires the domain packages
together; domain packages must not depend back on ``core``.
"""
