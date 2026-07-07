"""House building.

A residence where villagers sleep to restore energy and shelter from weather.
Assigned to villagers as their ``home``.
"""

from __future__ import annotations

from buildings.building import BaseBuilding
from config.constants import BuildingType


class House(BaseBuilding):
    """A villager residence."""

    building_type: BuildingType = BuildingType.HOUSE

    # TODO: Add residency capacity and a list of resident villagers.
    # TODO: Provide a rest/shelter service used by the sleep behavior.
