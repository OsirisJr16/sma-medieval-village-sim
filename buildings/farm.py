"""Farm building.

A workplace where farmers grow and harvest crops. Produces food that is stored
and supplied to the village and market.
"""

from __future__ import annotations

from buildings.building import BaseBuilding
from config.constants import BuildingType


class Farm(BaseBuilding):
    """A crop-producing workplace."""

    building_type: BuildingType = BuildingType.FARM

    # TODO: Add crop fields, growth stage, and yield tracking.
    # TODO: Provide a harvest service used by the work behavior.
