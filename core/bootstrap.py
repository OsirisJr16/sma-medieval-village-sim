"""Composition root — dependency wiring for the application.

The ``bootstrap`` function is the single place where concrete implementations
are constructed and injected into one another. Centralizing construction here
keeps the rest of the codebase free of hidden global state and makes the
dependency graph explicit and testable (Dependency Inversion Principle).

At this stage it only assembles the object graph and returns a lightweight
container; it does not start the simulation.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

from config.settings import get_settings
from core.logger import configure_logging, get_logger

if TYPE_CHECKING:
    from core.engine import Engine
    from core.model import GameModel
    from rendering.renderer import Renderer


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
    # Mesa emits verbose INFO-level step logs on its own logger; keep our output
    # limited to the simulation's own progress messages.
    logging.getLogger("MESA").setLevel(logging.WARNING)

    logger = get_logger(__name__)
    logger.debug("Bootstrapping application (headless=%s)...", headless)

    model = GameModel(
        settings.grid_width,
        settings.grid_height,
        num_villagers=settings.initial_villagers,
        num_guards=settings.initial_guards,
        num_prey=settings.initial_prey,
        num_predators=settings.initial_predators,
        torus=settings.grid_torus,
        scenery_density=settings.scenery_density,
        seed=settings.random_seed,
    )

    renderer: Renderer | None = None
    if not headless and settings.render_enabled:
        from rendering.renderer import Renderer

        renderer = Renderer(
            settings.window_width,
            settings.window_height,
            max_tile_size=settings.tile_size,
            show_grid=settings.show_grid,
            show_sidebar=settings.show_sidebar,
        )

    engine = Engine(
        model,
        renderer=renderer,
        target_fps=settings.target_fps,
        simulation_fps=settings.simulation_fps,
    )

    logger.debug("Application object graph wired.")
    return Application(model=model, engine=engine)
