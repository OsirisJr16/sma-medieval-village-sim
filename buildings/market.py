"""Market building.

The physical marketplace on the map where agents gather to trade. It hosts an
:class:`economy.market.Market` (the trading *mechanism*); this class models the
*structure* — the place agents walk to. Named :class:`MarketBuilding` to avoid
ambiguity with the economic :class:`~economy.market.Market`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from buildings.building import BaseBuilding
from config.constants import BuildingType

if TYPE_CHECKING:
    from economy.market import Market


class MarketBuilding(BaseBuilding):
    """The physical marketplace structure.

    Attributes:
        market: The economic market mechanism hosted here.
    """

    building_type: BuildingType = BuildingType.MARKET

    # TODO: Bind the hosted economic Market instance during setup.
    market: Market | None = None

    # TODO: Provide a trading service used by the trade behavior.
