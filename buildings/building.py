"""Abstract base building.

:class:`BaseBuilding` is the common ancestor of all structures. It captures the
shared scaffolding: a footprint on the map, a storage inventory, occupancy, and
construction/integrity state. Concrete buildings specialize the services they
offer.

Buildings are modeled as plain domain objects (not Mesa agents) that the world
places on the grid; this keeps their lifecycle independent of agent activation.
Only structure and TODO markers are defined here.
"""

from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

from config.constants import BuildingType

if TYPE_CHECKING:
    from economy.inventory import Inventory

# A grid coordinate.
Coord = tuple[int, int]


class BaseBuilding(ABC):
    """Abstract base class for all buildings.

    Attributes:
        building_type: The kind of building (set by subclasses).
        position: The building's anchor ``(x, y)`` cell.
        footprint: Cells occupied by the building.
        storage: The building's resource stockpile.
        occupants: Identifiers of agents currently inside.
        is_built: False while under construction, True once complete.
    """

    #: The building kind; overridden by concrete subclasses.
    building_type: BuildingType

    def __init__(self, position: Coord) -> None:
        """Initialize the building at a map position.

        Args:
            position: The anchor cell the building occupies.
        """
        self.position: Coord = position
        self.footprint: list[Coord] = [position]
        self.storage: Inventory | None = None
        self.occupants: list[object] = []
        self.is_built: bool = False

    def enter(self, agent: object) -> None:
        """Register an agent as being inside the building.

        Args:
            agent: The agent entering.
        """
        # TODO: Add the agent to occupants (respecting any capacity limit).
        raise NotImplementedError("BaseBuilding.enter is not implemented yet.")

    def leave(self, agent: object) -> None:
        """Remove an agent from the building's occupants.

        Args:
            agent: The agent leaving.
        """
        # TODO: Remove the agent from occupants.
        raise NotImplementedError("BaseBuilding.leave is not implemented yet.")
