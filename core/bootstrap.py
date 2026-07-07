"""Composition root — dependency wiring for the application.

The ``bootstrap`` function is the single place where concrete implementations
are constructed and injected into one another. Centralizing construction here
keeps the rest of the codebase free of hidden global state and makes the
dependency graph explicit and testable (Dependency Inversion Principle).

At this stage it only assembles the object graph and returns a lightweight
container; it does not start the simulation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from config.settings import get_settings
from core.logger import configure_logging, get_logger

if TYPE_CHECKING:
    from core.engine import Engine
    from core.model import GameModel


@dataclass(slots=True)
class Application:
    """Container holding the fully-wired top-level objects.

    Attributes:
        model: The central simulation model.
        engine: The loop orchestrator bound to ``model``.
    """

    model: GameModel
    engine: Engine


def bootstrap(*, headless: bool = False) -> Application:
    """Construct and wire the application object graph.

    Args:
        headless: If True, do not create a rendering layer.

    Returns:
        A wired :class:`Application` ready to run.
    """
    # Imported lazily to keep the module import graph shallow and cycle-free.
    from core.engine import Engine
    from core.model import GameModel

    settings = get_settings()
    configure_logging(
        settings.log_level,
        to_file=settings.log_to_file,
        log_dir=settings.log_dir,
    )
    logger = get_logger(__name__)
    logger.debug("Bootstrapping application (headless=%s)...", headless)

    # Construct the top-level object graph. Note this only *wires* objects; it
    # does not call model.setup() (world/agent population) which is a later
    # roadmap phase. Constructing objects is real composition — not simulation
    # logic — so the skeleton is runnable end-to-end.
    model = GameModel(
        settings.grid_width,
        settings.grid_height,
        seed=settings.random_seed,
    )

    # TODO: Build a real Renderer when the rendering layer exists, e.g.:
    #   renderer = None if headless or not settings.render_enabled \
    #              else Renderer(width=settings.window_width, ...)
    renderer = None

    engine = Engine(model, renderer=renderer, target_fps=settings.target_fps)

    logger.debug("Application object graph wired.")
    return Application(model=model, engine=engine)
