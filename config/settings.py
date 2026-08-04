"""Typed application settings.

Settings are declared with :mod:`pydantic-settings` so they can be populated
from environment variables and/or a local ``.env`` file (see ``.env.example``)
with full validation and type coercion.

Access the singleton through :func:`get_settings` rather than instantiating
:class:`Settings` directly — this keeps configuration consistent across the
application and cheap to reuse.

This module contains configuration scaffolding only; it holds no simulation
logic.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed, environment-driven configuration.

    Every field maps to an ``MVS_``-prefixed environment variable. Defaults are
    chosen so the project runs out of the box without a ``.env`` file.
    """

    model_config = SettingsConfigDict(
        env_prefix="MVS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
    )

    # --- General -------------------------------------------------------------
    env: Literal["development", "testing", "production"] = "development"
    debug: bool = True
    random_seed: int | None = Field(
        default=None,
        description="Seed for deterministic runs; None means non-deterministic.",
    )

    # --- Logging -------------------------------------------------------------
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_to_file: bool = False
    log_dir: str = "logs"

    # --- World / grid --------------------------------------------------------
    grid_width: int = Field(default=80, ge=1)
    grid_height: int = Field(default=80, ge=1)
    grid_torus: bool = False
    scenery_density: float = Field(
        default=0.35, ge=0.0, le=1.0, description="Fraction of cells carrying scenery."
    )

    # --- Simulation ----------------------------------------------------------
    max_steps: int = Field(default=0, ge=0, description="0 = run until stopped.")
    initial_villagers: int = Field(default=40, ge=0)
    initial_guards: int = Field(default=8, ge=0)
    initial_farmers: int = Field(default=12, ge=0)
    initial_merchants: int = Field(default=6, ge=0)
    initial_prey: int = Field(default=50, ge=0)
    initial_predators: int = Field(default=4, ge=0)

    # --- Rendering (Pygame) --------------------------------------------------
    render_enabled: bool = True
    window_width: int = Field(default=1280, ge=1)
    window_height: int = Field(default=720, ge=1)
    target_fps: int = Field(default=60, ge=1)
    # Largest a grid cell may be drawn; the world otherwise scales to fill the
    # (resizable) window.
    tile_size: int = Field(default=64, ge=1)
    show_grid: bool = False
    show_sidebar: bool = True
    # Model steps per second when rendering; decoupled from target_fps so the
    # window stays smooth/responsive while movement remains watchable.
    simulation_fps: int = Field(default=3, ge=1)

    # --- Persistence ---------------------------------------------------------
    save_dir: str = "saves"

    # TODO: Add nested settings groups (WorldSettings, RenderSettings, ...) as
    #       the configuration surface grows, to keep this class cohesive.


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide :class:`Settings` singleton.

    Cached so environment/`.env` parsing happens exactly once.

    Returns:
        The validated settings instance.
    """
    return Settings()
