
from __future__ import annotations

from typing import TYPE_CHECKING

from core.logger import get_logger

if TYPE_CHECKING:
    from core.model import GameModel
    from rendering.renderer import Renderer

_logger = get_logger(__name__)


class Engine:
    """Owns and runs the main simulation loop.

    Attributes:
        model: The simulation model to advance each tick.
        renderer: Optional renderer; ``None`` runs the simulation headless.
        target_fps: Frame-rate cap used when rendering.
        running: Whether the loop should continue.
    """

    def __init__(
        self,
        model: GameModel,
        *,
        renderer: Renderer | None = None,
        target_fps: int = 60,
        simulation_fps: int = 6,
    ) -> None:
        """Initialize the engine.

        Args:
            model: The simulation model to drive.
            renderer: Optional rendering layer (headless when ``None``).
            target_fps: Target frames per second when rendering.
            simulation_fps: Model steps per second when rendering.
        """
        self.model: GameModel = model
        self.renderer: Renderer | None = renderer
        self.target_fps: int = target_fps
        self.simulation_fps: int = simulation_fps
        self.running: bool = False

    def run(self, max_steps: int = 0) -> None:
        """Run the main loop until stopped.

        Dispatches to a rendered loop when a renderer is present, otherwise to
        the headless loop. In both cases ``max_steps`` bounds the simulation
        (``0`` runs indefinitely).

        Args:
            max_steps: Stop after this many steps; ``0`` runs indefinitely.
        """
        if self.renderer is None:
            self._run_headless(max_steps)
        else:
            self._run_rendered(max_steps)

    def _run_headless(self, max_steps: int) -> None:
        self.running = True
        tick = 0
        while self.running and self.model.running:
            if max_steps and tick >= max_steps:
                break
            tick += 1
            _logger.info("Tick %d", tick)
            self.model.step()

        self.running = False
        _logger.info("Simulation finished.")

    def _run_rendered(self, max_steps: int) -> None:
        import pygame

        assert self.renderer is not None
        pygame.init()
        self.renderer.setup()
        clock = pygame.time.Clock()
        frames_per_step = max(1, round(self.target_fps / self.simulation_fps))

        self.running = True
        done = False
        frame = 0
        tick = 0
        try:
            while self.running and self.model.running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False
                    elif event.type == pygame.VIDEORESIZE:
                        self.renderer.resize(event.size)
                    else:
                        self.renderer.handle_event(event)
                if not self.running:
                    break
                self.renderer.handle_input()

                # Advance the model on the fixed simulation cadence; once the
                # step budget is spent, keep the window responsive on its final
                # frame until the user closes it.
                if not done and frame % frames_per_step == 0:
                    if max_steps and tick >= max_steps:
                        done = True
                        _logger.info("Reached max steps (%d).", max_steps)
                    else:
                        tick += 1
                        _logger.info("Tick %d", tick)
                        self.model.step()

                self.renderer.render(self.model)
                clock.tick(self.target_fps)
                frame += 1
        finally:
            self.renderer.shutdown()
            self.running = False
            _logger.info("Simulation finished.")

    def stop(self) -> None:
        """Request that the main loop terminate."""
        self.running = False
