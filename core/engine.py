"""Simulation/rendering loop orchestrator.

:class:`Engine` decouples *time progression* from *the model*. It drives the
main loop, decides when to advance :class:`~core.model.GameModel` by one step,
and — when rendering is enabled — asks the :class:`~rendering.renderer.Renderer`
to draw the current state and caps the frame rate.

Running headless (no renderer) is a first-class mode, which keeps the simulation
testable and suitable for batch experiments.

No loop logic is implemented yet — only the structural skeleton.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.model import GameModel
    from rendering.renderer import Renderer


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
    ) -> None:
        """Initialize the engine.

        Args:
            model: The simulation model to drive.
            renderer: Optional rendering layer (headless when ``None``).
            target_fps: Target frames per second when rendering.
        """
        self.model: GameModel = model
        self.renderer: Renderer | None = renderer
        self.target_fps: int = target_fps
        self.running: bool = False

    def run(self, max_steps: int = 0) -> None:
        """Run the main loop until stopped.

        Args:
            max_steps: Stop after this many steps; ``0`` runs indefinitely.
        """
        # TODO: Implement the loop:
        #   - process input/events (if rendering),
        #   - call self.model.step(),
        #   - self.renderer.render(self.model) when a renderer is present,
        #   - tick a clock to honor target_fps,
        #   - honor max_steps and self.model.running.
        raise NotImplementedError("Engine.run is not implemented yet.")

    def stop(self) -> None:
        """Request that the main loop terminate."""
        self.running = False
