"""Blacksmith building.

A workplace that refines raw materials (ore, wood) into processed goods such as
tools. Bridges raw resource gathering and higher-value production.
"""

from __future__ import annotations

from buildings.building import BaseBuilding
from config.constants import BuildingType


class Blacksmith(BaseBuilding):
    """A crafting workplace that produces tools and metalwork."""

    building_type: BuildingType = BuildingType.BLACKSMITH

    # TODO: Add crafting recipes and an input/output material buffer.
    # TODO: Provide a crafting service used by the work behavior.
