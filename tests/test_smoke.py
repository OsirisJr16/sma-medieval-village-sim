"""Smoke tests for the architecture skeleton.

These tests assert only that the project is *structurally* sound — packages
import cleanly, key classes exist, and inheritance/abstractness are wired
correctly. They intentionally do **not** exercise simulation behavior (there is
none yet); most methods are expected to raise ``NotImplementedError``.
"""

from __future__ import annotations

import pytest


def test_config_layer_imports() -> None:
    """Configuration modules import and expose their singletons/constants."""
    from config import colors, constants
    from config.settings import Settings, get_settings

    assert isinstance(get_settings(), Settings)
    assert get_settings() is get_settings()  # Cached singleton.
    assert constants.STEPS_PER_YEAR > 0
    assert isinstance(colors.GRASS_GREEN, tuple) and len(colors.GRASS_GREEN) == 3


def test_pure_domain_imports() -> None:
    """Dependency-light domain packages import without Mesa/Pygame."""
    from ai.behaviors import Behavior
    from ai.behaviors.eat import EatBehavior
    from communication.event_bus import EventBus
    from communication.message import Message, Performative
    from economy.inventory import Inventory
    from economy.resources import ResourceType
    from world.terrain import TerrainType

    assert issubclass(EatBehavior, Behavior)
    assert ResourceType.GOLD in ResourceType
    assert Performative.INFORM in Performative
    # Constructors that need no external services should not raise.
    assert EventBus().subscribers == {}
    assert Inventory().items == {}
    assert Message.__name__ == "Message"
    assert TerrainType.GRASS in TerrainType


def test_behavior_is_abstract() -> None:
    """The Behavior interface cannot be instantiated directly."""
    from ai.behaviors import Behavior

    with pytest.raises(TypeError):
        Behavior()  # type: ignore[abstract]


def test_mesa_agents_wired() -> None:
    """Mesa-dependent agent classes import and form the expected hierarchy."""
    pytest.importorskip("mesa")

    from agents.base_agent import BaseAgent
    from agents.farmer import Farmer
    from agents.villager import Villager
    from agents.wolf import Wolf

    assert issubclass(Villager, BaseAgent)
    assert issubclass(Farmer, Villager)
    assert issubclass(Wolf, BaseAgent)

    # BaseAgent is abstract (it declares an abstract ``step``).
    with pytest.raises(TypeError):
        BaseAgent(model=None)  # type: ignore[abstract, arg-type]


def test_bootstrap_wires_object_graph() -> None:
    """The composition root builds a runnable (but un-setup) object graph."""
    pytest.importorskip("mesa")

    from core.bootstrap import Application, bootstrap

    app = bootstrap(headless=True)
    assert isinstance(app, Application)
    assert app.engine.model is app.model
    assert app.engine.renderer is None  # Headless.
