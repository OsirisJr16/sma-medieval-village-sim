"""Economic goods.

Defines the tradable resource *types* that flow through the economy — the
abstract commodities (wheat, wood, ore, ...) as opposed to the physical
:mod:`world.resources` nodes they are harvested from. Currency is modeled as a
resource type so trades can be expressed uniformly.
"""

from __future__ import annotations

from enum import StrEnum


class ResourceType(StrEnum):
    """Tradable commodity types."""

    # Raw materials
    WOOD = "wood"
    STONE = "stone"
    ORE = "ore"

    # Food
    WHEAT = "wheat"
    BREAD = "bread"
    MEAT = "meat"

    # Processed goods
    TOOLS = "tools"

    # Currency
    GOLD = "gold"

    # TODO: Expand the commodity list and group by category as the economy
    #       and crafting chains are designed.
