"""Save / load manager.

:class:`SaveManager` serializes and restores simulation state so runs can be
paused, resumed, and shared. The serialization format (JSON for portability vs.
pickle for fidelity) is an implementation choice deferred to future work.

Only structure and TODO markers are defined here.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.model import GameModel


class SaveManager:
    """Persists and restores simulation state.

    Attributes:
        save_dir: Directory where save files are written and read.
    """

    def __init__(self, save_dir: str = "saves") -> None:
        """Initialize the save manager.

        Args:
            save_dir: Directory for save files.
        """
        self.save_dir: Path = Path(save_dir)

        # TODO: Ensure the save directory exists when saving is first used.

    def save(self, model: GameModel, name: str) -> Path:
        """Serialize the model to a save file.

        Args:
            model: The model to persist.
            name: The save slot / file name.

        Returns:
            The path the save was written to.
        """
        # TODO: Serialize model state (grid, agents, world, economy) to disk.
        raise NotImplementedError("SaveManager.save is not implemented yet.")

    def load(self, name: str) -> GameModel:
        """Reconstruct a model from a save file.

        Args:
            name: The save slot / file name to load.

        Returns:
            The restored model.
        """
        # TODO: Deserialize and rebuild the model from disk.
        raise NotImplementedError("SaveManager.load is not implemented yet.")
