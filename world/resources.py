"""World resource nodes.

Represents harvestable resources placed on the map — trees to fell, ore veins to
mine, berry bushes to forage, water to draw. These are the *spatial, physical*
sources of raw materials, distinct from the *economic* goods modeled in
:mod:`economy.resources`.

Only structure is defined; placement, depletion, and regrowth are future work.
"""

from __future__ import annotations

from enum import StrEnum


class ResourceNodeType(StrEnum):
    """Kinds of harvestable world resource nodes."""

    TREE = "tree"
    ORE_VEIN = "ore_vein"
    BERRY_BUSH = "berry_bush"
    WATER_SOURCE = "water_source"
    STONE_DEPOSIT = "stone_deposit"


class ResourceNode:
    """A single harvestable node at a map cell.

    Attributes:
        node_type: The kind of resource this node yields.
        position: The ``(x, y)`` cell the node occupies.
        amount: Remaining harvestable quantity.
        max_amount: Capacity used when regrowing renewable nodes.
    """

    def __init__(
        self,
        node_type: ResourceNodeType,
        position: tuple[int, int],
        amount: int,
    ) -> None:
        """Initialize a resource node.

        Args:
            node_type: The kind of resource.
            position: The cell the node occupies.
            amount: Initial harvestable quantity.
        """
        self.node_type: ResourceNodeType = node_type
        self.position: tuple[int, int] = position
        self.amount: int = amount
        self.max_amount: int = amount

    def harvest(self, quantity: int) -> int:
        """Harvest up to ``quantity`` units from this node.

        Args:
            quantity: The requested amount to harvest.

        Returns:
            The amount actually harvested (bounded by availability).
        """
        # TODO: Decrement `amount` and return the harvested quantity.
        raise NotImplementedError("ResourceNode.harvest is not implemented yet.")


class ResourceField:
    """Collection of all resource nodes on the map.

    Attributes:
        width: Field width in cells.
        height: Field height in cells.
    """

    def __init__(self, width: int, height: int) -> None:
        """Initialize an empty resource field.

        Args:
            width: Field width in cells.
            height: Field height in cells.
        """
        self.width: int = width
        self.height: int = height

        # TODO: Index nodes by position for O(1) spatial lookup.

    def regrow(self) -> None:
        """Regenerate renewable resource nodes by one tick."""
        # TODO: Grow renewable nodes toward their max_amount.
        raise NotImplementedError("ResourceField.regrow is not implemented yet.")
