"""Inventory.

A quantity store mapping :class:`~economy.resources.ResourceType` to integer
counts. Used by agents (what they carry) and buildings (what they stockpile).
Optionally bounded by a carrying capacity.

The container structure and public API are defined here; mutation logic is
future work.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from economy.resources import ResourceType


class Inventory:
    """A bounded (or unbounded) store of resources.

    Attributes:
        capacity: Maximum total units storable; ``None`` means unbounded.
        items: Current quantities keyed by resource type.
    """

    def __init__(self, capacity: int | None = None) -> None:
        """Initialize an empty inventory.

        Args:
            capacity: Optional maximum total units; ``None`` for unbounded.
        """
        self.capacity: int | None = capacity
        self.items: dict[ResourceType, int] = {}

    def add(self, resource: ResourceType, quantity: int) -> int:
        """Add units of a resource, respecting capacity.

        Args:
            resource: The resource type to add.
            quantity: The number of units to add.

        Returns:
            The number of units actually added (may be less if capacity binds).
        """
        if quantity <= 0:
            return 0
        if self.capacity is not None:
            quantity = min(quantity, self.capacity - self.total())
        if quantity <= 0:
            return 0
        self.items[resource] = self.items.get(resource, 0) + quantity
        return quantity

    def remove(self, resource: ResourceType, quantity: int) -> int:
        """Remove units of a resource.

        Args:
            resource: The resource type to remove.
            quantity: The number of units to remove.

        Returns:
            The number of units actually removed (bounded by what is held).
        """
        removed = min(max(0, quantity), self.items.get(resource, 0))
        if removed:
            self.items[resource] -= removed
        return removed

    def quantity_of(self, resource: ResourceType) -> int:
        """Return how many units of a resource are held.

        Args:
            resource: The resource type to query.

        Returns:
            The held quantity (``0`` if none).
        """
        return self.items.get(resource, 0)

    def total(self) -> int:
        """Return the total number of units held across all resources."""
        return sum(self.items.values())
