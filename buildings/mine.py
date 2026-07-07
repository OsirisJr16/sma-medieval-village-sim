"""Mine building.

A workplace where miners extract ore and stone. Depletes over time and supplies
raw materials to the blacksmith and builders.
"""

from __future__ import annotations

from buildings.building import BaseBuilding
from config.constants import BuildingType


class Mine(BaseBuilding):
    """An ore/stone extraction workplace."""

    building_type: BuildingType = BuildingType.MINE

    # TODO: Add remaining deposit amount and extraction rate.
    # TODO: Provide an extraction service used by the work behavior.
